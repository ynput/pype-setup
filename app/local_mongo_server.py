
import os
import sys
import platform
import subprocess

from pprint import pprint

import app
from app import api


log = api.Logger.getLogger(__name__)


def main():
    if not app.Templates:
        api.env_install()

    t = app.Templates
    log.debug(pprint(t))

    for k, v in os.environ.items():
        log.debug("os.environ.item: `{}`,`{}`".format(k, v))
    log.debug("\n")

    # Get database location.
    try:
        location = os.environ["AVALON_DB_DATA"]
    except KeyError:
        location = os.path.join(os.path.expanduser("~"), "data", "db")

    # Create database directory.
    if not os.path.exists(location):
        os.makedirs(location)

    # Start server.
    if platform.system().lower() == "linux":
        log.info("@ Local mongodb is running...")
        returncode = subprocess.Popen(
            ["mongod", "--dbpath", location, "--port",
             os.environ["AVALON_MONGO_PORT"]], close_fds=True
        )
    elif platform.system().lower() == "windows":
        log.info("@ Local mongodb is running...")
        returncode = subprocess.Popen(
            ["start", "Avalon MongoDB", "mongod", "--dbpath",
             location, "--port", os.environ["AVALON_MONGO_PORT"]],
            shell=True
        )

    api.env_uninstall()
    return returncode


if __name__ == "__main__":
    try:
        returncode = main()
        log.debug("Ending returncode: {}".format(returncode))
        sys.exit(returncode)
    except Exception as e:
        log.error("Exception at the end: {}".format(e))
        sys.exit(1)
