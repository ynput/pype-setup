
import os
import platform
import sys


properities = {
    'platform': platform.system().lower(),
    'version': "2018v2",
    'root': os.path.dirname(os.path.realpath(__file__)),
    'packages': ['{root}', '{root}/python/__DEV__/Qt5', '{root}/app/vendor', ],
    'preset': "My-Testing"
}


def set_pth_modules(properities):
    for k, v in properities.items():
        if isinstance(v, list):
            for i in v:
                path = os.path.normpath(i.format(**properities))
                print(path)
                sys.path.append(path)


def main():
    set_pth_modules(properities)
    print(sys.path)
    import app
    import app.tray as tray
    #
    tray._sys_tray(os.path.normpath("{root}/resources/icon/main.png".format(**properities)))

    Conf = app.tools.create_paths.get_paths(properities)

    Conf.app_store.path = Conf.app_store.path.format(**Conf)
    for k, v in Conf.app_store.items():
        print(k, v)


if __name__ == '__main__':
    main()
