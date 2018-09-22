# https://pyblish.gitbooks.io/developer-guide/content/setting_up.html
# https://legacy.gitbook.com/book/pyblish/developer-guide/details

# api.register_python_executable(r"C:\Users\Public\avalon_env\python.exe")
# api.register_pyqt5(r"C:\Users\Public\avalon_env\lib\site-packages\PyQt5")
from PyQt5.QtCore import PYQT_VERSION_STR as version
print(version)
from pyblish_qml import api, show
show(modal=True)
