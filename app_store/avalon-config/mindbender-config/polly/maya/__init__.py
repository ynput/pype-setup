import os
import uuid

from maya import cmds

from avalon import maya, api as avalon
from pyblish import api as pyblish

from . import menu

PARENT_DIR = os.path.dirname(__file__)
PACKAGE_DIR = os.path.dirname(PARENT_DIR)
PLUGINS_DIR = os.path.join(PACKAGE_DIR, "plugins")

PUBLISH_PATH = os.path.join(PLUGINS_DIR, "maya", "publish")
LOAD_PATH = os.path.join(PLUGINS_DIR, "maya", "load")
CREATE_PATH = os.path.join(PLUGINS_DIR, "maya", "create")


def install():
    pyblish.register_plugin_path(PUBLISH_PATH)
    avalon.register_plugin_path(avalon.Loader, LOAD_PATH)
    avalon.register_plugin_path(avalon.Creator, CREATE_PATH)

    menu.install()

    avalon.on("init", on_init)
    avalon.on("new", on_new)
    avalon.on("save", on_save)


def uninstall():
    pyblish.deregister_plugin_path(PUBLISH_PATH)
    avalon.deregister_plugin_path(avalon.Loader, LOAD_PATH)
    avalon.deregister_plugin_path(avalon.Creator, CREATE_PATH)

    menu.uninstall()


def _set_uuid(node):
    """Add mbID to `node`

    Unless one already exists.

    """

    attr = "{0}.mbID".format(node)

    if not cmds.objExists(attr):
        cmds.addAttr(node, longName="mbID", dataType="string")
        _, uid = str(uuid.uuid4()).rsplit("-", 1)
        cmds.setAttr(attr, uid, type="string")


def on_init():
    avalon.logger.info("Running callback on init..")

    maya.commands.reset_frame_range()
    maya.commands.reset_resolution()


def on_new():
    avalon.logger.info("Running callback on new..")

    # Load dependencies
    cmds.loadPlugin("AbcExport.mll", quiet=True)
    cmds.loadPlugin("AbcImport.mll", quiet=True)

    maya.commands.reset_frame_range()
    maya.commands.reset_resolution()


def on_save():
    """Automatically add IDs to new nodes

    Any transform of a mesh, without an exising ID,
    is given one automatically on file save.

    """

    avalon.logger.info("Running callback on save..")

    nodes = (set(cmds.ls(type="mesh", long=True)) -
             set(cmds.ls(long=True, readOnly=True)) -
             set(cmds.ls(long=True, lockedNodes=True)))

    transforms = cmds.listRelatives(list(nodes), parent=True) or list()

    # Add unique identifiers
    for node in transforms:
        _set_uuid(node)
