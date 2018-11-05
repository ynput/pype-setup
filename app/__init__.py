import os
import sys

Templates = None
_templates_loaded = None
_repos_installed = None


sys.path.append(os.path.join(os.environ["PYPE_SETUP_ROOT"], "app", "vendor"))
