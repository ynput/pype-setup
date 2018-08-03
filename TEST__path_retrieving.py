
import os
import platform
import sys


properities = {
    'platform': platform.system().lower(),
    'version': "2018v2",
    'root': os.path.dirname(os.path.realpath(__file__)),
    'packages': {"app_root": '{root}', "none": '{root}/app/vendor'},
    'preset': "My-Testing"
}


def set_pth_modules(properities):
    for k, v in properities.items():
        if isinstance(v, dict):
            for vk, vv in v.items():
                path = os.path.normpath(vv.format(**properities))
                sys.path.append(path)


def main():
    set_pth_modules(properities)
    import app
    Conf = app.tools.create_paths.get_paths(properities)

    # Conf.app_store.path = Conf.app_store.path.format(**Conf)
    for k, v in Conf.sys.items():
        print(k, v)


if __name__ == '__main__':
    main()
