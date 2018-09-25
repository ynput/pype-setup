set PYTHON_DIR=C:\Python36
set ROOT_DIR=%~dp0
set PATH=%PYTHON_DIR%\Scripts;%PYTHON_DIR%

call pip install PyQt5==5.7 pymongo==3.6.1

set PATH=%ROOT_DIR%avalon-setup;%PATH%
set PYTHONPATH=%ROOT_DIR%pype\studio-config;%ROOT_DIR%avalon-setup\git\pyblish-base;%ROOT_DIR%avalon-setup\git\pyblish-qml

set AVALON_CORE=%ROOT_DIR%reps\avalon-core-toke-nuke
set AVALON_LAUNCHER=%ROOT_DIR%avalon-setup\git\avalon-launcher
set AVALON_PROJECTS=%ROOT_DIR%avalon-setup\git\avalon-examples
set AVALON_CONFIG=config
set AVALON_DEBUG="True"

start "Avalon Launcher" avalon
