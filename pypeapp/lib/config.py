import os
import json
from .log import PypeLogger

log = PypeLogger().get_logger(__name__)


def collect_json_path(input_path):
    output = None
    if os.path.isdir(input_path):
        output = {}
        for file in os.listdir(input_path):
            full_path = os.path.sep.join([input_path, file])
            if os.path.isdir(full_path):
                loaded = collect_json_path(full_path)
                if loaded:
                    output[file] = loaded
            else:
                basename, ext = os.path.splitext(os.path.basename(file))
                if ext == '.json':
                    try:
                        with open(full_path, "r") as f:
                            output[basename] = json.load(f)
                    except json.decoder.JSONDecodeError:
                        log.warning(
                            'File "{}" has .json syntax error'.format(file)
                        )
                        output[basename] = {}
    else:
        basename, ext = os.path.splitext(os.path.basename(input_path))
        if ext == '.json':
            with open(input_path, "r") as f:
                output = json.load(f)

    return output


def get_presets(*args):
    '''
    *args specify folder or file in presets to load
    EXAMPLE:
    get_presets('ftrack', 'ftrack_config')
    1.) checks if path "{config_path}/presets/ftrack/ftrack_config" is dir
        and loops through all folders/files and load all jsons into dict
    2.) if path is not dir then checks if exists file:
        "{config_path}/presets/ftrack/ftrack_config.json"
        and returns data from this json
    3.) else return None
    '''
    # config_path should be set from environments?
    config_path = os.environ['PYPE_STUDIO_CONFIG']

    preset_items = [config_path, 'presets']
    preset_items.extend(args)
    config_path = os.path.sep.join(preset_items)
    if not os.path.isdir(config_path):
        config_path += '.json'
        if not os.path.exists(config_path):
            log.error('Preset path was not found: "{}"'.format(config_path))
            return None

    return collect_json_path(config_path)
