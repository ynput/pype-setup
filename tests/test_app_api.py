import os

from app.api import (
    solve_dependecies,
    Templates
)


solve_dependecies()

print(100*"_")

t = Templates()

print(100*"_")
for k, v in t.items():
    print(k, v)

# print(100*"_")
# for k, v in os.environ.items():
#     if "PYTHONPATH" in k:
#         print(k, v)
