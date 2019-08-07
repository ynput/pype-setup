"""
Logging to console and to mongo. For mongo logging, you need to set either
``PYPE_LOG_MONGO_URL`` to something like:

.. example::
   mongo://user:password@hostname:port/database/collection?authSource=avalon

or set ``PYPE_LOG_MONGO_HOST`` and other variables.
See :func:`_mongo_settings`

Best place for it is in ``repos/pype-config/environments/global.json``
"""
from future.standard_library import install_aliases
install_aliases()

import logging
import os
import datetime
import time
import datetime as dt
import platform
import getpass
from urllib.parse import urlparse
from urllib.parse import parse_qs

try:
    from log4mongo.handlers import MongoHandler
except ImportError:
    _mongo_logging = False
except NameError:
    _mongo_logging = False
else:
    _mongo_logging = True
    if (not os.environ.get('PYPE_LOG_MONGO_URL', False)
            and not os.environ.get('PYPE_LOG_MONGO_HOST', False)):
        # configuration missing
        _mongo_logging = False


from logging.handlers import TimedRotatingFileHandler
from pypeapp.lib.Terminal import Terminal


try:
    unicode
    _unicode = True
except NameError:
    _unicode = False


PYPE_DEBUG = int(os.getenv("PYPE_DEBUG", "0"))


def _mongo_settings():
    host = None
    port = None
    username = None
    password = None
    collection = None
    database = None
    auth_db = None

    if os.environ.get('PYPE_LOG_MONGO_URL'):
        result = urlparse(os.environ.get('PYPE_LOG_MONGO_URL'))

        host = result.hostname
        try:
            port = result.port
        except ValueError as e:
            raise RuntimeError("invalid port specified") from e
        username = result.username
        password = result.password
        try:
            database = result.path.lstrip("/").split("/")[0]
            collection = result.path.lstrip("/").split("/")[1]
        except IndexError as e:
            if not database:
                raise RuntimeError("missing database name for logging") from e
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

    host, port, database, username, password, collection, auth_db = _mongo_settings()  # noqa

    if not host or not port or not database or not collection:
        # fail silently
        return

    print(">>> connecting to log [ {}:{} ]".format(host, port))
    client = pymongo.MongoClient(
        host=[host], port=port, username=username, password=password,
        authSource=auth_db)

    # dblist = client.list_database_names()

    logdb = client[database]

    collist = logdb.list_collection_names()
    if collection not in collist:
        logdb.create_collection(collection, capped=True,
                                max=5000, size=1073741824)


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

        out = formatter.format(record)
        if record.exc_info is not None:
            line_len = len(str(record.exc_info[1]))
            out = "{}\n{}\n{}\n{}\n{}".format(out,
                                              "-" * line_len,
                                              str(record.exc_info[1]),
                                              "=" * line_len,
                                              self.formatException(
                                                record.exc_info))
        return out


class PypeMongoFormatter(logging.Formatter):

    DEFAULT_PROPERTIES = logging.LogRecord(
        '', '', '', '', '', '', '', '').__dict__.keys()

    def format(self, record):
        """Formats LogRecord into python dictionary."""
        # Standard document
        document = {
            'timestamp': dt.datetime.utcnow(),
            'level': record.levelname,
            'thread': record.thread,
            'threadName': record.threadName,
            'message': record.getMessage(),
            'loggerName': record.name,
            'fileName': record.pathname,
            'module': record.module,
            'method': record.funcName,
            'lineNumber': record.lineno,
            'host': platform.node(),
            'user': getpass.getuser()
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
        host, port, database, username, password, collection, auth_db = _mongo_settings()  # noqa: E501

        handler = MongoHandler(
            host=host,
            port=int(port),
            username=username,
            password=password,
            collection=collection,
            database_name=database,
            authentication_db=auth_db,
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

        add_stream_handler = True
        add_mongo_handler = True
        if len(logger.handlers) > 0:
            for handler in logger.handlers:
                if _mongo_logging and (isinstance(handler, MongoHandler)):
                    add_mongo_handler = False
                if isinstance(handler, PypeStreamHandler):
                    add_stream_handler = False
            if add_mongo_handler and _mongo_logging:
                logger.addHandler(self._get_mongo_handler())
            if add_stream_handler:
                logger.addHandler(self._get_console_handler())
        else:
            if _mongo_logging:
                logger.addHandler(self._get_mongo_handler())
                pass
            logger.addHandler(self._get_console_handler())

        return logger
