
import os
import sys
import platform
import subprocess
from app.lib import terminal

from app import api

terminal.c_echo(">>> Logger from pype-start: [ {} ]".format(api.Logger))

log = api.Logger.getLogger(__name__)


def main():
    if not api.Templates:
        api.env_install()

    # write into log file what is seen by templates
    for k, v in api.Templates.items():
        log.info("templates.item: `{}`,`{}`".format(k, v))
    log.info("\n")

    for k, v in os.environ.items():
        log.info("os.environ.item: `{}`,`{}`".format(k, v))
    log.info("\n")

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
        sys.exit(returncode)
    except Exception as e:
        print(e)
        sys.exit(1)
