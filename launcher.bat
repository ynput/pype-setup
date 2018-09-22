@echo off
set SYNC_ENV=1
call %~dp0bin\launch_conda.bat

:: Setup Avalon
set PATH=%~dp0app;%PATH%

:: Setup PYTHONPATH
set PYTHONPATH=%~dp0app\repos\pyblish-base;%PYTHONPATH%
set PYTHONPATH=%~dp0app\repos\pyblish-qml;%PYTHONPATH%
set PYTHONPATH=%~dp0studio\studio-config;%PYTHONPATH%

set AVALON_CONFIG=config
set AVALON_LAUNCHER=%~dp0app\repos\avalon-launcher
set AVALON_PYTHONPATH=%~dp0app\repos\avalon-core
set AVALON_CORE=%AVALON_PYTHONPATH%

set AVALON_MONGO=mongodb://localhost:27017

start "Avalon Launcher" avalon
