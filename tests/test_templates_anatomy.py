import os
from app.api import (
    solve_dependecies,
    Templates
)

t = Templates()

# print(100*"_")
# for k, v in t.items():
#     print(k, v)
# print(100*"_")
# for k, v in os.environ.items():
#     if k in "PYPE_CONTEXT_CODE":
#         print(k, v)
# print(100*"_")
anatomy = t.anatomy

anatomy = anatomy.format({"project": {"code": "tr"},
                          "representation": "exr",
                          "VERSION": 3,
                          "SUBVERSION": 10,
                          "shot": "sh001",
                          "sequence": "sq090"})

file = anatomy.workfiles.file

print(anatomy.workfiles.file)

anatomy2.format({"project": {"code": "tr"},
                 "representation": "exr",
                 "VERSION": 1,
                 "SUBVERSION": 10,
                 "shot": "sh020",
                 "sequence": "sq010"})

print(anatomy2.workfiles.file)
