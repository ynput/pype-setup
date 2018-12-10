import os
import sys
from pype.ftrack.ftrack_run import FtrackRunner
from app import style
from app.vendor.Qt import QtCore, QtGui, QtWidgets
from avalon import io

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

        # # TESTING
        # self.app_launcher = None
        # self.menu.addMenu(self.launcher_menu(self.menu))

        # Add Exit action to menu
        aExit = QtWidgets.QAction("Exit", self)
        aExit.triggered.connect(self.exit)
        self.menu.addAction(aExit)

        # Add menu to Context of SystemTrayIcon
        self.setContextMenu(self.menu)

    def exit(self):
        # self.hide()
        QtCore.QCoreApplication.exit()

    # def launcher_menu(self,parent):
    #     self.menu_l = QtWidgets.QMenu('Launcher', parent)
    #     self.menu_l.setProperty('submenu', 'on')
    #     self.menu_l.setStyleSheet(style.load_stylesheet())
    #
    #     self.ac_show_launcher = QtWidgets.QAction("Show Launcher", self.menu_l)
    #     self.ac_show_launcher.triggered.connect(self.show_launcher)
    #
    #     self.menu_l.addAction(self.ac_show_launcher)
    #
    #     return self.menu_l
    #
    # def show_launcher(self):
    #     if self.app_launcher is None:
    #         from launcher import lib, app
    #         import launcher
    #         import argparse
    #         parser = argparse.ArgumentParser()
    #         parser.add_argument("--demo", action="store_true")
    #         parser.add_argument("--root", default=os.environ["AVALON_PROJECTS"])
    #         kwargs = parser.parse_args()
    #
    #         root = kwargs.root
    #         root = os.path.realpath(root)
    #         io.install()
    #         APP_PATH = lib.resource("qml", "main.qml")
    #         self.app_launcher = app.Application(root, APP_PATH)
    #         # self.app_launcher.exec_()
    #         self.app_launcher.window.show()
    #     else:
    #         self.app_launcher.window.show()

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
