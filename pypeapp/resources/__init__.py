import os


resource_path = os.path.dirname(__file__)


def get_resource(*args):
    return os.path.normpath(os.path.join(resource_path, *args))
