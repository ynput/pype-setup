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

    def solve_dict(self, input, data, only_keys=True):
        ''' Solves anatomy and split results into:
        - :'solved': Fully solved anatomy strings (missing environs don't
        affect result if `only_keys` is `True`).
        - :'partial': At least one key was filled but still
                      remain keys to fill.
        - :'unsolved': Nothing has changed in these strings.

        :param input: All Anatomy templates which will be formatted.
        :type input: dict
        :param data: Containing keys to be filled into template.
        :type data: dict
        :param only_keys: Decides if environ will be used to fill anatomy
                          or only keys in data.
        :type only_keys: bool
        :rtype: dictionary
        '''
        check_regex_keys = r'\{[^\}]*\}'
        check_regex_env = r'\{\$[^\}]*\}'
        output = {
            'solved': {},
            'partial': {},
            'unsolved': {}
        }

        for key, orig_value in input.items():
            if isinstance(orig_value, dict):
                for s_key, s_value in self.solve_dict(
                    orig_value, data, only_keys
                ).items():
                    for sk_key, sk_value in s_value.items():
                        if not isinstance(output[s_key], dict):
                            output[s_key] = {}
                        if key not in output[s_key]:
                            output[s_key][key] = {}

                        output[s_key][key].update({sk_key: sk_value})

            else:
                value = self._format(orig_value, data)
                solved = True
                matches = re.findall(check_regex_keys, value)
                if only_keys is True:
                    for match in matches:
                        if len(re.findall(check_regex_env, match)) == 0:
                            solved = False
                            break
                else:
                    if len(matches) > 0:
                        solved = False
                if solved is True:
                    output['solved'][key] = value
                elif orig_value == value:
                    output['unsolved'][key] = value
                else:
                    output['partial'][key] = value

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
