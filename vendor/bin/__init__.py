import os
import sys
import importlib


def install():
    '''
    It's assumed that each bin app have __init__.py inside which sets
    neccessary parts for usage. Only import of the package should set
    it up.
    '''
    bin_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(bin_path)
    with os.scandir(bin_path) as bin_folder:
        for entry in bin_folder:
            if not entry.is_dir():
                continue
            # os.path.basename had issues
            name = os.path.split(entry.path)[-1]
            try:
                importlib.import_module(name)
            except Exception:
                pass


install()
