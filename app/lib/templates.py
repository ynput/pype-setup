import os
import logging
log = logging.getLogger(__name__)


class Templates(object):

    def __init__(self, *args, **kwargs):
        self.data = dict(*args)

    def update_data(self, args):
        if isinstance(args, dict):
            for k, v in args.items():
                print(k, v)
                self.data[k] = v
                print("added to self.data")


template = Templates({"context": "string"})

print(template.data)

template.update_data({"next": "string"})

print(template.data)


def get_configs():
    ''' Populates all available configs from templates

    Returns:
        configs (obj): dot operator
    '''
    main = {
        "preset_split": "..",
        "file_start": "pype-config.toml"
    }
    templates = {
        "anatomy": dict(),
        "softwares": dict(),
        "system": dict(),
        "colorspace": dict(),
        "dataflow": dict(),
        "metadata": dict(),
        "preset": str()
    }

# example: templates.anatomy.data.


def get_conf_file(
    dir,
    root_file_name,
    default_preset_name="default",
    split_pattern="..",
    representation=".toml"
):
    '''Gets any available `config template` file from given
    **path** and **name**

    Attributes:
        dir (str): path to root directory where files could be searched
        root_file_name (str): root part of name it is searching for
        default_preset_name (str): default preset name
        split_pattern (str): default pattern for spliting name and preset
        representation (str): extention of file used for config files
                              can be ".toml" but also ".conf"

    Returns:
        file_name (str): if matching name found or None
    '''
    conf_file = root_file_name + representation

    try:
        preset = os.environ["PYPE_TEMPLATES_PRESET"]
    except KeyError:
        preset = default_preset_name

    test_files = [
        f for f in os.listdir(dir)
        if split_pattern in f
    ]

    try:
        conf_file = [
            f for f in test_files
            if preset in os.path.splitext(f)[0].split(split_pattern)[1]
            if root_name in os.path.splitext(f)[0].split(split_pattern)[0]
        ][0]
    except IndexError as error:
        log.warning("File is missing '{}' will be"
                    "used basic config file: {}".format(error, conf_file))
        pass

    return conf_file if os.path.exists(os.path.join(dir, conf_file)) else None
