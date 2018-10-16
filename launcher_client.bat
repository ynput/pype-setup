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

start "Pype Launcher" pype-start
