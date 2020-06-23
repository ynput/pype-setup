@echo off
cls
net use
echo "arguments: %*"
%PYPE_SETUP_PATH%\pype.bat launch --app mayabatch_%PYPE_MAYA_VERSION% %*
