import subprocess
import os
import sys
import platform


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

    if platform.system() == "Linux":
        subprocess.Popen(
            ["exec", "mongod", "--dbpath", location],
            shell=True
        )
    elif platform.system() == "Windows":

        subprocess.Popen(
            ["start", "Avalon MongoDB", "mongod", "--dbpath",
                location, "--port", os.environ["AVALON_MONGO_PORT"]],
            shell=True
        )


if __name__ == "__main__":
    main()
