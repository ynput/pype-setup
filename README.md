# Pype-setup

### Installing in steps:
1. clone repository:
    - if git.exe in PATH: $ `git clone https://github.com/pypeclub/pype-setup.git`
    - if not then download zip: https://github.com/pypeclub/pype-setup/archive/master.zip


2. `$ cd pype-setup`


3. for now basic variables need to be set in `set_environment.bat`


4. run `$ server.bat`


5. installation of Avalon dependencies will work automatically. Mongo dB and Git will be installed from `./bin/environment.yml`


6. `./bin/launchh_conda.bat` will clone --recursive all dependencies
    - it copy all `python executable` with `site-packages` into `C:\Users\Public\pype_env` and runs it from there if not `set REMOTE_ENV_ON=1` in **launcher.bat** or **termial.bat**
    - If any additional pip install needs to happen then run **termial.bat** with `REMOTE_ENV_ON=1` and install. Then `set SYNC_ENV=1` in **launcher.bat** and all additional installed packages will by synchronised from **remote** to **local** environment


7. All Avalon Pyblish and Studio related repository needs to be added to relative `vendor` folder


8. to start avalon just run `$ launcher.bat`


****

### Contribution in steps:
1. Install pype-setup and Atom IDE:
    - install pype-setup as said above
    - create bat with this content

    ```code
    @echo off
    :: set to Local but better to run it from remote env for additional
    :: installation into python path, but as you are not going to install pype
    :: tools here only IDE features then it could be installed locally
    set PATH=C:\Users\Public\pype_env;C:\Users\Public\pype_env\Scripts;%systemdrive%%homepath%\AppData\Local\atom\bin;C:\Windows\System32

    :: settup Atom for synchronization
    set GITHUB_TOKEN=<< your git token >>
    set GIST_ID=<< your gist id >>
    call apm install sync-settings

    call atom
    start cmd.exe
    ```
    - follow this simple quick tutorial [link](https://hackernoon.com/setting-up-a-python-development-environment-in-atom-466d7f48e297). It is possible pip install from opened terminal window and all will be installed into correct Atom's dp0set_environment
    - always run atom from this .bat and all will be set correctly
    - in Atom/menu/file/settings/packages/autocomplete-python/settings/Extra paths for packages add `$PROJECT/app/repos/avalon-core;$PROJECT/app/repos/avalon-launcher;$PROJECT/app/repos/pyblish-qml;$PROJECT/app/repos/pyblish-base` and even more if you want to make autocomplete be aware of our api
    - then all is set and you are good to go! Enjoy :)

2. Any master branch of pype-setup or studio repos are locked for direct commit or PR so create your own branch and name it accordingly to an issue you are dealing with `"<sofware>_<module>_<yourfirstname>"`. Exampe: working on maya config in studio-config, branch name `"maya_pipeline_jakub"`


3. for now we are respecting the `avalon-setup` original setting for software launchers, so any new software needst to be added first as **toml** file into `app/bin` then .bat executives need to be created in `app/bin/windows`. Then the sofware needst to be added into `app\repos\avalon-examples\projects\batman\.config.toml` and from `app\repos\avalon-examples\projects\batman` run `$ avalon --save`.


4. any additional python packages for avalon could be added into `app/bin/pythonpath`
