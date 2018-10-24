import toml
import os
import sys
import json


def _json_load(path):
    return json.load(
        open(
            path
        )
    )


def _toml_load(path):
    return toml.load(path)


def _toml_dump(path, data):
    with open(path, "w+") as file:
        file.write(toml.dumps(data))
    return True


templates_schema_dir = os.path.join(
    os.environ["PYPE_STUDIO_TEMPLATES"],
    "schema"
)


for schema in os.listdir(templates_schema_dir):
    path = os.path.join(templates_schema_dir, schema)
    schema_name = os.path.splitext(schema)
    print(path, schema_name)
    data = _json_load(path)
    print(data)
    print(_toml_dump(
        os.path.join(
            templates_schema_dir,
            (schema_name[0] + ".toml")
        ),
        data
    )
    )
