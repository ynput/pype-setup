@echo off

call %~dp0bin\launch_conda.bat

:: set path to this environment
set PATH=%~dp0app;%PATH%

:: Setup Avalon
set AVALON_CONFIG=config
set AVALON_LAUNCHER=%~dp0app\repos\avalon-launcher
set AVALON_PYTHONPATH=%~dp0app\repos\avalon-core
set AVALON_EXAMPLES=%~dp0app\repos\avalon-examples
::%~dp0..\..\avalon-core-toke-nuke
set AVALON_CORE=%AVALON_PYTHONPATH%

:: mongo db settigs
set AVALON_DB_DATA=C:\data\db
set AVALON_MONGO=mongodb://localhost:27017

:: studio
set PYPE_STUDIO_CONFIG=%~dp0studio\studio-config
set PYPE_STUDIO_TEMPLATES=%~dp0studio\studio-templates

:: Setup PYTHONPATH
set PYTHONPATH=%~dp0app\repos\pyblish-base;%PYTHONPATH%
set PYTHONPATH=%~dp0app\repos\pyblish-qml;%PYTHONPATH%
set PYTHONPATH=%~dp0app\repos\pyblish-lite;%PYTHONPATH%
set PYTHONPATH=%PYPE_STUDIO_CONFIG%;%PYTHONPATH%
