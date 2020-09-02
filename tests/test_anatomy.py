import os
import pytest
from pypeapp.lib.anatomy import Anatomy, AnatomyUnsolved
import ruamel.yaml as yaml


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

solve_templates = {
    "basic": {
        "comment": "{asset}_{task}_v{version:0>3}<_{comment}>.{ext}",
        "nocomment": "{asset}_{task}_v{version:0>3}<_{nocomment}>.{ext}",
        "noDictKey": "{project[code]}_{asset[name]}_v{version:0>3}.{ext}",
        "multiple_optional": "{project[code]}</{asset}></{hierarchy}><_v{version:0>3}><_{nocomment}>.{ext}"
    }
}

features_templates = {
    "version_padding": 3,
    "version": "v{version:0>{@version_padding}}",
    "inner_keys": {
        "folder": "{project[name]}/{hierarchy}/{asset}/{@version}",
        "file": "{project[code]}_{asset}_v{version:0>3}.{ext}",
        "path": "{@folder}/{@file}"
    },
    "inner_override": {
        "version_padding": 2,
        "version": "ver{version:0>{@version_padding}}",
        "folder": "{hierarchy}/{asset}/{@version}",
        "file": "{project[code]}_{asset}_{@version}.{ext}",
        "path": "{@folder}/{@file}"
    },
    "missing_keys": {
        "missing_1": "{missing_key}/{project[code]}_{asset}",
        "missing_2": "{missing_key1}_{asset}<_{comment}>.{ext}{missing_key2}"
    },
    "invalid_types": {
        "invalid_type": "{project}_{asset[name]}"
    }
}
features_templates.update(solve_templates)


@pytest.fixture
def anatomy_file(tmp_path):
    """ Provide valid sample of deployment.json

        :param tmp_path: temporary path provided by pytest fixture
        :type tmp_path: path
        :returns: path to json file
        :rtype: string
    """

    yaml_path = tmp_path / "repos" / "pype-config" / "anatomy"
    os.makedirs(yaml_path)
    yaml_file = yaml_path / "default.yaml"
    with open(yaml_file.as_posix(), "w") as write_yaml:
        yaml.dump(features_templates, write_yaml)
    return tmp_path.as_posix()


def test_format_anatomy():

    anatomy = Anatomy()
    solved = anatomy.solve_dict(solve_templates, valid_data)

    assert solved['basic']['comment'] == "BOB_MODELING_v001_iAmComment.ABC"
    assert solved['basic']['nocomment'] == "BOB_MODELING_v001.ABC"

    assert solved['basic']['noDictKey'] == "PRJ_{asset[name]}_v001.ABC"


def test_anatomy(anatomy_file, monkeypatch):
    anatomy_file = os.path.join(anatomy_file, "repos", "pype-config")
    print(anatomy_file)

    monkeypatch.setitem(os.environ, 'PYPE_CONFIG', anatomy_file)
    anatomy = Anatomy()

    filled_all = anatomy.format_all(valid_data)
    filled = anatomy.format(valid_data)

    # Basic tests
    assert filled_all['basic']['comment'] == "BOB_MODELING_v001_iAmComment.ABC"
    assert filled_all['basic']['nocomment'] == "BOB_MODELING_v001.ABC"
    assert filled_all['basic']['noDictKey'] == "PRJ_{asset[name]}_v001.ABC"

    # Missing keys
    missing_1 = filled_all['missing_keys']['missing_1'].missing_keys
    assert missing_1 == ["missing_key"]

    missing_2 = sorted(filled_all['missing_keys']['missing_2'].missing_keys)
    assert missing_2 == ["missing_key1", "missing_key2"]

    try:
        filled['missing_keys']['missing_1']
        raise AssertionError("Should raise error about missing key")
    except AnatomyUnsolved:
        pass

    # Invalid types
    assert filled_all["invalid_types"]["invalid_type"].invalid_types == {
        "project": dict,
        "asset": str
    }

    # Inner keys
    inner_path = "P001_ProjectX/asset/characters/BOB/v001/PRJ_BOB_v001.ABC"
    assert filled["inner_keys"]["path"] == inner_path

    inner_override_file = "PRJ_BOB_ver01.ABC"
    assert filled["inner_override"]["file"] == inner_override_file
