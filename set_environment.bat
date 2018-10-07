@echo off

set PYPE_SETUP_ROOT=%~dp0

call %PYPE_SETUP_ROOT%bin\launch_conda.bat

:: set path to this environment
set PATH=%PYPE_SETUP_ROOT%app;%PATH%

:: set pythonpath for adding app into python context
set PYTHONPATH=%PYPE_SETUP_ROOT%;%PYTHONPATH%

:: mongo db settigs
set AVALON_DB_DATA=C:\data\db
set AVALON_MONGO=mongodb://localhost:27017

:: workfile Setup
set AVALON_WORKFILE_TEMPLATE="{project[name]}_{task[name]}_v{version:0>3}<_{comment}>"
