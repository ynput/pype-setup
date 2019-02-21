"""
        ______                          ______          _____
  _____|\     \  ______   _____   _____|\     \    _____\    \
 /     / |     ||\     \ |     | /     / |     |  /    / |    |
|      |/     /|\ \     \|     ||      |/     /| /    /  /___/|
|      |\____/ | \ \           ||      |\____/ ||    |__ |___|/
|\     \    | /   \ \____      ||\     \    | / |       \
| \     \___|/     \|___/     /|| \     \___|/  |     __/ __
|  \     \             /     / ||  \     \      |\    \  /  \
 \  \_____\           /_____/  / \  \_____\     | \____\/    |
  \ |     |           |     | /   \ |     |     | |    |____/|
   \|_____|           |_____|/     \|_____|      \|____|   | |
                                                       |___|/
              ..---===[[ PyP3 Setup ]]===---...
"""
import json
import os
import jsonschema
from pypeapp import Logger
from pypeapp.lib.Terminal import Terminal


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

    _pype_root = None
    log = Logger().getLogger()
    t = Terminal()

    def __init__(self, pype_root):
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

    def _read_deployment_file(self, file):
        """ Just reads deployment file as a json

            :param file: path to json file
            :type file: string
            :return: parsed json
            :rtype: dict

        """
        with open(file) as deployment_file:
            data = json.load(deployment_file)
        return data

    def _read_schema(self):
        """ Reads json schema from file

            Using hardcoded path in *deploy/deploy_schema-1.0.json*

            :return: parsed json schema
            :rtype: dict
            :raises: DeployException

        """
        schema_file = os.path.join(self._pype_root,
                                   "deploy", "deploy_schema-1.0.json")
        if (not os.path.exists(schema_file)):
            raise DeployException(
                "Cannot find schema to validate `deploy.json`")
        with open(schema_file) as schema:
            data = json.load(schema)
        return data

    def _determine_deployment_file(self):
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
                            "deploy", "deploy.json")
        if (not os.path.exists(file)):
            raise DeployException("Factory `deploy.json` doesn't exist")

        override = None
        with os.scandir(self._pype_root) as i:
            for entry in i:
                if not entry.name.startswith('.') and entry.is_dir():
                    override = os.path.join(entry.path, "deploy.json")
                    if (os.path.exists(override)):
                        file = override
                        break
        return file

    def _validate_schema(self, settings):
        """ Validate json deployment setting against json schema.

            :param settings: Deployment settings from parsed json
            :type settings: dict
            :return: True if validated, False if not
            :rtype: boolean

            .. see::
                :func:`Deployment._read_schema`
                :func:`Deployment.__read_deployment_file`

        """
        schema = self._read_schema()

        try:
            jsonschema.validate(settings, schema)
        except jsonschema.exceptions.ValidationError as e:
            self.log.error(e)
            return False
        except jsonschema.exceptions.SchemaError as e:
            self.log.error(e)
            return False
        return True

    def validate(self):
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
        return True
