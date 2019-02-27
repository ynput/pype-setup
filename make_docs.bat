@echo off
call "C:\Users\Public\pype_env2\Scripts\activate.bat"
call "docs\make.bat" clean
sphinx-apidoc -M -f -d 4 --ext-autodoc --ext-intersphinx --ext-viewcode -o docs\source\ pypeapp
call "docs\make.bat" html
call "C:\Users\Public\pype_env2\Scripts\deactivate.bat"
