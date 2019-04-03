@echo off
set PYPE_DEBUG=3
call powershell -noexit -nologo -executionpolicy bypass -File pype.ps1 --traydebug -skip
