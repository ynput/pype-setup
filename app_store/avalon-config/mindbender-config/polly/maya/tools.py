import sys
import logging

from maya import cmds

from avalon import api, maya
from avalon.vendor import requests
from avalon.vendor.Qt import QtWidgets, QtCore

module = sys.modules[__name__]
module.log = logging.getLogger(__name__)
module.window = None


class _RenderGlobalsEditor(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(_RenderGlobalsEditor, self).__init__(parent)
        self.setWindowTitle(api.Session["AVALON_LABEL"] + " Render Globals")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        pools = QtWidgets.QComboBox()
        groups = QtWidgets.QComboBox()

        button = QtWidgets.QPushButton("Refresh")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Current Pool"))
        layout.addWidget(pools)
        layout.addWidget(QtWidgets.QLabel("Current Group"))
        layout.addWidget(groups)
        layout.addWidget(QtWidgets.QLabel(""))
        layout.addWidget(button)

        self.pools = pools
        self.groups = groups
        self.render_globals = None

        self.resize(300, 100)
        self.setMinimumWidth(200)

        self.refresh()

        button.clicked.connect(self.refresh)
        pools.currentIndexChanged.connect(self.on_pool_changed)
        groups.currentIndexChanged.connect(self.on_group_changed)

    def on_pool_changed(self, index):
        pool = self.pools.itemText(index)
        cmds.setAttr(self.render_globals + ".pool", pool, type="string")

    def on_group_changed(self, index):
        group = self.groups.itemText(index)
        cmds.setAttr(self.render_globals + ".group", group, type="string")

    def refresh(self, *args):
        self.pools.blockSignals(True)
        self.groups.blockSignals(True)
        self.pools.clear()
        self.groups.clear()
        self.pools.blockSignals(False)
        self.groups.blockSignals(False)

        exists = maya.lsattr("id", "avalon.renderglobals")
        assert len(exists) <= 1, (
            "More than one renderglobal exists, this is a bug")

        if exists:
            render_globals = exists[0]
        else:
            render_globals = maya.create(
                "renderGlobals",
                api.Session["AVALON_ASSET"],
                "mindbender.renderglobals"
            )

        # Store reference for editing
        self.render_globals = render_globals

        render_globals = maya.read(render_globals)
        current_pool = render_globals["pool"] or "none"
        current_group = render_globals["group"] or "none"

        url = api.Session["AVALON_DEADLINE"] + "/api/pools"
        module.log.debug("Requesting pools from %s.." % url)
        response = requests.get(url)
        pools = response.json()

        url = api.Session["AVALON_DEADLINE"] + "/api/groups"
        module.log.debug("Requesting groups from %s.." % url)
        response = requests.get(url)
        groups = response.json()

        valid_pool = False
        for index, pool in enumerate(pools):
            self.pools.insertItem(index, pool)

            if pool == current_pool:
                self.pools.setCurrentIndex(index)
                valid_pool = True

        valid_group = False
        for index, group in enumerate(groups):
            self.groups.insertItem(index, group)

            if group == current_group:
                self.groups.setCurrentIndex(index)
                valid_group = True

        if not valid_pool:
            cmds.warning("%s is not a valid pool" % current_pool)

        if not valid_group:
            cmds.warning("%s is not a valid pool" % current_group)


def render_globals_editor(*args):
    parent = {
        widget.objectName(): widget
        for widget in QtWidgets.QApplication.topLevelWidgets()
    }["MayaWindow"]

    # Remember window
    if module.window is not None:
        try:
            return module.window.show()
        except RuntimeError as e:
            if not e.message.rstrip().endswith("already deleted."):
                raise

            # Garbage collected
            module.window = None

    module.window = _RenderGlobalsEditor(parent)
    module.window.show()
