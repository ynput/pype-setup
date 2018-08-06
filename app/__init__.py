import os
import platform


from .tools import *
from .tray import *


def init(_dict=dict()):
    global cfg
    cfg = dict()
    cfg = create_paths.get_paths(_dict)


def __set_pth_modules(_dict=dict()):
    for k, v in _dict.items():
        if isinstance(v, list):
            for i in v:
                path = os.path.normpath(i.format(**_dict))
                # print(path)
                sys.path.append(path)
        if isinstance(v, dict):
            for vk, vv in v.items():
                v[vk] = vv.format(**_dict)


if __name__ == '__main__':
    properities = {
        'platform': platform.system().lower(),
        'tray_icon': {'path': '{root}/resources/icon/main.png'},
        'version': "",
        'root': os.path.dirname(os.path.realpath(__file__)),
        'packages': ['{root}', '{root}/python/__DEV__/Qt5', '{root}/app/vendor', ],
        'preset': "My-Testing"
    }
    __set_pth_modules(properities)
    init(properities)
