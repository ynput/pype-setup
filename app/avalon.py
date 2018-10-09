"""Avalon Command-line Interface

This module contains a CLI towards Avalon and all of what
is bundled together in this distribution.

- https://github.com/getavalon/setup

dependencies:
    - Python 2.6+ or 3.6+
    - PyQt5

example:
    $ python avalon.py --help

overrides:
    avalon.py takes into account dependencies bundled
    together with this distribution, but these can be
    overridden via environment variables.

    Set any of the below to override which path to put
    on your PYTHONPATH

    # Database
    - AVALON_MONGO=mongodb://localhost:27017
    - AVALON_DB=avalon

    # Dependencies
    - PYBLISH_BASE=absolute/path
    - PYBLISH_QML=absolute/path
    - AVALON_CORE=absolute/path
    - AVALON_LAUNCHER=absolute/path
    - AVALON_EXAMPLES=absolute/path

    # Enable additional output
    - AVALON_DEBUG=True

"""

import os
import sys
import shutil
import tempfile
import platform
import contextlib
import subprocess

from app.api import (
    Templates,
    Loaded_templates,

    studio_depandecies,
    get_config_repos,

    forward,
    git_update,
    git_checkout
)

print(get_config_repos())


# Having avalon.py in the current working directory
# exposes it to Python's import mechanism which conflicts
# with the actual avalon Python package.
if os.path.basename(__file__) in os.listdir(os.getcwd()):
    sys.stderr.write("Error: Please change your current "
                     "working directory\n%s\n" % os.getcwd())
    sys.exit(1)


PYPE_APP_ROOT = os.path.dirname(os.path.abspath(__file__))


init = """\
from avalon import api, shell
api.install(shell)
"""


@contextlib.contextmanager
def install():
    tempdir = tempfile.mkdtemp()
    usercustomize = os.path.join(tempdir, "usercustomize.py")

    with open(usercustomize, "w") as f:
        f.write(init)

    os.environ["PYTHONVERBOSE"] = "True"
    os.environ["PYTHONPATH"] = os.pathsep.join([
        tempdir, os.environ["PYTHONPATH"]
    ])

    try:
        yield
    finally:
        shutil.rmtree(tempdir)


def _install(root=None):
    missing_dependencies = list()
    for dependency in ("PyQt5",):
        try:
            __import__(dependency)
        except ImportError:
            missing_dependencies.append(dependency)

    if missing_dependencies:
        print("Sorry, there are some dependencies missing from your system.\n")
        print("\n".join(" - %s" % d for d in missing_dependencies) + "\n")
        print("See https://getavalon.github.io/2.0/howto/#install "
              "for more details.")
        sys.exit(1)

    # Enable overriding from local environment
    for dependency, name in (("PYBLISH_BASE", "pyblish-base"),
                             ("PYBLISH_QML", "pyblish-qml"),
                             ("PYBLISH_LITE", "pyblish-lite"),
                             ("AVALON_CORE", "avalon-core"),
                             ("AVALON_LAUNCHER", "avalon-launcher"),
                             ("AVALON_EXAMPLES", "avalon-examples")):
        if dependency not in os.environ:
            os.environ[dependency] = os.path.join(PYPE_APP_ROOT, "repos", name)

    os.environ["PYTHONPATH"] = os.pathsep.join(
        # Append to PYTHONPATH
        os.getenv("PYTHONPATH", "").split(os.pathsep) + [
            # Third-party dependencies for Avalon
            os.path.normpath(
                os.path.join(PYPE_APP_ROOT, "vendor")
            ),

            # Default config and dependency
            os.getenv("PYBLISH_BASE"),
            os.getenv("PYBLISH_QML"),
            os.getenv("PYBLISH_LITE"),

            # The Launcher itself
            os.getenv("AVALON_LAUNCHER"),
            os.getenv("AVALON_CORE"),
        ]
    )

    # get studio depandencies into PATH and PYTHONPATH
    studio_depandecies()

    os.environ["PATH"] = os.pathsep.join([
        # Expose "avalon", overriding existing
        os.path.normpath(PYPE_APP_ROOT),

        os.environ["PATH"],

        # Add OS-level dependencies - absolete!
        # TODO: remove this feature after templates work
        os.path.join(
            os.environ["PYPE_STUDIO_TEMPLATES"],
            "templates",
            "bin",
            platform.system().lower()
        )
    ])

    # Override default configuration by setting this value.
    if "AVALON_CONFIG" not in os.environ:
        os.environ["AVALON_CONFIG"] = "polly"
        os.environ["PYTHONPATH"] += os.pathsep + os.path.join(
            PYPE_APP_ROOT, "repos", "mindbender-config")

    if root is not None:
        os.environ["AVALON_PROJECTS"] = root
    else:
        try:
            root = os.environ["AVALON_PROJECTS"]
        except KeyError:
            root = os.path.join(os.environ["AVALON_EXAMPLES"], "projects")
            os.environ["AVALON_PROJECTS"] = root

    try:
        config = os.environ["AVALON_CONFIG"]
    except KeyError:
        config = "polly"
        os.environ["AVALON_CONFIG"] = config

    if subprocess.call([sys.executable, "-c", "import %s" % config]) != 0:
        print("ERROR: config not found, check your PYTHONPATH.")
        sys.exit(1)


def main():
    import argparse

    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument("--root", help="Projects directory")
    parser.add_argument("--import", dest="import_", action="store_true",
                        help="Import an example project into the database")
    parser.add_argument("--export", action="store_true",
                        help="Export a project from the database")
    parser.add_argument("--build", action="store_true",
                        help="Build one of the bundled example projects")
    parser.add_argument("--update", action="store_true",
                        help="Update Avalon Setup to the latest version")
    parser.add_argument("--init", action="store_true",
                        help="Establish a new project in the "
                             "current working directory")
    parser.add_argument("--load", action="store_true",
                        help="Load project at the current working directory")
    parser.add_argument("--save", action="store_true",
                        help="Save project from the current working directory")
    parser.add_argument("--forward",
                        help="Run arbitrary command from setup environment")
    parser.add_argument("--publish", action="store_true",
                        help="Publish from current working directory, "
                             "or supplied --root")

    kwargs, args = parser.parse_known_args()

    _install(root=kwargs.root)

    cd = os.path.normpath(os.environ["PYPE_SETUP_ROOT"])
    examplesdir = os.getenv("AVALON_EXAMPLES",
                            os.path.join(
                                cd,
                                "app",
                                "repos",
                                "avalon-examples"
                            )
                            )

    if kwargs.import_:
        fname = os.path.join(examplesdir, "import.py")
        returncode = forward(
            [sys.executable, "-u", fname] + args)

    elif kwargs.export:
        fname = os.path.join(examplesdir, "export.py")
        returncode = forward(
            [sys.executable, "-u", fname] + args)

    elif kwargs.build:
        fname = os.path.join(examplesdir, "build.py")
        returncode = forward(
            [sys.executable, "-u", fname] + args)

    elif kwargs.init:
        returncode = forward([
            sys.executable, "-u", "-m",
            "avalon.inventory", "--init"])

    elif kwargs.load:
        returncode = forward([
            sys.executable, "-u", "-m",
            "avalon.inventory", "--load"])

    elif kwargs.save:
        returncode = forward([
            sys.executable, "-u", "-m",
            "avalon.inventory", "--save"])

    elif kwargs.update:
        returncode = git_update(cd)

    elif kwargs.forward:
        returncode = forward(kwargs.forward.split())

    elif kwargs.publish:
        os.environ["PYBLISH_HOSTS"] = "shell"

        with install():
            returncode = forward([
                sys.executable, "-u", "-m", "pyblish", "gui"
            ] + args, silent=True)

    else:
        root = os.environ["AVALON_PROJECTS"]
        returncode = forward([
            sys.executable, "-u", "-m", "launcher", "--root", root
        ] + args)

    sys.exit(returncode)


if __name__ == '__main__':
    main()
