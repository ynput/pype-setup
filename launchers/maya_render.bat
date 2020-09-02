@echo off
cls
net use
set PYPE_SETUP_PATH=%~dp0..\
echo "arguments: %*"
%PYPE_SETUP_PATH%\pype.bat launch --app mayabatch_%PYPE_MAYA_VERSION% %*
