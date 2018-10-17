@echo off
set PYPE_SETUP_GIT_URL=git@github.com:pypeclub/pype-setup.git
set PYPE_SETUP_GIT_BRANCH=app-lib-all-jakub

set PYPE_SETUP_ROOT=%~dp0

:: maintain python environment
set SYNC_ENV=0 :: will synchronize remote with local
set REMOTE_ENV_ON=0 :: will switch to remote
call %PYPE_SETUP_ROOT%bin\launch_conda.bat

:: set pythonpath for adding app into python context
set PYTHONPATH=%PYPE_SETUP_ROOT%

:: set path to this environment
set PATH=%PYPE_SETUP_ROOT%app;%PATH%

set AVALON_MONGO=mongodb://localhost:27017
set AVALON_DB=avalon
set AVALON_DB_DATA=%PYPE_SETUP_ROOT%..\mongo_db_data

call python %PYPE_SETUP_ROOT%app\local_mongo_server.py %*
