from avalon import maya


class CreateRenderGlobals(maya.Creator):
    """Submit scene to rendering"""

    name = "renderGlobals"
    label = "Render Gloabls"
    family = "mindbender.renderglobals"

    def __init__(self, *args, **kwargs):
        super(CreateRenderGlobals, self).__init__(*args, **kwargs)

        # We won't be publishing this one
        self.data["id"] = "avalon.renderglobals"

        self.data.update({
            "pool": "",
            "group": "",
        })

    def process(self):
        from maya import cmds
        from avalon import maya

        exists = maya.lsattr("id", "avalon.renderglobals")
        assert len(exists) <= 1, (
            "More than one renderglobal exists, this is a bug")

        if exists:
            return cmds.warning("%s already exists." % exists[0])

        super(CreateRenderGlobals, self).process()
