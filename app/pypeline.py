from app.lib.templates import Templates as _Templates

from app import api

from pprint import pprint

log = api.Logger.getLogger(__name__)


def test():
    log.debug("________starting app_____________")
    log.debug("app.Templates: {}".format(pprint(api.Templates)))
    return 1


def env_install(type=None, environment=None):
    api.Templates = _Templates(type, environment)
    log.info("Pype's environment was installed...")


def env_uninstall():
    api.Templates = None
    log.info("Pype's environment was uninstalled...")


if __name__ == '__main__':
    if not api.Templates:
        env_install()
