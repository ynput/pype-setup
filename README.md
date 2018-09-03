# MOCK-UP APPLICATION
- this project was created for a proposal and therefore it is not a properly running application, although some functions are implemented and could be runned from `TEST_*.py`

# Proposal: **app-store**, **app.tray**

> **avalon-app** and **app_store**

- the avalon-app will globalize the avalon environment for _stand-alone_ or any installed application connected to _avalon ecosystem_. It will read all data from **.config file** similarly as avalon does.  [`[conf.bin.{app}]`](https://github.com/pypeclub/avalon-app/blob/8948a7eafc35ccd56195b85f5ffba6580b923330/.config.app..My-Testing#L18) most of these app paths point to directory which contain other .toml files for each version of software used in pipeline. This .toml file stores all environment for the wrapper. [conf.bin.nuke.Nuke11.1v4](https://github.com/pypeclub/avalon-app/blob/8948a7eafc35ccd56195b85f5ffba6580b923330/app/bin/Nuke/Nuke11.1v4.toml#L6)

- we will install the app to the system we are working on and by [`[{avalon-app.root.path}/.config.app..My_config_preset]`](https://github.com/pypeclub/avalon-app/blob/master/.config.app..My-Testing) all will be set to the **user/dev **environment

- `avalon-core`, `avalon-launcher`, `pyblish-base`, `pyblish-qml` are installed in [.config.app..My-Testing](https://github.com/pypeclub/avalon-app/blob/master/.config.app..My-Testing) by default and rest of `packages` (apps) in **app_store**, for example [`[{app_store.path}/{avalon.maya.path}]`](https://github.com/pypeclub/avalon-app/blob/8948a7eafc35ccd56195b85f5ffba6580b923330/.config.app_store..My-Testing#L60)

- ass you can see we are working with `format()` by nesting all data from `toml` files as  **.config**. All is converted on the go even with optional path elements. From here is anything possible :)

- Toml conf files will also hold ability for changing different `presets` and it could be used in combination of interface from `app.tray` app.

- in case **git** is not present on user workstation system it will download all required apps and extracted them into app-store as **zip** files from url pointing to `github/.../*-master.zip`. Paths are stored in _.config_ files
</br>
</br>
</br>

> **app.tray**

- allows **user/dev** better interaction with the **avalon/pyblish** `ecosystem`

- it has to be set in `app_store` .conf file and on start is automatically started (if not installed: it will run avalon-core tray icon)

- if avalon-academy is installed menu includes text input where user can get access to help and tutorials

-
