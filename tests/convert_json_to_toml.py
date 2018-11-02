#!/usr/bin/env python3
import os
import sys
import json
import toml


file = [r"K:\core\pype-setup\repos\studio-templates\environments\maya_2018.json",
        r"K:\core\pype-setup\repos\studio-templates\environments\mtoa_3.1.1.json"]


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


for f in file:
    schema_name = os.path.splitext(f)
    print(f, schema_name)
    data = _json_load(f)
    print(data)
    toml_file = f.replace('json', 'toml')
    print(toml_file)
    print(_toml_dump(toml_file,
        data
    )
    )
