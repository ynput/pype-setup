import logging
import os
import datetime
import time
from io import open

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
class PypeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            fs = "%s\n"
            if not _unicode: #if no unicode support...
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
        except:
            self.handleError(record)



def logger():
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

    log_file = open(logger_file_path, "w", encoding="utf-8")

    logging.basicConfig(
        level=logging.INFO
    )

    #formatter = logging.Formatter('%(asctime)-15s: %(levelname)-7s - %(message)s')
    ch = PypeStreamHandler(log_file)
    ch.setLevel(logging.DEBUG)
    #ch.setFormatter(formatter)

    if PYPE_DEBUG:
        logging.getLogger().addHandler(ch)

    return logging


Logger = logger()
