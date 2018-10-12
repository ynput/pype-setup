import os

from app.api import (
    solve_dependecies,
    Templates
)

solve_dependecies()
t = Templates()

print("\n", t, "\n")

for k, v in t.items():
    print(k, v)

for k, v in os.environ.items():
    for i in ("PYPE", "AVALON", "PATH", "PYTHONPATH"):
        if i in k:
            print(k, v)
