@echo off
echo [92m^>^>^>[0m Generating pype-setup documentation, please wait ...
call "C:\Users\Public\pype_env2\Scripts\activate.bat"

setlocal enableextensions enabledelayedexpansion
set _OLD_PYTHONPATH=%PYTHONPATH%
echo [92m^>^>^>[0m Adding repos path
rem add stuff in repos
for /d %%d in ( %~dp0repos\*) do (
echo   - adding path %%d
set PYTHONPATH=%%d;!PYTHONPATH!
)

echo [92m^>^>^>[0m Adding python vendors path
rem add python vendor paths
for /d %%d in ( %~dp0vendor\python\*) do (
echo   - adding path %%d
set PYTHONPATH=%%d;!PYTHONPATH!
)

echo [92m^>^>^>[0m Setting PYPE_CONFIG
set PYPE_CONFIG=%~dp0repos\pype-config

call "docs\make.bat" clean
sphinx-apidoc -M -f -d 4 --ext-autodoc --ext-intersphinx --ext-viewcode -o docs\source\ pypeapp
call "docs\make.bat" html
echo [92m^>^>^>[0m Doing cleanup ...
set PYTHONPATH=%_OLD_PYTHONPATH%
set PYPE_CONFIG=
call "C:\Users\Public\pype_env2\Scripts\deactivate.bat"
