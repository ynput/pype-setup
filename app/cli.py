
import platform
import sys
import subprocess
import os
import app

from app import api

log = api.Logger.getLogger(__name__, "cli")

TERMINAL = {
    "windows": {
        "clean_terminal": "cls",
        "cmd": ["cmd"],
        "env": {
            "PROMPT": "(PYPE terminal) $P$G"
        }
    },
    "linux": {
        "clean_terminal": "cls",
        "cmd": ["xfce4-terminal"],
        "env": {
            "PS1": "(PYPE terminal):\\u@\\h \\w > "
        }
    },
    "darwin": {
        "clean_terminal": "cls",
        "cmd": ["iTerm2"],
        "env": {
            "PS1": "(PYPE terminal):\\u@\\h \\w > "
        }
    }
}


def main():

    if not api.Templates:
        api.env_install()

    os.system(TERMINAL[platform.system().lower()]["clean_terminal"])

    subprocess.Popen(
        TERMINAL[platform.system().lower()]["cmd"],
        env=dict(
            os.environ,
            **TERMINAL[platform.system().lower()]["env"]),
    )

    return 1


if __name__ == '__main__':
    try:
        returncode = main()
    except Exception as e:
        print(e)
        sys.exit(returncode)
