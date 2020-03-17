# storage.py
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

import os
from pathlib import Path
import sys
from pypeapp import Logger
import json
import jsonschema


class PypeStorageException(Exception):
    """ Wrapped custom exception """
    def __init__(self, message):
        super().__init__(message)


class Storage:
    """ Process storage configuration file and set it as environment for later
        use. File will be loaded and validated against json schema.

        Example of storage::

           {
                "path": {
                    "windows": "//store/vfx/projects",
                    "darwin": "//Volumes/vfx/projects",
                    "linux": "/mnt/vfx/projects"
                },
                "mount": {
                    "windows": "P:/vfx",
                    "darwin": ""
                    "linux": "/studio/pojects/vfx"
                }
           }

        This will result in environment variable ``PYPE_STUDIO_PROJECTS_ROOT``
        with content based on platform and ``PYPE_STUDIO_PROJECTS_MOUNT``.
    """

    _prefix = 'PYPE_CORE'
    _config = None
    _log = Logger().get_logger()

    def __init__(self, storage=None):
        """ class constructor.

            :param storage: custom path to storage file
            :type storage: str
            :raises: :class:`PypeStorageException`
        """
        storage = storage or os.environ.get('PYPE_CONFIG')

        if storage is None:
            raise PypeStorageException(
                'Path to storage definitions not provided.'
            )

        self._config = storage

    def _get_storage_path(self):
        """ get paths to storage definition file and its schema

            :returns: resolved path to **storage.json**
            :rtype: str
        """
        config_path = Path(self._config)
        storage_path = config_path / "system" / "core.json"
        return storage_path.as_posix()

    def _read_storage_file(self, file: str) -> dict:
        """ Load JSON file containing storage informations.

            :param file: path to json file
            :type file: str
            :return: parsed json
            :rtype: dict
        """
        with open(file) as storage_file:
            data = json.load(storage_file)
        return data

    @staticmethod
    def paths(tree: dict, cur=()) -> tuple:
        """ Recurse dictionary and return paths to leaf nodes in a tuple

            :param tree: dict to be parsed
            :type tree: dict
            :param output: dictionary of path nodes
            :type output: dict
            :returns: string computed from dictionary
            :rtype: str
        """
        if not tree or not isinstance(tree, dict):
            yield cur
        else:
            for n, s in tree.items():
                for path in Storage.paths(s, cur+(n,)):
                    yield path

    @staticmethod
    def find_by_keys(keys: list, data: dict):
        """ Get value from dictionary by its path - keys in list.

            :param keys: list of keys forming paths
            :type keys: list
            :param data: dict of data
            :type data: dict
            :returns: value defined by path

            Data like::

                {"A": {"B": {"C": "value"}}}

            then ``['A', 'B', 'C']`` will return ``value``
        """
        r = data
        for k in keys:
            r = r[k]
        return r

    def _format_var(self, data, platform=None) -> dict:
        """ Format key name and get its value. This will get paths in
            dictionary, format them with prefix to resemble environment
            variable, use it as a key in dictionary and assign it proper
            value based on current platform.

            :param data: dict of paths
            :type data: dict
            :returns: dict containing formatted keys with their values
            :rtype: dict
        """
        def create_var(path, data):
            out = {}
            value = Storage.find_by_keys(path, data)
            var_name_list = [self._prefix]
            var_name_list.extend(path)
            # make it uppercase, join with underscore and dont use last key
            # as it is platform string
            var_name = "_".join(var_name_list[:-1]).upper()
            out[var_name] = value
            return out
        paths = Storage.paths(data)
        out = {}
        for path in paths:
            # platform should be last item: path[-1]

            if path[-1] == platform:
                out.update(create_var(path, data))
                continue

            if sys.platform == "win32" and path[-1] == "windows":
                out.update(create_var(path, data))
            if sys.platform.startswith("linux") and path[-1] == "linux":
                out.update(create_var(path, data))
            if sys.platform == "darwin" and path[-1] == "darwin":
                out.update(create_var(path, data))
        return out

    def get_storage_dictionary(self):
        """ Get content of storage file as dictionary

            :returns: content as dictionary
            :rtype: dict
        """
        path = self._get_storage_path()
        storage = self._read_storage_file(path)

        return storage

    def get_storage_vars(self, platform=None):
        """ Process storage json and returns formatted variables

            :param platform: platform for which to get variables
            :type platform: str
            :returns: dictionary of formatted variables
            :rtype: dict
        """
        storage = self.get_storage_dictionary()
        env = self._format_var(storage, platform)
        return env

    def update_environment(self):
        """ Process storage json and update environment by formatted variables
            derived from it.
        """
        env = self.get_storage_vars()
        os.environ.update(env)
