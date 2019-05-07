@echo off
call powershell -noexit -nologo -executionpolicy bypass -command "%~dp0pype.ps1 %*"
