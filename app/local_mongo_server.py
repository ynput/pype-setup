import subprocess
import os
import sys
import platform
from app.lib import terminal

from app.api import (
    Templates as templates,
    forward,
    git_make_repository,
    Logger,
    logger
)

from app import (
    Templates,
    _repos_installed,
    _templates_loaded,
)

from app.lib import terminal

if not _templates_loaded:
    Templates = templates()
    _templates_loaded = True

terminal.c_echo(">>> Logger from pype-start: [ {} ]".format(Logger))

log = Logger.getLogger(__name__)
PYPE_DEBUG = bool(os.getenv("PYPE_DEBUG"))

if PYPE_DEBUG:
    for k, v in Templates.items():
        log.debug("templates.item: `{}`,`{}`".format(k, v))
    log.debug("\n")

    for k, v in os.environ.items():
        log.debug("os.environ.item: `{}`,`{}`".format(k, v))
    log.debug("\n")


def main():
    # Get database location.
    try:
        location = os.environ["AVALON_DB_DATA"]
    except KeyError:
        location = os.path.join(os.path.expanduser("~"), "data", "db")

    if len(sys.argv) == 2:
        location = sys.argv[1]

    # Create database directory.
    if not os.path.exists(location):
        os.makedirs(location)

    # Start server.

    if platform.system().lower() == "linux":
        subprocess.Popen(
            ["mongod", "--dbpath", location, "--port",
             os.environ["AVALON_MONGO_PORT"]]
            ,close_fds=True
        )
    elif platform.system().lower() == "windows":

        subprocess.Popen(
            ["start", "Avalon MongoDB", "mongod", "--dbpath",
                location, "--port", os.environ["AVALON_MONGO_PORT"]],
            shell=True
        )


if __name__ == "__main__":
    main()
