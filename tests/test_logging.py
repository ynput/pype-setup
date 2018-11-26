from app.api import Logger

log = Logger.getLogger(__name__)
log.warning("this is a message")

log = Logger.getLogger(__name__, "atom")

log.info("this is a message")
log.debug("this is a message")
log.warning("this is a message")
log.error("this is a message")
log.critical("this is a message")
