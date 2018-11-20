@echo off
:: set basic environments
pushd %~dp0
set PYPE_SETUP_ROOT=%cd%
set PYPE_STUDIO_TEMPLATES=%PYPE_SETUP_ROOT%\repos\pype-templates

:: set main repository
set PYPE_SETUP_GIT_URL=git@github.com:pypeclub/pype-setup.git
set PYPE_SETUP_GIT_BRANCH=master

:: set studio-templates repository
set PYPE_STUDIO_TEMPLATES_NAME=pype-templates
set PYPE_STUDIO_TEMPLATES_URL=git@bitbucket.org:pypeclub/pype-templates.git
set PYPE_STUDIO_TEMPLATES_SUBM_PATH=repos
set PYPE_STUDIO_TEMPLATES_BRANCH=master


:: maintain python environment
:: will synchronize remote with local
set SYNC_ENV=0
:: will switch to remote
set REMOTE_ENV_ON=0
call %PYPE_SETUP_ROOT%\bin\launch_conda.bat

:: debugging
set PYPE_DEBUG=1
