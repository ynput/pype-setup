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
        from vendor import bin

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

        elif self._kwargs.eventserver:
            self._launch_eventserver()

        elif self._kwargs.eventservercli:
            self._launch_eventservercli()

        elif self._kwargs.localmongodb:
            self._launch_local_mongodb()

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
        parser.add_argument("--publish-gui",
                            help=("Publish with GUI from current working"
                                  "directory, or supplied --root"),
                            action="store_true")
        parser.add_argument("--root", help="set project root directory")
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

        if (os.environ.get('PYTHONPATH')):
            python_paths = os.environ.get('PYTHONPATH').split(os.pathsep)
        else:
            python_paths = []

        # add only if not already present
        for p in paths:
            if p not in python_paths:
                os.environ['PYTHONPATH'] += os.pathsep + p
            if p not in sys.path:
                sys.path.append(p)
        pass

    def _load_default_environments(self, tools):
        """ Load and apply default environment files. """

        import acre
        os.environ['PLATFORM'] = platform.system().lower()
        tools_env = acre.get_tools(tools)
        env = acre.compute(dict(tools_env))
        env = acre.merge(env, dict(os.environ))
        os.environ = acre.append(dict(os.environ), env)
        pass

    def _launch_tray(self, debug=False):
        """ Method will launch tray.py

            :param debug: if True, tray will run in debug mode (not detached)
            :type debug: bool

            .. seealso:: :func:`subprocess.Popen`
        """
        import subprocess
        from pypeapp import Logger
        from pypeapp.storage import Storage
        from pypeapp import execute
        from pypeapp.deployment import Deployment

        d = Deployment(os.environ.get('PYPE_ROOT', None))

        tools, config_path = d.get_environment_data()

        os.environ['PYPE_CONFIG'] = config_path
        os.environ['TOOL_ENV'] = os.path.normpath(os.path.join(config_path,
                                                  'environments'))

        self._add_modules()
        Storage().update_environment()
        self._load_default_environments(tools=tools)

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
        from pypeapp.storage import Storage
        from pypeapp import execute
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
        from pypeapp.storage import Storage
        from pypeapp import execute
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
        items = [
            pype_setup, "repos", "pype", "pype", "ftrack", "ftrack_server",
            "event_server_cli.py"
        ]
        fname = os.path.sep.join(items)

        returncode = execute([
            sys.executable, "-u", fname
        ])
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
