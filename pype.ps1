
# install dependencies
if (-not (Get-Module -ListAvailable -Name "PSWriteColor")) {

  Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -Scope CurrentUser
  Install-Module -Name "PSWriteColor" -Scope CurrentUser
}

Write-Color -Text ">>> ", "Welcome to ", "Pype Club !" -C Green, Gray, White
Write-Color -Text $ARGS -C Green, Gray, White
