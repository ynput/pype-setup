#!/usr/bin/env python3

import os
import sys

from app.api import (
    Templates as templates,
    forward
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


ftrack_api = __import__("ftrack_api")
print(ftrack_api)
session = ftrack_api.Session()
print(session)
