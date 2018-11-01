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

    log_file = open(logger_file_path, "w", encoding="utf-8")

    logging.basicConfig(
        format=config.FORMAT,
        level=logging.DEBUG
    )

    formatter = logging.Formatter('%(asctime)-15s: %(levelname)-7s - %(message)s')
    ch = logging.StreamHandler(log_fh)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    if PYPE_DEBUG_STDOUT:
        logging.getLogger().addHandler(ch)

    return logging


Logger = logger()
