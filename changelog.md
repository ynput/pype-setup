# Pype changelog #
This is Pype changelog.


### 2.1.1 ###
_next release_

- **fix**:
  - Presets won't crash when there is extra comma `,` in the jsons _(PYPE-443)_
  - Reintroducing environment check and automatic installation

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
