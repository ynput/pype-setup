
import os
from pprint import pprint

from app.api import (
    Templates,
)
# test = Templates(type=["context"], filled=None)
# pprint(test)

t = Templates(
    type=["context"],
    filled=None,
    environmnet=["maya", "nuke", "pyblish"]
)

print(100*"_")
for k, v in t.items():
    print(k, v)
print(100*"_")

# for k, v in os.environ.items():
#     if "PYPE" in k or "AVALON" in k:
#         print(k, v)
# print(100*"_")

# #
# data = {"project": {"name": "D001_projectX",
#                     "code": "prjX"},
#         "VERSION": 3,
#         "SUBVERSION": 10,
#         "task": "animation",
#         "asset": "101sh010",
#         "hierarchy": "episodes/ep101/sq01",
#         "representation": "abc"}
#
# anatomy = t.anatomy
# anatomy = anatomy.format(data)
#
# print('work testing')
# pprint(anatomy.work)
# pprint(anatomy.render)
#
# data = {"project": {"name": "D001_projectX",
#                     "code": "prjX"},
#         "asset": 'sh010',
#                  "family": 'model',
#                  "subset": 'modelMain',
#                  "VERSION": 5,
#                  "subversion": 24,
#                  "hierarchy": "test/of/folder",
#                  "representation": "exr"}
#
# # anatomy = t.anatomy
# # print(anatomy)
# print('FORMATING')
# anatomy = anatomy.format(data)
#
# print('publish testing')
# pprint(anatomy.publish.pathmaster)
