
from pprint import pprint

from app.lib.templates import Templates
from app.api import Logger
import os

os.environ["PYPE_DEBUG"] = "1"

log = Logger.getLogger(__name__)

base = Templates()
# print(100*"_")
# pprint(base)
# print(100*"_")

t = Templates(
    type=["anatomy"]
)
print(100*"_")
pprint(t)
print(100*"_")


data = {"project": {"name": "D001_projectX",
                    "code": "prjZ",
                    "test": {"this": "here"}},
        "VERSION": 3,
        "SUBVERSION": 10,
        "task": "animation",
        "asset": "sh010",
        "hierarchy": "episodes/ep101",
        "representation": "abc"}

anatomy = t.anatomy
anatomy = anatomy.format(data)

print('\nFORMATING WORK')
print(anatomy.work.file)

# print(100*"_")
# pprint(anatomy)
# print(100*"_")
##
# data = {"project": {"name": "D001_projectX",
#                     "code": "prjX"},
#         "asset": 'sh020',
#         "family": 'model',
#         "subset": 'modelMain',
#         "VERSION": 5,
#         "subversion": 24,
#         "hierarchy": "episodes/ep201",
#         "representation": "exr"}
#
#
# anatomy = anatomy.format(data)
# print('\nFORMATING PUBLISH')
# print(anatomy.publish.pathmaster)
