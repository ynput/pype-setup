@echo off

setlocal
cd /d %~dp0

call powershell -noexit -nologo -executionpolicy bypass -File pype.ps1 %*
