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


class Pype_logging(object):
    def __init__(self):
        self.host_name = None
        self.logging = logging
        self.attach_file_handler()
        self.logging.getLogger().addHandler(self.get_console_handler())
        logging.propagate = False

    def get_console_handler(self):
        formater = Pype_formatter(FRMT_TERMINAL)
        console_handler = self.logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formater)
        return console_handler

    def get_file_handler(self):
        if not self.host_name:
            self.host_name = "pype"

        ts = time.time()
        log_name = datetime.datetime.fromtimestamp(ts).strftime(
            '%Y-%m-%d'  # '%Y-%m-%d_%H-%M-%S'
        )

        logger_file_root = os.path.join(
            os.path.expanduser("~"),
            ".pype-setup"
        )

        logger_file_path = os.path.join(
            logger_file_root,
            "{}--{}.{}".format(self.host_name, log_name, 'log')
        )

        if not os.path.exists(logger_file_root):
            os.mkdir(logger_file_root)

        formater = Pype_formatter(FRMT_FILE)

        file_handler = TimedRotatingFileHandler(
            logger_file_path,
            when='midnight'
        )

        file_handler.setFormatter(formater)
        return file_handler

    def set_levels(self):
        self.logging.getLogger().setLevel(logging.INFO)

        if PYPE_DEBUG:
            print("this is it")
            self.logging.getLogger().setLevel(logging.DEBUG)

    def attach_file_handler(self):
        [logging.root.removeHandler(h) for h in logging.root.handlers[:]
         if isinstance(h, logging.FileHandler)]

        self.logging.getLogger().addHandler(self.get_file_handler())
        # self.logging.getLogger().setLevel(logging.DEBUG)
        # self.logging.debug("-"*50)
        # self.logging.getLogger().setLevel(logging.WARNING)

    def getLogger(self, name=None, host_name=None):
        self.host_name = host_name

        self.attach_file_handler()
        self.set_levels()

        if name:
            self.logger = self.logging.getLogger(name)
        else:
            self.logger = self.logging.getLogger()
        return self.logger
