import app
from app.api import Logger

log = Logger.getLogger(__name__)


def main():
    log.debug("________starting app_____________")
    log.debug("app._templates_loaded: {}".format(app._templates_loaded))
    log.debug("app.Templates: {}".format(app.Templates))
