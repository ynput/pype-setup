import pyblish.api


class ValidateMindbenderProtectedScene(pyblish.api.ContextPlugin):
    """Guard against publishing a scene that has already been published"""

    label = "Protected Scene"
    order = pyblish.api.ValidatorOrder
    hosts = ["maya"]
    optional = True

    def process(self, context):
        from maya import cmds
        assert not cmds.file(renameToSave=True, query=True), (
            "This file is protected, please save scene under a new name"
        )
