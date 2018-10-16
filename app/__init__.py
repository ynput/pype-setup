import logging
import os

logger_file_path = os.path.join(
    os.path.dirname(__name__),
    'example.log'
)
if os.path.exists(logger_file_path):
    os.remove(logger_file_path)

logging.basicConfig(
    filename=logger_file_path,
    level=logging.DEBUG
)
Logger = logging
Templates = None
_templates_loaded = None
_repos_installed = None
