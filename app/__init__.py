import os
import sys

Templates = None
_templates_loaded = None
_repos_installed = None

os.environ["PYPE_APP_ROOT"] = os.path.normpath(os.path.dirname(__file__))

sys.path.append(os.path.join(os.environ["PYPE_APP_ROOT"], "vendor"))
