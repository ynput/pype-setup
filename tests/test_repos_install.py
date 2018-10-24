import os
import sys

from app.api import forward


path = os.path.join(
    os.environ["PYPE_SETUP_ROOT"],
    "app",
    "pype-start.py"
)


forward(
    [sys.executable,
     '-u',
     path,
     "--make"]
)
