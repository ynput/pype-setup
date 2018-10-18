import sys
import os
import subprocess
import toml


from .utils import (forward, get_conf_file)
from .. import logger

Logger = logger()
log = Logger.getLogger(__name__)
PYPE_DEBUG = os.getenv("PYPE_DEBUG") is "1"

# TODO: updating repositories into defined branches from .gitmodules
# TODO: write our own gitmodules and ensure it will install all
# submodules at first run in case the .gitmodules got lostself.
# TODO: checking out into defined branches in case branch is
# different from the one in .gitmodules and activated


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
                             "it again with PYPE_DEBUG=True\n")
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
                             "it again with PYPE_DEBUG=True\n")
            return returncode

    print("All done")


def _add_config(dir_name):
    '''adding config name of module'''
    # print("adding AVALON_CONFIG: '{}'".format(dir_name))
    os.environ['AVALON_CONFIG'] = dir_name


def _test_module_import(module_path, module_name):
    ''' test import module see if all is set correctly'''
    if subprocess.call([
        sys.executable, "-c",
        "import {}".format(module_name)
    ]) != 0:
        print("ERROR: '{}' not found, check your "
              "PYTHONPATH for '{}'.".format(module_name, module_path))
        sys.exit(1)


def _add_to_path(add_to_path):
    # Append to PATH
    # print("---------1", os.environ["PATH"])
    os.environ["PATH"] = os.pathsep.join(
        [add_to_path] +
        os.getenv("PATH", "").split(os.pathsep)
    )


def _add_to_pythonpath(add_to_pythonpath):
    # Append to PYTHONPATH
    # print("---------2", os.environ["PYTHONPATH"])
    os.environ["PYTHONPATH"] = os.pathsep.join(
        [add_to_pythonpath] +
        os.getenv("PYTHONPATH", "").split(os.pathsep)
    )


def _setup_environment(repos=None):
    '''Sets all environment variables regarding attributes found
    pype-setup/config-repos.toml

    '''
    assert isinstance(repos, dict), "`repos` must be <dict>"

    testing_list = list()
    for key, value in repos.items():

        if key not in list(os.environ.keys()):
            # print("Checking '{}'...".format(key))
            path = os.path.normpath(
                os.path.join(
                    os.environ['PYPE_SETUP_ROOT'],
                    value['submodule_root'],
                    value['name']
                )
            )
            # print("Checking path '{}'...".format(path))
            if value['env'] in "path":
                path = os.path.normpath(
                    os.path.join(path, value['subdir'])
                )
                _add_to_path(path)
            else:
                # for PYTHONPATH
                if "config" in value['name']:
                    _add_config(value['subdir'])
                    # print("Config added...")
                _add_to_pythonpath(path)
                # print("/// added to pythonpath")
                # add to list for testing
                testing_list.append(
                    {
                        "path": path,
                        "subdir": value['subdir']
                    }
                )
            os.environ[key] = path

    if testing_list:
        for m in testing_list:
            _test_module_import(m["path"], m["subdir"])


def solve_dependecies():

    ROOT = os.path.join(os.environ["PYPE_STUDIO_TEMPLATES"], "install")

    REPOS_CONFIG_FILE = get_conf_file(ROOT, "pype-repos")

    config_content = toml.load(
        os.path.join(
            ROOT,
            REPOS_CONFIG_FILE
        )
    )
    # adding stuff to environment variables
    _setup_environment(config_content)
    print("All pype, avalon, pyblish environment variables are set")
