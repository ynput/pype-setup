import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import datetime
import time


PYPE_DEBUG = os.getenv("PYPE_DEBUG") is "1"
FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ts = time.time()
log_name = datetime.datetime.fromtimestamp(ts).strftime(
    '%Y-%m-%d_%H-%M-%S'
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
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logging():
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
