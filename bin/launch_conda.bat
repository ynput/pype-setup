
title Avalon conda environment setup
cls :: clear the screen command

:: Change the working directory to the conda-git-deployment directory.
:: "pushd" is being used so any UNC paths get mapped until a restart happens.
pushd %~dp0

:: Make CWD root of avalon-environment repository.
cd ..

:: Get installation directory.
set MINICONDA_DIRECTORY=%~dp0python
set INSTALLATION_DIRECTORY=%MINICONDA_DIRECTORY%\__DEV__

set AVALON_ENV_NAME=pype_env
set REMOTE_ENV_DIR=%MINICONDA_DIRECTORY%\%AVALON_ENV_NAME%

:: create local data disk paths
set LOCAL_ENV_DIR=C:\Users\Public\%AVALON_ENV_NAME%
IF EXIST %LOCAL_ENV_DIR% GOTO LOCAL_ENV_EXISTS
echo [92m^>^>^>[0m Local Python env in [ [96m%LOCAL_ENV_DIR%[0m ] is missing ...

:REMOTE_ENV_NOT_EXISTS
:: Install miniconda if the directory %INSTALLATION_DIRECTORY% does not exist.
IF EXIST %INSTALLATION_DIRECTORY% GOTO INSTALLATION_EXISTS
echo [92m^>^>^>[0m Conda installation dir [ [96m%INSTALLATION_DIRECTORY%[0m ] is missing ...
:: Create "installers" directory if it does not exist, and download miniconda into it.
IF EXIST %MINICONDA_DIRECTORY%\miniconda.exe GOTO INSTALLER_EXISTS
echo [92m^>^>^>[0m Miniconda.exe in [ [96m%MINICONDA_DIRECTORY%[0m ] is missing ...

:: Isolating the execution environment.
:: Powershell is needed for downloading miniconda.
set PATH=C:\WINDOWS\System32\WindowsPowerShell\v1.0

mkdir %MINICONDA_DIRECTORY%
echo [92m^>^>^>[0m Created dir [ [96m%MINICONDA_DIRECTORY%[0m ]

:: create miniconda executable file
set CONDA_EXE_FILENAME=%MINICONDA_DIRECTORY%\miniconda.exe

:: download last build of miniconda trough powershell
set "URL=https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe"
powershell "Import-Module BitsTransfer; Start-BitsTransfer '%URL%' '%CONDA_EXE_FILENAME%'"
echo [92m^>^>^>[0m Miniconda.exe downloaded to in [ [96m%CONDA_EXE_FILENAME%[0m ]

:INSTALLER_EXISTS

:: Install miniconda
echo [92m^>^>^>[0m Installing Conda root env.. Please wait! :)
%CONDA_EXE_FILENAME% /RegisterPython=0 /AddToPath=0 /S /D=%INSTALLATION_DIRECTORY%
echo [92m^>^>^>[0m Conda created root env in [ [96m%INSTALLATION_DIRECTORY%[0m ]



:INSTALLATION_EXISTS
:: Ensure Remote Avalon environment is available for copying to local
IF EXIST %REMOTE_ENV_DIR% GOTO REMOTE_ENV_EXISTS
echo [92m^>^>^>[0m Remote environemt in [ [96m%REMOTE_ENV_DIR%[0m ]

:: Set minimum PATH for conda to function.
:: PATH has to have "C:\Windows\System32" for conda to function properly.
:: Specifically for "cmd" and "chcp" executables.
set PATH=%INSTALLATION_DIRECTORY%\Scripts;C:\Windows\System32

:: Activate conda by activating the root environment
call activate root

:: create avalon env into local computer first lately to by coppied back to
:: remote directory for faster distribution to other computers in the network
IF EXIST %LOCAL_ENV_DIR% (
  echo [92m^>^>^>[0m Removing outdated env from [ [96m%LOCAL_ENV_DIR%[0m ]
  call rmdir /s /q %LOCAL_ENV_DIR%
  )

call conda env create -f %~dp0environment.yml -p %LOCAL_ENV_DIR%
echo [92m^>^>^>[0m Conda created [ [96m%LOCAL_ENV_DIR%[0m ]

:: activatin the local env for pip updgrading
call activate %LOCAL_ENV_DIR%
call python -m pip install --upgrade pip
echo [92m^>^>^>[0m Pip updated to last version to Local env

:: Deactivate avalon_env local environment as it is more save to activate it
:: with feeding it into the path (there was a bug with cPython bynary)
call deactivate

:: Deactivate root environment to escape completely from conda. We dont need it
:: anymore
call deactivate

:: creates the local folder for environment
mkdir %REMOTE_ENV_DIR%

:: copy files into local folder for faster redistribution to other pc in network
call xcopy /s %LOCAL_ENV_DIR% %REMOTE_ENV_DIR%

echo [92m^>^>^>[0m Remote env created in [ [96m%REMOTE_ENV_DIR%[0m ]



:REMOTE_ENV_EXISTS
IF EXIST %LOCAL_ENV_DIR% GOTO LOCAL_ENV_EXISTS
:: if the user's computer doesn't have the local environment yet
:: creates the local folder for environment
mkdir %LOCAL_ENV_DIR%


:: copy files into local folder from remote env dir
call xcopy /s %REMOTE_ENV_DIR% %LOCAL_ENV_DIR%
echo [92m^>^>^>[0m Local env created in [ [96m%LOCAL_ENV_DIR%[0m ]


:LOCAL_ENV_EXISTS

if "%SYNC_ENV%"=="1" (
    if not exist "%REMOTE_ENV_DIR%" (
        goto REMOTE_ENV_NOT_EXISTS
        ) else (
            echo [92m^>^>^>[0m Synchronizing environment from REMOTE to [ [96m%LOCAL_ENV_DIR%[0m ]
            call %REMOTE_ENV_DIR%\python.exe %~dp0sync_dirs.py %REMOTE_ENV_DIR% %LOCAL_ENV_DIR%
        )

)

if "%REMOTE_ENV_ON%"=="1" (
    set PATH="%REMOTE_ENV_DIR%";"%REMOTE_ENV_DIR%\Scripts";"%REMOTE_ENV_DIR%\Library";"%REMOTE_ENV_DIR%\Library\bin";"C:\Windows\System32";"C:\Program Files (x86)\QuickTime\QTSystem\";"%systemdrive%%homepath%\AppData\Local\Microsoft\WindowsApps";"C:\Windows"
    set PYTHONPATH=%REMOTE_ENV_DIR%\Lib\site-packages
    set PYTHON_ENV=%REMOTE_ENV_DIR%
    set GIT_PYTHON_GIT_EXECUTABLE=%REMOTE_ENV_DIR%\Library\bin\git.exe
    echo [92m^>^>^>[0m Running env from: [ [96m"%REMOTE_ENV_DIR%"[0m ]
) else (
    set PATH="%LOCAL_ENV_DIR%";"%LOCAL_ENV_DIR%\Scripts";"%LOCAL_ENV_DIR%\Library";"%LOCAL_ENV_DIR%\Library\bin";"C:\Windows\System32";"C:\Program Files (x86)\QuickTime\QTSystem\";"%systemdrive%%homepath%\AppData\Local\Microsoft\WindowsApps";"C:\Windows"
    set PYTHONPATH=%LOCAL_ENV_DIR%\Lib\site-packages
    set PYTHON_ENV=%LOCAL_ENV_DIR%
    set GIT_PYTHON_GIT_EXECUTABLE=%LOCAL_ENV_DIR%\Library\bin\git.exe
    echo [92m^>^>^>[0m Running env from: [ [96m"%LOCAL_ENV_DIR%"[0m ]
)


:: get all submodules and update them if they are not
IF EXIST %~dp0..\repos\avalon-core\avalon GOTO SUBMODULES_EXISTS
echo [92m^>^>^>[0m Git submodules in [ [96m%~dp0..\repos\avalon-core\avalon[0m ] missing ...


python %~dp0initialize_git.py
REM git submodule update --init --recursive
REM git submodule foreach --recursive git pull origin master
echo [92m^>^>^>[0m Git submodules created and updated

:SUBMODULES_EXISTS

:: Initialize submodules
set PYTHONPATH=%PYPE_SETUP_ROOT%;%PYTHONPATH%
echo [92m^>^>^>[0m All setup and goot to go!
