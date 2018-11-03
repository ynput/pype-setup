#!/usr/bin/env python3

import os
import sys

from app.api import (
    Templates as templates,
    forward
)

Templates = templates()

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

returncode = forward(
    [executable, '-u',
     path]
)
