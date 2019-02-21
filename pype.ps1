#     ____________  ____      ____  ____________  ____________
#   / \           \/\   \    /\   \/\           \/\           \
#   \  \      ---  \ \   \___\_\   \ \      ---  \ \     ------\
#    \  \     _____/  \____     ____\ \     _____/  \    \___\
#     \  \    \__/  \____/ \    \__/\  \    \__/  \  \    -------\
#      \  \____\         \  \____\   \  \____\     \  \___________\
#       \/____/           \/____/     \/____/       \/___________/
#
#                    ...  █░░ --=[ CLuB ]]=-- ░░█ ...

param(
  [switch]$install=$false,
  [switch]$force=$false,
  [switch]$ignore=$false,
  [switch]$offline=$false,
  [switch]$download=$false
)

$arguments = $ARGS
$env:PYPE_ROOT = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

# Install PSWriteColor to support colorized output to terminal
if (-not (Get-Module -ListAvailable -Name "PSWriteColor")) {
  Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -Scope CurrentUser
  Install-Module -Name "PSWriteColor" -Scope CurrentUser
}

function Activate-Venv {
  param(
    [string]$Environment
  )
  try {
    . ("$Environment\Scripts\Activate.ps1")
  }
  catch {
    Write-Color -Text "!!! ", "Failed to activate." -Color Red, Gray
    Write-Host $_.Exception.Message
    return $false
  }
  return $true
}

function Check-Environment {
  # get current pip environment
  $p = &{pip freeze}
  # get requirements file
  $r = Get-Content "$($env:PYPE_ROOT)\pypeapp\requirements.txt"
  if (Compare-Object -ReferenceObject $p -DifferenceObject $r) {
    # environment differs from requirements.txt
    return $false
  }
  return $true
}

function Bootstrap-Pype {
  # ensure latest pip version
  if ($offline -ne $true)
  {
    & python -m pip install --upgrade pip

    # install essential dependecies
    & pip install -r pypeapp/requirements.txt
  } else {
    # in offline mode, install all from vendor
    & pip install -r pypeapp/requirements.txt -f vendor/packages
  }
}

function Deploy-Pype {
  param(
    [bool]$Force=$false
  )
  # process pype deployment
  if ($Force -eq $true) {
    & python -m "pypeapp" --deploy --force
  } else {
    & python -m "pypeapp" --deploy
  }
}

function Validate-Pype {
  & python -m "pypeapp" --validate
}

Write-Color -Text "*** ", "Welcome to ", "Pype", " !" -Color Green, Gray, White, Gray

# Set default environment variables if not already set
if (-not (Test-Path 'env:PYPE_ENV')) { $env:PYPE_ENV = "C:\Users\Public\pype_env2" }
if (-not (Test-Path 'env:PYPE_DEBUG')) { $env:PYPE_DEBUG = 0 }
# Add pypeapp to PYTHONPATH
$env:PYTHONPATH = "$($env:PYPE_ROOT)\pypeapp;$($env:PYTHONPATH)"

# Test if python is available
Write-Color -Text ">>> ", "Detecting python ... " -Color Green, Gray -NoNewLine
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
  Write-Color -Text "FAILED", " Python not detected" -Color Red, Yellow
  exit
}

# Test python version available
$version_command = @'
import sys
print('{0}.{1}'.format(sys.version_info[0], sys.version_info[1]))
'@

$p = &{python -c $version_command}
$m = $p -match '(\d+)\.(\d+)'
if(-not $m) {
  Write-Color -Text "FAILED", " Cannot determine version" -Color Red, Yellow
  exit
}
# We are supporting python 3.6 and up
if(($matches[1] -lt 3) -or ($matches[2] -lt 6)) {
  Write-Color -Text "FAILED", " Version [ ", $p, " ] is old and unsupported" -Color Red, Yellow, Cyan, Yellow
  exit
}

Write-Color -Text "OK" -Color Green -NoNewLine
Write-Color -Text " - version [ ", $p ," ]" -Color Gray, Cyan, Gray

# Detect existing venv
Write-Color -Text ">>> ", "Detecting environment ... " -Color Green, Gray -NoNewLine

$needToInstall = $false
# Does directory exist?
if (Test-Path -Path "$($env:PYPE_ENV)" -PathType Container) {
  # If so, is it empy?
  if ((Get-ChildItem $env:PYPE_ENV -Force | Select-Object -First 1 | Measure-Object).Count -eq 0) {
    $needToInstall = $true
  }
} else {
  $needToInstall = $true
}

if ($install -eq $true) {
  $needToInstall = $true
}

if ($needToInstall -eq $true) {
  if ($install -eq $true) {
    Write-Color -Text "WILL BE INSTALLED" -Color Yellow
  } else {
    Write-Color -Text "NOT FOUND" -Color Yellow
  }

  Write-Color -Text ">>> ", "Installing environment to [ ", $env:PYPE_ENV, " ]" -Color Green, Gray, White, Gray
  if($force -eq $true) {
      & python -m "pypeapp" --install --force
  } else {
      & python -m "pypeapp" --install
  }
  if ($LASTEXITCODE -ne 0) {
    Write-Color -Text "!!! ", "Installation failed (", $LASTEXITCODE, ")" -Color Red, Yellow, Magenta, Yellow
    exit 1
  }
  # activate environment
  Write-Color -Text "--> ", "Activating environment [ ", $env:PYPE_ENV," ]" -Color Cyan, Gray, White, Gray
  $r = Activate-Venv -Environment $env:PYPE_ENV
  if ($r -eq $false) {
    exit 1
  }

  Bootstrap-Pype
  Deploy-Pype

} else {
  Write-Color -Text "FOUND", " - [ ", $env:PYPE_ENV, " ]" -Color Green, Gray, White, Gray
  Write-Color -Text "--> ", "Activating environment [ ", $env:PYPE_ENV," ]" -Color Cyan, Gray, White, Gray
  $r = Activate-Venv -Environment $env:PYPE_ENV
  if ($r -eq $false) {
    exit 1
  }

  Write-Color -Text ">>> ", "Validating environment dependencies ... " -Color Green, Gray -NoNewLine
  $r = Check-Environment
  if ($r -eq $false) {
    Write-Color -Text "FAILED" -Color Yellow
    Write-Color -Text "*** ", "Environment dependencies inconsistent, fixing ..." -Color Yellow, Gray
    if ($offline -ne $true) {
      & pip install -r pypeapp\requirements.txt
    } else {
      & pip install -r pypeapp\requirements.txt -f vendor\packages
    }

  } else {
    Write-Color -Text "OK" -Color Green
  }
}

# Download
# This will download pip packages to vendor/packages for later offline installation and exit
if ($download -eq $true) {
  Write-Color -Text ">>> ", "Downloading packages for offline installation ... " -Color Green, Gray
  & pip download -r pypeapp\requirements.txt -d vendor\packages --platform any
  Write-Color -Text "<-- ", "Deactivating environment ..." -Color Cyan, Gray
  deactivate
  Write-Color -Text "xxx ", "Terminating ..." -Color Magenta, Gray
  exit
}

Write-Color -Text ">>> ", "Validating ", "Pype", " deployment ... " -Color Green, Gray, White, Gray -NoNewLine
$r = Validate-Pype
if ($r -eq $false) {
  # if force set, than re-deploy
  if ($force -eq $true) {
    Write-Color -Text "INVALID", " - forcing re-deployment" -Color Yellow
    Write-Color -Text ">>> ", "Deploying ", "Pype", " ..." -Color Green, Gray, White, Gray
    Deploy-Pype -Force $force
  }
  # if ignore set, run even if validation failed
  if ($ignore -ne $true) {
    Write-Color -Text "INVALID" -Color Red
    Write-Color -Text "!!! ", "Pype deployment is invalid. Use ", "--force", " to re-deploy." -Color Red, Gray, White, Gray
    Write-Color -Text "... ", "Use ", "--ignore", "if you want to run Pype nevertheless at your own risk."
    exit 1
  } else {
    Write-Color -Text "INVALID", " - forced to ignore" -Color Red, Yellow
  }
} else {
  Write-Color -Text "OK" -Color Green
}
