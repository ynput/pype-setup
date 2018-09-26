@echo off
set SYNC_ENV=0
set REMOTE_ENV_ON=0
call %~dp0set_environment.bat
start "Avalon Launcher" avalon
