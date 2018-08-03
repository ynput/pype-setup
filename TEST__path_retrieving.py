
import os
import platform

import sys
import app

# this root folder
conf_path = os.path.dirname(os.path.realpath(__file__))

properities = {
    'platform': platform.system().lower(),
    'version': "2018v2",
    'root': conf_path,
    'preset': "My-Testing"
}

Conf = app.tools.create_paths.get_paths(properities)

# Conf.app_store.path = Conf.app_store.path.format(**Conf)
for k, v in Conf.sys.items():
    print(k, v)
