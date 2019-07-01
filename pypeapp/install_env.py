"""
Handle creation of **venv**.

"""

import venv
import sys
import os
from pypeapp.lib.log import PypeLogger
from pypeapp.lib.Terminal import Terminal

log = PypeLogger().get_logger(__name__)
t = Terminal()

EX_IOERR = 74  # IO error
EX_TEMPFAIL = 75  # temporary failure
EX_CONFIG = 78  # configuration error


def _create_venv(env_dir, force):
    eb = venv.EnvBuilder(clear=force, with_pip=True)

    eb.create(env_dir)
    pass


def install(force=False):
    """ Install venv (virtualenv).

        If force specified, existing one will be overwritten.

        :param force: Force **venv** creation.
        :type force: boolean

    """
    # test path for venv
    pype_env = os.path.normpath(os.environ.get('PYPE_ENV'))
    if pype_env is None:
        log.error("Missing PYPE_ENV. Terminating.")
        t.echo("!!! Destination directory isn't specified")
        sys.exit(78)

    if os.path.exists(pype_env):
        t.echo("--- Destination path exists")
        # we skip content detection when force=True because content
        # will be deleted anyway
        if force is False:
            for dirpath, dirnames, files in os.walk(pype_env):
                if files or dirnames:
                    t.echo("!!! Destination directory is not empty.")
                    # t.echo("Use --force argument to delete content")
                    sys.exit(75)
                    break
        # exists but is empty
    else:
        try:
            t.echo(">>> Creating directory [ {} ]". format(pype_env))
            os.makedirs(pype_env)
        except PermissionError:
            t.echo("!!! We have no permission to create [ {} ].".format(pype_env))
            sys.exit(74)
        except OSError as e:
            t.echo(
                "!!! Cannot create destination directory [ {0} ].\n{1}".format(
                    pype_env, e.message
                ))
            # log.error(m[3:])
            sys.exit(74)
        pass

    # we have destination directory
    t.echo(">>> Creating environment ...")
    _create_venv(pype_env, force)
