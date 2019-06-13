import argparse
import os
import sys
import platform


class PypeLauncher(object):
    """ Class handling start of different modes of Pype.

        Based of arguments passed to constructor, :class:`PypeLauncher` will
        launch Pype in different modes of operation:

        - **tray**: will detach from terminal and create GUI (icon in tray) to
          control pype.
        - **traydebug**: will do the same as above but won't detach from
          terminal, making it easy to see debug output in *stdout*
          and *stderr*.
        - **local_mongodb**: will start local mongodb instance based on
          configuration found in **config**.
        - **eventserver**: will launch standalone ftrack event server (usually
          started as system service or daemon on server as there has to be only
          one instance of it per site running reliably).

        Additional arguments are:

        - **install**: will install Pype - setup python environment and deploy
          repositories.

          - **force**: used in conjunction with **install** will force
            to overwrite environment directory with new one.

          - **skip**: is implemented on shell side but to that flag will skip
            installation of environmen at all.

        - **deploy**: will deploy repositories set in ``deploy/deploy.json``
          or in it's override directory. It will deploy git repositories and
          install additional python dependencies via pip.

          - **force**: used in conjunction with **deploy** will force
            git to overwrite all existing repositories already in path.

        - **validate**: will validate Pype deployment, comparing it to
          ``deploy/deploy.json`` or it override.

          - **skipmissing**: will skip validation of missing repositories.
            used during installation stage.

    """

    _kwargs = None
    _args = None

    def __init__(self, args=None):
        """ Constructor will parse arguments and then execute different modes
            of pype app.

            :param args: If supplied, used instead commandline arguments. If
                         set None, then commandline arguments will be used.
            :type args: List or None
        """
        parser = self._parse_args()
        self._kwargs, self._args = parser.parse_known_args(args)

        if self._kwargs.tray or self._kwargs.traydebug:
            if self._kwargs.traydebug:
                os.environ['PYPE_DEBUG'] = '3'
            self._launch_tray(debug=self._kwargs.traydebug)

        elif self._kwargs.install:
            self._install()

        elif self._kwargs.validate:
            self._validate()

        elif self._kwargs.deploy:
            self._deploy()

        elif self._kwargs.eventservercli:
            self._launch_eventservercli()

        elif self._kwargs.localmongodb:
            self._launch_local_mongodb()

        elif self._kwargs.publish:
            self._publish()

        elif self._kwargs.publishgui:
            self._publish(gui=True)

        elif self._kwargs.texturecopy:
            self._texture_copy()

    def _parse_args(self):
        """ Create argument parser.

            :returns: argument parser
            :rtype: :class:`ArgumentParser`
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("--install", help="Install environment",
                            action="store_true")
        parser.add_argument("--force",
                            help=("Used with --install will force "
                                  "installation of environment into "
                                  "destination directory even if it exists "
                                  "and is not empty. "
                                  "Content will be erased and replaced by "
                                  "new environment. With --deploy it will "
                                  "force existing repositories to be "
                                  "overrided by specified ones in "
                                  "deploy.json."),
                            action="store_true"
                            )
        parser.add_argument("--deploy",
                            help=("Deploy Pype repos and dependencies"),
                            action="store_true")
        parser.add_argument("--validate",
                            help="Validate Pype deployment",
                            action="store_true")
        parser.add_argument("--skipmissing",
                            help=("Skip missing repos during validation"),
                            action="store_true")
        parser.add_argument("--tray",
                            help="Launch Pype Tray",
                            action="store_true")
        parser.add_argument("--traydebug",
                            help="Launch Pype Tray in debug mode",
                            action="store_true")
        parser.add_argument("--localmongodb",
                            help=("Launch instance of local mongodb server"),
                            action="store_true")
        parser.add_argument("--publish",
                            help=("Publish from current working"
                                  "directory, or supplied --root"),
                            action="store_true")
        parser.add_argument("--texturecopy",
                            help="Run texture copy tool",
                            action="store_true")
        parser.add_argument("--asset", help="asset name")
        parser.add_argument("--project", help="project name")
        parser.add_argument("--publishgui",
                            help=("Publish with GUI from current working"
                                  "directory, or supplied --root"),
                            action="store_true")
        parser.add_argument("--root", help="set project root directory")
        parser.add_argument("--path", help="")
        parser.add_argument("--paths", help="set files or directories for "
                            "publishing", nargs="*", default=[])
        parser.add_argument("--eventserver",
                            help="Launch Pype ftrack event server",
                            action="store_true")
        parser.add_argument("--eventservercli",
                            help="Launch Pype ftrack event server headless",
                            action="store_true")

        return parser

    def _add_modules(self):
        """ Include in **PYTHONPATH** all necessary packages.

            This will add all paths to deployed repos and also everything
            in ""vendor/python"". It will add it to :class:`sys.path` and to
            **PYTHONPATH** environment variable.

            .. note:: This will append, not overwrite existing paths
        """
        from pypeapp.deployment import Deployment
        # from pypeapp import Logger

        # log = Logger().get_logger('launcher')
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
        env = acre.compute(dict(tools_env))
        env = acre.merge(env, dict(os.environ))
        os.environ = acre.append(dict(os.environ), env)
        os.environ = acre.compute(os.environ)
        pass

    def _launch_tray(self, debug=False):
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
                ] + self._args)
            return

        DETACHED_PROCESS = 0x00000008

        pype_setup = os.getenv('PYPE_ROOT')
        items = [pype_setup, "pypeapp", "tray.py"]
        fname = os.path.sep.join(items)

        args = [sys.executable, "-d", fname]
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

    def _launch_local_mongodb(self):
        """ This will run local instance of mongodb. """
        from pypeapp import Logger
        import subprocess

        self._initialize()

        log = Logger().get_logger('mongodb')
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
            log.info("Local mongodb is running...")
            log.info("Using port {} and db at {}".format(
                os.environ["AVALON_MONGO_PORT"], location))
            p = subprocess.Popen(
                ["mongod", "--dbpath", location, "--port",
                 os.environ["AVALON_MONGO_PORT"]], close_fds=True
            )
        elif platform.system().lower() == "windows":
            log.info("Local mongodb is running...")
            log.info("Using port {} and db at {}".format(
                os.environ["AVALON_MONGO_PORT"], location))
            p = subprocess.Popen(
                ["start", "Avalon MongoDB", "call", "mongod", "--dbpath",
                 location, "--port", os.environ["AVALON_MONGO_PORT"]],
                shell=True
            )
        return p.returncode

    def _launch_eventserver(self):
        """ This will run standalone ftrack eventserver. """
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

    def _launch_eventservercli(self):
        """ This will run standalone ftrack eventserver headless. """
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
        ] + sys.argv)
        return returncode

    def _install(self):
        """ This will run venv installation process.

            .. seealso:: :mod:`install_env`
        """
        from install_env import install
        install(self._kwargs.force)

    def _validate(self):
        """ This will run deployment validation process.

            Upon failure it will exit with return code 200
            to signal shell installation process about validation error.

            .. seealso:: :func:`Deployment.validate`
        """
        from pypeapp.deployment import Deployment, DeployException
        d = Deployment(os.environ.get('PYPE_ROOT', None))
        try:
            d.validate(self._kwargs.skipmissing)
        except DeployException:
            sys.exit(200)

    def _deploy(self):
        """ This will run deployment process.

            Upon failure it will exit with return code 200
            to signal shell installation process about deployment error.

        .. seealso:: :func:`Deployment.deploy`

        """
        from pypeapp.deployment import Deployment, DeployException
        d = Deployment(os.environ.get('PYPE_ROOT', None))
        try:
            d.deploy(self._kwargs.force)
        except DeployException:
            sys.exit(200)
        pass

    def _initialize(self):
        from pypeapp.storage import Storage
        from pypeapp.deployment import Deployment

        pype_setup = os.getenv('PYPE_ROOT')
        d = Deployment(pype_setup)

        tools, config_path = d.get_environment_data()

        os.environ['PYPE_CONFIG'] = config_path
        os.environ['TOOL_ENV'] = os.path.normpath(os.path.join(config_path,
                                                  'environments'))
        self._add_modules()
        Storage().update_environment()
        self._load_default_environments(tools=tools)

    def _texture_copy(self):
        from pypeapp import execute

        if not self._kwargs.project:
            print("Missing --project argument")
            exit(1)
        if not self._kwargs.asset:
            print("Missing --asset argument")
            exit(1)
        if not self._kwargs.project:
            print("Missing --path argument")
            exit(1)

        self._initialize()

        pype_setup = os.getenv('PYPE_ROOT')
        items = [
            pype_setup, "repos", "pype", "pype", "tools",
            "texture_copy", "app.py"
        ]
        fname = os.path.sep.join(items)

        returncode = execute([
            sys.executable, "-u", fname, "--project", self._kwargs.project,
            "--asset", self._kwargs.asset, "--path", self._kwargs.path])
        return returncode

    def _publish(self, gui=False):
        """ Starts headless publishing.

            Publish collects json from current working directory
            or supplied --path argument

        """
        # handle paths

        # from pypeapp import execute
        from pypeapp import Logger
        from pypeapp.lib.Terminal import Terminal
        from pypeapp.deployment import Deployment
        import json

        t = Terminal()

        error_format = "Failed {plugin.__name__}: {error} -- {error.traceback}"
        log = Logger().get_logger('publish')

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

        from pype import install, uninstall
        # Register target and host
        import pyblish.api

        install()
        pyblish.api.register_target("filesequence")
        pyblish.api.register_host("shell")

        self._update_python_path()

        paths = self._kwargs.paths

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
            context = pyblish.util.publish()

            if not context:
                log.warning("Nothing collected.")
                uninstall()
                sys.exit(1)

            # Collect errors, {plugin name: error}
            error_results = [r for r in context.data["results"] if r["error"]]

            if error_results:
                log.error("Errors occurred ...")
                for result in error_results:
                    log.error(error_format.format(**result))
                uninstall()
                sys.exit(2)
        uninstall()
