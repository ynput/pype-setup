import os
import sys
import time
from pypeapp import style, Logger
from Qt import QtCore, QtGui, QtWidgets
from pypeapp.lib.config import get_presets
from pypeapp.resources import get_resource


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    """Tray widget.

    :param parent: Main widget that cares about all GUIs
    :type parent: QtWidgets.QMainWindow
    """
    def __init__(self, parent):
        self.icon = QtGui.QIcon(get_resource('icon.png'))

        QtWidgets.QSystemTrayIcon.__init__(self, self.icon, parent)

        # Store parent - QtWidgets.QMainWindow()
        self.parent = parent

        # Setup menu in Tray
        self.menu = QtWidgets.QMenu()
        self.menu.setStyleSheet(style.load_stylesheet())

        # Set modules
        self.tray_man = TrayManager(self, self.parent)
        self.tray_man.process_presets()

        # Catch activate event
        self.activated.connect(self.on_systray_activated)
        # Add menu to Context of SystemTrayIcon
        self.setContextMenu(self.menu)

    def on_systray_activated(self, reason):
        # show contextMenu if left click
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            position = QtGui.QCursor().pos()
            self.contextMenu().popup(position)

    def exit(self):
        """ Exit whole application.

        - Icon won't stay in tray after exit.
        """
        self.hide()
        QtCore.QCoreApplication.exit()


class TrayManager:
    """Cares about context of application.

    Load submenus, actions, separators and modules into tray's context.
    """
    modules = {}
    services = {}
    services_submenu = None

    errors = []
    items = get_presets().get('tray', {}).get('menu_items', [])
    available_sourcetypes = ['python', 'file']

    def __init__(self, tray_widget, main_window):
        self.tray_widget = tray_widget
        self.main_window = main_window
        self.log = Logger().get_logger(self.__class__.__name__)

        self.icon_run = QtGui.QIcon(get_resource('circle_green.png'))
        self.icon_stay = QtGui.QIcon(get_resource('circle_orange.png'))
        self.icon_failed = QtGui.QIcon(get_resource('circle_red.png'))

        self.services_thread = None

    def process_presets(self):
        """Start up method for TrayManager
        """
        self.process_items(self.items, self.tray_widget.menu)
        # Add services if they are
        if self.services_submenu is not None:
            self.tray_widget.menu.addMenu(self.services_submenu)
            self.services_thread = ServicesThread(self)
            self.services_thread.start()
        # Add separator
        self.add_separator(self.tray_widget.menu)
        # Add Exit action to menu
        aExit = QtWidgets.QAction("&Exit", self.tray_widget)
        aExit.triggered.connect(self.tray_widget.exit)
        self.tray_widget.menu.addAction(aExit)
        # Tell each module which modules were imported
        self.connect_modules()

    def process_items(self, items, parent_menu):
        """ Loop through items and add them to parent_menu.

        :param items: contains dictionary objects representing each item
        :type items: list
        :param parent_menu: menu where items will be add
        :type parent_menu: QtWidgets.QMenu
        """
        for item in items:
            i_type = item.get('type', None)
            result = False
            if i_type is None:
                continue
            elif i_type == 'module':
                result = self.add_module(item, parent_menu)
            elif i_type == 'action':
                result = self.add_action(item, parent_menu)
            elif i_type == 'menu':
                result = self.add_menu(item, parent_menu)
            elif i_type == 'separator':
                result = self.add_separator(parent_menu)

            if result is False:
                self.errors.append(item)

    def add_module(self, item, parent_menu):
        """Inicialize object of module and add it to context.

        :param item: item from presets containing information about module
        :type item: dict
        :param parent_menu: menu where module's submenus/actions will be add
        :type parent_menu: QtWidgets.QMenu
        :returns: success of module implementation
        :rtype: bool

        REQUIRED KEYS (item):
            :import_path (*str*):
                - full import path as python's import
                - e.g. *"path.to.module"*
            :fromlist (*list*):
                - subparts of import_path (as from is used)
                - e.g. *["path", "to"]*
        OPTIONAL KEYS (item):
            :title (*str*):
                - represents label shown in services menu
                - import_path is used if title is not set
                - title is not used at all if module is not a service
        .. note::
            Module is added as **service** if object does not have
            *tray_menu* method.
        """
        import_path = item.get('import_path', None)
        title = item.get('title', import_path)
        fromlist = item.get('fromlist', [])
        try:
            module = __import__(
                "{}".format(import_path),
                fromlist=fromlist
            )
            obj = module.tray_init(self.tray_widget, self.main_window)
            name = obj.__class__.__name__
            if hasattr(obj, 'tray_menu'):
                obj.tray_menu(parent_menu)
            else:
                if self.services_submenu is None:
                    self.services_submenu = QtWidgets.QMenu(
                        'Services', self.tray_widget.menu
                    )
                action = QtWidgets.QAction(title, self.services_submenu)
                self.services_submenu.addAction(action)
                self.services[name] = action
            self.modules[name] = obj
            self.log.info("{} - Module imported".format(title))
        except ImportError as ie:
            self.log.warning(
                "{} - Module import Error: {}".format(title, str(ie))
            )
            return False
        return True

    def add_action(self, item, parent_menu):
        """Adds action to parent_menu.

        :param item: item from presets containing information about action
        :type item: dictionary
        :param parent_menu: menu where action will be added
        :type parent_menu: QtWidgets.QMenu
        :returns: success of adding item to parent_menu
        :rtype: bool

        REQUIRED KEYS (item):
            :title (*str*):
                - represents label shown in menu
            :sourcetype (*str*):
                - type of action *enum["file", "python"]*
            :command (*str*):
                - filepath to script *(sourcetype=="file")*
                - python code as string *(sourcetype=="python")*
        OPTIONAL KEYS (item):
            :tooltip (*str*):
                - will be shown when hover over action
        """
        sourcetype = item.get('sourcetype', None)
        command = item.get('command', None)
        title = item.get('title', '*ERROR*')
        tooltip = item.get('tooltip', None)

        if sourcetype not in self.available_sourcetypes:
            self.log.error('item "{}" has invalid sourcetype'.format(title))
            return False
        if command is None or command.strip() == '':
            self.log.error('item "{}" has invalid command'.format(title))
            return False

        new_action = QtWidgets.QAction(title, parent_menu)
        if tooltip is not None and tooltip.strip() != '':
            new_action.setToolTip(tooltip)

        if sourcetype == 'python':
            new_action.triggered.connect(
                lambda: exec(command)
            )
        elif sourcetype == 'file':
            command = os.path.normpath(command)
            if '$' in command:
                command_items = command.split(os.path.sep)
                for i in range(len(command_items)):
                    if command_items[i].startswith('$'):
                        # TODO: raise error if environment was not found?
                        command_items[i] = os.environ.get(
                            command_items[i].replace('$', ''), command_items[i]
                        )
                command = os.path.sep.join(command_items)

            new_action.triggered.connect(
                lambda: exec(open(command).read(), globals())
            )

        parent_menu.addAction(new_action)

    def add_menu(self, item, parent_menu):
        """ Adds submenu to parent_menu.

        :param item: item from presets containing information about menu
        :type item: dictionary
        :param parent_menu: menu where submenu will be added
        :type parent_menu: QtWidgets.QMenu
        :returns: success of adding item to parent_menu
        :rtype: bool

        REQUIRED KEYS (item):
            :title (*str*):
                - represents label shown in menu
            :items (*list*):
                - list of submenus / actions / separators / modules *(dict)*
        """
        try:
            title = item.get('title', None)
            if title is None or title.strip() == '':
                self.log.error('Missing title in menu from presets')
                return False
            new_menu = QtWidgets.QMenu(title, parent_menu)
            new_menu.setProperty('submenu', 'on')
            parent_menu.addMenu(new_menu)

            self.process_items(item.get('items', []), new_menu)
            return True
        except Exception:
            return False

    def add_separator(self, parent_menu):
        """ Adds separator to parent_menu.

        :param parent_menu: menu where submenu will be added
        :type parent_menu: QtWidgets.QMenu
        :returns: success of adding item to parent_menu
        :rtype: bool
        """
        try:
            parent_menu.addSeparator()
            return True
        except Exception:
            return False

    def connect_modules(self):
        """Sends all imported modules to imported modules
        which have process_modules method.
        """
        for name, obj in self.modules.items():
            if hasattr(obj, 'process_modules'):
                obj.process_modules(self.modules)

    def check_services_status(self):
        """Check services activity.

        *Changing service's icon based on service activity.*
        """
        for service, action in self.services.items():
            obj = self.modules[service]
            # TODO: how to recognize that service failed?
            if not obj:
                action.setIcon(self.icon_failed)
            if obj.is_running:
                action.setIcon(self.icon_run)
            else:
                action.setIcon(self.icon_stay)


class ServicesThread(QtCore.QThread):
    """Triggers checking services activity in manager every 3 sec.

    :param manager: object where check will be triggered
    :type manager: TrayManager
    """
    def __init__(self, manager):
        QtCore.QThread.__init__(self)
        self.manager = manager
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        while self.is_running:
            self.manager.check_services_status()
            time.sleep(3)


class TrayMainWindow(QtWidgets.QMainWindow):
    """Modified MainWindow with ability to show splash.

    :param app: Qt app that hold all Qt widgets
    :type app: QtWidgets.QApplication
    """
    def __init__(self, app):
        super().__init__()
        self.app = app
        splash_pix = QtGui.QPixmap(get_resource('splash.png'))
        self.splash = QtWidgets.QSplashScreen(
            splash_pix, QtCore.Qt.WindowStaysOnTopHint
        )
        self.splash.setMask(splash_pix.mask())
        self.splash.setEnabled(False)
        self.splash.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )

    def show_splash(self):
        self.splash.show()
        self.app.processEvents()

    def hide_splash(self):
        self.splash.hide()


class Application(QtWidgets.QApplication):
    """Main Qt application almost all pipeline widgets are running underneath.

    .. note::
        Contains *main_window* which should be used as parent for showing GUIs.
    """
    def __init__(self):
        super(Application, self).__init__(sys.argv)
        # Allows to close widgets without exiting app
        self.setQuitOnLastWindowClosed(False)

        self.main_window = TrayMainWindow(self)
        self.main_window.show_splash()

        self.trayIcon = SystemTrayIcon(self.main_window)
        self.trayIcon.show()

        self.main_window.hide_splash()


def main():
    app = Application()
    sys.exit(app.exec_())


if (__name__ == ('__main__')):
    main()
