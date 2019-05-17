import os
import sys


'''
Adds ffmpeg into PATH so it's executable in terminal
'''
current_path = os.path.dirname(os.path.realpath(__file__))
# MacOs - never tested
if sys.platform == 'darwin':
    path_to_bin = os.path.join(current_path, 'darwin')

# Windows
elif sys.platform == 'win32':
    path_to_bin = os.path.join(current_path, 'windows', 'bin')

# Linux
else:
    path_to_bin = os.path.join(current_path, 'linux')

if os.path.exists(path_to_bin):
    os.environ['PATH'] += os.pathsep + path_to_bin
