import logging
import os
import datetime
import time

ts = time.time()
log_name = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')

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
Logger = logging
Templates = None
_templates_loaded = None
_repos_installed = None
