set SYNC_ENV=0
set REMOTE_ENV_ON=0
call %~dp0set_environment.bat
set PYTHONPATH=%AVALON_CORE%;%PYTHONPATH%
start "Avalon Terminal" cmd
