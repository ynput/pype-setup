import os
import logging
import toml

# from .studio import (studio_depandecies)
from .formating import format
from .repos import get_conf_file

AVALON_DEBUG = bool(os.getenv("AVALON_DEBUG"))

log = logging.getLogger(__name__)


MAIN = {
    "preset_split": "..",
    "file_start": "pype-config",
    "representation": ".toml"
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

    def __init__(self, *args, **kwargs):
        print("init_parent")
        if kwargs:
            self._to_obj(kwargs)
        else:
            self._to_obj(args)

    def _to_obj(self, args):
        if isinstance(args, tuple):
            for arg in args:
                self._obj(arg)
        else:
            self._obj(args)

    def _obj(self, args):
        assert isinstance(args, dict), "filter must be <dict>"

        for key, value in args.items():
            if isinstance(value, dict):
                value = Dict_to_obj(value)
            self[key] = value


class Templates(Dict_to_obj):

    def __init__(self, *args, **kwargs):
        super(Templates, self).__init__(*args, **kwargs)
        try:
            self.templates_root = os.environ["PYPE_STUDIO_TEMPLATES"]
        except KeyError:
            self.templates_root = os.path.join(
                os.environ["PYPE_SETUP_ROOT"],
                "studio",
                "studio-templates",
                "templates"
            )
        # get all toml templates in order
        self._get_template_files()
        self._get_templates_to_args()

    def format(self, template="{template_string}", data=dict()):
        # from formating.format()
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

    def _get_templates_to_args(self):
        ''' Populates all available configs from templates

        Returns:
            configs (obj): dot operator
        '''
        for i in self._process_order:
            print("---", i)

    def _create_templ_item(self,
                           t_name=None,
                           t_type=None,
                           t_department=None
                           ):
        ''' Populates all available configs from templates

        Returns:
            configs (obj): dot operator
        '''
        t_root = os.path.join(self.templates_root, t_department)
        list_items = list()
        if not t_name:
            content = [f for f in os.listdir(t_root)
                       if not f.startswith(".")
                       if not os.path.isdir(
                       os.path.join(t_root, f)
                       )]
            for t in content:
                list_items.append(
                    self._create_templ_item(
                        t.replace(MAIN["representation"], ""),
                        t_type,
                        t_department
                    )
                )

        if list_items:
            return list_items
        else:
            t_file = get_conf_file(
                dir=t_root,
                root_file_name=t_name
            )
            return {
                "path": os.path.join(t_root, t_file),
                "department": t_department,
                "type": t_type
            }

    def _get_template_files(self):
        '''Gets all available templates from studio-templates

        Returns:
            self._process_order (list): ordered list of file paths
                                       and department and type
        '''
        file = get_conf_file(
            dir=self.templates_root,
            root_file_name=MAIN["file_start"]
        )

        self._process_order = list()
        for t in self.toml_load(
                os.path.join(
                    self.templates_root, file
                ))['templates']:

            # print("template: ", t)
            if "base" in t['type']:
                try:
                    if t['order']:
                        for item in t['order']:
                            self._process_order.append(
                                self._create_templ_item(
                                    item,
                                    t['type'],
                                    t['dir']
                                )
                            )
                except KeyError as error:
                    # print("// error: {}".format(error))
                    self._process_order.extend(
                        self._create_templ_item(
                            None,
                            t['type'],
                            t['dir']
                        )
                    )
                    pass
            else:
                self._process_order.append(
                    self._create_templ_item(
                        t['file'],
                        t['type'],
                        t['dir']
                    )
                )
        self._process_order

    def toml_load(self, path):
        return toml.load(path)
