import os
import logging

from .studio import (studio_depandecies)
from .formating import format

log = logging.getLogger(__name__)

MAIN = {
    "preset_split": "..",
    "file_start": "pype-config.toml"
}
TEMPLATES = {
    "anatomy": dict(),
    "softwares": dict(),
    "system": dict(),
    "colorspace": dict(),
    "dataflow": dict(),
    "metadata": dict(),
    "preset": str()
}


class Dict_to_obj(dict):
    """ Hiden class

    Converts `dict` dot string object with optional slicing metod

    Output:
        nested dotstring object for example: root.item.subitem.subitem_item
        also nested dict() for example: root["item"].subitem["subitem_item"]

    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self,  *args, **kwargs):
        print("init_parent")
        if kwargs:
            self._to_obj(kwargs)
        else:
            self._to_obj(args)

    def _to_obj(self, args):
        if isinstance(args, tuple):
            for arg in args:
                self._obj(arg)

        if isinstance(args, dict):
            self._obj(args)

    def _obj(self, args):
        for key, value in args.items():
            if isinstance(value, dict):
                value = Dict_to_obj(value)
            self[key] = value


class Templates(Dict_to_obj):

    def __init__(self, *args, **kwargs):
        super(Templates, self).__init__(*args, **kwargs)
        print("init_child")

    def format(self, template="{template_string}", data=dict()):
        return format(template, data)

    def update(self,  *args, **kwargs):
        '''Adding content to object

        Examples:
            - simple way by adding one arg: dict()
                ```python
                self.update({'one': 'one_string', 'two': 'two_string'})```

            - simple way by adding args: arg="string"
                ```python
                self.update(one='one_string', two='two_string')```

            - combined way of adding content: kwards
                ```python
                self.update(
                    one="one_string",
                    two="two_string",
                    three={
                        'one_in_three': 'one_in_three_string',
                        'two_in_three': 'two_in_three_string'
                    )```
        '''
        if kwargs:
            self._to_obj(kwargs)
        else:
            self._to_obj(args)

    def _get_templates(self):
        ''' Populates all available configs from templates

        Returns:
            configs (obj): dot operator
        '''


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
