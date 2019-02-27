import pytest
import os
import json
from pprint import pprint
from pathlib import Path
from shutil import copyfile
from pypeapp.deployment import Deployment
from pypeapp.deployment import DeployException


class TestDeployment(object):

    @pytest.fixture
    def set_path(self):
        return os.path.abspath('.')

    @pytest.fixture
    def deploy_file(self, tmp_path):
        data = {
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
        # json_path = tmpdir_factory.mktemp("deploy").join("valid-deploy.json")
        json_path = tmp_path / "valid-deploy.json"
        with open(json_path.as_posix(), "w") as write_json:
            json.dump(data, write_json)
        return json_path.as_posix()

    @pytest.fixture
    def invalid_deploy_file(self, tmp_path):
        # missing required url
        data = {
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
        # json_path = tmpdir_factory.mktemp("deploy").join("valid-deploy.json")
        json_path = tmp_path / "invalid-deploy.json"
        with open(json_path.as_posix(), "w") as write_json:
            json.dump(data, write_json)
        return json_path.as_posix()

    def test_invalid_path_raises_exception(self):
        with pytest.raises(DeployException) as excinfo:
            Deployment('some_invalid_path')
        assert "PYPE_ROOT" in str(excinfo.value)

    def test_read_deployment_file(self, set_path, deploy_file):
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
            r = d.validate()
        assert excinfo.match(r"Repo path doesn't exist")

    def test_deployment(self, tmp_path, deploy_file):
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

        d.deploy()
