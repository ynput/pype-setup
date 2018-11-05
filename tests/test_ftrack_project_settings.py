#!/usr/bin/env python3

import os
import sys

from app.api import (
    Templates as templates,
    forward
)

Templates = templates(environment=["ftrack"])

for k, v in os.environ.items():
    if "PYPE" in k or "AVALON" in k or "PYTHON_ENV" in k:
        print(k, v)
print(100*"_")


ftrack_api = __import__("ftrack_api")


path = os.path.join(
    os.environ["PYPE_STUDIO_CONFIG"],
    os.environ["AVALON_CONFIG"],
    "widgets",
    "project_settings.py"
)


executable = os.path.join(
    os.environ["PYTHON_ENV"],
    "python.exe"
)

os.environ["FTRACK_API_KEY"] = "ddb005c0-fec8-11e7-83b5-0a580aa01115"
os.environ["FTRACK_API_USER"] = "jakub.jezek"

returncode = forward(
    [executable, '-u',
     path]
)
