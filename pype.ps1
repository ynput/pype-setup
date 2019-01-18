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

$env:PYPE_SETUP_ROOT = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$env:PYPE_STUDIO_TEMPLATES = "$($env:PYPE_SETUP_ROOT)\repos\pype-templates"
# Directory prefix for local environment
$env:CONDA_LOCAL =  "C:\Users\Public"
$env:LOCAL_ENV_DIR = "$($env:CONDA_LOCAL)\pype_env"
# Debugging
$env:PYPE_DEBUG=0
$env:PYPE_DEBUG_STDOUT=0
# Syncing
# will synchronize remote with local if 1
$env:SYNC_ENV=0
# will switch to remote if 1
$env:REMOTE_ENV_ON=0


if (-not (Get-Module -ListAvailable -Name "PSWriteColor")) {

  Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -Scope CurrentUser
  Install-Module -Name "PSWriteColor" -Scope CurrentUser
}

function Launch-Conda {
  Write-Color -Text ">>> ", "Launching Conda ..." -Color Green, Gray
  try {
    . ("$($env:PYPE_SETUP_ROOT)\bin\launch_conda.ps1")
  }
  catch {
    Write-Color -Text "!!! ", "Failed to launch conda setup" -Color Red, Gray
    Write-Host $_.Exception.Message
    exit
  }
}

Write-Color -Text ">>> ", "Welcome to ", "Pype Club !" -C Green, Gray, White
Write-Color -Text ">>> ", "Checking environment ..." -C Green, Gray

$arguments = $ARGS

if (-not (Test-Path -Path "$($env:LOCAL_ENV_DIR)" -PathType Container)) {
  Launch-Conda
}

# if PYTHONPATH isn't present set it empty
if (-not (Test-Path $env:PYTHONPATH)) { $env:PYTHONPATH = '' }

if (($env:PYTHONPATH.split(";") | ?{$_ -Like "$($env:PYPE_SETUP_ROOT)"} | measure).count -lt 1) {
  Launch-Conda
}

if (-not (Test-Path -Path "$($env:LOCAL_ENV_DIR)\checksum" -PathType Leaf)) {
  Write-Color -Text "!!! ", "Environment at [ ", $env:LOCAL_ENV_DIR, " ] is corrupted." -Color Red, Gray, White, Gray
  exit 1
}

# compare checksums and notify if they differs.DESCRIPTION
if (Test-Path -Path "$($env:REMOTE_ENV_DIR)\checksum" -PathType Leaf) {
  if (Compare-Object -ReferenceObject $(Get-Content "$($env:REMOTE_ENV_DIR)\checksum") -DifferenceObject $(Get-Content "$($env:LOCAL_ENV_DIR)\checksum")) {
    Write-Color -Text "!!! ", "Warning: ", "REMOTE and LOCAL environments are not same." -Color Yellow, White, Gray
  }
}

& python "$($env:PYPE_SETUP_ROOT)\app\pype-start.py" "$arguments"
