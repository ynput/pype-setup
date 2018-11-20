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


PYPE_DEBUG_STDOUT = os.getenv("PYPE_DEBUG_STDOUT") is "1"

class PypeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
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
                            #Printing to terminals sometimes fails. For example,
                            #with an encoding of 'cp1251', the above write will
                            #work if written to a stream opened or wrapped by
                            #the codecs module, but fail when writing to a
                            #terminal even when the codepage is set to cp1251.
                            #An extra encoding step seems to be needed.
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
        level=logging.DEBUG
    )

    #formatter = logging.Formatter('%(asctime)-15s: %(levelname)-7s - %(message)s')
    ch = PypeStreamHandler(log_file)
    ch.setLevel(logging.DEBUG)
    #ch.setFormatter(formatter)

    if PYPE_DEBUG_STDOUT:
        logging.getLogger().addHandler(ch)

    return logging


Logger = logger()
