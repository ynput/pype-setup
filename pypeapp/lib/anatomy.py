import os
import re
import json
import copy
import platform
import collections
import numbers
try:
    StringType = basestring
except NameError:
    StringType = str

from . import config
from .log import PypeLogger

try:
    import ruamel.yaml as yaml
except ImportError:
    print("yaml module wasn't found, skipping anatomy")
else:
    directory = os.path.join(
        os.environ.get("PYPE_ENV", ""), "Lib", "site-packages", "ruamel"
    )
    file_path = os.path.join(directory, "__init__.py")
    if os.path.exists(directory) and not os.path.exists(file_path):
        print(
            "{0} found but not {1}. Patching ruamel.yaml...".format(
                directory, file_path
            )
        )
        open(file_path, "a").close()

log = PypeLogger().get_logger(__name__)


class Anatomy:
    ''' Anatomy module helps to keep project settings.

    :param project_name: Project name to look on project's anatomy overrides.
    :type project_name: str
    '''

    def __init__(self, project=None, keep_updated=False):
        if not project:
            project = os.environ.get("AVALON_PROJECT")

        self._templates = Templates(parent=self)
        self._roots = Roots(parent=self)
        self.project_name = project
        self.keep_updated = keep_updated

    @property
    def templates(self):
        return self._templates

    def format(self, *args, **kwargs):
        return self._templates.format(*args, **kwargs)

    def format_all(self, *args, **kwargs):
        return self._templates.format_all(*args, **kwargs)

    @property
    def roots(self):
        return self._roots


class TemplateMissingKey(Exception):
    """Exception for cases when key does not exist in Anatomy."""

    msg = "Anatomy key does not exist: `anatomy{0}`."

    def __init__(self, parents):
        parent_join = "".join(["[\"{0}\"]".format(key) for key in parents])
        super(TemplateMissingKey, self).__init__(
            self.msg.format(parent_join)
        )


class TemplateUnsolved(Exception):
    """Exception for unsolved template when strict is set to True."""

    msg = (
        "Anatomy template \"{0}\" is unsolved.{1}{2}"
    )
    invalid_types_msg = " Keys with invalid DataType: `{0}`."
    missing_keys_msg = " Missing keys: \"{0}\"."

    def __init__(self, template, missing_keys, invalid_types):
        invalid_type_items = []
        for _key, _type in invalid_types.items():
            invalid_type_items.append(
                "\"{0}\" {1}".format(_key, str(_type))
            )

        invalid_types_msg = ""
        if invalid_type_items:
            invalid_types_msg = self.invalid_types_msg.format(
                ", ".join(invalid_type_items)
            )

        missing_keys_msg = ""
        if missing_keys:
            missing_keys_msg = self.missing_keys_msg.format(
                ", ".join(missing_keys)
            )
        super(TemplateUnsolved, self).__init__(
            self.msg.format(template, missing_keys_msg, invalid_types_msg)
        )


class TemplateResult(str):
    """Result (formatted template) of anatomy with most of information in.

    used_values <dict>
        - Dictionary of template filling data (only used keys).
    solved <bool>
        - For check if all required keys were filled.
    template <str>
        - Original template.
    missing_keys <list>
        - Missing keys that were not in the data.
        - With optional keys.
    invalid_types <dict {key: type}>
        - Key was found in data, but value had not allowed DataType.
        - Allowed data types are `numbers` and `str`(`basestring`)
    """

    def __new__(
        cls, filled_template, template, solved,
        used_values, missing_keys, invalid_types
    ):
        new_obj = super(TemplateResult, cls).__new__(cls, filled_template)
        new_obj.used_values = used_values
        new_obj.solved = solved
        new_obj.template = template
        new_obj.missing_keys = list(set(missing_keys))
        _invalid_types = {}
        for invalid_type in invalid_types:
            for key, val in invalid_type.items():
                if key in _invalid_types:
                    continue
                _invalid_types[key] = val
        new_obj.invalid_types = _invalid_types
        return new_obj


class TemplatesDict(dict):
    """Holds and wrap TemplateResults for easy bug report."""

    def __init__(self, in_data, key=None, parent=None, strict=None):
        super(TemplatesDict, self).__init__()
        for _key, _value in in_data.items():
            if isinstance(_value, dict):
                _value = self.__class__(_value, _key, self)
            self[_key] = _value

        self.key = key
        self.parent = parent
        self.strict = strict
        if self.parent is None and strict is None:
            self.strict = True

    def __getitem__(self, key):
        # Raise error about missing key in anatomy.yaml
        if key not in self.keys():
            hier = self.hierarchy()
            hier.append(key)
            raise TemplateMissingKey(hier)

        value = super(TemplatesDict, self).__getitem__(key)
        if isinstance(value, self.__class__):
            return value

        # Raise exception when expected solved templates and it is not.
        if (
            self.raise_on_unsolved
            and (hasattr(value, "solved") and not value.solved)
        ):
            raise TemplateUnsolved(
                value.template, value.missing_keys, value.invalid_types
            )
        return value

    @property
    def raise_on_unsolved(self):
        """To affect this change `strict` attribute."""
        if self.strict is not None:
            return self.strict
        return self.parent.raise_on_unsolved

    def hierarchy(self):
        """Return dictionary keys one by one to root parent."""
        if self.parent is None:
            return []

        hier_keys = []
        par_hier = self.parent.hierarchy()
        if par_hier:
            hier_keys.extend(par_hier)
        hier_keys.append(self.key)

        return hier_keys

    @property
    def missing_keys(self):
        """Return missing keys of all children templates."""
        missing_keys = []
        for value in self.values():
            missing_keys.extend(value.missing_keys)
        return list(set(missing_keys))

    @property
    def invalid_types(self):
        """Return invalid types of all children templates."""
        invalid_types = {}
        for value in self.values():
            for invalid_type in value.invalid_types:
                _invalid_types = {}
                for key, val in invalid_type.items():
                    if key in invalid_types:
                        continue
                    _invalid_types[key] = val
                invalid_types = config.update_dict(
                    invalid_types, _invalid_types
                )
        return invalid_types

    @property
    def used_values(self):
        """Return used values for all children templates."""
        used_values = {}
        for value in self.values():
            used_values = config.update_dict(used_values, value.used_values)
        return used_values

    def get_solved(self):
        """Get only solved templates."""
        result = {}
        for key, value in self.items():
            if isinstance(value, self.__class__):
                value = value.get_solved()
                if not value:
                    continue
                result[key] = value

            elif (
                not hasattr(value, "solved") or
                value.solved
            ):
                result[key] = value
        return self.__class__(result, key=self.key, parent=self.parent)


class Templates:
    key_pattern = re.compile(r"(\{.*?[^{0]*\})")
    key_padding_pattern = re.compile(r"([^:]+)\S+[><]\S+")
    sub_dict_pattern = re.compile(r"([^\[\]]+)")
    optional_pattern = re.compile(r"(<.*?[^{0]*>)[^0-9]*?")

    inner_key_pattern = re.compile(r"(\{@.*?[^{}0]*\})")
    inner_key_name_pattern = re.compile(r"\{@(.*?[^{}0]*)\}")

    def __init__(
        self, project_name=None, keep_updated=False, roots=None, parent=None
    ):
        self._keep_updated = keep_updated
        self._project_name = project_name
        self._roots = roots
        self.parent = parent
        if parent is None and project_name is None:
            log.warning((
                "It is expected to enter project_name if Templates are created"
                " out of Anatomy."
            ))

        self.loaded_project = None
        self._templates = None

    def __getitem__(self, key):
        return self.templates[key]

    def get(self, key, default=None):
        return self.templates.get(key, default)

    @property
    def project_name(self):
        if self.parent:
            return self.parent.project_name
        return self._project_name

    @property
    def keep_updated(self):
        if self.parent:
            return self.parent.keep_updated
        return self._keep_updated

    @property
    def roots(self):
        if self.parent:
            return self.parent.roots
        return self._roots

    @property
    def templates(self):
        if self.parent is None and self.keep_updated:
            project = os.environ.get("AVALON_PROJECT", None)
            if project is not None and project != self.project_name:
                self._project_name = project

        if self.project_name != self.loaded_project:
            self._templates = None

        if self._templates is None:
            self._templates = self._discover()
            self.loaded_project = self.project_name
        return self._templates

    @staticmethod
    def default_templates():
        path = "{PYPE_CONFIG}/anatomy/default.yaml"
        path = os.path.normpath(path.format(**os.environ))
        with open(path, "r") as stream:
            # QUESTION Should we not raise exception if file is invalid?
            default_templates = yaml.load(
                stream, Loader=yaml.loader.Loader
            )

        return Templates.solve_template_inner_links(default_templates)

    def _discover(self):
        ''' Loads anatomy templates from yaml.
        Default templates are loaded if project is not set or project does
        not have set it's own.
        TODO: create templates if not exist.

        :rtype: dictionary
        '''

        if self.project_name is not None:
            project_configs_path = os.path.normpath(
                os.environ.get("PYPE_PROJECT_CONFIGS", "")
            )
            project_config_items = [
                project_configs_path,
                self.project_name,
                "anatomy",
                "default.yaml"
            ]
            project_templates_path = os.path.sep.join(project_config_items)
            if os.path.exists(project_templates_path):
                # QUESTION Should we not raise exception if file is invalid?
                with open(project_templates_path, "r") as stream:
                    proj_templates = yaml.load(
                        stream, Loader=yaml.loader.Loader
                    )
                return Templates.solve_template_inner_links(proj_templates)

            else:
                # QUESTION create project specific if not found?
                log.warning((
                    "Project \"{0}\" does not have his own templates."
                    " Trying to use default."
                ).format(self.project_name))

        return self.default_templates()

    @classmethod
    def replace_inner_keys(cls, matches, value, key_values, key):
        for match in matches:
            anatomy_sub_keys = (
                cls.inner_key_name_pattern.findall(match)
            )
            for anatomy_sub_key in anatomy_sub_keys:
                replace_value = key_values.get(anatomy_sub_key)
                if replace_value is None:
                    raise KeyError((
                        "Anatomy templates can't be filled."
                        " Anatomy key `{0}` has"
                        " invalid inner key `{1}`."
                    ).format(key, anatomy_sub_key))

                valid = isinstance(replace_value, (numbers.Number, StringType))
                if not valid:
                    raise ValueError((
                        "Anatomy templates can't be filled."
                        " Anatomy key `{0}` has"
                        " invalid inner key `{1}`"
                        " with value `{2}`."
                    ).format(key, anatomy_sub_key, str(replace_value)))

                value = value.replace(match, str(replace_value))

        return value

    @classmethod
    def solve_template_inner_links(cls, templates):
        default_key_value_keys = []
        for key, value in templates.items():
            if isinstance(value, dict):
                continue
            default_key_value_keys.append(key)

        default_key_values = {}
        for key in default_key_value_keys:
            default_key_values[key] = templates.pop(key)

        keys_by_subkey = {}
        for sub_key, sub_value in templates.items():
            key_values = {}
            key_values.update(default_key_values)
            key_values.update(sub_value)

            all_filled = False
            while not all_filled:
                found = False
                keys_to_pop = []
                for key, value in key_values.items():
                    if isinstance(value, StringType):
                        matches = cls.inner_key_pattern.findall(value)
                        if not matches:
                            continue

                        found = True
                        key_values[key] = cls.replace_inner_keys(
                            matches, value, key_values, key
                        )
                        continue

                    elif not isinstance(value, dict):
                        continue

                    for _key, _value in value.items():
                        matches = cls.inner_key_pattern.findall(_value)
                        if not matches:
                            continue

                        found = True
                        key_values[key][_key] = cls.replace_inner_keys(
                            matches, _value, key_values,
                            "{}.{}".format(key, _key)
                        )

                if not found:
                    break

            keys_by_subkey[sub_key] = key_values

        all_filled = False
        while not all_filled:
            found = False
            keys_to_pop = []
            for key, value in default_key_values.items():
                matches = None
                if isinstance(value, StringType):
                    matches = cls.inner_key_pattern.findall(value)

                if not matches:
                    keys_by_subkey[key] = value
                    keys_to_pop.append(key)
                    continue

                found = True
                default_key_values[key] = cls.replace_inner_keys(
                    matches, value, default_key_values, key
                )

            for key in keys_to_pop:
                default_key_values.pop(key)

            if not found:
                all_filled = True
                break

        for key, value in default_key_values.items():
            if key not in keys_by_subkey:
                keys_by_subkey[key] = value

        return keys_by_subkey

    def _filter_optional(self, template, data):
        """Filter invalid optional keys.

        Invalid keys may be missing keys of with invalid value DataType.

        :param template: Anatomy template which will be formatted.
        :type template: str
        :param data: Containing keys to be filled into template.
        :type data: dict
        :rtype: str
        """

        # Remove optional missing keys
        missing_keys = []
        invalid_types = []
        for optional_group in self.optional_pattern.findall(template):
            _missing_keys = []
            _invalid_types = []
            for optional_key in self.key_pattern.findall(optional_group):
                key = str(optional_key[1:-1])
                key_padding = list(
                    self.key_padding_pattern.findall(key)
                )
                if key_padding:
                    key = key_padding[0]

                validation_result = self._validate_data_key(
                    key, data
                )
                missing_key = validation_result["missing_key"]
                invalid_type = validation_result["invalid_type"]

                valid = True
                if missing_key is not None:
                    _missing_keys.append(missing_key)
                    valid = False

                if invalid_type is not None:
                    _invalid_types.append(invalid_type)
                    valid = False

                if valid:
                    try:
                        optional_key.format(**data)
                    except KeyError:
                        _missing_keys.append(key)
                        valid = False

            valid = len(_invalid_types) == 0 and len(_missing_keys) == 0
            missing_keys.extend(_missing_keys)
            invalid_types.extend(_invalid_types)
            replacement = ""
            if valid:
                replacement = optional_group[1:-1]

            template = template.replace(optional_group, replacement)
        return (template, missing_keys, invalid_types)

    def _validate_data_key(self, key, data):
        result = {
            "missing_key": None,
            "invalid_type": None
        }

        # check if key expects subdictionary keys (e.g. project[name])
        key_subdict = list(self.sub_dict_pattern.findall(key))
        used_keys = []
        if len(key_subdict) <= 1:
            if key not in data:
                result["missing_key"] = key
                return result

            used_keys.append(key)
            value = data[key]

        else:
            value = copy.deepcopy(data)
            missing_key = False
            invalid_type = False
            for sub_key in key_subdict:
                if (
                    value is None or
                    (hasattr(value, "items") and sub_key not in value)
                ):
                    missing_key = True
                    used_keys.append(sub_key)
                    break

                elif not hasattr(value, "items"):
                    invalid_type = True
                    break

                used_keys.append(sub_key)
                value = value.get(sub_key)

            if missing_key or invalid_type:
                if len(used_keys) == 0:
                    invalid_key = key_subdict[0]
                else:
                    invalid_key = used_keys[0]
                    for idx, sub_key in enumerate(used_keys):
                        if idx == 0:
                            continue
                        invalid_key += "[{0}]".format(sub_key)

                if missing_key:
                    result["missing_key"] = invalid_key

                elif invalid_type:
                    result["invalid_type"] = {invalid_key: type(value)}

                return result

        valid = isinstance(value, numbers.Number)
        if valid:
            return result

        for inh_class in type(value).mro():
            if inh_class == StringType:
                return result

        result["missing_key"] = key
        result["invalid_type"] = {key: type(value)}
        return result

    def _merge_used_values(self, current_used, keys, value):
        key = keys[0]
        _keys = keys[1:]
        if len(_keys) == 0:
            current_used[key] = value
        else:
            next_dict = {}
            if key in current_used:
                next_dict = current_used[key]
            current_used[key] = self._merge_used_values(
                next_dict, _keys, value
            )
        return current_used

    def _format(self, orig_template, data):
        ''' Figure out with whole formatting.
        Separate advanced keys (*Like '{project[name]}') from string which must
        be formatted separatelly in case of missing or incomplete keys in data.

        :param template: Anatomy template which will be formatted.
        :type template: str
        :param data: Containing keys to be filled into template.
        :type data: dict
        :rtype: TemplateResult
        '''
        template, missing_optional, invalid_optional = (
            self._filter_optional(orig_template, data)
        )
        # Remove optional missing keys
        used_values = {}
        invalid_required = []
        missing_required = []
        replace_keys = []
        for group in self.key_pattern.findall(template):
            orig_key = group[1:-1]
            key = str(orig_key)
            key_padding = list(self.key_padding_pattern.findall(key))
            if key_padding:
                key = key_padding[0]

            validation_result = self._validate_data_key(key, data)
            missing_key = validation_result["missing_key"]
            invalid_type = validation_result["invalid_type"]

            if invalid_type is not None:
                invalid_required.append(invalid_type)
                replace_keys.append(key)
                continue

            if missing_key is not None:
                missing_required.append(missing_key)
                replace_keys.append(key)
                continue

            try:
                value = group.format(**data)
                key_subdict = list(self.sub_dict_pattern.findall(key))
                if len(key_subdict) <= 1:
                    used_values[key] = value

                else:
                    used_values = self._merge_used_values(
                        used_values, key_subdict, value
                    )

            except (TypeError, KeyError):
                missing_required.append(key)
                replace_keys.append(key)

        final_data = copy.deepcopy(data)
        for key in replace_keys:
            key_subdict = list(self.sub_dict_pattern.findall(key))
            if len(key_subdict) <= 1:
                final_data[key] = "{" + key + "}"
                continue

            replace_key_dst = "---".join(key_subdict)
            replace_key_dst_curly = "{" + replace_key_dst + "}"
            replace_key_src_curly = "{" + key + "}"
            template = template.replace(
                replace_key_src_curly, replace_key_dst_curly
            )
            final_data[replace_key_dst] = replace_key_src_curly

        solved = len(missing_required) == 0 and len(invalid_required) == 0

        missing_keys = missing_required + missing_optional
        invalid_types = invalid_required + invalid_optional

        filled_template = template.format(**final_data)
        result = TemplateResult(
            filled_template, orig_template, solved,
            used_values, missing_keys, invalid_types
        )
        return result

    def solve_dict(self, templates, data):
        ''' Solves templates with entered data.

        :param templates: All Anatomy templates which will be formatted.
        :type templates: dict
        :param data: Containing keys to be filled into template.
        :type data: dict
        :rtype: dictionary
        '''
        output = collections.defaultdict(dict)
        for key, orig_value in templates.items():
            if isinstance(orig_value, StringType):
                output[key] = self._format(orig_value, data)
                continue

            # Check if orig_value has items attribute (any dict inheritance)
            if not hasattr(orig_value, "items"):
                # TODO we should handle this case
                output[key] = orig_value
                continue

            for s_key, s_value in self.solve_dict(orig_value, data).items():
                output[key][s_key] = s_value

        return output

    def format_all(self, in_data, only_keys=True):
        ''' Solves templates based on entered data.
        :param data: Containing keys to be filled into template.
        :type data: dict
        :param only_keys: Decides if environ will be used to fill templates
        or only keys in data.
        :type only_keys: bool
        :rtype: dictionary
        Returnes dictionary split into 3 categories: solved/partial/unsolved
        '''
        output = self.format(in_data, only_keys)
        output.strict = False
        return output

    def format(self, in_data, only_keys=True):
        ''' Solves templates based on entered data.
        :param data: Containing keys to be filled into template.
        :type data: dict
        :param only_keys: Decides if environ will be used to fill templates
        or only keys in data.
        :type only_keys: bool
        :rtype: dictionary
        Returnes only solved
        '''
        # Create a copy of inserted data
        data = copy.deepcopy(in_data)

        # Add environment variable to data
        if only_keys is False:
            for key, val in os.environ.items():
                data["$" + key] = val

        # override root value
        roots = self.roots
        if roots:
            data["root"] = roots
        solved = self.solve_dict(self.templates, data)

        return TemplatesDict(solved)


class MissingRootDefinition(Exception):
    pass


class RootItem:
    expected_keys = ["mount", "path"]
    _default_key = "path"

    def __init__(self, root_raw_data, name=None, default_key=None):
        self.raw_data = root_raw_data

        if name is None:
            name = "N/A"
        self.name = name
        if default_key is None:
            default_key = self._default_key
        self.default_key = default_key

        self.data = self.choose_platform(root_raw_data)
        # QUESTION should we add force validation?
        # - if "mount" and "path" are both set
        missing_keys = []
        for key in self.expected_keys:
            if key not in self.data:
                missing_keys.append(key)

        if len(missing_keys) == len(self.expected_keys):
            log.warning("Root key {0} miss all expected keys. {1}".format(
                self.name,
                ", ".join(['"{0}"'.format(key) for key in self.expected_keys])
            ))
            for key in self.expected_keys:
                self.data[key] = None

        elif missing_keys:
            ending = "" if len(missing_keys) == 1 else "s"
            _name = "" if name is None else " item \"{}\"".format(name)
            log.warning(
                "Root{} missing expected key{}: {}".format(
                    _name, ending, ", ".join(missing_keys)
                )
            )

    def choose_platform(self, values, platform_name=None):
        output = {}
        if platform_name is None:
            platform_name = platform.system().lower()

        for key, per_platform_value in values.items():
            if platform_name not in per_platform_value:
                continue
            output[key] = per_platform_value[platform_name]
        return output

    def _root_exists(self, root):
        drive = os.path.splitdrive(root)[0]
        if not os.path.exists(drive + "/"):
            return False
        return True

    def _clean_root(self, path):
        path = path.replace("\\", "/")
        while path.endswith("/"):
            path = path[:-1]
        return path

    def __format__(self, addict):
        value = self.data[self.default_key]
        if value is None:
            raise MissingRootDefinition(
                "Root key {0} miss all expected keys. {1}".format(
                    self.name,
                    ", ".join(
                        ['"{0}"'.format(key) for key in self.expected_keys]
                    )
                )
            )
        return self.data[self.default_key].__format__(addict)

    def __str__(self):
        return self.data[self.default_key]

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)


class Roots:
    def __init__(self, project_name=None, keep_updated=False, parent=None):
        self.loaded_project = None
        self._project_name = project_name
        self._keep_updated = keep_updated

        if parent is None and project_name is None:
            log.warning((
                "It is expected to enter project_name if Roots are created"
                " out of Anatomy."
            ))

        self.parent = parent
        self._roots = None

    @property
    def project_name(self):
        if self.parent:
            return self.parent.project_name
        return self._project_name

    @property
    def keep_updated(self):
        if self.parent:
            return self.parent.keep_updated
        return self._keep_updated

    def check_updates(self):
        if self.parent is None and self.keep_updated:
            project_name = os.environ.get("AVALON_PROJECT")
            if project_name != self.project_name:
                self.project_name = project_name

        if self.project_name != self.loaded_project:
            self._roots = None

        if self._roots is not None:
            return

        self._roots = self._discover()
        self.loaded_project = self.project_name

        # Backwards compatibility
        if self._roots is None:
            self._roots = self._backwards_discover()

    @property
    def roots(self):
        self.check_updates()
        return self._roots

    @staticmethod
    def default_roots():
        defaults_path_items = [
            os.environ["PYPE_CONFIG"],
            "anatomy",
            "roots.json"
        ]
        default_roots_path = os.path.normpath(
            os.path.join(*defaults_path_items)
        )
        with open(default_roots_path, "r") as default_roots_file:
            raw_default_roots = json.load(default_roots_file)

        roots = {}
        for root_key, values in raw_default_roots.items():
            roots[root_key] = RootItem(values, root_key)
        return roots

    def _backwards_discover(self):
        if self.project_name is None:
            return None

        # Return project specific roots
        project_configs_path = os.path.normpath(
            os.environ.get("PYPE_PROJECT_CONFIGS", "")
        )
        project_config_items = [
            project_configs_path,
            self.project_name,
            "system",
            "storage.json"
        ]
        project_storage_path = os.path.sep.join(project_config_items)
        # If path does not exist we assume it is older project without roots
        if not os.path.exists(project_storage_path):
            return None

        with open(project_storage_path, "r") as project_storage_file:
            project_storage = json.load(project_storage_file)

        return RootItem(project_storage["studio"]["projects"])

    def _discover(self):
        ''' Loads root from json.
        Default roots are loaded if project is not set.

        :rtype: dictionary
        '''

        # Return default roots if project is not set
        if self.project_name is None:
            return Roots.default_roots_with_raw()

        # Return project specific roots
        project_configs_path = os.path.normpath(
            os.environ.get("PYPE_PROJECT_CONFIGS", "")
        )
        project_config_items = [
            project_configs_path,
            self.project_name,
            "anatomy",
            "roots.json"
        ]
        project_roots_path = os.path.sep.join(project_config_items)
        # If path does not exist we assume it is older project without roots
        if not os.path.exists(project_roots_path):
            return (None, None)

        with open(project_roots_path, "r") as project_roots_file:
            raw_project_roots = json.load(project_roots_file)

        roots = {}
        for root_key, values in raw_project_roots.items():
            roots[root_key] = RootItem(values, root_key)
        return roots
