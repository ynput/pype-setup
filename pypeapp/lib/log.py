"""
Logging to console and to mongo. For mongo logging, you need to set either
``PYPE_LOG_MONGO_URL`` to something like:

.. example::
   mongo://user:password@hostname:port/database/collection?authSource=avalon

or set ``PYPE_LOG_MONGO_HOST`` and other variables.
See :func:`_mongo_settings`

Best place for it is in ``repos/pype-config/environments/global.json``
"""


import logging
import os
import sys
import datetime
import time
import datetime as dt
import platform
import getpass
import socket
try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs

try:
    from log4mongo.handlers import MongoHandler
except ImportError:
    _mongo_logging = False
else:
    _mongo_logging = True

from logging.handlers import TimedRotatingFileHandler
from pypeapp.lib.Terminal import Terminal

try:
    unicode
    _unicode = True
except NameError:
    _unicode = False


PYPE_DEBUG = int(os.getenv("PYPE_DEBUG", "0"))

if _mongo_logging:
    from bson.objectid import ObjectId
    MONGO_PROCESS_ID = ObjectId()

system_name, pc_name = platform.uname()[:2]
host_name = socket.gethostname()
try:
    ip = socket.gethostbyname(host_name)
except socket.gaierror:
    ip = "127.0.0.1"

# Get process name
if len(sys.argv) > 0 and os.path.basename(sys.argv[0]) == "tray.py":
    process_name = "Tray"
else:
    try:
        import psutil
        process = psutil.Process(os.getpid())
        process_name = process.name()

    except ImportError:
        process_name = os.environ.get("AVALON_APP_NAME")
        if not process_name:
            process_name = os.path.basename(sys.executable)


def _mongo_settings():
    host = None
    port = None
    username = None
    password = None
    collection = None
    database = None
    auth_db = ""

    if os.environ.get('PYPE_LOG_MONGO_URL'):
        result = urlparse(os.environ.get('PYPE_LOG_MONGO_URL'))

        host = result.hostname
        try:
            port = result.port
        except ValueError:
            raise RuntimeError("invalid port specified")
        username = result.username
        password = result.password
        try:
            database = result.path.lstrip("/").split("/")[0]
            collection = result.path.lstrip("/").split("/")[1]
        except IndexError:
            if not database:
                raise RuntimeError("missing database name for logging")
        try:
            auth_db = parse_qs(result.query)['authSource'][0]
        except KeyError:
            # no auth db provided, mongo will use the one we are connecting to
            pass
    else:
        host = os.environ.get('PYPE_LOG_MONGO_HOST')
        port = int(os.environ.get('PYPE_LOG_MONGO_PORT', "0"))
        database = os.environ.get('PYPE_LOG_MONGO_DB')
        username = os.environ.get('PYPE_LOG_MONGO_USER')
        password = os.environ.get('PYPE_LOG_MONGO_PASSWORD')
        collection = os.environ.get('PYPE_LOG_MONGO_COL')
        auth_db = os.environ.get('PYPE_LOG_MONGO_AUTH_DB', 'avalon')

    return host, port, database, username, password, collection, auth_db


def _bootstrap_mongo_log():
    """
    This will check if database and collection for logging exist on server.
    """
    import pymongo

    host, port, database, username, password, collection, auth_db = _mongo_settings()

    if not host or not port or not database or not collection:
        # fail silently
        return

    user_pass = ""
    if username and password:
        user_pass = "{}:{}@".format(username, password)

    socket_path = "{}:{}".format(host, port)

    dab = ""
    if database:
        dab = "/{}".format(database)

    auth = ""
    if auth_db:
        auth = "?authSource={}".format(auth_db)

    uri = "mongodb://{}{}{}{}".format(user_pass, socket_path, dab, auth)

    print(">>> connecting to log [ {} ]".format(uri))

    client = pymongo.MongoClient(uri)

    logdb = client[database]

    collist = logdb.list_collection_names()
    if collection not in collist:
        logdb.create_collection(collection, capped=True,
                                max=5000, size=1073741824)
    return logdb


if _mongo_logging:
    _bootstrap_mongo_log()


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
            msg = Terminal.log(msg)
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
            print(repr(record))
            self.handleError(record)


class PypeFormatter(logging.Formatter):

    DFT = '%(levelname)s >>> { %(name)s }: [ %(message)s ]'
    default_formatter = logging.Formatter(DFT)

    def __init__(self, formats):
        super(PypeFormatter, self).__init__()
        self.formatters = {}
        for loglevel in formats:
            self.formatters[loglevel] = logging.Formatter(formats[loglevel])

    def format(self, record):
        formatter = self.formatters.get(record.levelno, self.default_formatter)

        _exc_info = record.exc_info
        record.exc_info = None

        out = formatter.format(record)
        record.exc_info = _exc_info

        if record.exc_info is not None:
            line_len = len(str(record.exc_info[1]))
            out = "{}\n{}\n{}\n{}\n{}".format(
                out,
                line_len * "=",
                str(record.exc_info[1]),
                line_len * "=",
                self.formatException(record.exc_info)
            )
        return out


class PypeMongoFormatter(logging.Formatter):

    DEFAULT_PROPERTIES = logging.LogRecord(
        '', '', '', '', '', '', '', '').__dict__.keys()

    def format(self, record):
        """Formats LogRecord into python dictionary."""
        # Standard document
        document = {
            'timestamp': dt.datetime.now(),
            'level': record.levelname,
            'thread': record.thread,
            'threadName': record.threadName,
            'message': record.getMessage(),
            'loggerName': record.name,
            'fileName': record.pathname,
            'module': record.module,
            'method': record.funcName,
            'lineNumber': record.lineno,
            'process_id': MONGO_PROCESS_ID,
            'hostname': host_name,
            'hostip': ip,
            'username': getpass.getuser(),
            'system_name': system_name,
            'process_name': process_name
        }
        # Standard document decorated with exception info
        if record.exc_info is not None:
            document.update({
                'exception': {
                    'message': str(record.exc_info[1]),
                    'code': 0,
                    'stackTrace': self.formatException(record.exc_info)
                }
            })
        # Standard document decorated with extra contextual information
        if len(self.DEFAULT_PROPERTIES) != len(record.__dict__):
            contextual_extra = set(record.__dict__).difference(
                set(self.DEFAULT_PROPERTIES))
            if contextual_extra:
                for key in contextual_extra:
                    document[key] = record.__dict__[key]
        return document


class PypeLogger:

    PYPE_DEBUG = 0

    DFT = '%(levelname)s >>> { %(name)s }: [ %(message)s ] '
    DBG = "  - { %(name)s }: [ %(message)s ] "
    INF = ">>> [ %(message)s ] "
    WRN = "*** WRN: >>> { %(name)s }: [ %(message)s ] "
    ERR = "!!! ERR: %(asctime)s >>> { %(name)s }: [ %(message)s ] "
    CRI = "!!! CRI: %(asctime)s >>> { %(name)s }: [ %(message)s ] "

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

    def _get_mongo_handler(self):
        handler = MongoHandler(
            host=os.environ.get('PYPE_LOG_MONGO_HOST'),
            port=int(os.environ.get('PYPE_LOG_MONGO_PORT')),
            database_name=os.environ.get('PYPE_LOG_MONGO_DB'),
            capped=True,
            formatter=PypeMongoFormatter())
        return handler

    def _get_console_handler(self):

        formatter = PypeFormatter(self.FORMAT_FILE)
        console_handler = PypeStreamHandler()

        console_handler.set_name("PypeStreamHandler")
        console_handler.setFormatter(formatter)
        return console_handler

    def get_logger(self, name=None, host=None):
        logger = logging.getLogger(name or '__main__')

        if self.PYPE_DEBUG > 1:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        if len(logger.handlers) > 0:
            for handler in logger.handlers:
                if (
                    _mongo_logging and
                    not isinstance(handler, MongoHandler) and
                    not isinstance(handler, PypeStreamHandler)
                ):
                    if os.environ.get('PYPE_LOG_MONGO_HOST') and _mongo_logging:  # noqa
                        logger.addHandler(self._get_mongo_handler())
                        pass
                    logger.addHandler(self._get_console_handler())
        else:
            if os.environ.get('PYPE_LOG_MONGO_HOST') and _mongo_logging:
                logger.addHandler(self._get_mongo_handler())
                pass
            logger.addHandler(self._get_console_handler())

        return logger
