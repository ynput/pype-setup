import os
import json
from .log import PypeLogger

log = PypeLogger().get_logger(__name__)


def load_json(fpath, first_run=False):
    with open(fpath, "r") as opened_file:
        lines = opened_file.read().splitlines()

    standard_json = ""

    for line in lines:
        # Remove all whitespace on both sides
        line = line.strip()

        # Skip blank lines
        if len(line) == 0:
            continue

        standard_json += line

    extra_comma = False
    if ",]" in standard_json or ",}" in standard_json:
        extra_comma = True
    standard_json = standard_json.replace(",]", "]")
    standard_json = standard_json.replace(",}", "}")

    if extra_comma:
        if first_run:
            log.error("Extra comma in json file: \"{}\"".format(fpath))

    # return empty dict if file is empty
    if standard_json == "":
        if first_run:
            log.error("Empty json file: \"{}\"".format(fpath))
        return {}

    return json.loads(standard_json)


def collect_json_from_path(input_path, first_run=False):
    r""" Json collector
    iterate through all subfolders and json files in *input_path*

    Example:
    ``{input_path}/path/to/file.json`` will return dictionary

    .. code-block:: none

        {'path':
            {'to':
                {'file': {file.json data}
            }
        }

    """
    output = None
    if os.path.isdir(input_path):
        output = {}
        for file in os.listdir(input_path):
            full_path = os.path.sep.join([input_path, file])
            if os.path.isdir(full_path):
                loaded = collect_json_from_path(full_path, first_run)
                if loaded:
                    output[file] = loaded
            else:
                basename, ext = os.path.splitext(os.path.basename(file))
                if ext == '.json':
                    output[basename] = load_json(full_path, first_run)
    else:
        basename, ext = os.path.splitext(os.path.basename(input_path))
        if ext == '.json':
            output = load_json(input_path, first_run)

    return output


def get_presets(project=None, first_run=False):
    """ Loads preset files with usage of 'collect_json_from_path'
    Default preset path is set to: ``{PYPE_CONFIG}/presets``
    Project preset path is set to: ``{PYPE_PROJECT_CONFIGS}/*project_name*``
    - environment variable **PYPE_STUDIO_CONFIG** is required
    - **PYPE_STUDIO_CONFIGS** only if want to use overrides per project

    Returns:
    - None

      - if default path does not exist

    - default presets (dict)

      - if project_name is not set
      - if project's presets folder does not exist

    - project presets (dict)

      - if project_name is set and include override data

    """
    # config_path should be set from environments?
    config_path = os.path.normpath(os.environ['PYPE_CONFIG'])
    preset_items = [config_path, 'presets']
    config_path = os.path.sep.join(preset_items)
    if not os.path.isdir(config_path):
        log.error('Preset path was not found: "{}"'.format(config_path))
        return None
    default_data = collect_json_from_path(config_path, first_run)

    if not project:
        project = os.environ.get('AVALON_PROJECT', None)

    if not project:
        return default_data

    project_configs_path = os.environ.get('PYPE_PROJECT_CONFIGS')
    if not project_configs_path:
        return default_data

    project_configs_path = os.path.normpath(project_configs_path)
    project_config_items = [project_configs_path, project, 'presets']
    project_config_path = os.path.sep.join(project_config_items)

    if not os.path.isdir(project_config_path):
        log.warning('Preset path for project {} not found: "{}"'.format(
            project, project_config_path
        ))
        return default_data
    project_data = collect_json_from_path(project_config_path, first_run)

    return update_dict(default_data, project_data)


def get_init_presets(project=None):
    """ Loads content of presets like get_presets() but also evaluate init.json ponter to default presets

    Returns:
    - None

      - if default path does not exist

    - default presets (dict)

      - if project_name is not set
      - if project's presets folder does not exist

    - project presets (dict)

      - if project_name is set and include override data

    """
    presets = get_presets(project)

    try:
        # try if it is not in projects custom directory
        # `{PYPE_PROJECT_CONFIGS}/[PROJECT_NAME]/init.json`
        # init.json define preset names to be used
        p_init = presets["init"]
        presets["colorspace"] = presets["colorspace"][p_init["colorspace"]]
        presets["dataflow"] = presets["dataflow"][p_init["dataflow"]]
    except KeyError:
        log.warning("No projects custom preset available...")
        presets["colorspace"] = presets["colorspace"]["default"]
        presets["dataflow"] = presets["dataflow"]["default"]
        log.info("Presets `colorspace` and `dataflow` loaded from `default`...")

    return presets


def update_dict(main_dict, enhance_dict):
    """ Merges dictionaries by keys.
    Function call itself if value on key is again dictionary

    .. note:: does not overrides whole value on first found key
              but only values differences from enhance_dict
    """
    for key, value in enhance_dict.items():
        if key not in main_dict:
            main_dict[key] = value
        elif isinstance(value, dict) and isinstance(main_dict[key], dict):
            main_dict[key] = update_dict(main_dict[key], value)
        else:
            main_dict[key] = value
    return main_dict
