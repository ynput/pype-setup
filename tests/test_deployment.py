import pytest
import os
import json
from pprint import pprint
from pathlib import Path
from shutil import copyfile
from git import Repo
from pypeapp.deployment import Deployment
from pypeapp.deployment import DeployException


class TestDeployment(object):
    """ Test class for Deployment
    """

    _valid_deploy_data = {
        "PYPE_CONFIG": "{PYPE_SETUP_PATH}/repos/pype-config",
        "init_env": ["global"],
        "repositories": [
            {
                "name": "avalon-core",
                "url": "git@github.com:pypeclub/avalon-core.git",
                "branch": "develop"
            },
            {
                "name": "avalon-launcher",
                "url": "git@github.com:pypeclub/avalon-launcher.git",
                "branch": "develop"
            }
        ]
    }

    # missing required url
    _invalid_deploy_data = {
        "PYPE_CONFIG": "{PYPE_SETUP_PATH}/repos/pype-config",
        "init_env": ["global"],
        "repositories": [
            {
                "name": "avalon-core",
                "branch": "develop"
            },
            {
                "name": "avalon-launcher",
                "url": "git@github.com:pypeclub/avalon-launcher.git",
                "branch": "develop"
            }
        ]
    }

    @pytest.fixture
    def set_path(self):
        return os.path.abspath('.')

    @pytest.fixture
    def deploy_file(self, tmp_path):
        """ Provide valid sample of deployment.json

            :param tmp_path: temporary path provided by pytest fixture
            :type tmp_path: path
            :returns: path to json file
            :rtype: string
        """
        json_path = tmp_path / "valid-deploy.json"
        with open(json_path.as_posix(), "w") as write_json:
            json.dump(self._valid_deploy_data, write_json)
        return json_path.as_posix()

    @pytest.fixture
    def invalid_deploy_file(self, tmp_path):
        """ Provide **invalid** sample of deployment.json

            :param tmp_path: temporary path provided by pytest fixture
            :type tmp_path: path
            :returns: path to json file
            :rtype: string
        """
        json_path = tmp_path / "invalid-deploy.json"
        with open(json_path.as_posix(), "w") as write_json:
            json.dump(self._invalid_deploy_data, write_json)
        return json_path.as_posix()

    def test_invalid_path_raises_exception(self):
        """ Tests if invalid path provided to :class:`Deployment` will raise
            an exception.
        """
        with pytest.raises(DeployException) as excinfo:
            Deployment('some_invalid_path')
        assert "PYPE_SETUP_PATH" in str(excinfo.value)

    def test_read_deployment_file(self, set_path, deploy_file):
        """ Tests if we can read deployment file.

            :param set_path: pype setup root path
            :type set_path: string
            :param deploy_file: path to valid temporary deploy file
            :type deploy_file: string
        """
        d = Deployment(set_path)
        data = d._read_deployment_file(deploy_file)
        assert data.get('repositories')[0].get('name') == "avalon-core"
        assert data.get('repositories')[1].get('branch') == "develop"

    def test_read_invalid_deployment_file(self, set_path):
        d = Deployment(set_path)
        with pytest.raises(FileNotFoundError):
            d._read_deployment_file('wfjagp')

    def test_read_schema(self, set_path):
        d = Deployment(set_path)
        schema_file = os.path.join(
            d._pype_root,
            d._deploy_dir,
            d._schema_file
        )
        pprint(schema_file)
        schema = d._read_schema(schema_file)
        assert schema.get('title') == 'pype:deployment-schema'

    def test_read_schema_raises_exception(self, set_path):
        d = Deployment(set_path)
        with pytest.raises(DeployException):
            d._read_schema("blabla")

    def test_determine_deployment_file(self, tmp_path):
        d = Deployment(tmp_path.as_posix())
        path = Path(d._pype_root)
        deploy_dir = path / d._deploy_dir
        deploy_dir.mkdir()
        default_deploy_file = deploy_dir / d._deploy_file
        default_deploy_file.write_text('default')

        r = d._determine_deployment_file()
        assert r == os.path.normpath(default_deploy_file.as_posix())
        override_dir = deploy_dir / "override"
        override_dir.mkdir()
        # it still should pick default one
        r = d._determine_deployment_file()
        assert r == os.path.normpath(default_deploy_file.as_posix())
        override_deploy_file = override_dir / d._deploy_file
        override_deploy_file.write_text('override')
        # now it should pick override
        r = d._determine_deployment_file()
        assert r == os.path.normpath(override_deploy_file.as_posix())

    def test_validate_schema(self, invalid_deploy_file, deploy_file):
        d = Deployment(os.path.abspath('.'))
        r = d._validate_schema(d._read_deployment_file(invalid_deploy_file))
        assert r is False
        r = d._validate_schema(d._read_deployment_file(deploy_file))
        assert r is True

    def test_validate_deployment(self, tmp_path, deploy_file):
        d = Deployment(os.path.normpath(tmp_path.as_posix()))
        deploy_test_path = tmp_path / "deploy"
        deploy_test_path.mkdir()
        root_path = os.path.abspath('.')

        # copy deploy and schema to temp test dir
        copyfile(os.path.join(root_path, d._deploy_dir, d._schema_file),
                 os.path.join(
                    os.path.normpath(deploy_test_path.as_posix()),
                    d._schema_file))

        copyfile(os.path.join(root_path, d._deploy_dir, d._deploy_file),
                 os.path.join(
                    os.path.normpath(deploy_test_path.as_posix()),
                    d._deploy_file))

        repo_test_path = tmp_path / "repos"
        repo_test_path.mkdir()

        # should fail as `repos` is empty
        with pytest.raises(DeployException) as excinfo:
            d.validate()
        assert excinfo.match(r"Repo path doesn't exist")

    def setup_deployment(self, tmp_path, deploy_json=None):
        """ Setup environment for deployment test.

            Create temporary **deploy** and **repos** directories with
            correct **deploy.json** and it's schema.

            :param tmp_path: path to temporary directory
            :type tmp_path: string
            :param deploy_json: provide optional content for **deploy.json**
            :type deploy_json: str
            :returns: Deployment instance
            :rtype: :class:`Deployment`
        """
        d = Deployment(os.path.normpath(tmp_path.as_posix()))
        deploy_test_path = tmp_path / "deploy"
        deploy_test_path.mkdir()
        root_path = os.path.abspath('.')

        # copy deploy and schema to temp test dir
        copyfile(os.path.join(root_path, d._deploy_dir, d._schema_file),
                 os.path.join(
                    os.path.normpath(deploy_test_path.as_posix()),
                    d._schema_file))

        if deploy_json is not None:
            with open(os.path.join(
               os.path.normpath(deploy_test_path.as_posix()),
               d._deploy_file), "w") as dfile:
                json.dump(deploy_json, dfile)
        else:
            copyfile(os.path.join(root_path, d._deploy_dir, d._deploy_file),
                     os.path.join(
                        os.path.normpath(deploy_test_path.as_posix()),
                        d._deploy_file))

        repo_test_path = tmp_path / "repos"
        repo_test_path.mkdir()

        return d

    def test_get_deployment_paths(self, tmp_path):
        d = self.setup_deployment(tmp_path, self._valid_deploy_data)
        paths = d.get_deployment_paths()
        data = self._valid_deploy_data
        for item in data.get('repositories'):
            path = os.path.join(
                d._pype_root, "repos", item.get('name'))
            assert any(path in p for p in paths)

    def test_get_environment_paths(self, tmp_path, monkeypatch):
        d = self.setup_deployment(tmp_path, self._valid_deploy_data)
        paths = d.get_environment_data()
        data = self._valid_deploy_data
        monkeypatch.setitem(os.environ, 'PYPE_SETUP_PATH', d._pype_root)
        pype_config = data.get('PYPE_CONFIG').format(PYPE_SETUP_PATH=d._pype_root)
        pprint(paths)
        for item in data.get('init_env'):
            path = os.path.join(
                pype_config, "environments", item + '.json')
            path = os.path.normpath(path)
            pprint(path)
            assert paths[1] in path

    def test_deployment_clean(self, tmp_path):
        d = self.setup_deployment(tmp_path)

        d.deploy()

        settings = d._determine_deployment_file()
        deploy = d._read_deployment_file(settings)

        for d_item in deploy.get('repositories'):
            path = os.path.join(
                d._pype_root, "repos", d_item.get('name'))

            assert d._validate_is_directory(path)
            assert d._validate_is_repo(path)
            assert d._validate_is_branch(path,
                                         d_item.get('branch') or
                                         d_item.get('tag'))

    def test_deployment_empty_dir(self, tmp_path):
        d = self.setup_deployment(tmp_path)
        root = Path(d._pype_root)
        repo_path = root / 'repos'
        empty_repo = repo_path / 'avalon-core'
        empty_repo.mkdir()

        d.deploy()

        settings = d._determine_deployment_file()
        deploy = d._read_deployment_file(settings)

        for d_item in deploy.get('repositories'):
            path = os.path.join(
                d._pype_root, "repos", d_item.get('name'))

            assert d._validate_is_directory(path)
            assert d._validate_is_repo(path)
            assert d._validate_is_branch(path,
                                         d_item.get('branch') or
                                         d_item.get('tag'))

    def test_deployment_invalid_repo(self, tmp_path):
        """ Test behavior if there is invalid repository present

            :param tmp_path: temporary pype root path
            :type tmp_path: :class:`Path`
        """
        d = self.setup_deployment(tmp_path)
        root = Path(d._pype_root)
        repo_path = root / 'repos'
        invalid_repo_path = repo_path / 'avalon-core'
        dirty_repo = Repo.init(str(invalid_repo_path))
        dirty_file_path = invalid_repo_path / "dirt.txt"
        with open(dirty_file_path.as_posix(), "w") as write_dirty:
            write_dirty.write("dirt")

        dirty_repo.index.add(['dirt.txt'])
        print("dirt path - {}".format(dirty_file_path.as_posix()))
        assert dirty_repo.is_dirty() is True

        # now we have dirty repository so without force=True we should raise
        # exception
        with pytest.raises(DeployException):
            d.deploy()

        # with force=True, invalid repository should be forcefully replaced
        d.deploy(force=True)

        settings = d._determine_deployment_file()
        deploy = d._read_deployment_file(settings)

        for d_item in deploy.get('repositories'):
            path = os.path.join(
                d._pype_root, "repos", d_item.get('name'))

            assert d._validate_is_directory(path)
            assert d._validate_is_repo(path)
            assert d._validate_is_branch(path,
                                         d_item.get('branch') or
                                         d_item.get('tag'))
