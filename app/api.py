from .lib import Logger

from .lib.formating import format

from .lib.utils import (
    forward,
    get_conf_file
)
from .lib.repos import (
    solve_dependecies,
    git_make_repository,
    git_set_repository
)

from . import (
    Templates
)


from .pypeline import (
    env_install,
    env_uninstall
)


__all__ = [
    "env_install",  # install repositories and environment from template
    "env_uninstall",

    "format",

    "Templates",
    "get_conf_file",

    "solve_dependecies",
    "git_make_repository",
    "git_set_repository",

    "forward",

    "Logger",
]
