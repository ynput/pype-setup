import os
import logging
import toml
import platform
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

    platform = platform.system().lower()

    def __init__(self, *args, **kwargs):

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
        assert isinstance(args, dict), "`args` must be <dict>"
        for key, value in args.items():
            if isinstance(value, dict):
                if key not in "path":
                    value = Dict_to_obj(value)
                else:
                    value = value[self.platform]

            if not key.isupper():
                self[key] = value

    def _to_env(self, args):
        if isinstance(args, tuple):
            for arg in args:
                self._env(arg)
        else:
            self._env(args)

    def _env(self, args):
        assert isinstance(args, dict), "`args` must be <dict>"
        for key, value in args.items():
            if isinstance(value, dict):
                value = self._to_env(value)

            if key.isupper():
                os.environ[key] = str(value)


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
        main_list = [t for t in self._process_order
                     if t['type'] in "main"]
        self._distribute(main_list)

        base_list = [t for t in self._process_order
                     if t['type'] in "base"]
        self._distribute(base_list)

        apps_list = [t for t in self._process_order
                     if t['type'] in "apps"]
        self._distribute(apps_list)

        context_list = [t for t in self._process_order
                        if t['type'] in "context"]
        self._distribute(context_list)

        # run trough environ and format values
        # with environ and self also os.path.normpath

        # treat software separatly from system as NUKE_PATH
        # if PYTHONPATH then os.pathsep
        # if PATH then os.pathsep
    def _distribute(self, template_list):
        data = dict()
        for t in template_list:
            content = self.toml_load(t['path'])
            file_name = os.path.split(t['path'])[1].split(".")[0]

            try:
                if "__storage__" in t['path']:
                    data["locations"].update(content)
                elif t['type'] in "context":
                    data[t["department"]].update(content)
                else:
                    data[t["department"]][file_name].update(content)
            except KeyError:
                if "__storage__" in t['path']:
                    data["locations"] = content
                elif t['type'] in "context":
                    data[t["department"]] = content
                else:
                    try:
                        data[t["department"]][file_name] = content
                    except KeyError:
                        data[t["department"]] = dict()
                        data[t["department"]][file_name] = content

        if t['type'] in ["main", "base"]:
            self.update(data)
            self._to_env(data)
            self._format_env_vars()

        elif t['type'] in ["apps"]:
            self.update(data)

        elif t['type'] in ["context"]:
            self.update(data)

    def _format_env_vars(self):
        for k, v in os.environ.items():
            for i in ("PYPE", "AVALON", "PATH", "PYTHONPATH"):
                if i in k:
                    # print("--len of split", len(v.split(":")), v)
                    if not len(v.split(":")) >= 2:
                        os.environ[k] = os.path.normpath(
                            self.format(v, self)
                        )
                    else:
                        os.environ[k] = self.format(v, self)

    def _create_templ_item(self,
                           t_name=None,
                           t_type=None,
                           t_department=None,
                           t_preset=None
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
                root_file_name=t_name,
                preset_name=t_preset
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
            if t['type'] in ["base", "main", "apps"]:
                try:
                    if t['order']:
                        for item in t['order']:
                            self._process_order.append(
                                self._create_templ_item(
                                    item,
                                    t['type'],
                                    t['dir'],
                                    t['preset']
                                )
                            )
                except KeyError as error:
                    # print("// error: {}".format(error))
                    self._process_order.extend(
                        self._create_templ_item(
                            None,
                            t['type'],
                            t['dir'],
                            t['preset']
                        )
                    )
                    pass
            else:
                self._process_order.append(
                    self._create_templ_item(
                        t['file'],
                        t['type'],
                        t['dir'],
                        t['preset']
                    )
                )
        self._process_order

    def toml_load(self, path):
        return toml.load(path)
