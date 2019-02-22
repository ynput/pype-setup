#         ______                          ______          _____
#   _____|\     \  ______   _____   _____|\     \    _____\    \
#  /     / |     ||\     \ |     | /     / |     |  /    / |    |
# |      |/     /|\ \     \|     ||      |/     /| /    /  /___/|
# |      |\____/ | \ \           ||      |\____/ ||    |__ |___|/
# |\     \    | /   \ \____      ||\     \    | / |       \
# | \     \___|/     \|___/     /|| \     \___|/  |     __/ __
# |  \     \             /     / ||  \     \      |\    \  /  \
# \  \_____\           /_____/  / \  \_____\     | \____\/    |
#  \ |     |           |     | /   \ |     |     | |    |____/|
#   \|_____|           |_____|/     \|_____|      \|____|   | |
#                                                       |___|/
#              ..---===[[ PyP3 Setup ]]===---...

import json
import os
import jsonschema
# from pprint import pprint
from pypeapp import Logger
from pypeapp.lib.Terminal import Terminal
from git import Repo


class DeployException(Exception):
    """ Wraps exceptions raised from Deployment.
        Logs them via logger facility
    """
    def __init__(self, message):
        super().__init__(message)
        log = Logger().getLogger()
        t = Terminal()
        log.error(message[3:])
        t.echo("!!! {}".format(message))


class Deployment(object):
    """ Deployment class will load settings from `deploy/deploy.json` or
        if exists, use `deploy/studio/deploy.json`. Then it will process
        information, create `repos` and setup `vendors`
    """

    _deploy_dir = 'deploy'
    _deploy_file = 'deploy.json'
    _schema_file = 'deploy_schema-1.0.json'
    _pype_root = None
    log = Logger().getLogger()
    t = Terminal()

    def __init__(self, pype_root: str):
        """ Init deployment object

        This will initialize object and check if **pype_root** is valid
        location. It will normalize path.

        :param pype_root: Path to Pype setup
        :type pype_root: string
        :raises: DeployException

        """
        normalized = os.path.normpath(pype_root)
        if not os.path.exists(normalized):
            raise DeployException(
                "PYPE_ROOT {} doesn't exists or wasn't set.".format(normalized)
                )
        self._pype_root = normalized
        pass

    def _read_deployment_file(self, file: str) -> dict:
        """ Just reads deployment file as a json

            :param file: path to json file
            :type file: string
            :return: parsed json
            :rtype: dict

        """
        with open(file) as deployment_file:
            data = json.load(deployment_file)
        return data

    def _read_schema(self, file: str) -> dict:
        """ Reads json schema from file

            :param file: path to schema json
            :type file: string
            :return: parsed json schema
            :rtype: dict
            :raises: DeployException

        """
        if (not os.path.exists(file)):
            raise DeployException(
                "Cannot find schema to validate `{}`".format(
                    self._deploy_file))
        with open(file) as schema:
            data = json.load(schema)
        return data

    def _determine_deployment_file(self) -> str:
        """ Determine which deployment file to use.

            We use default one distributed with **Pype**. But if
            under *deploy* directory is another with *deploy.json*, that
            one will take priority.

            :return: Path to deployment file
            :rtype: string
            :raises: DeployException

            .. note::
                If there are more then one directory, only first found is used.

        """
        file = os.path.join(self._pype_root,
                            self._deploy_dir, self._deploy_file)
        if (not os.path.exists(file)):
            raise DeployException("Factory `{}` doesn't exist".format(
                self._deploy_file))

        override = None
        deploy_path = os.path.join(self._pype_root, self._deploy_dir)
        with os.scandir(deploy_path) as i:

            for entry in i:
                if entry.is_dir():
                    override = os.path.join(entry.path, self._deploy_file)
                    if (os.path.exists(override)):
                        file = override
                        break
        return os.path.normpath(file)

    def _validate_schema(self, settings: dict) -> bool:
        """ Validate json deployment setting against json schema.

            :param settings: Deployment settings from parsed json
            :type settings: dict
            :return: True if validated, False if not
            :rtype: boolean

            .. seealso::
                :func:`Deployment._read_schema`
                :func:`Deployment.__read_deployment_file`

        """
        schema_file = os.path.join(
            self._pype_root,
            self._deploy_dir,
            self._schema_file
            )
        schema = self._read_schema(schema_file)

        try:
            jsonschema.validate(settings, schema)
        except jsonschema.exceptions.ValidationError as e:
            self.log.error(e)
            return False
        except jsonschema.exceptions.SchemaError as e:
            self.log.error(e)
            return False
        return True

    def validate(self) -> bool:
        """ Do deployment setting validation.

            First, deployment settings is determined. It can be default
            provided *deploy.json* or overrided one in
            *deploy/somedir/deploy.json*. This file is then validated against
            json schema. Then it will check, if stuff defined in settings is
            present and deployed.

        """
        settings = self._determine_deployment_file()
        if (not self._validate_schema(settings)):
            self.t.echo("Invalid deployment file [ {} ]", format(settings))
            return False

        # go throught repos and find existing
        deploy = self._read_deployment_file()
        for ritem in deploy.get('repositories'):
            test_path = os.path.join(
                self._pype_root, "repos", ritem.get('name'))
            # does repo directory exist?
            if not os.path.exists(test_path):
                return False

            repo = Repo(test_path)
            # bare repo isn't allowed
            if repo.bare is True:
                return False

            head = repo.heads[0]
            # check we are on branch
            if ritem.get('branch'):
                if head.name != ritem.get('branch'):
                    self.log.error(
                        'repo {0} head is not on {1}(!={2}) branch'.format(
                            ritem.get('name'),
                            ritem.get('branch'),
                            head.name
                        ))
                    return False
            commit = head.commit
            # check we are on ref
            if ritem.get('ref'):
                if not commit.hexsha.startswith(ritem.get('ref')):
                    return False
            # check tag
            if ritem.get('tag'):
                tag = next(
                    rtag for rtag in head.tags
                    if rtag["tag"] == ritem.get('tag'))
                if tag.commit.hexsha != commit.hexsha:
                    return False

        return True
