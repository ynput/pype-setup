import logging
import sys

DFT = '%(levelname)s in %(name)s: [%(message)s]'
DBG = "  - %(module)s: [%(message)s]"
INF = ">>> [%(message)s]"
WRN = "*** WRN:  %(module)s: [%(message)s]"
ERR = "--- ERR: %(asctime)s -- [%(message)s]"
CRI = "!!! CRI: [%(message)s]"


FORMATTING = {
    logging.INFO: INF,
    logging.DEBUG: DBG,
    logging.WARNING: WRN,
    logging.ERROR: ERR,
    logging.CRITICAL: CRI,
}


class Pype_formatter(logging.Formatter):
    default_formatter = logging.Formatter(DFT)

    def __init__(self, formats):
        """ formats is a dict { loglevel : logformat } """
        self.formatters = {}
        for loglevel in formats:
            self.formatters[loglevel] = logging.Formatter(formats[loglevel])

    def format(self, record):
        formatter = self.formatters.get(record.levelno, self.default_formatter)
        return formatter.format(record)


formatter = Pype_formatter(FORMATTING)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)
logging.getLogger().setLevel(logging.DEBUG)

log = logging.getLogger(__file__)


log.info("print info message")
log.debug("print debug message")
log.warning("print warning message")
log.error("print error message")
