import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import datetime
import time

from .terminal import c_log


PYPE_DEBUG = os.getenv("PYPE_DEBUG") is "1"

DFT = '%(levelname)s >>> {%(name)s}: [%(message)s] '
DBG = "  - {%(name)s}: [%(message)s] "
INF = ">>> [%(message)s] "
WRN = "*** WRN: >>> {%(name)s}: [%(message)s] "
ERR = "--- ERR: %(asctime)s >>> {%(name)s}: [%(message)s] "
CRI = "!!! CRI: %(asctime)s >>> {%(name)s}: [%(message)s] "


FRMT_TERMINAL = {
    logging.INFO: c_log(INF),
    logging.DEBUG: c_log(DBG),
    logging.WARNING: c_log(WRN),
    logging.ERROR: c_log(ERR),
    logging.CRITICAL: c_log(CRI),
}

FRMT_FILE = {
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


ts = time.time()
log_name = datetime.datetime.fromtimestamp(ts).strftime(
    '%Y-%m-%d_%H-%M'  # '%Y-%m-%d_%H-%M-%S'
)

logger_file_root = os.path.join(
    os.path.expanduser("~"),
    ".pype-setup"
)
logger_file_path = os.path.join(
    logger_file_root,
    (log_name + '.log')
)

if not os.path.exists(logger_file_root):
    os.mkdir(logger_file_root)

LOG_FILE = logger_file_path


def get_console_handler():
    formater = Pype_formatter(FRMT_TERMINAL)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formater)
    return console_handler


def get_file_handler():
    formater = Pype_formatter(FRMT_FILE)
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(formater)
    return file_handler


def get_logging():
    logging.getLogger().setLevel(logging.INFO)
    # better to have too much log than not enough
    if PYPE_DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(get_console_handler())
    logging.getLogger().addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to
    # propagate the error up to parent
    logging.propagate = False
    return logging


Logger = get_logging()
