import os
import re
import copy

from . import config
try:
    import ruamel.yaml as yaml
except ImportError:
    print("yaml module wasn't found, skipping anatomy")
else:
    directory = os.path.join(
        os.environ["PYPE_ENV"], "Lib", "site-packages", "ruamel"
    )
    file_path = os.path.join(directory, "__init__.py")
    if os.path.exists(directory) and not os.path.exists(file_path):
        print(
            "{0} found but not {1}. Patching ruamel.yaml...".format(
                directory, file_path
            )
        )
        open(file_path, "a").close()


class AnatomyMissingKey(Exception):
    """Exception for cases when key does not exist in Anatomy."""

    msg = "Anatomy key does not exist: `anatomy{0}`."

    def __init__(self, parents):
        parent_join = "".join(["[\"{0}\"]".format(key) for key in parents])
        super(AnatomyMissingKey, self).__init__(
            self.msg.format(parent_join)
        )


class AnatomyUnsolved(Exception):
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
        super(AnatomyUnsolved, self).__init__(
            self.msg.format(template, missing_keys_msg, invalid_types_msg)
        )


class AnatomyResult(str):
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
        new_obj = super(AnatomyResult, cls).__new__(cls, filled_template)
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


class AnatomyDict(dict):
    """Holds and wrap AnatomyResults for easy bug report."""

    def __init__(self, in_data, key=None, parent=None, strict=None):
        super(AnatomyDict, self).__init__()
        for _key, _value in in_data.items():
            if not isinstance(_value, AnatomyResult):
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
            raise AnatomyMissingKey(hier)

        value = super(AnatomyDict, self).__getitem__(key)
        if isinstance(value, self.__class__):
            return value

        # Raise exception when expected solved anatomy template and it is not.
        if self.raise_on_unsolved and not value.solved:
            raise AnatomyUnsolved(
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
        """Return missing keys for all children templates."""
        missing_keys = []
        for value in self.values():
            missing_keys.extend(value.missing_keys)
        return list(set(missing_keys))

    @property
    def used_values(self):
        """Return used values for all children templates."""
        used_values = {}
        for value in self.values():
            used_values = config.update_dict(used_values, value.used_values)
        return used_values

class Anatomy:
    ''' Anatomy module help get anatomy and format anatomy with entered data.

    .. todo:: should be able to load Project specific anatomy.

    Anatomy string Example:
    ``{$APP_PATH}/{project[code]}_{task}_v{version:0>3}<_{comment}>``
    - ``$APP_PATH``: environment variable
    - ``project[code]``: dictionary
    fill ``{'project':{'code': 'PROJECT_CODE'}}``
    - task, version: basic string format ``'TASK_NAME', 1``
    - comment: optional key, if not entered ``'<_{comment}>'`` will be removed

    :param project_name: Project name to look on project's anatomy overrides.
    :type project_name: str
    '''

    def __init__(self, project=None, keep_updated=False):
        if not project:
            project = os.environ.get('AVALON_PROJECT', None)

        self._anatomy = None
        self.loaded_project = None
        self.project_name = project
        self.keep_updated = keep_updated

    @property
    def templates(self):
        if self.keep_updated:
            project = os.environ.get("AVALON_PROJECT", None)
            if project is not None and project != self.project_name:
                self.project_name = project

        if self.project_name != self.loaded_project:
            self._anatomy = None

        if self._anatomy is None:
            self._anatomy = self._discover()
            self.loaded_project = self.project_name
        return self._anatomy

    def _discover(self):
        ''' Loads anatomy from yaml.
        Default anatomy is loaded all the time.
        TODO: if project_name is set also tries to find project's
        anatomy overrides.

        :rtype: dictionary
        '''
        # TODO: right way to get templates path
        path = '{PYPE_CONFIG}/anatomy/default.yaml'
        path = os.path.normpath(path.format(**os.environ))
        with open(path, 'r') as stream:
            try:
                anatomy = yaml.load(stream, Loader=yaml.loader.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        if self.project_name is not None:
            project_configs_path = os.path.normpath(
                os.environ.get('PYPE_PROJECT_CONFIGS', "")
            )
            project_config_items = [
                project_configs_path,
                self.project_name,
                'anatomy',
                'default.yaml'
            ]
            project_anatomy_path = os.path.sep.join(project_config_items)
            proj_anatomy = {}
            if os.path.exists(project_anatomy_path):
                with open(project_anatomy_path, 'r') as stream:
                    try:
                        proj_anatomy = yaml.load(
                            stream, Loader=yaml.loader.Loader
                        )
                    except yaml.YAMLError as exc:
                        print(exc)
            anatomy = config.update_dict(anatomy, proj_anatomy)
        return anatomy

    def _solve_with_optional(self, template, data):
        """
        Solving optional elements in template string regarding to available
        keys in used data object.

        :param template: Anatomy template which will be formatted.
        :type template: str
        :param data: Containing keys to be filled into template.
        :type data: PartialDict
        :rtype: str
        """

        # Remove optional missing keys
        pattern = re.compile(r"(<.*?[^{0]*>)[^0-9]*?")
        invalid_optionals = []
        for group in pattern.findall(template):
            try:
                group.format(**data)
                # group without `<` and `>`
                replacement = group[1:-1]
            except KeyError:
                replacement = ""

            template = template.replace(group, replacement)

        solved = format_map(template, data)

        # solving after format optional in second round
        for catch in re.compile(r"(<.*?[^{0]*>)[^0-9]*?").findall(solved):
            if "{" in catch:
                # remove all optional
                solved = solved.replace(catch, "")
            else:
                # Remove optional symbols
                solved = solved.replace(catch, catch[1:-1])

        return solved

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
            valid = True
            for sub_key in key_subdict:
                if (
                    value is None or
                    not hasattr(value, "items") or
                    sub_key not in value
                ):
                    valid = False
                    break

                used_keys.append(sub_key)
                value = value.get(sub_key)

            if not valid:
                if len(used_keys) == 0:
                    invalid_key = key_subdict[0]
                else:
                    invalid_key = used_keys[0]
                    for idx, sub_key in enumerate(used_keys):
                        if idx == 0:
                            continue
                        invalid_key += "[{0}]".format(sub_key)

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

    def _format(self, template, data):
        ''' Figure out with whole formatting.
        Separate advanced keys (*Like '{project[name]}') from string which must
        be formatted separatelly in case of missing or incomplete keys in data.

        :param template: Anatomy template which will be formatted.
        :type template: str
        :param data: Containing keys to be filled into template.
        :type data: dict
        :rtype: str
        '''

        partial_data = PartialDict(data)

        # remove subdict items from string (like 'project[name]')
        subdict = PartialDict()
        count = 1
        store_pattern = 5*'_'+'{:0>3}'
        regex_patern = r"\{\w*\[[^\}]*\]\}"
        matches = re.findall(regex_patern, template)

        for match in matches:
            key = store_pattern.format(count)
            subdict[key] = match
            template = template.replace(match, '{'+key+'}')
            count += 1
        # solve fillind keys with optional keys
        solved = self._solve_with_optional(template, partial_data)
        # try to solve subdict and replace them back to string
        for k, v in subdict.items():
            try:
                v = format_map(v, data)
            except (KeyError, TypeError):
                pass
            subdict[k] = v

        return format_map(solved, subdict)

    def solve_dict(self, templates, data):
        ''' Solves anatomy templates with entered data.

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
        ''' Solves anatomy based on entered data.
        :param data: Containing keys to be filled into template.
        :type data: dict
        :param only_keys: Decides if environ will be used to fill anatomy
        or only keys in data.
        :type only_keys: bool
        :rtype: dictionary
        Returnes dictionary split into 3 categories: solved/partial/unsolved
        '''
        # Create a copy of inserted data
        data = copy.deepcopy(in_data)

        # Add environment variable to data
        if only_keys is False:
            for k, v in os.environ.items():
                data['$'+k] = v

        # Do not override keys if they are already set
        datetime_data = config.get_datetime_data()
        for key, value in datetime_data.items():
            if key not in data:
                data[key] = value

        return self.solve_dict(self.templates, data, only_keys)

    def format(self, data, only_keys=True):
        ''' Solves anatomy based on entered data.
        :param data: Containing keys to be filled into template.
        :type data: dict
        :param only_keys: Decides if environ will be used to fill anatomy
        or only keys in data.
        :type only_keys: bool
        :rtype: dictionary
        Returnes only solved
        '''
        return self.format_all(data, only_keys)['solved']
