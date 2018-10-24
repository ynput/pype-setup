import os
from app.api import (
    Templates
)

t = Templates()

print(100*"_")
for k, v in t.items():
    print(k, v)
print(100*"_")
for k, v in os.environ.items():
    if "PYPE" in k or "AVALON" in k:
        print(k, v)
print(100*"_")
anatomy = t.anatomy

anatomy = anatomy.format(
    {"project": {"code": "tr"},
     "representation": "exr",
     "VERSION": 3,
     "SUBVERSION": 10,
     "shot": "sh001",
     "sequence": "sq090"}
)

print(anatomy.workfiles.file)

anatomy = t.anatomy
anatomy = anatomy.format({"project": {"code": "frk"},
                          "representation": "exr",
                          "VERSION": 5,
                          "SUBVERSION": 70,
                          "shot": "sh101",
                          "sequence": "sq490"})

print(anatomy.workfiles.file)

data = {"obj": anatomy}
print(data)
print(data['obj'].workfiles.file)

anatomy = t.anatomy
wf_file = anatomy.format({"project": {"code": "frk"},
                          "representation": "exr",
                          "VERSION": 5,
                          "SUBVERSION": 70,
                          "shot": "sh101",
                          "sequence": "sq490"}).workfiles.file
print(wf_file)

print(anatomy)
data = {
    outer_k: {
        inner_k: inner_v
        for inner_k, inner_v in outer_v.items()
    }
    for outer_k, outer_v in anatomy.items()
    if isinstance(outer_v, dict)
}
print(data)
