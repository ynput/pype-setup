import pyblish.api


class AvalonProtectScene(pyblish.api.ContextPlugin):
    """Prevent accidental overwrite of original scene once published"""

    label = "Protect Scene"
    order = pyblish.api.IntegratorOrder + 0.5
    optional = True

    def process(self, context):
        from maya import cmds

        cmds.file(save=True, force=True)
        cmds.file(renameToSave=True)
