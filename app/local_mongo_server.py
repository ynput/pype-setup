
import os
import sys
import platform
import subprocess
from app.lib import terminal

from app.api import (
    env_install,
    env_uninstall,
    forward,
    Logger,
)


terminal.c_echo(">>> Logger from pype-start: [ {} ]".format(Logger))

log = Logger.getLogger(__name__)


def main():
    import app
    if not app._templates_loaded:
        env_install()

    # write into log file what is seen by templates
    for k, v in app.Templates.items():
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
        print("@ Local mongodb is running...")
        returncode = subprocess.Popen(
            ["mongod", "--dbpath", location, "--port",
             os.environ["AVALON_MONGO_PORT"]], close_fds=True
        )
    elif platform.system().lower() == "windows":
        print("@ Local mongodb is running...")
        returncode = subprocess.Popen(
            ["start", "Avalon MongoDB", "mongod", "--dbpath",
                location, "--port", os.environ["AVALON_MONGO_PORT"]],
            shell=True
        )

    env_uninstall()
    return returncode


if __name__ == "__main__":
    try:
        returncode = main()
        sys.exit(returncode)
    except Exception as e:
        print(e)
        sys.exit(1)
