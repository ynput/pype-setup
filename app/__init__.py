import logging

logger_file_path = os.path.join(
    os.path.dirname(__name__),
    'example.log'
)

Logger = logging.basicConfig(
    filename=,
    level=logging.DEBUG
)

Templates = None
_templates_loaded = None
_repos_installed = None
