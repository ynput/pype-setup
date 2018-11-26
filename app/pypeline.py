import app
from app.lib.templates import Templates
from app.api import Logger

from pprint import pprint

log = Logger.getLogger(__name__)


def test():
    log.debug("________starting app_____________")
    log.debug("app.Templates: {}".format(pprint(app.Templates)))
    return 1


def env_install(type=None, environment=None):
    app.Templates = Templates(type, environment)
    log.info("Pype's environment was installed...")


def env_uninstall():
    app.Templates = None
    log.info("Pype's environment was uninstalled...")


if __name__ == '__main__':
    if not app.Templates:
        env_install()
