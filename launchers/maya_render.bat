@echo off
cls
@pushd %~dp0
echo "arguments: %*"
..\pype.bat launch --app mayabatch_2019 %*
@popd
