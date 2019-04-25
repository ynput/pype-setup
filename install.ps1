# Pypeclub / Pype
# part of pype-setup
#     ____________  ____      ____  ____________  ____________
#   / \           \/\   \    /\   \/\           \/\           \
#   \  \      ---  \ \   \___\_\   \ \      ---  \ \     ------\
#    \  \     _____/  \____     ____\ \     _____/  \    \___\
#     \  \    \__/  \____/ \    \__/\  \    \__/  \  \    -------\
#      \  \____\         \  \____\   \  \____\     \  \___________\
#       \/____/           \/____/     \/____/       \/___________/
#
#                    ...  █░░ --=[ CLuB ]]=-- ░░█ ...

# install dependencies
if (-not (Get-Module -ListAvailable -Name "PSWriteColor")) {
  Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -Scope CurrentUser
  Install-Module -Name "PSWriteColor" -Scope CurrentUser
}

$env:PYPE_SETUP_ROOT = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$env:PYPE_STUDIO_TEMPLATES = "$($env:PYPE_SETUP_ROOT)\repos\pype-templates"
# basic Setup
$env:PYPE_SETUP_GIT_URL="git@bitbucket.org:pypeclub/pype-setup.git"
$env:PYPE_SETUP_GIT_BRANCH="master"
$env:PYPE_STUDIO_TEMPLATES_NAME="pype-templates"
$env:PYPE_STUDIO_TEMPLATES_URL="git@bitbucket.org:pypeclub/pype-config.git"
$env:PYPE_STUDIO_TEMPLATES_SUBM="repos"
$env:PYPE_STUDIO_TEMPLATES_BRANCH="master"

# Directory prefix for local environment
$env:CONDA_LOCAL =  "C:\Users\Public"

# Debugging
$env:PYPE_DEBUG=1

# Syncing
# will synchronize remote with local if 1
$env:SYNC_ENV=0
# will switch to remote if 1
$env:REMOTE_ENV_ON=0

Write-Color -Text ">>> ", "Welcome to Pype Club" -Color Green, White
Write-Color -Text ">>> ", "Launching Conda ..." -Color Green, Gray

$arguments = $ARGS
# Launch Conda
try {
  . ("$($env:PYPE_SETUP_ROOT)\bin\launch_conda.ps1")
}
catch {
  Write-Color -Text "!!! ", "Failed to launch conda setup" -Color Red, Gray
  Write-Host $_.Exception.Message
}
exit
