# getting paths from toml templates in .config files
# fill individual teplates in paths
# create config file if there is none

import os
import re
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


# pattern = r'[thistext]'
# text = 'this is text and [thistext] and [thisext]'
# print(text.replace(pattern, 'thistext'))


def _convert_all_paths(source, destination):
    if "{root}" in source.app_store.path:
        source.app_store.path = source.app_store.path.format(**source)
    for k, v in destination.items():
        if isinstance(v, dict):
            _convert_all_paths(source, v)
        else:
            if (isinstance(v, str)) and ("[" in v):
                found_list = re.findall(r'(\[.*?\])', v)
                print(found_list)
                if found_list:
                    if source.sys.python.dev.mode:
                        v = v.replace(found_list[1], "").replace(found_list[0], found_list[0].replace(
                            "[", "").replace("]", "").format(**source))
                        print(v)
                    else:
                        if "/bin" in v:
                            v = v.replace(found_list[0], "").replace(
                                "[", "").replace("]", "").format(**source)
                            print(v)
                        else:
                            for i in found_list:
                                try:
                                    v = v.replace(i, i.replace(
                                        "[", "").replace("]", "").format(**source))
                                except:
                                    v = v.replace(i, "")

            if "path" in k:
                destination[k] = os.path.normpath(v.format(**source))
            if "qt" in k:
                destination[k] = os.path.normpath(v.format(**source))
    return destination
