# Proposal: **avalon-app/app-store** system, **avalon-tray**

> **avalon-app** and **app_store**

- the app will globalize the avalon environment for _stand-alone_ or any installed application in **.config file** [`[conf.bin.{app}]`](https://github.com/jezscha/avalon-app/blob/682469d31b98510f6f6efb2b247f8550e445d105/.config.app_store..My-Testing#L18) related processes
- we will install the app to the system we are working on and by [`[{avalon-app.root.path}/.config.app..My_config_preset]`](https://github.com/jezscha/avalon-app/blob/master/.config.app..My-Testing) all will be
set to the **user/dev **environment
- `avalon-core`, `pyblish-base` is installed in [.config.app..My-Testing](https://github.com/jezscha/avalon-app/blob/master/.config.app..My-Testing) by default and rest of `packages` (apps) in [`[{app_store.path}/{avalon.maya.path}]`](https://github.com/jezscha/avalon-app/blob/a1f29e8de57fafe5edf8f4a8ba0a42eb171c7920/.config.app_store..My-Testing#L34)
- ass you can see we are working with `format()` by nesting all data from `toml` files as  **.config**. All is converted on the go even with optional path elements. From here is anything possible :)
- Toml conf files will also hold ability for changing different `presets` and it could be used
in combination of interface from `avalon-tray` app.
- all required apps are downloaded and extracted into app-store as **zip** files from url pointing to `github/.../*-master.zip`. Git and pip are not usable as they have to be installed on user's os.
</br>
</br>
</br>

> **avalon-tray**

- allows **user/dev** better interaction with the **avalon/pyblish** `ecosystem`
- it has to be set in `app_store` .conf file and on start is automatically started (if not installed: it will run avalon-core tray icon)
- if avalon-academy is installed menu includes text input where user can get access to help and tutorials

- there is a git repository you can try yourself. It looks like this:
