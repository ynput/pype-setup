import os
import sys
import subprocess

PYPE_SETUP_ROOT = os.environ['PYPE_SETUP_ROOT']

# TODO: setup for projects os.environ["AVALON_PROJECTS"]
# TODO: connect repos.py for getting studio repositories
''' projects:
        - AVALON_PROJECTS var pointing to PYPE_STUDIO_PROJECTS/projects, here we are storing
        only metadata and config for each shot in hiearchical order
        - PYPE_STUDIO_PROJECTS_RAW = comming from anatomy set in locations
        - PYPE_STUDIO_PROJECTS_PLATES =
        - PYPE_STUDIO_PROJECTS_WORK =
        - PYPE_STUDIO_PROJECTS_RENDER =
        - PYPE_STUDIO_PROJECTS_PUBLISH =
'''


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
        print("ERROR: '{}' not found, check your PYTHONPATH for '{}'.".format(module_name, module_path))
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


def studio_depandecies():
    # Studio repositories
    default_repos = {
        "PYPE_STUDIO_CONFIG": {
            "name": "studio-config",
            "subdir": "pype",
            "env": "pythonpath",
            "git": "git@github.com:pypeclub/studio-config.git",
            "branch": "master",
            "submodule_root": "studio"
        },
        "PYPE_STUDIO_TEMPLATES": {
            "name": "studio-templates",
            "subdir": "templates",
            "env": "path",
            "git": "git@github.com:pypeclub/studio-templates.git",
            "branch": "master",
            "submodule_root": "studio"
        },
        "PYPE_STUDIO_PROJECTS": {
            "name": "studio-projects",
            "subdir": "projects",
            "env": "path",
            "git": "git@github.com:pypeclub/studio-projects.git",
            "branch": "master",
            "submodule_root": "studio"
        }
    }
    for key, value in default_repos.items():

        if key not in os.environ:
            # print("Checking '{}'...".format(key))
            path = os.path.normpath(
                os.path.join(
                    PYPE_SETUP_ROOT,
                    value['submodule_root'],
                    value['name']
                )
            )
            # print("Checking path '{}'...".format(path))
            if "path" is value['env']:
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
                _test_module_import(path, value['subdir'])
            os.environ[key] = path
