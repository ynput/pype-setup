import pytest
from pypeapp import Anatomy
import yaml
import os
import pathlib


valid_data = {
    'root': {
        'work': '\\volume\\projects'
    },
    'version': '1',
    'hierarchy': 'asset/characters',
    'ext': 'ABC',
    'project': {
        'code': 'PRJ',
        'name': 'P001_ProjectX'
    },
    'asset': 'BOB',
    'task': 'MODELING',
    'comment': 'iAmComment'
}


valid_templates = {
    "resources": {
        "footage": "{root[resources]}/{nonExistent}/resources/footage"
    },
    "work": {
        "file": "{project[code]}_{asset}_{task}_v{version:0>3}<_{comment}>.{ext}",
        "file2": "{project[code]}_{asset}_{task}_v{version:0>3}<_{nocomment}>.{ext}",
        "noDictKey": "{project[code]}_{asset[name]}_{task}_v{version:0>3}<_{nocomment}>.{ext}",
        "path": "{root[work]}/{projaect[name]}/{hierarchy}/{asset}/publish/{family}/{subset}/v{version:0>3}/{project[code]}_{asset}_{subset}_v{version:0>3}.{representation}"
    },
    "avalon": {
        "workfile": "{asset}_{task}_v{version:0>3}<_{comment}>",
        "work": "{root}/{project[name]}/{hierarchy}/{asset}/work/{task}",
        "publish": "{root}/{project[name]}/{hierarchy}/{asset}/publish/{family}/{subset}/v{version:0>3}/{project[code]}_{asset}_{subset}_v{version:0>3}.{representation}"
    }
}


@pytest.fixture
def anatomy_file(tmp_path):
    """ Provide valid sample of deployment.json

        :param tmp_path: temporary path provided by pytest fixture
        :type tmp_path: path
        :returns: path to json file
        :rtype: string
    """

    yaml_path = tmp_path / "repos" / "pype-templates" / "anatomy"
    os.makedirs(yaml_path)
    yaml_file = yaml_path / "default.yaml"
    with open(yaml_file.as_posix(), "w") as write_yaml:
        yaml.dump(valid_templates, write_yaml)
    return tmp_path.as_posix()


def test_format_anatomy():

    anatomy = Anatomy()
    a = anatomy.solve_dict(valid_templates, valid_data)
    # formatted_no_optional = anatomy.solve_dict(template, test_data_2)

    assert a['solved']['work']['file'] == "PRJ_BOB_MODELING_v001_iAmComment.ABC"
    assert a['solved']['work']['file2'] == "PRJ_BOB_MODELING_v001.ABC"
    assert a['partial']['work']['noDictKey'] == "PRJ_{asset[name]}_MODELING_v001.ABC"
    assert a['unsolved']
    # assert formatted_no_optional == "iamrequiredKey"


def test_anatomy(anatomy_file, monkeypatch):

    print(anatomy_file)
    monkeypatch.setitem(os.environ, 'PYPE_ROOT', anatomy_file)
    anatomy = Anatomy()

    a = anatomy.format_all(valid_data)

    b = anatomy.format(valid_data)

    assert a['solved']['work']['file'] == "PRJ_BOB_MODELING_v001_iAmComment.ABC"
    assert a['solved']['work']['file2'] == "PRJ_BOB_MODELING_v001.ABC"
    assert a['partial']['work']['noDictKey'] == "PRJ_{asset[name]}_MODELING_v001.ABC"
    assert a['unsolved']

    assert b['work']['file'] == "PRJ_BOB_MODELING_v001_iAmComment.ABC"
    assert b['work']['file2'] == "PRJ_BOB_MODELING_v001.ABC"
