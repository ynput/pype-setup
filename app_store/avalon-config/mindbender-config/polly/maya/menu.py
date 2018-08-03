import sys
from maya import cmds

from avalon import api
from avalon.vendor.Qt import QtCore

self = sys.modules[__name__]
self._menu = api.Session["AVALON_LABEL"] + "menu"


def install():
    from . import interactive, tools

    def deferred():
        # Append to Avalon's menu
        cmds.menuItem(divider=True)

        # Modeling sub-menu
        cmds.menuItem("Modeling",
                      label="Modeling",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Combine", command=interactive.combine)

        # Rigging sub-menu
        cmds.menuItem("Rigging",
                      label="Rigging",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Auto Connect", command=interactive.auto_connect)
        cmds.menuItem("Clone (Local)", command=interactive.clone_localspace)
        cmds.menuItem("Clone (World)", command=interactive.clone_worldspace)
        cmds.menuItem("Clone (Special)", command=interactive.clone_special)
        cmds.menuItem("Create Follicle", command=interactive.follicle)

        # Animation sub-menu
        cmds.menuItem("Animation",
                      label="Animation",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Set Defaults", command=interactive.set_defaults)

        # Rendering sub-menu
        cmds.menuItem("Rendering",
                      label="Rendering",
                      tearOff=True,
                      subMenu=True,
                      parent=self._menu)

        cmds.menuItem("Edit Render Globals",
                      command=tools.render_globals_editor)

        cmds.setParent("..", menu=True)

        cmds.menuItem(divider=True)

        cmds.menuItem("Auto Connect", command=interactive.auto_connect_assets)

    # Allow time for uninstallation to finish.
    QtCore.QTimer.singleShot(200, deferred)


def uninstall():
    pass
