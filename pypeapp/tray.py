import os
import sys
from pypeapp import style, Logger
from Qt import QtCore, QtGui, QtWidgets
from pypeapp.lib.config import get_presets


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        # TODO: Better way to get icon
        pathname = os.path.dirname(sys.argv[0])
        items = [pathname, "resources", "icon.png"]
        self.icon = QtGui.QIcon(os.path.sep.join(items))

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
        # icon won't stay in tray after exit
        self.hide()
        QtCore.QCoreApplication.exit()


class TrayManager:
    modules = {}
    errors = []
    items = get_presets().get('tray', {}).get('menu_items', [])
    available_sourcetypes = ['python', 'file']
    def __init__(self, tray_widget, main_window):
        self.tray_widget = tray_widget
        self.main_window = main_window
        self.log = Logger().get_logger(self.__class__.__name__)

    def process_presets(self):
        self.process_items(self.items, self.tray_widget.menu)

        # Add Exit action to menu
        aExit = QtWidgets.QAction("&Exit", self.tray_widget)
        aExit.triggered.connect(self.tray_widget.exit)
        self.tray_widget.menu.addAction(aExit)

    def process_items(self, items, parent_menu):
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
        import_path = item.get('import_path', None)
        title = item.get('title', import_path)
        fromlist = item.get('fromlist', [])
        try:
            module = __import__(
                "{}".format(import_path),
                fromlist=fromlist
            )
            self.modules[title] = module.tray_init(
                self.tray_widget, self.main_window, parent_menu
            )
        except ImportError as ie:
            self.log.warning(
                "{} - Module import Error: {}".format(title, str(ie))
            )
            return False
        return True

    def add_action(self, item, parent_menu):
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
        try:
            parent_menu.addSeparator()
            return True
        except Exception:
            return False


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
