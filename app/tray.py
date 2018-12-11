import os
import sys
import argparse
from pype.ftrack.ftrack_run import FtrackRunner
from app import style
from app.vendor.Qt import QtCore, QtGui, QtWidgets
from avalon import io
from launcher import lib as launcher_lib, launcher_widget

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

        # Add Launcher action
        self.app_launcher = None
        self.menu.addAction(self.launcher_menu(self.menu))

        # Add Exit action to menu
        aExit = QtWidgets.QAction("Exit", self)
        aExit.triggered.connect(self.exit)
        self.menu.addAction(aExit)

        # Add menu to Context of SystemTrayIcon
        self.setContextMenu(self.menu)

    def exit(self):
        # icon won't stay in tray after exit
        self.hide()
        QtCore.QCoreApplication.exit()

    def launcher_menu(self,parent):
        icon_path = launcher_lib.resource("icon", "main.png")
        self.ac_show_launcher = QtWidgets.QAction(QtGui.QIcon(icon_path),"&Launcher", parent)
        self.ac_show_launcher.triggered.connect(self.show_launcher)

        return self.ac_show_launcher

    def show_launcher(self):
        # if app_launcher don't exist create it/otherwise only show main window
        if self.app_launcher is None:
            parser = argparse.ArgumentParser()
            parser.add_argument("--demo", action="store_true")
            parser.add_argument("--root", default=os.environ["AVALON_PROJECTS"])
            kwargs = parser.parse_args()

            root = kwargs.root
            root = os.path.realpath(root)
            io.install()
            APP_PATH = launcher_lib.resource("qml", "main.qml")
            self.app_launcher = launcher_widget.Launcher(root, APP_PATH)

            self.app_launcher.window.show()
        else:
            self.app_launcher.window.show()


class Application(QtWidgets.QApplication):
    # Main app where IconSysTray widget is running
    def __init__(self):
        super(Application, self).__init__(sys.argv)
        # Allows to close widgets without exiting app
        self.setQuitOnLastWindowClosed(False)

        self.main_window = QtWidgets.QMainWindow()

        self.trayIcon = SystemTrayIcon(self.main_window)
        self.trayIcon.show()

def main():
    app = Application()
    sys.exit(app.exec_())


if (__name__ == ('__main__')):
    main()
