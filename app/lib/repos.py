import sys
import os
import subprocess
import toml

AVALON_DEBUG = bool(os.getenv("AVALON_DEBUG"))
CONFIG_REPOS_FILE = os.path.normpath(
    os.path.join(
        os.environ['PYPE_SETUP_ROOT'],
        "config_repos.toml"
    )
)


def get_config_repos():
    return toml.load(CONFIG_REPOS_FILE)

# TODO: updating repositories into defined branches from .gitmodules
# TODO: write our own gitmodules and ensure it will install all submodules at first run in case the .gitmodules got lostself.
# TODO: checking out into defined branches in case branch is different from the one in .gitmodules and activated


def forward(args, silent=False, cwd=None):
    """Pass `args` to the Avalon CLI, within the Avalon Setup environment

    Arguments:
        args (list): Command-line arguments to run
            within the active environment

    """

    if AVALON_DEBUG:
        print("avalon.py: Forwarding '%s'.." % " ".join(args))

    popen = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        cwd=cwd
    )

    # Blocks until finished
    while True:
        line = popen.stdout.readline()
        if line != '':
            if not silent or AVALON_DEBUG:
                sys.stdout.write(line)
        else:
            break

    if AVALON_DEBUG:
        print("avalon.py: Finishing up..")

    popen.wait()
    return popen.returncode


def git_update(cd, branch="master"):
    """Update Pype-setup to the latest version"""

    script = (
        # Discard any ad-hoc changes
        ("Resetting..", ["git", "reset", "--hard"]),
        ("Downloading..", ["git", "pull", "origin", branch]),

        # In case there are new submodules since last pull
        ("Looking for submodules..", ["git", "submodule", "init"]),

        ("Updating submodules..",
            ["git", "submodule", "update", "--recursive"]),
    )

    for message, args in script:
        print(message)
        returncode = forward(args, silent=True, cwd=cd)
        if returncode != 0:
            sys.stderr.write("Could not update, try running "
                             "it again with AVALON_DEBUG=True\n")
            return returncode

    print("All done")


def git_checkout(repository=dict()):
    """checkout all to defined branches"""

    if not repository:
        print("To checkout properly you need to give"
              "repository dictionary")
        return

    script = (
        # Discard any ad-hoc changes
        ("Checkingout to defined branch..",
         ["git", "checkout", repository["branch"]]),
        ("Updating the branch..",
         ["git", "pull", "origin", repository["branch"]])
    )

    cd = os.path.join(
        os.environ["PYPE_SETUP_ROOT"],
        repository["submodule_root"],
        repository["name"]
    )

    for message, args in script:
        print(message)
        returncode = forward(args, silent=True, cwd=cd)
        if returncode != 0:
            sys.stderr.write("Could not checkout, check if you've\n"
                             "commited before any previous changes and try\n"
                             "it again with AVALON_DEBUG=True\n")
            return returncode

    print("All done")
