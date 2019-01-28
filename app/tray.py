import os
import sys
import argparse
from pype.ftrack.ftrack_run import FtrackRunner
from app import style
from app.vendor.Qt import QtCore, QtGui, QtWidgets
from avalon import io
from launcher import lib as launcher_lib, launcher_widget
from avalon.tools import libraryloader


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

        # Add Avalon apps submenu
        self.avalon_app = AvalonApps(self.parent, self)
        self.menu.addMenu(self.avalon_app.tray_menu(self.menu))

        # Add Exit action to menu
        aExit = QtWidgets.QAction("Exit", self)
        aExit.triggered.connect(self.exit)
        self.menu.addAction(aExit)
        # Catch activate event
        self.activated.connect(self.on_systray_activated)
        # Add menu to Context of SystemTrayIcon
        self.setContextMenu(self.menu)

    def on_systray_activated(self, reason):
        # show contextMenu if left click
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            # get position of cursor
            position = QtGui.QCursor().pos()
            self.contextMenu().popup(position)

    def exit(self):
        # icon won't stay in tray after exit
        self.hide()
        QtCore.QCoreApplication.exit()


class AvalonApps:
    def __init__(self, main_parent=None, parent=None):

        self.main_parent = main_parent
        self.parent = parent
        self.app_launcher = None

    # Definition of Tray menu
    def tray_menu(self, parent):
        # Menu for Tray App
        menu = QtWidgets.QMenu('Avalon', parent)
        menu.setProperty('submenu', 'on')
        menu.setStyleSheet(style.load_stylesheet())

        # Actions
        avalon_launcher_icon = launcher_lib.resource("icon", "main.png")
        aShowLauncher = QtWidgets.QAction(
            QtGui.QIcon(avalon_launcher_icon), "&Launcher", menu
        )

        aLibraryLoader = QtWidgets.QAction("Library Loader", menu)

        menu.addAction(aShowLauncher)
        menu.addAction(aLibraryLoader)

        aShowLauncher.triggered.connect(self.show_launcher)
        aLibraryLoader.triggered.connect(self.show_library_loader)

        menu = menu

        return menu

    def show_launcher(self):
        # if app_launcher don't exist create it/otherwise only show main window
        if self.app_launcher is None:
            parser = argparse.ArgumentParser()
            parser.add_argument("--demo", action="store_true")
            parser.add_argument(
                "--root", default=os.environ["AVALON_PROJECTS"]
            )
            kwargs = parser.parse_args()

            root = kwargs.root
            root = os.path.realpath(root)
            io.install()
            APP_PATH = launcher_lib.resource("qml", "main.qml")
            self.app_launcher = launcher_widget.Launcher(root, APP_PATH)

        self.app_launcher.window.show()

    def show_library_loader(self):
        libraryloader.show(
            parent=self.main_parent,
            icon=self.parent.icon
        )


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
