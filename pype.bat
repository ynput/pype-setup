@echo off
pushd %~dp0
powershell -NoProfile -noexit -nologo -executionpolicy bypass -command ".\pype.ps1 %*; exit $LASTEXITCODE"
