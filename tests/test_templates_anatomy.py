import os

from app.api import (
    solve_dependecies,
    Templates
)


solve_dependecies()

print(100*"_")

t = Templates()

# print(100*"_")
# for k, v in t.items():
#     print(k, v)

anatomy = t.anatomy
anatomy._format(this="that")
anatomy._format({"those": "fuck"})
anatomy._format()
