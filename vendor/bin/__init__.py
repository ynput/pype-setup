import os
import sys
import importlib


current_path = os.path.realpath(__file__)


def install_ffmpeg():
    '''
    Adds ffmpeg into PATH so it's executable in terminal
    '''
    ffmpeg_path = os.path.join(current_path, 'ffmpeg_exec')
    # MacOs - never tested
    if sys.platform == 'darwin':
        path_to_bin = os.path.sep.join([ffmpeg_path, 'darwin'])

    # Windows
    elif sys.platform == 'win32':
        path_to_bin = os.path.sep.join([ffmpeg_path, 'windows', 'bin'])

    # Linux
    else:
        path_to_bin = os.path.sep.join([ffmpeg_path, 'linux'])

    if os.path.exists(path_to_bin):
        os.environ['PATH'] += os.pathsep + path_to_bin


def install():
    install_ffmpeg()


install()
