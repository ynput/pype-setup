import toml
import os

from ..vendor import toml


class _config_get_toml(dict):
    """
    - converting dict into root.item.subitem.subitem_item
    - can be selected from two ways of working with the entity
      eather dictionary way  root["item"].subitem["subitem_item"]
      or by simple root.item.subitem.subitem_item
      but as practised it is always good to list available items for iterations

      todo: add more functions for attaching new dictionaries into the object
      todo:
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct):
        for key, value in dct.items():
            if hasattr(value, 'keys'):
                value = _config_get_toml(value)
            self[key] = value


def toml_config(file="file_path"):
    '''
    Connecting to file path and reads from it data into object.tree
    '''
    if os.path.isfile(file):
        print(file)
        with open(file, 'r') as f:
            config_file = toml.loads(f.read())
            app = _config_get_toml(config_file)
        # print(app)
        return app
