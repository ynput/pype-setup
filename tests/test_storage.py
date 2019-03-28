import pytest
import os
from pathlib import Path
from shutil import copyfile
import json
from pypeapp.storage import Storage
from pprint import pprint


class TestStorage():

    # valid json
    _valid_storage = """\
{
    "studio": {
        "projects": {
            "path": {
                "windows": "//store/vfx/projects",
                "darwin": "//Volumes/vfx/projects",
                "linux": "/mnt/vfx/projects"
            },
            "mount": {
                "windows": "P:/vfx",
                "darwin": "",
                "linux": "/studio/pojects/vfx"
            }
        }
    }
}
"""
    # missing mount
    _invalid_storage1 = """\
{
    "studio": {
        "projects": {
            "path": {
                "windows": "//store/vfx/projects",
                "darwin": "//Volumes/vfx/projects",
                "linux": "/mnt/vfx/projects"
            }
        }
    }
}
"""
    # missing darwin
    _invalid_storage2 = """\
{
    "studio": {
        "projects": {
            "path": {
                "windows": "//store/vfx/projects",
                "linux": "/mnt/vfx/projects"
            },
            "mount": {
                "windows": "P:/vfx",
                "linux": "/studio/pojects/vfx"
            }
        }
    }
}
"""

    @pytest.fixture
    def storage_file(self, tmp_path):
        """ Provide valid sample of storage.json

            :param tmp_path: temporary path provided by pytest fixture
            :type tmp_path: path
            :returns: path to json file
            :rtype: string
        """
        json_path = tmp_path / "valid-storage.json"
        with open(json_path.as_posix(), "w") as write_json:
            json.dump(self._valid_storage, write_json)
        return json_path.as_posix()

    @pytest.fixture
    def invalid_storage_file(self, tmp_path):
        """ Provide **invalid** sample of storage.json

            :param tmp_path: temporary path provided by pytest fixture
            :type tmp_path: path
            :returns: path to json file
            :rtype: string
        """
        json_path = tmp_path / "invalid-storage.json"
        with open(json_path.as_posix(), "w") as write_json:
            json.dump(self._invalid_storage1, write_json)
        return json_path.as_posix()

    def setup_storage(self, data, tmp_path, monkeypatch):
        """ setup temporary files to test upon. This will copy schema file
            to temporary directory structure mocking real one, and set
            environment to point there.

            :param data: json data
            :type data: str
            :param tmp_path: pytest fixture for temp path
            :type tmp_path: :class:`pathlib.Path`
            :param monkeypatch: monkeypatch fixture
            :type monkeypatch: monkeypath
            :returns: list with paths to storage.json and its schema
            :rtype: List
        """
        config_test_path = tmp_path / "repos" / "pype-config"
        os.makedirs(config_test_path.as_posix())
        root_path = Path(os.path.abspath('.'))
        storage_schema_path = root_path / "repos" / "pype-config" / "system"
        storage_schema_file = storage_schema_path / "storage_schema.json"
        config_schema_path = config_test_path / "system"
        os.makedirs(config_schema_path.as_posix(), exist_ok=True)
        copyfile(storage_schema_file.as_posix(),
                 os.path.join(config_schema_path.as_posix(),
                              "storage_schema.json"))
        storage_json = config_test_path / "system" / "storage.json"
        self.write_json(storage_json.as_posix(), data)

        monkeypatch.setitem(os.environ,
                            'PYPE_CONFIG',
                            config_test_path.as_posix())
        return [storage_json, storage_schema_file]

    def write_json(self, path, data):
        """ Write provided data as file.

            :param path: path to file
            :type path: str
            :param data: data to write
            :type data: str
        """
        with open(path, "w") as json_file:
            json_file.write(data)

    def test_read_storage_file(self, tmp_path, monkeypatch):
        paths = self.setup_storage(self._valid_storage, tmp_path, monkeypatch)
        s = Storage()
        loaded = s._read_storage_file(paths[0])
        data = json.loads(self._valid_storage)
        assert loaded == data

    @pytest.mark.skip(reason="no schema validation supported yet")
    def test_read_schema_file(self, tmp_path, monkeypatch):
        paths = self.setup_storage(self._valid_storage, tmp_path, monkeypatch)
        s = Storage()
        loaded = s._read_schema(paths[1])
        data = json.load(paths[1])
        assert loaded == data

    @pytest.mark.skip(reason="no schema validation supported yet")
    def test_validate_schema(self,
                             invalid_storage_file,
                             storage_file,
                             tmp_path,
                             monkeypatch):
        self.setup_storage(self._valid_storage, tmp_path, monkeypatch)
        s = Storage()
        r = s._validate_schema(s._read_storage_file(invalid_storage_file))
        assert r is False
        r = s._validate_schema(s._read_storage_file(storage_file))
        assert r is True

    def test_recurse_dict(self):
        data_dict = json.loads(self._valid_storage)

        paths = list(Storage.paths(data_dict))
        assert paths[0] == ('studio', 'projects', 'path', 'windows')

    def test_format_var(self, tmp_path, monkeypatch):
        self.setup_storage(self._valid_storage, tmp_path, monkeypatch)
        s = Storage()
        vars = s._format_var(json.loads(self._valid_storage))
        pprint(vars)
        assert vars.get('PYPE_STUDIO_PROJECTS_PATH') == '//store/vfx/projects'
        assert vars.get('PYPE_STUDIO_PROJECTS_MOUNT') == 'P:/vfx'

    def test_get_storage_vars(self, tmp_path, monkeypatch):
        self.setup_storage(self._valid_storage, tmp_path, monkeypatch)
        s = Storage()
        env = s.get_storage_vars()
        assert env.get('PYPE_STUDIO_PROJECTS_PATH') == '//store/vfx/projects'
        assert env.get('PYPE_STUDIO_PROJECTS_MOUNT') == 'P:/vfx'
