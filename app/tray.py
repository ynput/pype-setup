import os
import sys
from pype.ftrack.ftrack_run import FtrackRunner
from app import style
from app.vendor.Qt import QtCore, QtGui, QtWidgets


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):

        pype_setup = os.getenv('PYPE_SETUP_ROOT')
        items = [pype_setup, "app", "resources", "icon.png"]
        fname = os.path.sep.join(items)
        self.icon = QtGui.QIcon(fname)

        QtWidgets.QSystemTrayIcon.__init__(self, self.icon, parent)

        # Store parent - QtWidgets.QMainWindow()
        self.parent = parent

        # Setup menu in Tray
        self.menu = QtWidgets.QMenu()
        self.menu.setStyleSheet(style.load_stylesheet())

        # Add ftrack menu
        if os.environ.get('FTRACK_SERVER') is not None:
            self.ftrack = FtrackRunner(self.parent, self)
            self.menu.addMenu(self.ftrack.trayMenu(self.menu))
            self.ftrack.validate()

        # Add Exit action to menu
        aExit = QtWidgets.QAction("Exit", self)
        aExit.triggered.connect(self.exit)
        self.menu.addAction(aExit)

        # Add menu to Context of SystemTrayIcon
        self.setContextMenu(self.menu)

    def exit(self):
        QtCore.QCoreApplication.exit()


def _sys_tray():
    app = QtWidgets.QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(True)
    w = QtWidgets.QMainWindow()
    # w = QtWidgets.QWidget()
    trayIcon = SystemTrayIcon(w)
    trayIcon.show()
    sys.exit(app.exec_())


if (__name__ == ('__main__')):
    _sys_tray()
