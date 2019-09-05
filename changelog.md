# Pype Setup changelog #

### 2.2.0 ###
_5 Sept 2019_

- **fix**:
  - Presets won't crash when there is extra comma `,` in the jsons _(PYPE-443)_
  - Reintroducing environment check and automatic installation
  - fix linux compatibility when closing shell after tray is launched
  - ffmpeg is now prepended to start of PATH

- **changed**:
  - better traceback printing. Now it's possible to return
  - only pype specific paths are now being cleaned up at the start to prevent breaking certain linux variables.

- **new**:
  - support for local archive and md5 checksums during deployment
  - All logs are now stored in mongo DB for easier collection and retrieval


### 2.1.1 ###

- **fix**:
  - bug with color dependency in powershell
  - wrong variable showing in the error output during launch

### 2.1.0 ###
_5 Aug 2019_

- **new**:
  - You can now run tests using pype command `pype test`
  - Adde texture publishing flag `pype texturecopy`
  - cleaned up documentation for pype command. You can build it using `pype documentation`


- **changed**:
  - pype now prints more informative logs at the start _(PYPE-435)_
  - All the launching arguments have been reworked to be possix compliant
  - Tray launcher now uses pythonw to prevent showing of console window


- **fix**:
  - bug with color dependency in powershell


- **deprecated**:
  - something was marked deprecated it this version

## 2.0 ##
New Pype version changing deployment, setup and environment handling
