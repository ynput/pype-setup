import logging
import os
import datetime
import time


PYPE_DEBUG_STDOUT = os.getenv("PYPE_DEBUG_STDOUT") is "1"


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

    logging.basicConfig(
        filename=logger_file_path,
        level=logging.DEBUG
    )

    if PYPE_DEBUG_STDOUT:
        logging.getLogger().addHandler(logging.StreamHandler())

    return logging


Logger = logger()
