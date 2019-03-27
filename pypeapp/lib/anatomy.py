import os
import re

from pypeapp.config import update_dict
from pyyaml.lib3 import yaml


class PartialDict(dict):
    ''' Modified dict class as helper.

    If is used as input data for string formatting
    missing keys won't change in string.

    .. code-block:: python
        data = PartialDict({
            'project': 'Turtle King'
        })
        string = '{project} will raise on {date}'
        result = string.format(data)
        __
        result >> 'Turtle King will raise on {date}'
    '''
    def __getitem__(self, item):
        out = super().__getitem__(item)
        if isinstance(out, dict):
            return '{'+item+'}'
        return out

    def __missing__(self, key):
        return '{'+key+'}'


class Anatomy:
    ''' Anatomy module help get anatomy and format anatomy with entered data.
    TODO: should be able to load Project specific anatomy.
    Anatomy string Example:
        "{$APP_PATH}/{project[code]}_{task}_v{version:0>3}<_{comment}>
        - $APP_PATH: environment variable
        - project[code]: dictionary fill {'project':{'code': 'PROJECT_CODE'}}
        - task, version: basic string format 'TASK_NAME', 1
        - comment: optional key, if not entered '<_{comment}>' will be removed


    :param project_name: Project name to look on project's anatomy overrides.
    :type project_name: str
    '''
    anatomy = None

    def __init__(self, project_name=None):
        self.project_name = project_name

    def _discover(self):
        ''' Loads anatomy from yaml.
        Default anatomy is loaded all the time.
        TODO: if project_name is set also tries to find project's
        anatomy overrides.

        :rtype: dictionary
        '''
        # TODO: right way to get templates path
        path = r'{PYPE_APP_ROOT}\repos\pype-templates\anatomy\default.yaml'
        path = path.format(**os.environ)
        with open(path, 'r') as stream:
            try:
                anatomy = yaml.load(stream, Loader=yaml.loader.Loader)
            except yaml.YAMLError as exc:
                print(exc)

        if self.project_name is not None:
            project_configs_path = os.path.normpath(
                os.environ['PYPE_PROJECT_CONFIGS']
            )
            project_config_items = [
                project_configs_path, project_name, 'anatomy', 'default.yaml'
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
            anatomy = update_dict(anatomy, proj_anatomy)
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
            except KeyError:
                invalid_optionals.append(group)
        for group in invalid_optionals:
            template = template.replace(group, "")

        solved = template.format_map(data)

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
        regex_patern = '\{\w*\[[^\}]*\]\}'
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
                v = v.format_map(data)
            except (KeyError, TypeError):
                pass
            subdict[k] = v

        return solved.format_map(subdict)

