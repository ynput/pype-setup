
import app

from app.api import (
    Templates as templates,
    Logger
)


log = Logger.getLogger(__name__)

app._templates_loaded

if not app._templates_loaded:
    app.Templates = templates()
    app._templates_loaded = True
