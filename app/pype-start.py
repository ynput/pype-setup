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
import contextlib

from app.api import (
    env_install,
    env_uninstall,

    forward,
    git_make_repository,
    Logger
)

from app import (
    _templates_loaded,
)

self = sys.modules[__name__]
self._templates_loaded = _templates_loaded


log = Logger.getLogger(__name__)


if os.path.basename(__file__) in os.listdir(os.getcwd()):
    '''
    Having avalon.py in the current working directory
    exposes it to Python's import mechanism which conflicts
    with the actual avalon Python package.
    '''
    sys.stderr.write("Error: Please change your current "
                     "working directory\n%s\n" % os.getcwd())
    sys.exit(1)


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
        log.warning("Sorry, there are some dependencies missing"
                    "from your system.\n")
        log.warning("\n".join(" - %s"
                              % d for d in missing_dependencies) + "\n")
        log.warning("See https://getavalon.github.io/2.0/howto/#install "
                    "for more details.")
        sys.exit(1)

    if root is not None:
        os.environ["AVALON_PROJECTS"] = root
    else:
        try:
            root = os.environ["AVALON_PROJECTS"]
        except KeyError:
            root = os.path.join(os.environ["AVALON_EXAMPLES"], "projects")
            os.environ["AVALON_PROJECTS"] = root


def main():
    import argparse
    import app
    if not app._templates_loaded:
        env_install()

    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument("--root", help="Projects directory")
    parser.add_argument("--launcher", action="store_true",
                        help="Launch avalon launcher app")
    parser.add_argument("--init", action="store_true",
                        help="Establish a new project in the "
                             "current working directory")
    parser.add_argument("--load", action="store_true",
                        help="Load project at the current working directory")
    parser.add_argument("--save", action="store_true",
                        help="Save project from the current working directory")
    parser.add_argument("--make", action="store_true",
                        help="Install dependent repositories from "
                        "templates/install/pype_repos.toml, also checkout"
                        "to defined branches")
    parser.add_argument("--forward",
                        help="Run arbitrary command from setup environment")
    parser.add_argument("--publish", action="store_true",
                        help="Publish from current working directory, "
                             "or supplied --root")
    parser.add_argument("--actionserver", action="store_true",
                        help="launch action server for ftrack")
    parser.add_argument("--ftracklogout", action="store_true",
                        help="Logout from Ftrack")
    parser.add_argument("--terminal", action="store_true",
                        help="Logout from Ftrack")
    parser.add_argument("--local-mongodb", dest="localdb", action="store_true",
                        help="Start local mongo server do `localhost`")
    parser.add_argument("--testing", help="Testing templates")

    kwargs, args = parser.parse_known_args()

    if any([kwargs.launcher,
            kwargs.init,
            kwargs.load,
            kwargs.save,
            kwargs.publish,
            kwargs.actionserver,
            kwargs.ftracklogout,
            kwargs.localdb, ]):
        _install(root=kwargs.root)

    if kwargs.launcher:
        root = os.environ["AVALON_PROJECTS"]
        returncode = forward([
            sys.executable, "-u", "-m", "launcher", "--root", root
        ] + args)

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

    elif kwargs.make:
        # TODO: fix loop with Templates adding into function called
        # independetly on running this make procedure
        returncode = git_make_repository()

    elif kwargs.forward:
        returncode = forward(kwargs.forward.split())

    elif kwargs.publish:
        os.environ["PYBLISH_HOSTS"] = "shell"

        with install():
            returncode = forward([
                sys.executable, "-u", "-m", "pyblish", "gui"
            ] + args, silent=True)

    elif kwargs.actionserver:
        args = ["--actionserver"]

        # TODO this path is same for more args!
        stud_config = os.getenv('PYPE_STUDIO_CONFIG')
        items = [stud_config, "pype", "ftrack", "ftrackRun.py"]
        fname = os.path.sep.join(items)

        returncode = forward([
            sys.executable, "-u", fname
        ] + args)

    elif kwargs.ftracklogout:
        args = ["--logout"]

        stud_config = os.getenv('PYPE_STUDIO_CONFIG')
        items = [stud_config, "pype", "ftrack", "ftrackRun.py"]
        fname = os.path.sep.join(items)

        returncode = forward([
            sys.executable, "-u", fname
        ] + args)

    elif kwargs.terminal:
        import app.cli
        returncode = app.cli.main()

    elif kwargs.localdb:
        # import app.local_mongo_server
        # app.local_mongo_server.main()
        # args = ["--actionserver"]

        # TODO this path is same for more args!
        pype_setup_root = os.getenv('PYPE_SETUP_ROOT')
        items = [pype_setup_root, "app", "local_mongo_server.py"]
        fname = os.path.sep.join(items)

        returncode = forward([
            sys.executable, "-u", fname
        ] + args)
        # returncode = 1

    elif kwargs.testing:
        from app import pypeline
        # template should be filled and environment setup
        returncode = pypeline.test()
        env_uninstall()
        # template should be empty
        returncode = pypeline.test()

    else:
        print(__doc__)
        returncode = 1

    env_uninstall()
    return returncode


if __name__ == '__main__':
    try:
        returncode = main()
        sys.exit(returncode)
    except Exception as e:
        print(e)
        sys.exit(1)
