# getting paths from toml templates in .config files
# fill individual teplates in paths
# create config file if there is none

import os
import platform
from .config import _config_get_toml, toml_config

preset_configurations = "My-Testing"


def get_paths(dict={}):

    conf = _config_get_toml(dict)
    required = ['app', 'app_store']
    for i in required:
        path = os.path.normpath(os.path.join(
            dict["root"], ".config.{i}..{preset}".format(i=i, **dict)))
        if i != "app":
            conf.__setitem__(i, toml_config(path))
        else:
            for key, value in toml_config(path).items():
                conf.__setitem__(key, value)

    if dict != {}:
        for k, v in dict.items():
            conf.__setitem__(k, v)
    else:
        pass

    conf = _convert_all_paths(conf, conf)
    return conf


def _convert_all_paths(source, destination):
    if "{root}" in source.app_store.path:
        source.app_store.path = source.app_store.path.format(**source)
    for k, v in destination.items():
        if isinstance(v, dict):
            _convert_all_paths(source, v)
        else:
            if "path" in k:
                destination[k] = os.path.normpath(v.format(**source))
            if "qt" in k:
                destination[k] = os.path.normpath(v.format(**source))
    return destination
