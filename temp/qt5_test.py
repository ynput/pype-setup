# this snippet was modified from `pyblish_qml/ipc/server.py  Server.__init__`
import os
import subprocess

environ = {
    key: os.getenv(key)
    for key in ("SYSTEMROOT", "PYTHONPATH", "PATH")
    if os.getenv(key)
}

# this was set by launcher
pyqt5 = os.getenv("PYBLISH_QML_PYQT5")

# put pyqt5 into PYTHONPATH
environ["PYTHONPATH"] = os.pathsep.join(
    path for path in [os.getenv("PYTHONPATH"), pyqt5]
    if path is not None
)

kwargs = dict(args=[
    "python", "-c", "from PyQt5 import QtCore;print(QtCore.__file__)"],
    env=environ,  # got NO error if comment out this line
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
result = subprocess.Popen(**kwargs).communicate()
print(result[0])
