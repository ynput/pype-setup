import argparse
import os
import sys
from pprint import pprint


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

        - **deploy**: will deploy repositories set in ""deploy/deploy.json""
          or in it's override directory. It will deploy git repositories and
          install additional python dependencies via pip.

          - **force**: used in conjunction with **deploy** will force
            git to overwrite all existing repositories already in path.

        - **validate**: will validate Pype deployment, comparing it to
          ""deploy/deploy.json"" or it override.

          - **skipmissing**: will skip validation of missing repositories.
            used during installation stage.

    """

    _kwargs = None
    _args = None

    def __init__(self):
        sys.path.append(os.path.join(os.getenv('PYPE_ROOT'), 'vendor', 'acre'))

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
        parser.add_argument("--local-mongodb",
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
        self._kwargs, self._args = parser.parse_known_args()

        pprint(self._kwargs)

        if self._kwargs.tray or self._kwargs.traydebug:

            if self._kwargs.traydebug:

                os.environ['PYPE_DEBUG'] = '3'
                print('setdebug {}'.format(os.getenv('PYPE_DEBUG')))

            self._launch_tray(debug=self._kwargs.traydebug)

        elif self._kwargs.install:
            self._install()

        elif self._kwargs.validate:
            self._validate()

        elif self._kwargs.deploy:
            self._deploy()

    def _launch_tray(self, debug=False):
        """ Method will launch tray.py

            :param debug: if True, tray will run in debug mode (not detached)
            :type debug: bool

            .. seealso:: :func:`subprocess.Popen`
        """
        import subprocess
        from api import Api
        from pypeapp import Logger

        api = Api()

        if debug:
            print(">>> debug {}".format(os.environ['PYPE_DEBUG']))
            pype_setup = os.getenv('PYPE_ROOT')
            items = [pype_setup, "pypeapp", "tray.py"]
            fname = os.path.sep.join(items)

            api.execute([
                sys.executable,
                "-u",
                fname
                ] + self._args)
            return

        DETACHED_PROCESS = 0x00000008

        pype_setup = os.getenv('PYPE_ROOT')
        items = [pype_setup, "pypeapp", "tray.py"]
        fname = os.path.sep.join(items)

        args = ["-d", fname]
        if sys.platform.startswith('linux'):
            subprocess.Popen(
                args,
                universal_newlines=True,
                bufsize=1,
                executable=sys.executable,
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
                executable=sys.executable,
                env=os.environ,
                # stdin=None,
                stdout=open(Logger.get_file_path(), 'w+'),
                stderr=subprocess.STDOUT,
                creationflags=DETACHED_PROCESS
            )

    def _launch_local_mongodb(self):
        """ This will run local instance of mongodb. """
        raise RuntimeError("Not implemented yet.")

    def _launch_eventserver(self):
        """ This will run standalone ftrack eventserver. """
        raise RuntimeError("Not implemented yet.")
        pass

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
        from deployment import Deployment, DeployException
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
        from deployment import Deployment, DeployException
        d = Deployment(os.environ.get('PYPE_ROOT', None))
        try:
            d.deploy(self._kwargs.force)
        except DeployException:
            sys.exit(200)
        pass
