# getting paths from toml templates in .config files
# fill individual teplates in paths
# create config file if there is none

import os
import re
import platform
from .config import _dic_to_nested_obj, toml_config


def get_paths(dict=dict()):
    # will get configuratoins and convert paths templates into proper paths
    conf = _dic_to_nested_obj(dict)
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
            if (isinstance(v, str)) and ("[" in v):
                found_list = re.findall(r'(\[.*?\])', v)
                if source.sys.python.dev.mode:
                    if found_list:
                        v.replace("this", found_list[1])
                        print(v)
            if "path" in k:
                destination[k] = os.path.normpath(v.format(**source))
            if "qt" in k:
                destination[k] = os.path.normpath(v.format(**source))
    return destination
