#!/usr/bin/env python3
import os
import sys

print(100*"_")
print(sys.path)
print(100*"_")

from app.api import (
    Templates as templates,
)
from app import (
    Templates,
    _templates_loaded,
)

if not _templates_loaded:
    Templates = templates()
    _templates_loaded = True


print(100*"_")
for k, v in os.environ.items():
    print(k, v)

print(100*"_")


# ftrack_api = __import__("ftrack_api")
import ftrack_api
print(ftrack_api)

print(ftrack_api.Session())
