import os
import sys
import platform


class PypeLauncher(object):
    """Class handling start of different modes of Pype.

    Most of its methods are called by :mod:`cli` module.
    """

    def print_info(self):
        """Print additional information to console."""
        from pypeapp.lib.Terminal import Terminal
        from pypeapp.lib.log import _mongo_settings

        t = Terminal()
        (
            host, port, database, username, password, collection, auth_db
        ) = _mongo_settings()

        infos = []
        if os.getenv('PYPE_DEV'):
            infos.append(("Pype variant", "staging"))
        else:
            infos.append(("Pype variant", "production"))
        infos.append(("Running pype from", os.environ.get('PYPE_SETUP_PATH')))
        infos.append(("Using config at", os.environ.get('PYPE_CONFIG')))
        infos.append(("Using mongodb", os.environ.get("AVALON_MONGO")))

        if os.environ.get("FTRACK_SERVER"):
            infos.append(("Using FTrack at",
                          os.environ.get("FTRACK_SERVER")))

        if os.environ.get('DEADLINE_REST_URL'):
            infos.append(("Using Deadline webservice at",
                          os.environ.get("DEADLINE_REST_URL")))

        if os.environ.get('MUSTER_REST_URL'):
            infos.append(("Using Muster at",
                          os.environ.get("MUSTER_REST_URL")))

        if host:
            infos.append(("Logging to mongodb", "{}/{}".format(
                host, database)))
            if port:
                infos.append(("  - port", port))
            if username:
                infos.append(("  - user", username))
            if collection:
                infos.append(("  - collection", collection))
            if auth_db:
                infos.append(("  - auth source", auth_db))

        maximum = max([len(i[0]) for i in infos])
        for info in infos:
            padding = (maximum - len(info[0])) + 1
            t.echo("... {}:{}[ {} ]".format(info[0], " " * padding, info[1]))
        print('\n')

    def _add_modules(self):
        """Include in **PYTHONPATH** all necessary packages.

        This will add all paths to deployed repos and also everything
        in ""vendor/python"". It will add it to :class:`sys.path` and to
        **PYTHONPATH** environment variable.

        .. note:: This will append, not overwrite existing paths
        """
        from pypeapp.deployment import Deployment

        d = Deployment(os.environ.get('PYPE_SETUP_PATH', None))
        paths = d.get_deployment_paths()

        # add self
        paths.append(os.environ.get('PYPE_SETUP_PATH'))

        # additional vendor packages
        vendor_path = os.path.join(
            os.getenv('PYPE_SETUP_PATH'), 'vendor', 'python'
        )

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
        """Load and apply default environment files."""
        import acre
        os.environ['PLATFORM'] = platform.system().lower()
        tools_env = acre.get_tools(tools)
        pype_paths_env = dict()
        for key, value in dict(os.environ).items():
            if key.startswith('PYPE_'):
                pype_paths_env[key] = value

        env = acre.append(tools_env, pype_paths_env)
        env = acre.compute(env, cleanup=True)
        os.environ = acre.append(dict(os.environ), env)
        os.environ = acre.compute(os.environ, cleanup=False)

    def launch_tray(self, debug=False):
        """Run tray.py.

        :param debug: if True, tray will run in debug mode (not detached)
        :type debug: bool

        .. seealso:: :func:`subprocess.Popen`
        """
        import subprocess
        from pypeapp import Logger
        from pypeapp import execute

        self._initialize()

        if debug:
            pype_setup = os.getenv('PYPE_SETUP_PATH')
            items = [
                pype_setup, "repos", "pype", "pype", "tools", "tray"
            ]
            fname = os.path.sep.join(items)

            execute([
                sys.executable,
                "-u",
                fname
                ])
            return

        DETACHED_PROCESS = 0x00000008  # noqa: N806

        pype_setup = os.getenv('PYPE_SETUP_PATH')
        items = [
            pype_setup, "repos", "pype", "pype", "tools", "tray"
        ]
        fname = os.path.sep.join(items)

        args = ["python", "-d", fname]
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
            args = ["pythonw", "-d", fname]
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
        """Run local instance of mongodb.

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
        if (platform.system().lower() == "linux"
                or platform.system().lower() == "darwin"):

            if platform.system().lower() == "darwin":
                t.echo(("*** You may need to allow mongod "
                        "to run in "
                        "[ System Settings / Security & Privacy ]"))
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
        else:
            t.echo("!!! Unsupported platorm - [ {} ]".format(
                platform.system().lower()
            ))
            return False
        return p.returncode

    def launch_eventserver(self):
        """Run standalone ftrack eventserver.

        :returns: process return code
        :rtype: int

        .. deprecated:: 2.1
           Use :meth:`launch_eventservercli` instead.
        """
        from pypeapp import execute

        self._initialize()

        pype_setup = os.getenv('PYPE_SETUP_PATH')
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
        """Run standalone ftrack eventserver headless.

        :param args: arguments passed to event server script. See event server
                     help for more info.
        :type args: list
        :returns: process return code
        :rtype: int
        """
        from pypeapp import execute
        self._initialize()

        pype_setup = os.getenv('PYPE_SETUP_PATH')
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
        """Run venv installation process.

        :param force: forcefully overwrite existing environment
        :type force: bool

        .. seealso:: :mod:`install_env`
        """
        from install_env import install
        install(force)

    def validate(self):
        """Run deployment validation process.

        Upon failure it will exit with return code 200
        to signal shell installation process about validation error.

        .. seealso:: :func:`Deployment.validate`
        """
        from pypeapp.deployment import Deployment, DeployException
        d = Deployment(os.environ.get('PYPE_SETUP_PATH', None))
        try:
            d.validate()
        except DeployException:
            sys.exit(200)

    def deploy(self, force):
        """Run deployment process.

        Upon failure it will exit with return code 200
        to signal shell installation process about deployment error.

        .. seealso:: :func:`Deployment.deploy`

        """
        from pypeapp.deployment import Deployment, DeployException
        d = Deployment(os.environ.get('PYPE_SETUP_PATH', None))
        try:
            d.deploy(force)
        except DeployException:
            sys.exit(200)
        pass

    def _initialize(self):
        from pypeapp.deployment import Deployment
        from pypeapp.lib.Terminal import Terminal
        try:
            import configparser
        except Exception:
            import ConfigParser as configparser

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(cur_dir, "config.ini")
        if os.path.exists(config_file_path):
            config = configparser.ConfigParser()
            config.read(config_file_path)
            try:
                value = config["DEFAULT"]["dev"]
                if value.lower() == "true":
                    os.environ["PYPE_DEV"] = "1"
            except KeyError:
                pass

        # if not called, console coloring will get mangled in python.
        Terminal()
        pype_setup = os.getenv('PYPE_SETUP_PATH')
        d = Deployment(pype_setup)

        tools, config_path = d.get_environment_data()

        os.environ['PYPE_CONFIG'] = config_path
        os.environ['TOOL_ENV'] = os.path.normpath(
            os.path.join(
                config_path,
                'environments'))
        self._add_modules()
        self._load_default_environments(tools=tools)
        self.print_info()

    def texture_copy(self, project, asset, path):
        """Copy textures specified in path asset publish directory.

        It doesn't interact with avalon, just copying files.

        :param project: name of project
        :type project: str
        :param asset: name of asset
        :type asset: str
        :param path: path to textures
        :type path: str
        """
        from pypeapp import execute

        self._initialize()

        pype_setup = os.getenv('PYPE_SETUP_PATH')
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
        """Start headless publishing.

        Publish collects json from current working directory
        or supplied paths argument.

        :param gui: launch Pyblish gui or not
        :type gui: bool
        :param paths: paths to jsons
        :type paths: list
        """
        from pypeapp.lib.Terminal import Terminal

        t = Terminal()

        error_format = "Failed {plugin.__name__}: {error} -- {error.traceback}"

        self._initialize()

        from pype import install, uninstall
        # Register target and host
        import pyblish.api

        install()
        pyblish.api.register_target("filesequence")
        pyblish.api.register_host("shell")

        self._update_python_path()

        if not any(paths):
            t.echo("No publish paths specified")
            return False

        os.environ["PYPE_PUBLISH_DATA"] = os.pathsep.join(paths)

        if gui:
            import pyblish_qml
            pyblish_qml.show(modal=True)
        else:

            import pyblish.util
            t.echo(">>> Running publish ...")

            # Error exit as soon as any error occurs.
            for result in pyblish.util.publish_iter():
                if result["error"]:
                    t.echo(error_format.format(**result))
                    uninstall()
                    sys.exit(1)

        uninstall()

    def run_pype_tests(self, keyword=None, id=None):
        """Run pytest on `pype/pype/tests` directory."""
        from pypeapp.lib.Terminal import Terminal
        import pytest

        self._initialize()
        t = Terminal()

        t.echo(">>> Running test on pype ...")
        args = ['-x', '--capture=sys', '--print',
                '-W', 'ignore::DeprecationWarning']

        if keyword:
            t.echo("  - selecting [ {} ]".format(keyword))
            args.append('-k')
            args.append(keyword)
            args.append(os.path.join(os.getenv('PYPE_SETUP_PATH'),
                                     'repos', 'pype', 'pype', 'tests'))

        elif id:
            t.echo("  - selecting test ID [ {} ]".format(id[0]))
            args.append(id[0])
        else:
            args.append(os.path.join(os.getenv('PYPE_SETUP_PATH'),
                                     'repos', 'pype', 'pype', 'tests'))

        pytest.main(args)

    def run_pype_setup_tests(self, keyword=None, id=None):
        """Run pytest on `tests` directory."""
        from pypeapp.lib.Terminal import Terminal
        import pytest

        self._initialize()
        t = Terminal()

        t.echo(">>> Running test on pype-setup ...")
        args = ['-x', '--capture=sys', '--print',
                '-W', 'ignore::DeprecationWarning']

        if keyword:
            t.echo("  - selecting [ {} ]".format(keyword))
            args.append('-k')
            args.append(keyword)
            args.append(os.path.join(os.getenv('PYPE_SETUP_PATH'), 'tests'))

        elif id:
            t.echo("  - selecting test ID [ {} ]".format(id[0]))
            args.append(id[0])
        else:
            args.append(os.path.join(os.getenv('PYPE_SETUP_PATH'), 'tests'))

        pytest.main(args)

    def pype_setup_coverage(self, pype):
        """Generate code coverage on pype-setup."""
        from pypeapp.lib.Terminal import Terminal
        import pytest

        self._initialize()
        t = Terminal()

        t.echo(">>> Generating coverage on pype-setup ...")
        pytest.main(['-v', '-x', '--color=yes', '--cov={}'.format(pype),
                     '--cov-config', '.coveragerc', '--cov-report=html',
                     '--ignore={}'.format(os.path.join(
                        os.environ.get("PYPE_SETUP_PATH"), "vendor")),
                     '--ignore={}'.format(os.path.join(
                        os.environ.get("PYPE_SETUP_PATH"), "repos"))
                     ])

    def make_docs(self):
        """Generate documentation using Sphinx.

        Documentation is generated for both **pype-setup** and **pype**.
        """
        from pypeapp.lib.Terminal import Terminal
        from pypeapp import execute

        self._initialize()
        t = Terminal()

        source_dir_setup = os.path.join(
            os.environ.get("PYPE_SETUP_PATH"), "docs", "source")
        build_dir_setup = os.path.join(
            os.environ.get("PYPE_SETUP_PATH"), "docs", "build")

        source_dir_pype = os.path.join(
            os.environ.get("PYPE_SETUP_PATH"), "repos",
            "pype", "docs", "source")
        build_dir_pype = os.path.join(
            os.environ.get("PYPE_SETUP_PATH"), "repos",
            "pype", "docs", "build")

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
            os.environ.get("PYPE_SETUP_PATH"), "repos",
            "pype", "pype", "vendor")
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

    def run_application(self, app, project, asset, task, tools, arguments):
        """Run application in project/asset/task context.

        With default or specified tools enviornment. This uses pre-defined
        launcher in `pype-config/launchers` where there must be *toml*
        file with definition and in platform directory its launcher shell
        script or binary executables. Arguments will be passed to this script
        or executable.

        :param app: Full application name (`maya_2018`)
        :type app: Str
        :param project: Project name
        :type project: Str
        :param asset: Asset name
        :type asset: Str
        :param task: Task name
        :type task: Str
        :param tools: Comma separated list of tools (`"mtoa_2.1.0,yeti_4"`)
        :type tools: Str
        :param arguments: List of other arguments passed to app
        :type: List
        :rtype: None
        """
        import toml
        import subprocess

        from pypeapp.lib.Terminal import Terminal
        from pypeapp import Anatomy

        t = Terminal()

        self._initialize()
        self._update_python_path()

        import acre
        from avalon import lib
        from pype import lib as pypelib

        abspath = lib.which_app(app)
        if abspath is None:
            t.echo("!!! Application [ {} ] is not registered.".format(app))
            t.echo("*** Please define its toml file.")
            return

        app_toml = toml.load(abspath)

        executable = app_toml['executable']
        app_dir = app_toml['application_dir']
        # description = app_toml.get('description', None)
        # preactions = app_toml.get('preactions', [])

        launchers_path = os.path.join(os.environ["PYPE_CONFIG"], "launchers")

        database = pypelib.get_avalon_database()

        avalon_project = database[project].find_one({
            "type": "project"
        })

        if avalon_project is None:
            t.echo(
                "!!! Project [ {} ] doesn't exists in Avalon.".format(project))
            return False

        # get asset from db
        avalon_asset = database[project].find_one({
            "type": "asset",
            "name": asset
        })

        avalon_tools = avalon_project["data"]["tools_env"]
        if tools:
            avalon_tools = tools.split(",") or []

        hierarchy = ""
        parents = avalon_asset["data"]["parents"] or []
        if parents:
            hierarchy = os.path.join(*parents)

        data = {
            "project": {
                "name": project,
                "code": avalon_project['data']['code']
            },
            "task": task,
            "asset": asset,
            "app": app_dir,
            "hierarchy": hierarchy,
        }

        anatomy = Anatomy(project)
        anatomy_filled = anatomy.format(data)
        workdir = os.path.normpath(anatomy_filled["work"]["folder"])

        # set PYPE_ROOT_* environments
        anatomy.set_root_environments()

        # set environments for Avalon
        os.environ["AVALON_PROJECT"] = project
        os.environ["AVALON_SILO"] = None
        os.environ["AVALON_ASSET"] = asset
        os.environ["AVALON_TASK"] = task
        os.environ["AVALON_APP"] = app.split("_")[0]
        os.environ["AVALON_APP_NAME"] = app
        os.environ["AVALON_WORKDIR"] = workdir
        os.environ["AVALON_HIERARCHY"] = hierarchy

        try:
            os.makedirs(workdir)
        except FileExistsError:
            pass

        tools_attr = [os.environ["AVALON_APP"], os.environ["AVALON_APP_NAME"]]
        tools_attr += avalon_tools

        print("TOOLS: {}".format(tools_attr))

        tools_env = acre.get_tools(tools_attr)
        env = acre.compute(tools_env)

        env = acre.merge(env, current_env=dict(os.environ))
        env = {k: str(v) for k, v in env.items()}

        # sanitize slashes in path
        env["PYTHONPATH"] = env["PYTHONPATH"].replace("/", "\\")
        env["PYTHONPATH"] = env["PYTHONPATH"].replace("\\\\", "\\")

        launchers_path = os.path.join(launchers_path,
                                      platform.system().lower())
        execfile = None

        if sys.platform == "win32":
            # test all avaliable executable format, find first and use it
            for ext in os.environ["PATHEXT"].split(os.pathsep):
                fpath = os.path.join(launchers_path.strip('"'),
                                     executable + ext)
                if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
                    execfile = fpath
                    break

                # Run SW if was found executable
            if execfile is not None:
                try:
                    t.echo(">>> Running [ {} {} ]".format(executable,
                                                          " ".join(arguments)))
                    args = [execfile]
                    args.extend(arguments)
                    subprocess.run(args, env=env)

                except ValueError as e:
                    t.echo("!!! Error while launching application:")
                    t.echo(e)
                    return
            else:
                t.echo(
                    "!!! cannot find application launcher [ {} ]".format(app))
                return

        if sys.platform.startswith('linux'):
            execfile = os.path.join(launchers_path.strip('"'), executable)
            if os.path.isfile(execfile):
                try:
                    fp = open(execfile)
                except PermissionError as p:
                    t.echo("!!! Access denied on launcher [ {} ]".format(app))
                    t.echo(p)
                    return

                fp.close()
            else:
                t.echo("!!! Launcher doesn\'t exist [ {} ]".format(
                    execfile))
                return

            # Run SW if was found executable
            if execfile is not None:
                args = ['/usr/bin/env', 'bash', execfile]
                args.extend(arguments)
                t.echo(">>> Running [ {} ]".format(" ".join(args)))
                try:
                    subprocess.run(args, env=env)
                except ValueError as e:
                    t.echo("!!! Error while launching application:")
                    t.echo(e)
                    return
            else:
                t.echo(
                    "!!! cannot find application launcher [ {} ]".format(app))
                return

    def validate_jsons(self):
        """Validate configuration JSON files for syntax errors."""
        import json
        import glob
        from pypeapp.lib.Terminal import Terminal

        self._initialize()
        t = Terminal()

        t.echo(">>> validating ...")
        files = [f for f in glob.glob(
            os.environ.get("PYPE_CONFIG") + os.path.sep + "**/*.json",
            recursive=True)] or []

        files += [f for f in glob.glob(
            os.environ.get("PYPE_PROJECT_CONFIGS") + os.path.sep + "**/*.json",
            recursive=True)] or []

        failures = 0
        for f in files:
            t.echo("  - {}".format(f))
            with open(f, "r") as jf:
                json_str = jf.read()
            try:
                json.loads(json_str)
            except json.decoder.JSONDecodeError as e:
                t.echo("!!! failed on [ {} ]".format(f))
                t.echo(str(e))
                failures += 1

        if failures > 0:
            t.echo(
                "!!! Failed on [ {} ] file(s), "
                "see log above.".format(failures))
        else:
            t.echo(">>> All OK.")
