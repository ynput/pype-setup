@echo off
set AVALON_APP_ROOT=%~dp0

set APP_ROOT=%AVALON_APP_ROOT%app

set AVALON_APP_PYTHON=python\__DEV__\3.6.6\dist\windows
set avalon_app_python_dev_packages=%AVALON_APP_ROOT%%AVALON_APP_PYTHON%\Lib\site-packages

set PYTHONPATH=%AVALON_APP_ROOT%;%avalon_app_python_dev_packages%;%APP_ROOT%;%PYTHONPATH%

REM echo %PYTHONPATH%

set python_exe=%AVALON_APP_ROOT%%AVALON_APP_PYTHON%\python.exe
echo %python_exe%

"%python_exe%" "%AVALON_APP_ROOT%TEST__path_retrieving.py"

REM echo %PYTHONPATH%
set PYTHONPATH=
