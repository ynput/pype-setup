import os

from app.api import (
    solve_dependecies,
    Templates

)


solve_dependecies()

print(100*"_")

# os.environ["TOOL_ENV"] = os.path.join(templates_root, "studio-templates", "environments")
#
# print(os.environ["TOOL_ENV"])

t = Templates()


for key in os.environ:
    if 'AVALON' in key:
        print(key + ":" + os.environ[key])

print(100*"_")
for k, v in t.items():
    print(k, v)

# print(100*"_")
# for k, v in os.environ.items():
#     if "PYTHONPATH" in k:
#         print(k, v)
