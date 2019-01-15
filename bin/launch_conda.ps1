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

# Check if local and remote environments are same

# This use robocopy, parsing its logs to show progress bar
# Slightly hackish, but doing it's job quite well. I have feeling that it is
# copying slow, maybe parsing logs overhead. Need more testing.
# https://keithga.wordpress.com/2014/06/23/copy-itemwithprogress/
function Copy-ItemWithProgress {
  param(
	[Parameter(Mandatory = $true,ValueFromRemainingArguments=$true)]
	[string[]] $RobocopyArgs
)

$ScanLog  = [IO.Path]::GetTempFileName()
$RoboLog  = [IO.Path]::GetTempFileName()
$ScanArgs = $RobocopyArgs + "/ndl /TEE /bytes /Log:$ScanLog /nfl /L".Split(" ")
$RoboArgs = $RobocopyArgs + "/ndl /TEE /bytes /Log:$RoboLog /NC".Split(" ")

# Launch Robocopy Processes
write-verbose ("Robocopy Scan:`n" + ($ScanArgs -join " "))
write-verbose ("Robocopy Full:`n" + ($RoboArgs -join " "))
$ScanRun = start-process robocopy -PassThru -WindowStyle Hidden -ArgumentList $ScanArgs
$RoboRun = start-process robocopy -PassThru -WindowStyle Hidden -ArgumentList $RoboArgs

# Parse Robocopy "Scan" pass
$ScanRun.WaitForExit()
$LogData = get-content $ScanLog
if ($ScanRun.ExitCode -ge 10)
{
	$LogData|out-string|Write-Error
	throw "Robocopy $($ScanRun.ExitCode)"
}
$FileSize = [regex]::Match($LogData[-4],".+:\s+(\d+)\s+(\d+)").Groups[2].Value
write-verbose ("Robocopy Bytes: $FileSize `n" +($LogData -join "`n"))

# Monitor Full RoboCopy
while (!$RoboRun.HasExited)
{
	$LogData = get-content $RoboLog
	$Files = $LogData -match "^\s*(\d+)\s+(\S+)"
    if ($Files -ne $Null )
    {
	    $copied = ($Files[0..($Files.Length-2)] | %{$_.Split("`t")[-2]} | Measure -sum).Sum
	    if ($LogData[-1] -match "(100|\d?\d\.\d)\%")
	    {
		    write-progress Copy -ParentID $RoboRun.ID -percentComplete $LogData[-1].Trim("% `t") $LogData[-1]
		    $Copied += $Files[-1].Split("`t")[-2] /100 * ($LogData[-1].Trim("% `t"))
	    }
	    else
	    {
		    write-progress Copy -ParentID $RoboRun.ID -Completed
	    }
		$PercentComplete = [math]::min(100,(100*$Copied/[math]::max($Copied,$FileSize)))
		write-progress ROBOCOPY -ID $RoboRun.ID -PercentComplete $PercentComplete $Files[-1].Split("`t")[-1]
    }
}

write-progress Copy -ParentID $RoboRun.ID -Completed
write-progress Copy -ID $RoboRun.ID -Completed

# Parse full RoboCopy pass results, and cleanup
(get-content $RoboLog)[-11..-2] | out-string | Write-Verbose
$res = [PSCustomObject]@{ ExitCode = $RoboRun.ExitCode }
remove-item $RoboLog, $ScanLog
return $res
}

# Check if environments match
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

# Sync remote environment to local
function Sync-RemoteToLocal {
  if (-not (Test-Path -Path "$($env:REMOTE_ENV_DIR)" -PathType Container)) {
    Write-Color -Text "!!! ", "Cannot sync, remote environment is missing." -Color Red, Gray
    exit 1
  }
  if ((Get-ChildItem $env:REMOTE_ENV_DIR -Force | Select-Object -First 1 | Measure-Object).Count -eq 0) {
    Write-Color -Text "!!! ", "Remote environment dir exists but is empty." -Color Red, Gray
    Write-Color -Text "!!! ", "[ ", $env:REMOTE_ENV_DIR, " ]" -Color Red, Gray, White, Gray
    exit 1
  }
  Write-Color -Text "--> ", "Syncing [ ", "REMOTE", " ] -> [ ", "LOCAL", " ] " -Color Green, Gray, White, Gray, White, Gray

  $r = Copy-ItemWithProgress $env:REMOTE_ENV_DIR $env:LOCAL_ENV_DIR /MIR
  # robocopy exit code 0 is no file copied and no error occured, 1 is one or more where copied
  if ($r.ExitCode -ne 1 -And $r.ExitCode -ne 0) {
    Write-Color -Text "!!! ", "Sync failed" -Color Red, Gray
    Write-Color -Text "!!! ", "robocopy exit code $LASTEXITCODE"
    exit 1
  }
  Write-Color -Text ">>> ", "Remote environment synced to local [ ", $env:LOCAL_ENV_DIR, " ]" -Color Green, Gray, White, Gray
}

# Sync local directory to remote location
function Sync-LocalToRemote {
  if (-not (Test-Path -Path "$($env:REMOTE_ENV_DIR)" -PathType Container)) {
    New-Item -ItemType directory -Path "$($env:REMOTE_ENV_DIR)" | Out-Null
  }
  if ((Get-ChildItem $env:REMOTE_ENV_DIR -Force | Select-Object -First 1 | Measure-Object).Count -ne 0) {
    Write-Color -Text "!!! ", "Remote environment dir exists and is not empty." -Color Red, Gray
    Write-Color -Text "!!! ", "[ ", $env:REMOTE_ENV_DIR, " ]" -Color Red, Gray, White, Gray
    Write-Host @'
As a safety measure, we will not install environment to already existing one.
You should check this directory and remove it. After that run installation again.
'@
    exit 1
  }
  Write-Color -Text "--> ", "Copying [ ", $env:LOCAL_ENV_DIR, " ] -> [ ", $env:REMOTE_ENV_DIR, " ]" -Color Green, Gray, White, Gray, White, Gray

  $r = Copy-ItemWithProgress $env:LOCAL_ENV_DIR $env:REMOTE_ENV_DIR /MIR
  # robocopy exit code 0 is no file copied and no error occured, 1 is one or more where copied
  if ($r.ExitCode -ne 1 -And $r.ExitCode -ne 0) {
    Write-Color -Text "!!! ", "Sync failed" -Color Red, Gray
    Write-Color -Text "!!! ", "robocopy exit code ", $LASTEXITCODE -Color Red, Gray, Yellow
    exit 1
  }

  Write-Color -Text ">>> ", "Remote environment created in [ ", $env:REMOTE_ENV_DIR, " ]" -Color Green, Gray, White, Gray
}

# Display spinner for running job
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
}

# Compute checksum for local environment
function Compute-LocalChecksum {
  param ($folder)
  Write-Color -Text ">>> ", "Computing checksum for [ ", $folder, " ] ..." -Color Green, Gray, White, Gray
  Write-Color -Text "  - ", "Building file list (this can take a moment) ..." -Color Cyan, Gray
  Write-Host "    Building " -NoNewline

  $files = Start-Progress {Get-ChildItem -Path $folder -Recurse -Force | Sort-Object | Get-FileHash | Select Hash, Path }

  $allBytes = New-Object System.Collections.Generic.List[byte]
  $I=0
  $PD = 153051
  Write-Color -Text "  - ", "Calculating checksums ..." -Color Cyan, Gray
  foreach ($file in $files)
  {
    Write-Progress -Activity "Calculating checksum" -ID $PD -PercentComplete ($I/$files.count*100) -Status $file.Path
    $file.Path = $file.Path.Replace($folder, "")
    $allBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes($file.Path))
    $allBytes.AddRange([System.Text.Encoding]::UTF8.GetBytes($file.Hash))
    $I = $I + 1
  }
  $hasher = [System.Security.Cryptography.SHA256]::Create()
  $checksum = [string]::Join("", $($hasher.ComputeHash($allBytes.ToArray()) | %{"{0:x2}" -f $_}))
  Write-Progress -Activity "Complete" -ID $PD -Completed
  return $checksum
}

# Check if local environment is valid
function Check-LocalValidity {
  if (-not (Test-Path -Path "$($env:LOCAL_ENV_DIR)\checksum" -PathType Leaf)) {
    Write-Color -Text "!!! ", "Checksum file is missing [ ", "$($env:LOCAL_ENV_DIR)\checksum", " ]" -Color Red, Gray, White, Gray
    Write-Host @'
Checksum file must be present in environment. Either remote environment is invalid (empty or otherwise),
or sync didn't finish properly. Check remote environment, delete it if necessary and run installer again.
'@
  }
  $invalid = false
  $checksum = Compute-LocalChecksum $env:LOCAL_ENV_DIR
  if (Compare-Object -ReferenceObject $checksum -DifferenceObject $(Get-Content "$($env:LOCAL_ENV_DIR)\checksum")) {
      $invalid = true
  }

  if ($invalid) {
    Write-Color -Text "!!! ", "Checksum is invalid." -Color Red, Gray
    Write-Host @'
      We've synced either invalid environment or sync failed. Delete both local and remote and run installer again.
'@
    exit
  }
}

# Download Miniconda if missing
function Create-Installer {
  if (-not (Test-Path -Path "$($env:CONDA_FILENAME)" -PathType Leaf)) {
    # miniconda cannot be found, so we download it via wget
    Write-Color -Text "*** ", "miniconda.exe", " in [ ", $env:MINICONDA_DIRECTORY, " ] is missing ..." -Color Yellow, Cyan, Gray, White, Gray
    New-Item -ItemType directory -Force -Path "$($env:MINICONDA_DIRECTORY)" | Out-Null
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

# Run Miniconda install
function Run-Installer {

  if (Test-Path -Path "$($env:INSTALLATION_DIRECTORY)" -PathType Container) {
    <#
    Write-Color -Text ">>> ", "Updating Conda. Please wait ..." -Color Green, Gray
    $a = "/RegisterPython=0", "/AddToPath=0", "/S", "/D=$($env:INSTALLATION_DIRECTORY)"
    & $env:CONDA_FILENAME $a | Out-Null
    Start-Process -FilePath $env:CONDA_FILENAME -ArgumentList $a -NoNewWindow -Wait
    #>
    # Do nothing.
    # TODO: Find update option on windows (-u is on linux)
    Write-Color -Text "--- ", "Conda already installed." -Color Cyan, Gray
  }
  else {
    Write-Color -Text ">>> ", "Installing Conda. Please wait ..." -Color Green, Gray
    $a = "/RegisterPython=0", "/AddToPath=0", "/S", "/D=$($env:INSTALLATION_DIRECTORY)"
    Start-Process -FilePath $env:CONDA_FILENAME -ArgumentList $a -NoNewWindow -Wait

  }
  Write-Color -Text ">>> ", "Conda is in [ ", $env:INSTALLATION_DIRECTORY, " ]" -Color Green, Gray, White, Gray
}

# Create local environment
function Create-LocalEnv {
  # check if we have remote
  if (-not (Test-Path -Path "$($env:REMOTE_ENV_DIR)" -PathType Container)) {
    # we don't so create local one and sync to remote
    Create-Installer
    Run-Installer
    Create-RemoteEnv
  }
  else {
    # we have remote
    # Do we need sync?
    if ($env:SYNC_ENV -eq "1") {
      # sync remote environment to local
      Sync-RemoteToLocal
      # check its validity
      Check-LocalValidity
    }
    if ($env:REMOTE_ENV_ON -ne "1") {
      # but we are not using it
      if ($env:SYNC_ENV -ne "1") {
        # and we even don't want to sync it. Throw error.
        Write-Color -Text "--- ", "Forcing sync" -Color Yellow, Gray
        # sync remote environment to local
        Sync-RemoteToLocal
        # check its validity
        Check-LocalValidity
      }
    }
  }
}

# Create remote environment
function Create-RemoteEnv {
  Write-Color -Text ">>> ", "Installing remote environment to [ ", $env:REMOTE_ENV_DIR, " ]" -Color Green, Gray, White, Gray
  $env:PATH = "$($env:INSTALLATION_DIRECTORY)\Scripts;C:\Windows;C:\Windows\System32;C:\Windows\System32\WindowsPowerShell\v1.0"

  Write-Color -Text ">>> ", "Updating conda ..." -Color Green, Gray
  # & cmd /k "activate.bat root & powershell"

  # update conda to latest version
  conda update -y -n root -c defaults conda

  # set execution policy
  Write-Color -Text ">>> ", "Setting conda powershell compatibility ..." -Color Green, Gray
  # Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  # conda as of 4.5.11 still doesn't have activate / deactivate support for powershell
  conda install -y -n root -c pscondaenvs pscondaenvs

  if (Test-Path -Path "$($env:LOCAL_ENV_DIR)" -PathType Container) {
    Write-Color -Text ">>> ", "Removing outdated local environment from [ ", $env:LOCAL_ENV_DIR, " ]" -Color Green, Gray, White, Gray
    try {
        Remove-Item -Path "$($env:LOCAL_ENV_DIR)" -Force -Recurse
    }
    catch {
      Write-Color -Text "!!! ", "Cannot remove local environment." -Color Red, Gray
      Write-Host $_.Exception.Message
      Write-Host @'
      Cannot remove directory containing local environment. It could be caused by
      permissions or process still running from within. Please consult error messages
      above.
'@
      exit
    }
  }
  Write-Color -Text ">>> ", "Processing environment for [ ", "python 2", " ] ..." -Color Green, Gray, White, Gray
  Write-Color -Text "--- ", "Creating conda environment using [ ", "$($env:PYPE_SETUP_ROOT)\bin\environment2.yml", " ] ..." -Color Cyan, Gray, White, Gray
  conda env create -f "$($env:PYPE_SETUP_ROOT)\bin\environment2.yml" -p "$($env:LOCAL_ENV_DIR)\python2"
  if ($LASTEXITCODE -ne 0) {
    Write-Color -Text "!!! ", "Creating conda env failed." -Color Red, Gray
    Write-Host @'
Unable to create Conda environment. Usually this is caused by insufficient permissions
on local environment directory or some dependency issues in Conda. Please consult error
messages above.
'@
    exit 1
  }
  Write-Color -Text ">>> ", "Conda created [ ", "$($env:LOCAL_ENV_DIR)\python2", " ]" -Color Green, Gray, White, Gray

  Write-Color -Text ">>> ", "Processing environment for [ ", "python 3", " ] ..." -Color Green, Gray, White, Gray
  Write-Color -Text "--- ", "Creating conda environment using [ ", "$($env:PYPE_SETUP_ROOT)\bin\environment3.yml", " ] ..." -Color Cyan, Gray, White, Gray
  conda env create -f "$($env:PYPE_SETUP_ROOT)\bin\environment3.yml" -p "$($env:LOCAL_ENV_DIR)\python3"
  if ($LASTEXITCODE -ne 0) {
    Write-Color -Text "!!! ", "Creating conda env failed." -Color Red, Gray
    Write-Host @'
Unable to create Conda environment. Usually this is caused by insufficient permissions
on local environment directory or some dependency issues in Conda. Please consult error
messages above.
'@
    exit 1
  }
  Write-Color -Text ">>> ", "Conda created [ ", "$($env:LOCAL_ENV_DIR)\python3", " ]" -Color Green, Gray, White, Gray

# We don't really want to do this stuff, don't we. Latest version of pip should be
# Downloaded by Conda

<#
  # activating the local env for pip updgrading
  Write-Color -Text "--> ", "Entering local environment ..." -Color Cyan, Gray
  . "$($env:INSTALLATION_DIRECTORY)\Scripts\activate.ps1 $($env:LOCAL_ENV_DIR)/python2 & powershell"
  Write-Color -Text ">>> ", "Updating PIP to latest version ..." -Color Cyan, Gray
  python -m pip install --upgrade pip
  if ($LASTEXITCODE -ne 0) {
    Write-Color -Text "!!! ", "PIP wasn't updated successfully." -Color Yellow, Gray
    Write-Host @'
This is not fatal error, but using outdated PIP version can result in many
different compatibility issues later on while installing pipeline dependencies.
'@
  }
  else {
      Write-Color -Text ">>> ", "PIP updated." -Color Green, Gray
  }
  Write-Color -Text "<-- ", "Leaving local environment ..." -Color Cyan, Gray
  . "$($env:INSTALLATION_DIRECTORY)\Scripts\deactivate.ps1"

  # Deactivate root environment to escape completely from conda. We dont need it
  # anymore
  # Write-Color -Text "<-- ", "Leaving root environment ..." -Color Cyan, Gray
  # & cmd /k "deactivate & powershell"
#>

  # Calculate checksum
  $checksum = Compute-LocalChecksum $env:LOCAL_ENV_DIR
  $checksum | Out-File "$($env:LOCAL_ENV_DIR)\checksum"
  Sync-LocalToRemote
}

# main entry
#-------------------------------------------------------------------------------

# TODO: not all has to be env. Maybe just remote and local env dirs
$env:MINICONDA_DIRECTORY="$($env:PYPE_SETUP_ROOT)\bin\python"
$env:CONDA_FILENAME="$($env:MINICONDA_DIRECTORY)\miniconda.exe"
$env:INSTALLATION_DIRECTORY="$($env:MINICONDA_DIRECTORY)\__DEV__"
$env:AVALON_ENV_NAME="pype_env"
$env:REMOTE_ENV_DIR="$($env:MINICONDA_DIRECTORY)\$($env:AVALON_ENV_NAME)"
$env:LOCAL_ENV_DIR="$($env:CONDA_LOCAL)\$($env:AVALON_ENV_NAME)"

if ($arguments -eq "--pushtoremote") {
  Sync-LocalToRemote
}

if ($arguments -eq "--sync") {
  Sync-RemoteToLocal
}

# Does local environment exist?
if (Test-Path -Path "$($env:LOCAL_ENV_DIR)" -PathType Container) {
  # If so, is it empy?
  if ((Get-ChildItem $env:LOCAL_ENV_DIR -Force | Select-Object -First 1 | Measure-Object).Count -eq 0) {
    # It is empty, create it
    Create-LocalEnv
  }
  else {
    # It's not empty
    # Does remote environment exist?
    if (-not (Test-Path -Path "$($env:REMOTE_ENV_DIR)" -PathType Container)) {
      if ($env:SYNC_ENV -eq "1") {
        # If not and we want to sync remote -> local, throw error.
        Write-Color -Text "!!! ", "Cannot sync, missing remote environment." -Color Red, Gray
        exit 1
      }
      else {
        # If not and we don't want to sync, but want to use it directly, throw error.
        if ($env:REMOTE_ENV_ON -eq "1") {
          Write-Color -Text "!!! ", "Cannot use remote environmnet because it is missing." -Color Red, Gray
          Write-Host @'
We are forcing use of remote environment, but it wasn't found. If you want
to create new one, delete local environment too and run installer again, or
manually copy existing local environment to remote destination.
'@
          exit 1
        }
        Write-Color -Text "!!! ", "Remote environment is missing." -Color Yellow, Gray
      }
    }
    else {
      # Remote environment exists
      if ($env:SYNC_ENV -eq "1") {
        # And we want to sync it
        Sync-RemoteToLocal
        Check-LocalValidity
      }
    }
  }
}
else {
  # Local environment doesn't exist, we create one
  Write-Color -Text ">>> ", "Local environment not exists: [ ", $env:LOCAL_ENV_DIR, " ]" -Color Yellow, Gray, White, Gray
  Create-LocalEnv
}

# At this point we should have environment


# Set variables
if ($env:REMOTE_ENV_ON -eq "1") {

  # One last check - test if we have checksum file. If not, enironment is probably corrupted.
  if (-not (Test-Path -Path "$($env:REMOTE_ENV_DIR)\checksum" -PathType Leaf)) {
    Write-Color -Text "!!! ", "Environment at [ ", $env:REMOTE_ENV_DIR, " ] is corrupted." -Color Red, Gray, White, Gray
    Write-Host @'
Remote environment is probably corrupted and unusable. Please, delete it and either run
with --pushtormote to sync your local environment to remote, or delete both and run install again
to populate both environments.
'@
    exit 1
  }
  $env:PYTHON_ENV = $env:REMOTE_ENV_DIR
  Write-Color -Text ">>> ", "Running remote environment from [ ", $env:REMOTE_ENV_DIR, " ]" -Color Green, Gray, White, Gray
}
else {

  # One last check - test if we have checksum file. If not, enironment is probably corrupted.
  if (-not (Test-Path -Path "$($env:LOCAL_ENV_DIR)\checksum" -PathType Leaf)) {
    Write-Color -Text "!!! ", "Environment at [ ", $env:LOCAL_ENV_DIR, " ] is corrupted." -Color Red, Gray, White, Gray
    Write-Color -Text "*** ", "Trying to sync remote to local ..." -Color Yellow, Gray
    Sync-RemoteToLocal
  }
  # compare checksums and notify if they differs.DESCRIPTION
  if (Test-Path -Path "$($env:REMOTE_ENV_DIR)\checksum" -PathType Leaf) {
    if (Compare-Object -ReferenceObject $(Get-Content "$($env:REMOTE_ENV_DIR)\checksum") -DifferenceObject $(Get-Content "$($env:LOCAL_ENV_DIR)\checksum")) {
      Write-Color -Text "!!! ", "Warning: ", "REMOTE and LOCAL environments are not same." -Color Yellow, White, Gray
    }
  }
  $env:PYTHON_ENV = $env:LOCAL_ENV_DIR
  Write-Color -Text ">>> ", "Running local environment from [ ", $env:LOCAL_ENV_DIR, " ]" -Color Green, Gray, White, Gray
}

# Default path pointing to python3 environment
$env:PATH = "$($env:PYTHON_ENV)\python3;$($env:PYTHON_ENV)\python3\Scripts;$($env:PYTHON_ENV)\python3\Library\bin;$($env:PYTHON_ENV)\Python3\Library;$PATH"
# We omit python3 environment from python path. That way, we can set it for every app independently
$env:PYTHONPATH = "$($env:PYPE_SETUP_ROOT);$($env:PYPE_SETUP_ROOT)\app\vendor"
$env:GIT_PYTHON_GIT_EXECUTABLE = "$($env:PYTHON_ENV)\python3\Library\bin\git.exe"

# Test if we have pype-templates
if (-not (Test-Path -Path "$($env:PYPE_SETUP_ROOT)\repos\pype-templates" -PathType Container)) {
  # If not, init git repositories
  Write-Color -Text "*** ", "Git repositories in [ ", "$($env:PYPE_SETUP_ROOT)\repos", " ] are missing ..." -Color Yellow, Gray, White, Gray
  Write-Color -Text ">>> ", "Running Git Repositories initialization procedure ..." -Color Green, Gray

  & python "$($env:PYPE_SETUP_ROOT)\bin\initialize_git.py"
  if ($LASTEXITCODE -ne 0) {
    Write-Color -Text "!!! ", "Initialization failed." -Color Red, Gray
    Write-Host @'
Something failed during Git repositories initialization. Those repositories are essential for Pype.DESCRIPTION
Check error messages above.
'@
    exit 1
  }

  Write-Color -Text ">>> ", "Git repositories created and updated." -Color Green, Gray
}
exit
