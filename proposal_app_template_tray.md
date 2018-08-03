# Proposal: **avalon-app/app-store** system, **avalon-tray**

> **avalon-app** and **app_store**

- the app will `globalize` environment for `stand-alone `or [`[conf.bin.{app}]`]() related processes
- we will install the app to the system we are working on and by [`[{avalon-app.root.path}/.config.app..My_config_preset]`]() all will be
set to the **user/dev **environment
- `avalon-core`, `pyblish-base` is installed by default and rest of `packages` (apps) in [`[{app_store.path}/{avalon.maya.path}]`]()
- ass you can see we are working with `format()` by nesting all data from `toml` files as  **.config**. All is converted on the go. From here is anything possible :)
- Toml conf files will also hold ability for changing different `presets` and it could be used
in combination of interface from `avalon-tray` **app**.

> **avalon-tray**

- allows **user/dev** better interaction with the **avalon/pyblish** `ecosystem`
- it has to be set in `app_store` .conf file and on start is automatically started (if not installed: it will run avalon-core tray icon)

```python
#the menu structure:
{'Install avalon plugins': "action",
    'Plugins': {
        'Avalon Core': [
            'Config core',
            'Create new project',
            None,
            'Save database',
            ],
        '&Avalon Users': [
            'Config User',
            'Cre&ate new user',
            ],
        'Avalon Workfiles': [
            'Config Workfiles',
            ],
        'Pyblish': [
            'Config Pyblish',
            'Create new micro-plugin',
            None,
            'Micro-plugins manager'
            ],
        'Pipeline': [
            'Config pipeline',
            'Create new template',
            None,
            'Templates manager'
            ],
        'CG-wire': [
            'Config CG-wire',
            None,
            'Pull database',
            'Push database'
            ]

        },
    'Minimalize': "action",
    #'Close': "action"
    }

```
- there is a git repository you can try yourself. It looks like this:
