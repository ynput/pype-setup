@echo off

set PYPE_SETUP_ROOT=%~dp0

call %PYPE_SETUP_ROOT%bin\launch_conda.bat

:: set path to this environment
set PATH=%PYPE_SETUP_ROOT%app;%PATH%

:: set pythonpath for adding app into python context
set PYTHONPATH=%PYPE_SETUP_ROOT%;%PYTHONPATH%

REM :: mongo db settigs
REM set AVALON_DB_DATA=C:\data\db
REM set AVALON_MONGO=mongodb://localhost:27017
