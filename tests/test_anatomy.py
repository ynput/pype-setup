import pytest
from pypeapp import anatomy


@pytest.fixture
def valid_data(self):
    """ Provide valid sample of anatomy

        :param tmp_path: temporary path provided by pytest fixture
        :type tmp_path: path
        :returns: path to json file
        :rtype: string
    """

    data = {
        'root': {
            'work': 'ROOT_WORK'
        },
        'version': '1',
        'hierarchy': 'HIER',
        'ext': 'EXT',
        'project': {
            'code': 'PROJECT_CODE',
            'name': 'PROJECT_NAME'
        },
        'asset': 'ASSET',
        'task': 'TASK'
    }

    # # json_path = tmpdir_factory.mktemp("deploy").join("valid-deploy.json")
    # json_path = tmp_path / "valid-deploy.json"
    # with open(json_path.as_posix(), "w") as write_json:
    #     json.dump(data, write_json)
    # return json_path.as_posix()

@pytest.fixture
def valid_templates(self):
    {
        "resources": {
            "footage": "{root[resources]}/{project[name]}/resources/footage",
        }

        "work": {
            "file": "{project[code]}_{asset}_{task}_v{version:0>3}<_{comment}>.{ext}",
            "path": "{root[publish]}/{project[name]}/{hierarchy}/{asset}/publish/{family}/{subset}/v{version:0>3}/{project[code]}_{asset}_{subset}_v{version:0>3}.{representation}"
        }

        "avalon": {
            "workfile": "{asset}_{task}_v{version:0>3}<_{comment}>",
            "work": "{root}/{project[name]}/{hierarchy}/{asset}/work/{task}",
            "publish": "{root}/{project[name]}/{hierarchy}/{asset}/publish/{family}/{subset}/v{version:0>3}/{project[code]}_{asset}_{subset}_v{version:0>3}.{representation}"
        }
    }

@pytest.fixture
def invalid_data(self):
    """ Provide **invalid** sample of deployment.json

        :param tmp_path: temporary path provided by pytest fixture
        :type tmp_path: path
        :returns: path to json file
        :rtype: string
    """

    data = {
        'root': 'ROOT_WORK',
        'version': '1',
        'hierarchy': 'HIER',
        'ext': 'EXT',
        'project': {
            'code': 'PROJECT_CODE',
            'name': 'PROJECT_NAME'
        },
        'asset': {'name': 'ASSET'},
        'task': 'TASK'
    }

def test_solve_optional(valid_templates, valid_data):

    anatomy = Anatomy()
    formatted_with_optional = anatomy.(valid_templates, valid_data)
    formatted_no_optional = anatomy.(template, test_data_2)

    assert formatted_with_optional == valid_work_folder
    assert formatted_no_optional == "iamrequiredKey"
