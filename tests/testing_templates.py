import app
from app.api import Logger

log = Logger.getLogger(__file__)

log.debug(app._templates_loaded)
log.debug(app.Templates)
