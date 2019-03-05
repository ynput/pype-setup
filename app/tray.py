import os
import sys
import argparse
import psutil
from app import style
from app.vendor.Qt import QtCore, QtGui, QtWidgets
from avalon import io
from launcher import lib as launcher_lib, launcher_widget
from avalon.tools import libraryloader
from pype.lib import set_io_database


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, app, parent=None):
        pype_setup = os.getenv('PYPE_SETUP_ROOT')
        items = [pype_setup, "app", "resources", "icon.png"]
        fname = os.path.sep.join(items)
        self.icon = QtGui.QIcon(fname)

        QtWidgets.QSystemTrayIcon.__init__(self, self.icon, parent)

        # Store parent - QtWidgets.QMainWindow()
        self.parent = parent
        self.app = app

        # Setup menu in Tray
        self.menu = QtWidgets.QMenu()
        self.menu.setStyleSheet(style.load_stylesheet())

        self.try_connect()

        # Catch activate event
        self.activated.connect(self.on_systray_activated)
        # Add menu to Context of SystemTrayIcon
        self.setContextMenu(self.menu)

    def set_menu(self):
        self.menu.clear()
        if self.db_connected:
            # Add ftrack menu
            if os.environ.get('FTRACK_SERVER') is not None:
                from pype.ftrack.ftrack_run import FtrackRunner
                self.ftrack = FtrackRunner(self.parent, self)
                self.menu.addMenu(self.ftrack.trayMenu(self.menu))
                self.ftrack.validate()

            os.environ['CLOCKIFY_WORKSPACE'] = 'PypeTimer'
            if os.environ.get('CLOCKIFY_WORKSPACE', None) is not None:
                from pype.clockify import ClockifyModule
                self.clockify = ClockifyModule(self.parent, self)
                self.menu.addMenu(self.clockify.tray_menu(self.menu))
                self.clockify.start_up()
            # Add Avalon apps submenu
            self.avalon_app = AvalonApps(self.parent, self)
            self.avalon_app.tray_menu(self.menu)
        else:
            aTryAgain = QtWidgets.QAction("Try again", self)
            aTryAgain.triggered.connect(self.try_connect)
            self.menu.addAction(aTryAgain)
            msg_title = 'Can\'t connect to Database!'
            msg = (
                'Please contact your Administrator, Supervisor or Coordinator'
            )
            title = 'DB connection error'
            self.show_error(msg, title, msg_title)

        # Add Exit action to menu
        aExit = QtWidgets.QAction("Exit", self)
        aExit.triggered.connect(self.exit)
        self.menu.addAction(aExit)

    def show_error(self, msg, title, msg_title=None):
        error_msg = QtWidgets.QMessageBox(self.parent)
        error_msg.setWindowIcon(self.icon)
        error_msg.setStyleSheet(style.load_stylesheet())
        error_msg.setIcon(QtWidgets.QMessageBox.Critical)
        if msg_title is None:
            error_msg.setText(msg)
        else:
            error_msg.setText(msg_title)
            error_msg.setInformativeText(msg)
        error_msg.setWindowTitle(title)
        d_height = self.app.desktop().screen().rect().height()
        d_width = self.app.desktop().screen().rect().width()
        em_height = error_msg.rect().height()
        em_width = error_msg.rect().width()
        ax = d_width/2-em_width/2*3
        ay = d_height/2-em_height/2*3
        error_msg.move(ax, ay)
        error_msg.show()

    def try_connect(self):
        # Try connect to DB
        self.db_connected = True
        try:
            set_io_database()
        except IOError:
            self.db_connected = False

        self.set_menu()

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
    from app.api import Logger
    log = Logger.getLogger(__name__)

    def __init__(self, main_parent=None, parent=None):

        self.main_parent = main_parent
        self.parent = parent
        self.app_launcher = None

    # Definition of Tray menu
    def tray_menu(self, parent_menu=None):
        # Actions
        if parent_menu is None:
            if self.parent is None:
                self.log.warning('Parent menu is not set')
                return
            elif self.parent.hasattr('menu'):
                parent_menu = self.parent.menu
            else:
                self.log.warning('Parent menu is not set')
                return

        avalon_launcher_icon = launcher_lib.resource("icon", "main.png")
        aShowLauncher = QtWidgets.QAction(
            QtGui.QIcon(avalon_launcher_icon), "&Launcher", parent_menu
        )

        aLibraryLoader = QtWidgets.QAction("Library", parent_menu)

        parent_menu.addAction(aShowLauncher)
        parent_menu.addAction(aLibraryLoader)

        aShowLauncher.triggered.connect(self.show_launcher)
        aLibraryLoader.triggered.connect(self.show_library_loader)

        return

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
            icon=self.parent.icon,
            show_projects=True,
            show_libraries=True
        )


class Application(QtWidgets.QApplication):
    # Main app where IconSysTray widget is running
    def __init__(self):
        super(Application, self).__init__(sys.argv)

        pype_setup = os.getenv('PYPE_SETUP_ROOT')
        items = [pype_setup, "app", "resources", "splash.png"]

        # Create and display the splash screen
        splash_pix = QtGui.QPixmap(os.path.sep.join(items))
        splash = QtWidgets.QSplashScreen(
            splash_pix, QtCore.Qt.WindowStaysOnTopHint
        )
        splash.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )
        splash.setEnabled(False)

        splash.setMask(splash_pix.mask())
        splash.show()

        # Terminate powershell that runs this script
        powershell_procs = [p for p in psutil.process_iter() if (
            'powershell.exe' in p.name() and
            '--tray' in p.cmdline()
        )]
        if len(powershell_procs) > 0:
            for running_proc in powershell_procs:
                running_proc.terminate()
        self.processEvents()

        # Allows to close widgets without exiting app
        self.setQuitOnLastWindowClosed(False)

        self.main_window = QtWidgets.QMainWindow()

        self.trayIcon = SystemTrayIcon(self, self.main_window)
        self.trayIcon.show()

        splash.finish(self.main_window)


def main():
    app = Application()
    sys.exit(app.exec_())


if (__name__ == ('__main__')):
    main()
