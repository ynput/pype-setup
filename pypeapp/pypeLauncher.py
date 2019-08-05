import os
import sys
import platform


class PypeLauncher(object):
    """ Class handling start of different modes of Pype.

        Most of its methods are called by :mod:`cli` module.
    """

    _kwargs = None
    _args = None

    def print_info(self):
        """ This will print additional information to console. """
        from pypeapp.lib.Terminal import Terminal

        t = Terminal()

        t.echo("... Running pype from\t\t\t[ {} ]".format(
            os.environ.get('PYPE_ROOT')))
        t.echo("... Using config at\t\t\t[ {} ]".format(
            os.environ.get('PYPE_CONFIG')))
        t.echo("... Projects root\t\t\t[ {} ]".format(
            os.environ.get('PYPE_STUDIO_PROJECTS_PATH')))
        t.echo("... Using mongodb\t\t\t[ {} ]".format(
            os.environ.get("AVALON_MONGO")))
        if os.environ.get('FTRACK_SERVER'):
            t.echo("... Using FTrack at\t\t\t[ {} ]".format(
                os.environ.get("FTRACK_SERVER")))
        if os.environ.get('DEADLINE_REST_URL'):
            t.echo("... Using Deadline webservice at\t[ {} ]".format(
                os.environ.get("DEADLINE_REST_URL")))
        if os.environ.get('MUSTER_REST_URL'):
            t.echo("... Using Muster at\t\t[ {} ]".format(
                os.environ.get("DEADLINE_REST_URL")))

    def _add_modules(self):
        """ Include in **PYTHONPATH** all necessary packages.

            This will add all paths to deployed repos and also everything
            in ""vendor/python"". It will add it to :class:`sys.path` and to
            **PYTHONPATH** environment variable.

            .. note:: This will append, not overwrite existing paths
        """
        from pypeapp.deployment import Deployment

        d = Deployment(os.environ.get('PYPE_ROOT', None))
        paths = d.get_deployment_paths()

        # add self
        paths.append(os.environ.get('PYPE_ROOT'))

        # additional vendor packages
        vendor_path = os.path.join(os.getenv('PYPE_ROOT'), 'vendor', 'python')

        with os.scandir(vendor_path) as vp:
            for entry in vp:
                if entry.is_dir():
                    paths.append(entry.path)

        self._update_python_path(paths)

    def _update_python_path(self, paths=None):
        if (os.environ.get('PYTHONPATH')):
            python_paths = os.environ.get('PYTHONPATH').split(os.pathsep)
        else:
            python_paths = []

        if not paths:
            # paths are not set, sync PYTHONPATH with sys.path only
            for p in python_paths:
                if p not in sys.path:
                    sys.path.append(p)
        else:
            for p in paths:
                if p not in python_paths:
                    os.environ['PYTHONPATH'] += os.pathsep + p
                if p not in sys.path:
                    sys.path.append(p)

    def _load_default_environments(self, tools):
        """ Load and apply default environment files. """

        import acre
        os.environ['PLATFORM'] = platform.system().lower()
        tools_env = acre.get_tools(tools)
        env = acre.compute(dict(tools_env), cleanup=False)
        env = acre.merge(env, dict(os.environ))
        os.environ = acre.append(dict(os.environ), env)
        os.environ = acre.compute(os.environ, cleanup=False)

    def launch_tray(self, debug=False):
        """ Method will launch tray.py

            :param debug: if True, tray will run in debug mode (not detached)
            :type debug: bool

            .. seealso:: :func:`subprocess.Popen`
        """
        import subprocess
        from pypeapp import Logger
        from pypeapp import execute

        self._initialize()

        if debug:
            pype_setup = os.getenv('PYPE_ROOT')
            items = [pype_setup, "pypeapp", "tray.py"]
            fname = os.path.sep.join(items)

            execute([
                sys.executable,
                "-u",
                fname
                ])
            return

        DETACHED_PROCESS = 0x00000008

        pype_setup = os.getenv('PYPE_ROOT')
        items = [pype_setup, "pypeapp", "tray.py"]
        fname = os.path.sep.join(items)

        args = ["pythonw", "-d", fname]
        if sys.platform.startswith('linux'):
            subprocess.Popen(
                args,
                universal_newlines=True,
                bufsize=1,
                # executable=sys.executable,
                env=os.environ,
                # stdin=None,
                stdout=None,
                stderr=None,
                preexec_fn=os.setpgrp
            )

        if sys.platform == 'win32':
            subprocess.Popen(
                args,
                universal_newlines=True,
                bufsize=1,
                cwd=None,
                # executable=sys.executable,
                env=os.environ,
                # stdin=None,
                stdout=open(Logger.get_file_path(), 'w+'),
                stderr=subprocess.STDOUT,
                creationflags=DETACHED_PROCESS
            )

    def launch_local_mongodb(self):
        """ This will run local instance of mongodb.

        :returns: process return code
        :rtype: int

        """
        import subprocess
        from pypeapp.lib.Terminal import Terminal

        self._initialize()
        t = Terminal()

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
            t.echo("Local mongodb is running...")
            t.echo("Using port {} and db at {}".format(
                os.environ["AVALON_MONGO_PORT"], location))
            p = subprocess.Popen(
                ["mongod", "--dbpath", location, "--port",
                 os.environ["AVALON_MONGO_PORT"]], close_fds=True
            )
        elif platform.system().lower() == "windows":
            t.echo("Local mongodb is running...")
            t.echo("Using port {} and db at {}".format(
                os.environ["AVALON_MONGO_PORT"], location))
            p = subprocess.Popen(
                ["start", "Avalon MongoDB", "call", "mongod", "--dbpath",
                 location, "--port", os.environ["AVALON_MONGO_PORT"]],
                shell=True
            )
        return p.returncode

    def launch_eventserver(self):
        """
        This will run standalone ftrack eventserver.

        :returns: process return code
        :rtype: int

        .. deprecated:: 2.1
           Use :meth:`launch_eventservercli` instead.
        """
        from pypeapp import execute

        self._initialize()

        pype_setup = os.getenv('PYPE_ROOT')
        items = [
            pype_setup, "repos", "pype", "pype", "ftrack", "ftrack_server",
            "event_server.py"
        ]
        fname = os.path.sep.join(items)

        returncode = execute([
            sys.executable, "-u", fname
        ])
        return returncode

    def launch_eventservercli(self, args):
        """ This will run standalone ftrack eventserver headless.

        :param args: arguments passed to event server script. See event server
                     help for more info.
        :type args: list
        :returns: process return code
        :rtype: int
        """
        from pypeapp import execute
        self._initialize()

        pype_setup = os.getenv('PYPE_ROOT')
        items = [
            pype_setup, "repos", "pype", "pype", "ftrack", "ftrack_server",
            "event_server_cli.py"
        ]
        fname = os.path.sep.join(items)

        returncode = execute([
            sys.executable, "-u", fname
        ] + args)
        return returncode

    def install(self, force):
        """ This will run venv installation process.

        :param force: forcefully overwrite existing environment
        :type force: bool

        .. seealso:: :mod:`install_env`
        """
        from install_env import install
        install(force)

    def validate(self):
        """ This will run deployment validation process.

        Upon failure it will exit with return code 200
        to signal shell installation process about validation error.

        .. seealso:: :func:`Deployment.validate`
        """
        from pypeapp.deployment import Deployment, DeployException
        d = Deployment(os.environ.get('PYPE_ROOT', None))
        try:
            d.validate()
        except DeployException:
            sys.exit(200)

    def deploy(self, force):
        """ This will run deployment process.

        Upon failure it will exit with return code 200
        to signal shell installation process about deployment error.

        .. seealso:: :func:`Deployment.deploy`

        """
        from pypeapp.deployment import Deployment, DeployException
        d = Deployment(os.environ.get('PYPE_ROOT', None))
        try:
            d.deploy(force)
        except DeployException:
            sys.exit(200)
        pass

    def _initialize(self):
        from pypeapp.storage import Storage
        from pypeapp.deployment import Deployment
        from pypeapp.lib.Terminal import Terminal

        # if not called, console coloring will get mangled in python.
        Terminal()
        pype_setup = os.getenv('PYPE_ROOT')
        d = Deployment(pype_setup)

        tools, config_path = d.get_environment_data()

        os.environ['PYPE_CONFIG'] = config_path
        os.environ['TOOL_ENV'] = os.path.normpath(
            os.path.join(
                config_path,
                'environments'))
        self._add_modules()
        Storage().update_environment()
        self._load_default_environments(tools=tools)
        self.print_info()

    def texture_copy(self, project, asset, path):
        """ This will copy textures specified in path asset publish
        directory. It doesn't interact with avalon, just copying files.

        :param project: name of project
        :type project: str
        :param asset: name of asset
        :type asset: str
        :param path: path to textures
        :type path: str
        """
        from pypeapp import execute

        self._initialize()

        pype_setup = os.getenv('PYPE_ROOT')
        items = [
            pype_setup, "repos", "pype", "pype", "tools",
            "texture_copy", "app.py"
        ]
        fname = os.path.sep.join(items)

        returncode = execute([
            sys.executable, "-u", fname, "--project", project,
            "--asset", asset, "--path", path])
        return returncode

    def publish(self, gui=False, paths=None):
        """ Starts headless publishing.

        Publish collects json from current working directory
        or supplied paths argument.

        :param gui: launch Pyblish gui or not
        :type gui: bool
        :param paths: paths to jsons
        :type paths: list
        """
        # from pypeapp import execute
        from pypeapp import Logger
        from pypeapp.lib.Terminal import Terminal
        from pypeapp.deployment import Deployment
        import json

        t = Terminal()

        error_format = "Failed {plugin.__name__}: {error} -- {error.traceback}"

        # uninstall static part of AVALON environment
        # FIXME: this is probably very wrong way to do it. Can acre adjust
        # replace parts of environment instead of merging it?

        pype_setup = os.getenv('PYPE_ROOT')
        d = Deployment(pype_setup)

        tools, config_path = d.get_environment_data()
        os.environ['PYPE_CONFIG'] = config_path
        avalon_path = os.path.join(os.environ.get("PYPE_CONFIG"),
                                   "environments", "avalon.json")
        with open(avalon_path) as av_env:
            avalon_data = json.load(av_env)

        t.echo(">>> Unsetting static AVALON environment variables ...")
        for k, v in avalon_data.items():
            os.environ[k] = ""

        self._initialize()
        log = Logger().get_logger('publish')
        from pype import install, uninstall
        # Register target and host
        import pyblish.api

        install()
        pyblish.api.register_target("filesequence")
        pyblish.api.register_host("shell")

        self._update_python_path()

        if not any(paths):
            log.error("No publish paths specified")
            return False

        if paths:
            os.environ["PYPE_PUBLISH_PATHS"] = os.pathsep.join(paths)

        if gui:
            import pyblish_qml
            pyblish_qml.show(modal=True)
        else:

            import pyblish.util
            t.echo(">>> Running publish ...")

            # Error exit as soon as any error occurs.
            for result in pyblish.util.publish_iter():
                if result["error"]:
                    log.error(error_format.format(**result))
                    uninstall()
                    sys.exit(1)

        uninstall()

    def run_pype_tests(self):
        """ Run pytest on `pype/pype/tests` directory """

        from pypeapp.lib.Terminal import Terminal
        import pytest

        self._initialize()
        t = Terminal()

        t.echo(">>> Running test on pype ...")

        pytest.main(['-x', '--capture=sys', '--print',
                     '-W', 'ignore::DeprecationWarning',
                     os.path.join(os.getenv('PYPE_ROOT'),
                                  'repos', 'pype', 'pype', 'tests')])

    def run_pype_setup_tests(self):
        """ Run pytest on `tests` directory """

        from pypeapp.lib.Terminal import Terminal
        import pytest

        self._initialize()
        t = Terminal()

        t.echo(">>> Running test on pype-setup ...")

        pytest.main(['-x', '--capture=sys', '--print',
                     '-W', 'ignore::DeprecationWarning',
                     os.path.join(os.getenv('PYPE_ROOT'),
                                  'tests')])

    def make_docs(self):
        """
        Generate documentation using Sphinx for both **pype-setup** and
        **pype**.
        """

        from pypeapp.lib.Terminal import Terminal
        from pypeapp import execute

        self._initialize()
        t = Terminal()

        source_dir_setup = os.path.join(
            os.environ.get("PYPE_ROOT"), "docs", "source")
        build_dir_setup = os.path.join(
            os.environ.get("PYPE_ROOT"), "docs", "build")

        source_dir_pype = os.path.join(
            os.environ.get("PYPE_ROOT"), "repos", "pype", "docs", "source")
        build_dir_pype = os.path.join(
            os.environ.get("PYPE_ROOT"), "repos", "pype", "docs", "build")

        t.echo(">>> Generating documentation ...")
        t.echo("  - Cleaning up ...")
        execute(['sphinx-build', '-M', 'clean',
                 source_dir_setup, build_dir_setup],
                shell=True)
        execute(['sphinx-build', '-M', 'clean',
                 source_dir_pype, build_dir_pype],
                shell=True)
        t.echo("  - generating sources ...")
        execute(['sphinx-apidoc', '-M', '-f', '-d', '4', '--ext-autodoc',
                 '--ext-intersphinx', '--ext-viewcode', '-o',
                 source_dir_setup, 'pypeapp'], shell=True)
        vendor_ignore = os.path.join(
            os.environ.get("PYPE_ROOT"), "repos", "pype", "pype", "vendor")
        execute(['sphinx-apidoc', '-M', '-f', '-d', '6', '--ext-autodoc',
                 '--ext-intersphinx', '--ext-viewcode', '-o',
                 source_dir_pype, 'pype',
                 '{}{}*'.format(vendor_ignore, os.path.sep)], shell=True)
        t.echo("  - Building html ...")
        execute(['sphinx-build', '-M', 'html',
                 source_dir_setup, build_dir_setup],
                shell=True)
        execute(['sphinx-build', '-M', 'html',
                 source_dir_pype, build_dir_pype],
                shell=True)
        t.echo(">>> Done. Documentation id generated:")
        t.echo("*** For pype-setup: [ {} ]".format(build_dir_setup))
        t.echo("*** For pype: [ {} ]".format(build_dir_pype))
