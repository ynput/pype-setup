call %~dp0bin\launch_conda.bat
set AVALON_DB_DATA=C:\data\db
call python %~dp0bin\server.py %*
