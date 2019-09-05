<#
.SYNOPSIS
  This is main entry point into pype. Script is setting important
  environment variables and passes control to python.

.DESCRIPTION
  pype script will set all necessary environment variables if they are not set,
  mainly PYPE_ROOT, and adds pype to PYTHONPATH and PATH.DESCRIPTION

  Then it checks if we have python with correct version. When doing
  deployment or validation, git presence is checked. If launching mongodb,
  we test if mongod is in paths.

  If we don't detect PYPE_ENV, it will be automatically created and
  bootstrapped with required python dependencies specified in
  `pypeapp/requirements.txt`.

  This bootstrapping is done directly in this script along with downloading
  python packages with download command. For more help about available
  commands run `pype --help`.

.EXAMPLE

PS> .\pype.ps1 --help

.EXAMPLE

To install, forcefully recreating PYPE_ENV if exists:
PS> .\pype.ps1 install --force

.EXAMPLE

To deploy (you'll need to set git authentication methods beforehand)
PS> .\pype.ps1 deploy

.EXAMPLE

To run pype tray just:
PS> .\pype.ps1

.EXAMPLE

To run tray in debug mode:
PS> .\pype.ps1 tray --debug

#>

$art = @'


     ____________  ____      ____  ____________  ____________
   / \           \/\   \    /\   \/\           \/\           \
   \  \      ---  \ \   \___\_\   \ \      ---  \ \     ------\
    \  \     _____/  \____     ____\ \     _____/  \    \___\
     \  \    \__/  \____/ \    \__/\  \    \__/  \  \    -------\
      \  \____\         \  \____\   \  \____\     \  \___________\
       \/____/           \/____/     \/____/       \/___________/

                    ...  --[ CLuB ]--  ...


'@

# Process arguments
# .

$arguments=$ARGS
$traydebug=$false
$venv_activated=$false
# map double hyphens to single for powershell use
if($arguments -eq "install") {
  $install=$true
}
if($arguments -eq "--force") {
  $force=$true
}
if($arguments -eq "--offline") {
  $offline=$true
}
if($arguments -eq "--help") {
  $help=$true
}
if($arguments -eq "download") {
  $download=$true
}
if($arguments -eq "deploy") {
  $deploy=$true
}
if($arguments -eq "validate") {
  $validate=$true
}
if($arguments -eq "mongodb") {
  $mongodb=$true
}
if($argments -eq "update-requirements") {
  $update=$true
}


# -----------------------------------------------------------------------------
# Initialize important environment variables

# set PYPE_ROOT to current directory.
if (-not (Test-Path 'env:PYPE_ROOT')) {
  $env:PYPE_ROOT = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
}

# Install PSWriteColor to support colorized output to terminal
$env:PSModulePath = $env:PSModulePath + ";$($env:PYPE_ROOT)\vendor\powershell"

# Set default environment variables if not already set
if (-not (Test-Path 'env:PYPE_ENV')) { $env:PYPE_ENV = "C:\Users\Public\pype_env2" }
if (-not (Test-Path 'env:PYPE_DEBUG')) { $env:PYPE_DEBUG = 0 }

# Add pypeapp to PYTHONPATH
if($env:PYTHONPATH -NotLike "*$($env:PYPE_ROOT);*") {
  $env:PYTHONPATH = "$($env:PYPE_ROOT);$($env:PYTHONPATH)"
}
if($env:PYTHONPATH -NotLike "*$($env:PYPE_ROOT)\pypeapp;*") {
    $env:PYTHONPATH = "$($env:PYPE_ROOT)\pypeapp;$($env:PYTHONPATH)"
}

# Add pype-setup to PATH
if($env:PATH -NotLike "*$($env:PYPE_ROOT);*") {
  $env:PATH = "$($env:PYPE_ROOT);$($env:PATH)"
}

$env:PATH = "$($env:PYPE_ROOT)\vendor\bin\ffmpeg_exec\windows\bin;$($env:PATH)"

function Start-Progress {
  param(
    [ScriptBlock]
    $code
  )
  $scroll = "/-\|/-\|"
  $idx = 0
  $origpos = $host.UI.RawUI.CursorPosition
  $newPowerShell = [PowerShell]::Create().AddScript($code)
  $handle = $newPowerShell.BeginInvoke()
  while ($handle.IsCompleted -eq $false) {
    $host.UI.RawUI.CursorPosition = $origpos
    Write-Host $scroll[$idx] -NoNewline
    $idx++
    if($idx -ge $scroll.Length)
    {
      $idx = 0
    }
    Start-Sleep -Milliseconds 100
  }
  Write-Host ''
  $newPowerShell.EndInvoke($handle)
  $newPowerShell.Runspace.Close()
  $newPowerShell.Dispose()
  <#
  .SYNOPSIS
  Display spinner for running job
  .PARAMETER code
  Job to display spinner for
  #>
}


function Activate-Venv {
  param(
    [string]$Environment
  )
  Write-Color -Text "--> ", "Activating environment [ ", $Environment," ]" -Color Cyan, Gray, White, Gray
  try {
    . ("$Environment\Scripts\Activate.ps1")
  }
  catch {
    Write-Color -Text "!!! ", "Failed to activate." -Color Red, Gray
    Write-Host $_.Exception.Message
    exit 1
  }
  $venv_activated=$true
  <#
  .SYNOPSIS
  Activate virtual environment

  .PARAMETER Environment
  Path to virtual environment.
  #>
}


function Deactivate-Venv {
  Write-Color -Text "<-- ", "Deactivating environment" -Color Cyan, Gray
  if ($venv_activated -eq $true) {
    deactivate
  }

  <#
  .SYNOPSIS
  Deactivate virtual environment

  .PARAMETER Environment
  Path to virtual environment.
  #>
}


function Update-Requirements {
  Write-Color -Text "  -", " Updating requirements ..." -Color Cyan, Gray
  & pip freeze | Out-File -encoding ASCII "$($env:PYPE_ROOT)\pypeapp\requirements.txt"
  <#
  .SYNOPSIS
  This will update requirements.txt based on what's in virtual environment
  #>
}

function Install-Environment {
  if($help -eq $true) {
    & python -m "pypeapp" install --help
    exit 0
  }
  Write-Color -Text ">>> ", "Installing environment to [ ", $env:PYPE_ENV, " ]" -Color Green, Gray, White, Gray
  if($force -eq $true) {
      & python -m "pypeapp" install --force
  } else {
      & python -m "pypeapp" install
  }
  if ($LASTEXITCODE -ne 0) {
    Write-Color -Text "!!! ", "Installation failed (", $LASTEXITCODE, ")" -Color Red, Yellow, Magenta, Yellow
    exit 1
  }
  <#
  .SYNOPSIS
  Install virtual environment
  #>
}


function Check-Environment {
  # get current pip environment
  Write-Color -Text ">>> ", "Validating environment dependencies ... " -Color Green, Gray -NoNewLine
  $p = &{pip freeze}
  # get requirements file
  $r = Get-Content "$($env:PYPE_ROOT)\pypeapp\requirements.txt"
  if (Compare-Object -ReferenceObject $p -DifferenceObject $r) {
    # environment differs from requirements.txt
    Write-Color -Text "FAILED" -Color Yellow
    # TODO: Fix only if option flag present?
    Write-Color -Text "*** ", "Environment dependencies inconsistent, fixing ... " -Color Yellow, Gray
    Test-Offline
    if ($offline -ne $true) {
      & pip install -r "$($env:PYPE_ROOT)\pypeapp\requirements.txt"
    } else {
      & pip install -r "$($env:PYPE_ROOT)\pypeapp\requirements.txt" --no-index --find-links "$($env:PYPE_ROOT)\vendor\packages"
    }
    if ($LASTEXITCODE -ne 0) {
      Write-Color -Text "!!! ", "Installation ", "FAILED" -Color Red, Gray, Red
      return 1
    }
  } else {
    Write-Color -Text "OK" -Color Green
  }
  <#
  .SYNOPSIS
  This checks current environment against pype's requirement.txt
  #>
}

function Upgrade-pip {
  if ($offline -ne $true)
  {
    Write-Color -Text ">>> ", "Updating pip ... " -Color Green, Gray -NoNewLine
    Start-Progress {
      & python -m pip install --upgrade pip | out-null
    }
  }
  <#
  .SYNOPSIS
  Upgrade pip to latest version
  #>
}

function Bootstrap-Pype {

  if ($offline -ne $true)
  {
    # ensure latest pip version
    Upgrade-Pip
    Write-Color -Text ">>> ", "Bootstrapping Pype ... " -Color Green, Gray -NoNewLine

    # install essential dependecies
    Write-Color -Text "  - ", "Installing dependencies ... " -Color Cyan, Gray
    & pip install -r "$($env:PYPE_ROOT)\pypeapp\requirements.txt"
    if ($LASTEXITCODE -ne 0) {
      Write-Color -Text "!!! ", "Installation ", "FAILED" -Color Red, Gray, Red
      return 1
    }
  } else {
    # in offline mode, install all from vendor
    Write-Color -Text ">>> ", "Offline installation ... " -Color Green, Gray
    & pip install -r "$($env:PYPE_ROOT)\pypeapp\requirements.txt" --no-index --find-links "$($env:PYPE_ROOT)\vendor\packages"
    if ($LASTEXITCODE -ne 0) {
      Write-Color -Text "!!! ", "Installation ", "FAILED" -Color Red, Gray, Red
      return 1
    }
  }
  <#
  .SYNOPSIS
  This will install all requirements necessary from requirements.txt
  #>
}


function Deploy-Pype {
  param(
    [bool]$Force=$false
  )
  # process pype deployment
  if ($help -eq $true) {
    & python -m "pypeapp" deploy --help
    deactivate
    exit 0
  }
  if ($Force -eq $true) {
    & python -m "pypeapp" deploy --force
  } else {
    & python -m "pypeapp" deploy
  }
  <#
  .SYNOPSIS
  Run Deployment
  .DESCRIPTION
  This will pass control to python to deploy repositories and stuff
  Requires git
  #>
}


function Validate-Pype {
  if ($help -eq $true) {
      & python -m "pypeapp" validate --help
      deactivate
      exit 0
  }
  & python -m "pypeapp" validate
  <#
  .SYNOPSIS
  This will validate pype deployment
  .DESCRIPTION
  It will pass control to python to validate repositories deployment.
  Requires git
  #>
}





function Detect-Mongo {
  Write-Color -Text ">>> ", "Detecting MongoDB ... " -Color Green, Gray -NoNewLine
  if (-not (Get-Command "mongod" -ErrorAction SilentlyContinue)) {
    if(Test-Path 'C:\Program Files\MongoDB\Server\*\bin\mongod.exe' -PathType Leaf) {
      # we have mongo server installed on standard Windows location
      # so we can inject it to the PATH. We'll use latest version available.
      $mongoVersions = Get-ChildItem -Directory 'C:\Program Files\MongoDB\Server' | Sort-Object -Property {$_.Name -as [int]}
      if(Test-Path "C:\Program Files\MongoDB\Server\$($mongoVersions[-1])\bin\mongod.exe" -PathType Leaf) {
        $env:PATH="$($env:PATH);C:\Program Files\MongoDB\Server\$($mongoVersions[-1])\bin\"
        Write-Color -Text "OK" -Color Green
        Write-Color -Text "  - ", "auto-added from [ ", "C:\Program Files\MongoDB\Server\$($mongoVersions[-1])\bin\", " ]" -Color Cyan, Gray, White, Gray
      } else {
          Write-Color -Text "FAILED", " MongoDB not detected" -Color Red, Yellow
          Write-Color -Text "!!! ", "tried to find it on standard location [ ", "C:\Program Files\MongoDB\Server\$($mongoVersions[-1])\bin\", " ] but failed." -Color Red, Yellow, White, Yellow
          exit
      }
    } else {
      Write-Color -Text "FAILED", " MongoDB not detected" -Color Red, Yellow
      Write-Color -Text "!!! ", "'mongod' wasn't found in PATH" -Color Red, Yellow
      exit
    }

  } else {
    Write-Color -Text "OK" -Color Green
  }
  <#
  .SYNOPSIS
  Function to detect mongod in path.
  .DESCRIPTION
  This will test presence of mongod in PATH. If it's not there, it will try
  to find it in default install location. It support different mongo versions
  (using latest if found). When mongod is found, path to it is added to PATH
  #>
}


function Detect-Python {
  Write-Color -Text ">>> ", "Detecting python ... " -Color Green, Gray -NoNewLine
  if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Color -Text "FAILED", " Python not detected" -Color Red, Yellow
    exit
  }
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
  <#
  .SYNOPSIS
  Function detecting supported python
  #>
}

function Detect-Git {
  Write-Color -Text ">>> ", "Detecting Git ... " -Color Green, Gray -NoNewLine
  if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Color -Text "FAILED", " git not detected" -Color Red, Yellow
    exit
  }
  Write-Color -Text "OK" -Color Green
  <#
  .SYNOPSIS
  Function to detect git
  #>
}


function Test-Offline {
  Write-Color -Text ">>> ", "Test if we are online ... " -Color Green, Gray -NoNewLine
  if (-not (Test-Connection 8.8.8.8 -Count 2 -Quiet)) {
    Write-Color -Text "OFFLINE" -Color Yellow
    Write-Color -Text "--- ", "Enabling offline mode ..." -Color Green, Yellow
    $offline=$true
  } else {
    Write-Color -Text "ONLINE" -Color Green
  }
  <#
  .SYNOPSIS
  Test if we are online or offline
  #>
}

function Download {
  Test-Offline
  if ($offline -eq $true) {
    Write-Color -Text "!!! ", "Cannot download in offline mode." -Color Yellow, Gray
  }
  Write-Color -Text ">>> ", "Downloading packages for offline installation ... " -Color Green, Gray
  Write-Color -Text "  - ", "For platform [ ", "win_amd64", " ]... " -Color Cyan, Gray, White, Gray
  & pip download -r "$($env:PYPE_ROOT)\pypeapp\requirements.txt" -d "$($env:PYPE_ROOT)\vendor\packages"
  Write-Color -Text "<-- ", "Deactivating environment ..." -Color Cyan, Gray
  Deactivate_venv
  Write-Color -Text "+++ ", "Terminating ..." -Color Magenta, Gray
  <#
  .SYNOPSIS
  Download required packages
  #>
}

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------

Write-Color -Text $art -Color Cyan
Write-Color -Text "*** ", "Welcome to ", "Pype", " !" -Color Green, Gray, White, Gray
# Check invalid argument combination
if ($offline -eq $true -and $deploy -eq $true) {
  Write-Color -Text "!!! ", "Invalid invocation. Cannot deploy in offline mode." -Color Red, Gray
  exit 1
}

# Test if python is available and test its version
Detect-Python

# Detect git
# used only when deploying or validating deployment
if($deploy -eq $true -or $validate -eq $true) {
  Detect-Git
}

# Detect mongod in PATHs
# used only when starting local mongodb
if($mongodb -eq $true) {
  Detect-Mongo
}

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
  Test-Offline

  # install environment
  Install-Environment

  # activate environment
  Activate-Venv -Environment $env:PYPE_ENV

  # bootstrap pype
  Bootstrap-Pype

} else {
  Write-Color -Text "FOUND", " - [ ", $env:PYPE_ENV, " ]" -Color Green, Gray, White, Gray
  Activate-Venv -Environment $env:PYPE_ENV
  Check-Environment
  # Upgrade-pip
}

if ($install -eq $true) {
  Write-Color -Text "*** ", "Installation complete. ", "Have a nice day!" -Color Green, White, Gray
  Deactivate_venv
  exit 0
}

# Update
if ($update -eq $true) {
  Update-Requirements
  Deactivate_venv
  exit 0
}

# Download
# This will download pip packages to vendor/packages for later offline installation and exit
if ($download -eq $true) {
  Download
  Deactivate_venv
  exit
}

# Validate deployment
if ($validate -eq $true) {
  Write-Color -Text ">>> ", "Validating ", "Pype", " deployment ... " -Color Green, Gray, White, Gray
  Validate-Pype

  $validationStatus = $LASTEXITCODE

  if ($validationStatus -ne 0) {
    # Deployment is invalid
    Write-Color -Text "!!! WARNING:", "Deployment is invalid." -Color Yellow, Gray
    Write-Color -Text "  * ", "Contact your system administrator to resolve this issue." -Color Yellow, Gray
    Write-Color -Text "  * ", "You can try to fix deployment with ", "pype deploy --force" -Color Green, Gray, White
    Deactivate_venv
    exit 0
  }
}

# Deploy
if ($deploy -eq $true) {
  Test-Offline
  if ($offline -eq $true) {
    # If we are offline, we cannot deploy
    Write-Color -Text "!!! ", "Cannot deploy in offline mode." -Color Red, Gray
    Deactivate_venv
    exit 1
  }
  # if force set, then re-deploy
  if ($force -eq $true) {
    Write-Color -Text ">>> ", "Deploying ", "Pype", " forcefully ..." -Color Green, Gray, White, Gray
    Deploy-Pype -Force $force
    if ($LASTEXITCODE -ne 0) {
      Write-Color -Text "!!! ", "Deployment ", "FAILED" -Color Red, Yellow
      Deactivate_venv
      exit 1
    }
  } else {
    Write-Color -Text ">>> ", "Deploying ", "Pype", " ..." -Color Green, Gray, White, Gray
    Deploy-Pype
    if ($LASTEXITCODE -ne 0) {
      Write-Color -Text "!!! ", "Deployment ", "FAILED" -Color Red, Yellow
      Deactivate_venv
      exit 1
    }
  }

  Write-Color -Text ">>> ", "Re-validating ", "Pype", " deployment ... " -Color Green, Gray, White, Gray
  Validate-Pype
  if ($LASTEXITCODE -ne 0) {
    Write-Color -Text "!!! ", "Deployment is ", "INVALID" -Color Yellow, Gray, Red
    Deactivate_venv
    exit 1
  } else {
    Write-Color -Text ">>> ", "Deployment is ", "OK" -Color Green, Gray, Green
    deactivate
    exit
  }
}

Write-Color -Text ">>> ", "Running ", "pype", " ..." -Color Green, Gray, White
Write-Host ""
& python -m "pypeapp" @arguments
Write-Color -Text "<<< ", "Terminanting ", "pype", " ..." -Color Cyan, Gray, White
Deactivate_venv
