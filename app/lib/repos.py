import sys
import os
import subprocess
import toml
import logging

# TODO: setup for projects os.environ["AVALON_PROJECTS"]
log = logging.getLogger(__name__)

AVALON_DEBUG = bool(os.getenv("AVALON_DEBUG"))

# TODO: updating repositories into defined branches from .gitmodules
# TODO: write our own gitmodules and ensure it will install all
# submodules at first run in case the .gitmodules got lostself.
# TODO: checking out into defined branches in case branch is
# different from the one in .gitmodules and activated


def get_conf_file(
    dir,
    root_file_name,
    preset_name=None,
    split_pattern=None,
    representation=None
):
    '''Gets any available `config template` file from given
    **path** and **name**

    Attributes:
        dir (str): path to root directory where files could be searched
        root_file_name (str): root part of name it is searching for
        preset_name (str): default preset name
        split_pattern (str): default pattern for spliting name and preset
        representation (str): extention of file used for config files
                              can be ".toml" but also ".conf"

    Returns:
        file_name (str): if matching name found or None
    '''

    if not preset_name:
        preset_name = "default"
    if not split_pattern:
        split_pattern = ".."
    if not representation:
        representation = ".toml"

    conf_file = root_file_name + representation
    # print(dir, root_file_name, preset_name,
    # split_pattern, representation)
    try:
        preset = os.environ["PYPE_TEMPLATES_PRESET"]
    except KeyError:
        preset = preset_name

    test_files = [
        f for f in os.listdir(dir)
        if split_pattern in f
    ]

    try:
        conf_file = [
            f for f in test_files
            if preset in os.path.splitext(f)[0].split(split_pattern)[1]
            if root_file_name in os.path.splitext(f)[0].split(split_pattern)[0]
        ][0]
    except IndexError as error:
        if AVALON_DEBUG:
            log.warning("File is missing '{}' will be"
                        "used basic config file: {}".format(
                            error, conf_file
                        ))
        pass

    return conf_file if os.path.exists(os.path.join(dir, conf_file)) else None


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
    os.environ["PATH"] = os.pathsep.join(
        [add_to_path] +
        os.getenv("PATH", "").split(os.pathsep)
    )


def _add_to_pythonpath(add_to_pythonpath):
    # Append to PYTHONPATH
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
            print("Checking '{}'...".format(key))
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
                print("/// added to pythonpath")
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

    ROOT = os.environ["PYPE_SETUP_ROOT"]

    REPOS_CONFIG_FILE = get_conf_file(ROOT, "config-repos")

    config_content = toml.load(
        os.path.join(
            ROOT,
            REPOS_CONFIG_FILE
        )
    )
    # adding stuff to environment variables
    _setup_environment(config_content)
    print("All pype, avalon, pyblish environment variables are set")
