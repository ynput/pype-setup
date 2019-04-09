import logging
import os
import datetime
import time

from logging.handlers import TimedRotatingFileHandler
from .Terminal import Terminal


try:
    unicode
    _unicode = True
except NameError:
    _unicode = False


PYPE_DEBUG = int(os.getenv("PYPE_DEBUG", "0"))


class PypeStreamHandler(logging.StreamHandler):
    """ StreamHandler class designed to handle utf errors in python 2.x hosts.

    """

    def __init__(self, stream=None):
        super(PypeStreamHandler, self).__init__(stream)
        self.enabled = True

    def enable(self):
        """ Enable StreamHandler

            Used to silence output
        """
        self.enabled = True
        pass

    def disable(self):
        """ Disable StreamHandler

            Make StreamHandler output again
        """
        self.enabled = False

    def emit(self, record):
        if not self.enable:
            return
        try:
            msg = self.format(record)
            stream = self.stream
            fs = "%s\n"
            if not _unicode:  # if no unicode support...
                stream.write(fs % msg)
            else:
                try:
                    if (isinstance(msg, unicode) and  # noqa: F821
                            getattr(stream, 'encoding', None)):
                        ufs = u'%s\n'
                        try:
                            stream.write(ufs % msg)
                        except UnicodeEncodeError:
                            stream.write((ufs % msg).encode(stream.encoding))
                    else:
                        if (getattr(stream, 'encoding', 'utf-8')):
                            ufs = u'%s\n'
                            stream.write(ufs % unicode(msg))  # noqa: F821
                        else:
                            stream.write(fs % msg)
                except UnicodeError:
                    stream.write(fs % msg.encode("UTF-8"))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


class PypeFormatter(logging.Formatter):

    DFT = '%(levelname)s >>> { %(name)s }: [ %(message)s ] '
    default_formatter = logging.Formatter(DFT)

    def __init__(self, formats):
        super(PypeFormatter, self).__init__(formats)
        self.formatters = {}
        for loglevel in formats:
            self.formatters[loglevel] = logging.Formatter(formats[loglevel])

    def format(self, record):
        formatter = self.formatters.get(record.levelno, self.default_formatter)
        return formatter.format(record)


class PypeLogger:

    PYPE_DEBUG = 0

    DFT = '%(levelname)s >>> { %(name)s }: [ %(message)s ] '
    DBG = "  - { %(name)s }: [ %(message)s ] "
    INF = ">>> [ %(message)s ] "
    WRN = "*** WRN: >>> { %(name)s }: [ %(message)s ] "
    ERR = "--- ERR: %(asctime)s >>> { %(name)s }: [ %(message)s ] "
    CRI = "!!! CRI: %(asctime)s >>> { %(name)s }: [ %(message)s ] "

    terminal = Terminal()

    FORMAT_TERMINAL = {
        logging.INFO: terminal.log(INF),
        logging.DEBUG: terminal.log(DBG),
        logging.WARNING: terminal.log(WRN),
        logging.ERROR: terminal.log(ERR),
        logging.CRITICAL: terminal.log(CRI),
    }

    FORMAT_FILE = {
        logging.INFO: INF,
        logging.DEBUG: DBG,
        logging.WARNING: WRN,
        logging.ERROR: ERR,
        logging.CRITICAL: CRI,
    }

    def __init__(self):
        self.PYPE_DEBUG = int(os.environ.get("PYPE_DEBUG", "0"))

    @staticmethod
    def get_file_path(host='pype'):

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
            "{}-{}.{}".format(host, log_name, 'log')
        )

        if not os.path.exists(logger_file_root):
            os.mkdir(logger_file_root)

        return logger_file_path

    def _get_file_handler(self, host):
        logger_file_path = PypeLogger.get_file_path(host)

        formatter = PypeFormatter(self.FORMAT_FILE)

        file_handler = TimedRotatingFileHandler(
            logger_file_path,
            when='midnight'
        )
        file_handler.set_name("PypeFileHandler")
        file_handler.setFormatter(formatter)
        return file_handler

    def _get_console_handler(self):

        formatter = PypeFormatter(self.FORMAT_TERMINAL)
        console_handler = PypeStreamHandler()

        console_handler.set_name("PypeStreamHandler")
        console_handler.setFormatter(formatter)
        return console_handler

    def get_logger(self, name=None, host=None):
        host_name = host or 'pype'
        logger = logging.getLogger(name or '__main__')

        if self.PYPE_DEBUG > 1:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        logger.addHandler(self._get_file_handler(host_name))
        logger.addHandler(self._get_console_handler())

        return logger
