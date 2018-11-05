
import os
from pprint import pprint

from app.api import (
    Templates,
)


base = Templates()
print(100*"_")
for k, v in base.items():
    print(k, v)
print(100*"_")

t = Templates(
    type=["anatomy"]
)
print(100*"_")
for k, v in t.items():
    print(k, v)
print(100*"_")

a = Templates(
    type=["software"],
    environment=["ftrack"]
)
print(100*"_")
for k, v in a.items():
    print(k, v)
print(100*"_")

for k, v in os.environ.items():
    if "PYPE" in k or "AVALON" in k or "FTRACK" in k:
        print(k, v)
print(100*"_")


data = {"project": {"name": "D001_projectX",
                    "code": "prjZ"},
        "VERSION": 3,
        "SUBVERSION": 10,
        "task": "animation",
        "asset": "sh010",
        "hierarchy": "episodes/ep101",
        "representation": "abc"}

anatomy = t.anatomy
anatomy = anatomy.format(data)

print('\nFORMATING WORK')
print(anatomy.work.path)

data = {"project": {"name": "D001_projectX",
                    "code": "prjX"},
        "asset": 'sh020',
        "family": 'model',
        "subset": 'modelMain',
        "VERSION": 5,
        "subversion": 24,
        "hierarchy": "episodes/ep201",
        "representation": "exr"}


anatomy = anatomy.format(data)
print('\nFORMATING PUBLISH')
print(anatomy.publish.pathmaster)
