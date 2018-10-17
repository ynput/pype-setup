import platform
import os


from app.api import (
    Templates as templates,
    # solve_dependecies,
    forward,
    Logger
)


from app import (
    Templates,
    _repos_installed,
    _templates_loaded,
    local_mongo_server,
)

log = Logger.getLogger(__name__)
PYPE_DEBUG = os.getenv("PYPE_DEBUG_STDOUT") is "1"

terminal = {"windows": "cmd", "linux": "xterm", "darwin": "iTerm2"}

if not _templates_loaded:
    Templates = templates()
    _templates_loaded = True

cmd = [terminal[platform.system().lower()]]

forward(cmd)
