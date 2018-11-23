
from app.api import (
    Templates,
    Logger
)

from pprint import pprint

log = Logger.getLogger(__name__)


def test():
    log.debug("________starting app_____________")
    log.debug("app._templates_loaded: {}".format(app._templates_loaded))
    log.debug("app.Templates: {}".format(pprint(app.Templates)))
    return 1


def env_install():
    app.Templates = Templates()
    app._templates_loaded = True
    log.info("Pype's environment was installed...")


def env_uninstall():
    app.Templates = None
    app._templates_loaded = None
    log.info("Pype's environment was uninstalled...")


if __name__ == '__main__':
    if not app._templates_loaded:
        install()
