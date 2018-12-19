# part of pype-setup

function Check-EnvMatch {
  Write-Color -Text ">>> ", "Checking difference between local and remote env (this can take a momet) ..." -Color Green, Gray
  $local = Get-ChildItem -Recurse -Path $env:LOCAL_ENV_DIR
  $remote = Get-ChildItem -Recurse -Path $env:REMOTE_ENV_DIR
  $same = false

  if (!$local -Or !$remote) {
    $same = false
  }
  else {
    if (Compare-Object $local $remote) {
      $same = false
    } else {
      $same = true
    }
  }

  if (!$same) {
    Write-Color -Text "*** ", "local and remote environment are not in sync" -Color Yellow, Gray
    if ($env:SYNC_ENV -eq "1") {
      Sync-RemoteToLocal
    }
  }
}

function Sync-RemoteToLocal {
  Write-Color -Text "--> ", "Syncing [ ", "REMOTE", " ] -> [ ", "LOCAL", " ] " -Color Green, Gray, White, Gray, White, Gray
  Import-Module BitTansfer
  try {
      Start-BitTransfer -Source $env:REMOTE_ENV_DIR -Destination $LOCAL_ENV_DIR -Description "Syncing" -DisplayName "Syncing Remote to Local"
  }
  catch {
    Write-Color -Text "!!! ", "Sync failed" -Color Red, Gray
    Write-Host $_.Exception.Message
    exit
  }
}

function Compute-LocalChecksum {
  Write-Color -Text ">>> ", "Computing checksum for [ ", $env:LOCAL_ENV_DIR, " ] ..." -Color Green, Gray, White, Gray
  # TODO: Implement
}

function Check-LocalValidity {
  if (-not Test-Path -Path "$($env:LOCAL_ENV_DIR)\checksum" -PathType Leaf) {
    Write-Color -Text "!!! ", "Checksum file is missing [ ", "$($env:LOCAL_ENV_DIR)\checksum", " ]" -Color Red, Gray, White, Gray
    Write-Host @'
Checksum file must be present in environment. Either remote environment is invalid (empty or otherwise),
or sync didn't finish properly. Check remote environment, delete it if necessary and run installer again.
'@
  }
  Write-Color -Text ">>> ", "Computing checksum for [ ", $LOCAL_ENV_DIR, " ] ..." -Color Green, Gray, White, Gray
  $invalid = false
  # TODO: calculate checksum and Compare
  $invalid = true
  if ($invalid) {
    Write-Color -Text "!!! ", "Checksum is invalid." -Color Red, Gray
    Write-Host @'
      We've synced either invalid environment or sync failed. Delete both local and remote and run installer again.
'@
    exit
  }
}

function Create-Installer {
  if (-not Test-Path -Path "$($env:CONDA_FILENAME)" -PathType Leaf) {
    # miniconda cannot be found, so we download it via wget
    Write-Color -Text "*** ", "Miniconda.exe", " in [ ", $MINICONDA_DIRECTORY, " ] is missing ..." -Color Yellow, Cyan, Gray, White, Gray
    New-Item -ItemType directory -Path "$($env:MINICONDA_DIRECTORY)"
    # 64-bit version
    $URL = "https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    try {
      Write-Color -Text ">>> ", "Downloading Miniconda [ ", $env:MINICONDA_DIRECTORY, " ] ..." -Color Green, Gray, White, Gray
      Import-Module BitsTransfer
      Start-BitsTransfer -Source $URL -Destination $env:CONDA_FILENAME
    }
    catch {
      Write-Color -Text "!!! ", "Cannot download Miniconda" -Color Red, Gray
      Write-Host $_.Exception.Message
      exit
    }
    Write-Color -Text ">>> ", "Miniconda", " downloaded to [ ", $env:CONDA_FILENAME, " ]" -Color Green, Cyan, Gray, White, Gray
  }
}

function Run-Installer {
  #TODO: Find update option on windows
  if (Test-Path -Path "$($env:INSTALLATION_DIRECTORY)" -PathType Container) {
    Write-Color -Text ">>> ", "Updating Conda root env. Please wait ..." -Color Green, Gray
    $cmd = "& '$($env:CONDA_FILENAME)' /RegisterPython=0 /AddToPath=0 /S /D='$($env:INSTALLATION_DIRECTORY)'"
    Invoke-Expression $cmd
  }
  else {
    Write-Color -Text ">>> ", "Installing Conda root env. Please wait ..." -Color Green, Gray
    $cmd = "& '$($env:CONDA_FILENAME)' /RegisterPython=0 /AddToPath=0 /S /D='$($env:INSTALLATION_DIRECTORY)'"
    Invoke-Expression $cmd
  }
  Write-COlor -Text ">>> ", "Conda created root env in [ ", $env:INSTALLATION_DIRECTORY, " ]" -Color Green, Gray, White, Gray
}

function Create-LocalEnv {
  if ($env:REMOTE_ENV_ON -ne "1") {
    if ($env:SYNC_ENV -ne "1") {
      Write-Color -Text "!!! ", "Sync is disabled and we are forcing local environment." -Color Red, Gray
      Write-Color -Text "!!! ", "But local environment is empty." - Color Red, Gray
      Write-Host @'
Either allow sync from remote environment by setting $SYNC_ENV to 1, or use
remote environment by setting $REMOTE_ENV_ON to 1. Also, we have detected
existing remote environment directory. If you need to install remote directory,
remove existing one and run install again.
'@
    exit
    }
  }
  else {
    if (-not Test-Path -Path "$($env:REMOTE_ENV_DIR)" -PathType Container) {
      Write-Color -Text "!!! ", "Forcing remote environment use but it is missing." -Color Red, Gray
      Write-Host @'
We are forcing use of remote environment, but it wasn't found. If you want
to create new one, delete local environment too and run installer again, or
manually copy existing local environment to remote destination.
'@
      exit
    }
  }
  if ($env:SYNC_ENV) {
    # sync remote environment to local
    Sync-RemoteToLocal
    # check its validity
    Check-LocalValidity
  }

  Create-Installer
  Run-Installer
  Create-RemoteEnv
}

function Create-RemoteEnv {
  #TODO: implement
}


$env:MINICONDA_DIRECTORY="$($env:PYPE_SETUP_ROOT)\bin\python"
$env:CONDA_FILENAME="$($env:MINICONDA_DIRECTORY)\miniconda.exe"
$env:INSTALLATION_DIRECTORY="$($env:MINICONDA_DIRECTORY)\__DEV__"
$env:AVALON_ENV_NAME="pype_env"
$env:REMOTE_ENV_DIR="$($env:MINICONDA_DIRECTORY)\$($AVALON_ENV_NAME)"
$env:LOCAL_ENV_DIR="$($env:CONDA_LOCAL)\$($env:AVALON_ENV_NAME)"


Check-EnvMatch
