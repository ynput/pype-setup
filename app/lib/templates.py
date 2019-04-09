'''
TODO: check if shema validate can be used
TODO: check if precaching function can be used
TODO: cached versions of software tomls to ~/.pype/software
'''

import os
import re
import sys
import toml
import platform
import acre
from copy import deepcopy
from .formating import format

from .utils import (get_conf_file)
from .repos import (solve_dependecies)

from . import (
    Logger
)


log = Logger.getLogger(__name__)


MAIN = {
    "preset_split": "..",
    "main_templates": ["pype-repos", "pype-config"],
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
    os.environ['platform'] = platform

    def __init__(self, *args, **kwargs):
        self._to_obj(args or kwargs)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    # def format(self, *args, **kwargs):

    def _format(self, template="{template_string}", data=dict()):
        return format(template, data)

    def _to_obj(self, args):
        if isinstance(args, tuple):
            for arg in args:
                self._obj(arg)
        else:
            self._obj(args)

    def _iter_dict_to_obj(self, key, value, args):
        if key not in "path":
            value["obj_copy"] = args["obj_copy"]
            value = Dict_to_obj(value)
        else:
            value = value[self.platform]
        return value

    def _obj(self, args):
        assert isinstance(args, dict), "`args` must be <dict>"
        for key, value in args.items():
            if isinstance(value, list or tuple):
                temp_list = list()
                for i, item in enumerate(value):
                    if isinstance(value, dict):
                        value = self._iter_dict_to_obj(key, item, args)
                        temp_list.append(value)
                    else:
                        temp_list.append(item)
                value = temp_list

            if isinstance(value, dict):
                value = self._iter_dict_to_obj(key, value, args)

            if key.isupper():
                continue

            if args["obj_copy"]:
                if key.startswith("_") and not key.startswith("__"):
                    if key[1:] in args.keys():
                        self[key] = value
                else:
                    if key is not "obj_copy":
                        self[key] = value
                        self.format
            else:
                if "{" in str(value) \
                        and not isinstance(value, dict) \
                        and not isinstance(value, list):
                    _key = "_{}".format(key)
                    self[_key] = value
                if key is not "obj_copy":
                    if value:
                        self[key] = value
                        self.format

    def add_to_env_var(self, *args, **kwargs):

        if isinstance(args, tuple):
            for arg in args:
                self._env(arg)
        else:
            self._env(args)

    def _env(self, args):
        '''
        TODO:   read from root config info environment.including
                and implement here
        TODO:
        '''
        assert isinstance(args, dict), "`args` must be <dict>"
        for key, value in args.items():

            if not value:
                continue

            if isinstance(value, dict):
                value = self.add_to_env_var(value)

            # adding to env vars
            if key in self.including:
                if key in "PYTHONPATH":
                    if not isinstance(value, list):
                        paths = os.pathsep.join(
                            os.environ[key].split(os.pathsep)
                            + str(value).split(os.pathsep)
                        )
                        os.environ[key] = paths
                        [sys.path.append(p) for p in paths.split(os.pathsep)]
                    else:
                        paths = os.pathsep.join(
                            os.environ[key].split(os.pathsep)
                            + [os.path.normpath(self._format(str(p), self))
                               for p in value]
                        )
                        os.environ[key] = paths
                        [sys.path.append(p) for p in paths.split(os.pathsep)]
                        # replacing env vars
                else:
                    if not isinstance(value, list):
                        os.environ[key] = os.pathsep.join(
                            str(value).split(os.pathsep) +
                            os.environ[key].split(os.pathsep)
                        )
                    else:
                        os.environ[key] = os.pathsep.join(
                            [os.path.normpath(self._format(str(p), self))
                             for p in value]
                            + os.environ[key].split(os.pathsep)
                        )
                        # replacing env vars
            elif key.isupper() and key not in self.including:
                if isinstance(value, list):
                    try:
                        paths = os.pathsep.join(
                            os.environ[key].split(os.pathsep)
                            + [os.path.normpath(self._format(str(p), self))
                               for p in value]
                        )
                    except KeyError:
                        paths = os.pathsep.join(
                            [os.path.normpath(self._format(str(p), self))
                             for p in value]
                        )
                    os.environ[key] = paths
                else:
                    self._path_to_environ(key, value)

    def _path_to_environ(self, key, value):
        value = str(value)
        frward = re.compile(r'^//').search(value)
        bckwrd = re.compile(r'^\\').search(value)
        url = re.compile(r'://').search(value)

        if frward:
            os.environ[key] = os.path.normpath(
                self._format(value, self))
        elif bckwrd:
            os.environ[key] = self._format(value, self)
        elif url:
            os.environ[key] = self._format(value, self)
        else:
            os.environ[key] = os.path.normpath(
                self._format(value, self))

    def _distribute_args(self):
        ''' Populates all available configs from templates

        Returns:
            configs (obj): dot operator
        '''
        self._distribute(
            [t for t in self._templates
             if t['type'] in self.type]
        )

        if self.environment:
            self.environment = self.global_env + self.environment
        else:
            self.environment = self.global_env

        tools_env = acre.get_tools(self.environment, self.platform)
        env = acre.compute(dict(tools_env, platform=self.platform))
        os.environ = acre.merge(env, dict(os.environ))

    def _distribute(self, template_list):

        if not template_list:
            return

        data = dict(obj_copy=False)
        for t in template_list:
            content = self._toml_load(t['path'])
            file_name = os.path.split(t['path'])[1].split(".")[0]

            try:
                if "storage" in t['path']:
                    data["locations"].update(content)
                elif t['type'] in self.type:
                    data[t['type']].update(content)
                else:
                    data[t['type']][file_name].update(content)
            except KeyError:
                if "storage" in t['path']:
                    data["locations"] = content
                elif t['type'] in self.type:
                    data[t['type']] = content
                else:
                    try:
                        data[t['type']][file_name] = content
                    except KeyError:
                        data[t["type"]] = dict()
                        data[t["type"]][file_name] = content
        if not t:
            pass

        if t['type'] in ["system"]:
            # adds to object as attribute
            self.update(data)
            # adds to environment variables
            self.add_to_env_var(data)
            # format environment variables
            self._format_env_vars()
        else:
            self.update(data)

    def _format_env_vars(self):
        selected_keys = [k for k in list(os.environ.keys())
                         for i in self.filtering
                         if i in k]
        env_to_change = {k: v for k, v in os.environ.items()
                         if k in selected_keys}

        for k, v in env_to_change.items():
            self._path_to_environ(k, v)

        # fix sys.path
        sys_paths = sys.path
        new_sys_paths = [os.path.normpath(self._format(p, self))
                         for p in sys_paths]
        sys.path = []
        [sys.path.append(p)
         for p in new_sys_paths
         if p not in sys.path
         if p is not '.']

    def _create_templ_item(self,
                           t_name=None,
                           t_type=None,
                           t_preset=None
                           ):
        ''' Populates all available configs from templates

        Returns:
            configs (obj): dot operator
        '''

        t_root = os.path.join(self.templates_root, t_type)
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
                        t_type
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

            log.debug("t_root: {} ".format(t_root))
            log.debug("t_file: {} ".format(t_file))

            return {
                "path": os.path.join(t_root, t_file),
                "type": t_type
            }

    def _get_template_files(self):
        '''Gets all available templates from studio-templates

        Returns:
            self._templates (list): ordered list of file paths
                                       and department and type
        '''
        self.install_root = os.path.join(
            os.environ["PYPE_STUDIO_TEMPLATES"],
            "install"
        )
        for template in MAIN["main_templates"]:
            file = get_conf_file(
                dir=self.install_root,
                root_file_name=template
            )
            template_name = template.split("-")[1]
            self[template_name] = self._toml_load(
                os.path.join(
                    self.install_root, file
                ))

        self._templates = list()
        for t in self.config['templates']:
            if t['type'] in ["system", "software"]:
                if t['type'] not in self.type:
                    continue
                try:
                    if t['order']:
                        for item in t['order']:
                            self._templates.append(
                                self._create_templ_item(
                                    item,
                                    t['type'],
                                    t['preset']
                                )
                            )
                except KeyError:
                    if t['type'] not in self.type:
                        continue
                    self._templates.extend(
                        self._create_templ_item(
                            None,
                            t['type'],
                            t['preset']
                        )
                    )
                    pass
            else:
                if t['type'] not in self.type:
                    continue

                self._templates.append(
                    self._create_templ_item(
                        t['file'],
                        t['type'],
                        t['preset']
                    )
                )

        self._templates

        # insert environment setings into object root
        for k, v in self.config['environment'].items():
            self[k] = v

    def _toml_load(self, path):
        return toml.load(path)

    def _toml_dump(self, path, data):
        with open(path, "w+") as file:
            file.write(toml.dumps(data))
        return True

    def format(self, *args, **kwargs):
        args = args or kwargs
        # `obj_copy` True will secure it will preserve
        # original templates in `_key`
        data = dict(obj_copy=True)

        if args and isinstance(args, tuple):
            [data.update(d) for d in args]
        elif args:
            data.update(args)

        self.update(data)

        copy_dict = deepcopy(dict(**self).copy())

        def iter_dict(data):
            for k, v in data.items():
                if isinstance(v, dict):
                    iter_dict(v)
                else:
                    if k.startswith("_"):
                        continue
                    data[k] = os.path.normpath(
                        self._format(str(v), copy_dict)
                    )
            return data

        copy_dict = iter_dict(copy_dict)

        return_obj = Dict_to_obj(iter_dict(copy_dict))
        return return_obj


class Templates(Dict_to_obj):

    def __init__(self, type=None, environment=None, **kwargs):
        assert isinstance(type, list) \
            or type is None, "`type` must be <list>"
        assert isinstance(environment, list) \
            or environment is None, "`environment` must be <list>"

        self.type = type or ["system"]

        self.environment = environment

        super(Templates, self).__init__()

        if "system" in self.type:
            try:
                environ = list(os.environ.keys())
                environ_list = ['AVALON_CORE',
                                'AVALON_LAUNCHER',
                                'PYBLISH_BASE',
                                'PYBLISH_QML',
                                'PYBLISH_LITE',
                                'AVALON_EXAMPLES',
                                'PYPE_STUDIO_TEMPLATES',
                                'PYPE_STUDIO_CONFIG',
                                'PYPE_STUDIO_PROJECTS',
                                'PYTHON_QT5']

                tested = [r for r in environ_list
                          if r in environ]

                if len(environ_list) is not len(tested):
                    raise KeyError('Missing env key')

            except KeyError:
                solve_dependecies()

        self.templates_root = os.path.join(
            os.environ["PYPE_STUDIO_TEMPLATES"],
            "templates"
        )

        # get all toml templates in order
        self._get_template_files()
        self._distribute_args()

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
        self._to_obj(kwargs or args)
