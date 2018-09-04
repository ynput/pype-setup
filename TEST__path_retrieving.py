import os
import platform
import sys

# sets main running session environmnent
# and define .config preset
properities = {
    'platform': platform.system().lower(),
    'tray_icon': {'path': '{root}/resources/icon/main.png'},
    'version': "",
    'root': os.path.dirname(os.path.realpath(__file__)),
    'packages': ['{root}', '{root}/python/__DEV__/Qt5', '{root}/app/vendor', ],
    'preset': "My-Testing"
}


def set_pth_modules(p):
    # will go trough all values and convert namespaces into paths
    for k, v in p.items():
        if isinstance(v, list):
            for i in v:
                path = os.path.normpath(i.format(**p))
                # print(path)
                sys.path.append(path)
        if isinstance(v, dict):
            for vk, vv in v.items():
                v[vk] = vv.format(**p)


def main():
    # adding paths into sys.path before _app_ can be imported
    set_pth_modules(properities)

    import app
    # adding and formating data from .confs.toml into properities dict of
    # app.__init__.
    app.init(properities)
    # print(app.cfg, sep=' ', end='n', file=sys.stdout, flush=False)
    # for a in app.cfg.app_store.avalon:
    #     print(a.path)
    #     try:
    #         print(a.qt)
    #     except:
    #         pass
    app.tray._sys_tray(os.path.normpath(app.cfg.tray_icon.path))


if __name__ == '__main__':
    main()
