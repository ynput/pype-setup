@echo off
set PYPE_DEBUG=3
pushd %~dp0..\
call pype.bat --traydebug --ignore --skip
popd
