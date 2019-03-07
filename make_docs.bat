@echo off
call "C:\Users\Public\pype_env2\Scripts\activate.bat"
setlocal enableextensions enabledelayedexpansion
set _OLD_PYTHONPATH=%PYTHONPATH%
set PYTHONPATH=%~dp0vendor\acre;%PYTHONPATH%
for /d %%d in ( %~dp0repos\*) do (
echo adding path %%d
set PYTHONPATH=%%d;!PYTHONPATH!
)
call "docs\make.bat" clean
sphinx-apidoc -M -f -d 4 --ext-autodoc --ext-intersphinx --ext-viewcode -o docs\source\ pypeapp
call "docs\make.bat" html
set PYTHONPATH=%_OLD_PYTHONPATH%
call "C:\Users\Public\pype_env2\Scripts\deactivate.bat"
