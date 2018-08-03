# use .config.toml files and run the session of avalon-app
# if  files starting with .config.toml are not created then
# setup.py will install and generate .config.plugins.app-store.[your_preset_name].toml
# the initial runing of avalon-app.py will ask for `your_preset_name` so user
# can later change defined configuration to any from available presets
# import imp
# import platform
# import sys
# import os

# path to this files
# avalon_app_path = os.path.dirname(os.path.realpath(__file__))

# required modules for this scripts
# modules = ['toml']
# import required modules >> must be already in sys.path
# if they are not then generate path from __file__


# setup dependency
# def _setup():
#     config_dict = {"avalon.app.path": avalon_app_path,
#                     "config.sys.main.file": os.path.join(avalon_app_path, ".config.sys.main.{preset}.toml"),
#                     "config.plugins.app-store.file": os.path.join(avalon_app_path, ".config.plugins.app-store.{preset}.toml")
                    }
