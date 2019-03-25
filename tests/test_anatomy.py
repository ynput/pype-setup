import pytest
from pypeapp import anatomy


@pytest.fixture
def valid_data(self, tmp_path):
    """ Provide valid sample of anatomy

        :param tmp_path: temporary path provided by pytest fixture
        :type tmp_path: path
        :returns: path to json file
        :rtype: string
    """

    data = {"root": root,
             "project": {"name": PROJECT,
                         "code": project['data']['code']},
             "silo": asset['silo'],
             "asset": ASSET,
             "family": instance.data['family'],
             "subset": subset["name"],
             "version": int(version["name"]),
             "hierarchy": hierarchy}
    # # json_path = tmpdir_factory.mktemp("deploy").join("valid-deploy.json")
    # json_path = tmp_path / "valid-deploy.json"
    # with open(json_path.as_posix(), "w") as write_json:
    #     json.dump(data, write_json)
    # return json_path.as_posix()

@pytest.fixture
def valid_templates(self):

    resources:
      footage: {root[resources]}/{project[name]}/resources/footage
      reference: {root[resources]}/{project[name]}/resources/reference

    work:
      folder: {root[work]}/{project[name]}/{hierarchy}/{asset}/work/{task}
      file: {project[code]}_{asset}_{task}_v{version:0>3}<_{comment}>.{ext}
      path: {root[work]}/{project[name]}/{hierarchy}/{asset}/work/{task}/{asset}_{task}_v{version:0>3}<_{comment}>.{ext}

    render:
      path: {root[render]}/{project[name]}/{hierarchy}/{asset}/publish/render/{task}/{subset}/{version}/{project[code]}_{asset}_{task}_v{version:0>3}_{subset}<.{frame}>.{representation}

    publish:
      path: {root[publish]}/{project[name]}/{hierarchy}/{asset}/publish/{family}/{subset}/v{version:0>3}/{project[code]}_{asset}_{subset}_v{version:0>3}.{representation}

    avalon:
      workfile: {asset}_{task}_v{version:0>3}<_{comment}>
      work: {root}/{project[name]}/{hierarchy}/{asset}/work/{task}
      publish: {root}/{project[name]}/{hierarchy}/{asset}/publish/{family}/{subset}/v{version:0>3}/{project[code]}_{asset}_{subset}_v{version:0>3}.{representation}


def test_solve_optional(valid_templates, valid_data):

    formatted_with_optional = formatting._solve_optional(valid_templates, valid_data)
    formatted_no_optional = formatting._solve_optional(template, test_data_2)

    valid_work_folder = "/prj/seq/sh010/car/work/animation"

    assert formatted_with_optional == valid_work_folder
    assert formatted_no_optional == "iamrequiredKey"
