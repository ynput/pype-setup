from .terminal import c_log
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import datetime
import time

try:
    unicode
    _unicode = True
except NameError:
    _unicode = False


PYPE_DEBUG = os.getenv("PYPE_DEBUG") is "1"

"""
This is hack for StreamHandler in Python 2.7 environments. If logging is set to
utf-8, then standard StreamHandler in Maya 2018 will fail.
"""


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


class PypeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            fs = "%s\n"
            if not _unicode:  # if no unicode support...
                stream.write(fs % msg)
            else:
                try:
                    if (isinstance(msg, unicode) and
                            getattr(stream, 'encoding', None)):
                        ufs = u'%s\n'
                        try:
                            stream.write(ufs % msg)
                        except UnicodeEncodeError:
                            stream.write((ufs % msg).encode(stream.encoding))
                    else:
                        if (getattr(stream, 'encoding', 'utf-8')):
                            ufs = u'%s\n'
                            stream.write(ufs % unicode(msg))
                        else:
                            stream.write(fs % msg)
                except UnicodeError:
                    stream.write(fs % msg.encode("UTF-8"))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


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
        console_handler = PypeStreamHandler(sys.stdout)
        # self.logging.StreamHandler(sys.stdout)
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
            self.logging.getLogger().setLevel(logging.DEBUG)

    def attach_file_handler(self):
        [logging.root.removeHandler(h) for h in logging.root.handlers[:]
         if isinstance(h, logging.FileHandler)]

        self.logging.getLogger().addHandler(self.get_file_handler())

    def getLogger(self, name=None, host_name=None):
        self.host_name = host_name

        self.attach_file_handler()
        self.set_levels()

        if name:
            self.logger = self.logging.getLogger(name)
        else:
            self.logger = self.logging.getLogger()
        return self.logger
