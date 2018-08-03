import pyblish.api


class CollectMindbenderMayaRenderlayers(pyblish.api.ContextPlugin):
    """Gather instances by active render layers"""

    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    label = "Render Layers"

    def process(self, context):
        from maya import cmds

        def render_global(attr):
            return cmds.getAttr("defaultRenderGlobals." + attr)

        for layer in cmds.ls(type="renderLayer"):
            if layer.endswith("defaultRenderLayer"):
                continue

            data = {
                "family": "Render Layers",
                "families": ["mindbender.renderlayer"],
                "publish": cmds.getAttr(layer + ".renderable"),
                "startFrame": render_global("startFrame"),
                "endFrame": render_global("endFrame"),
                "byFrameStep": render_global("byFrameStep"),
                "renderer": render_global("currentRenderer")
            }

            # Apply each user defined attribute as data
            for attr in cmds.listAttr(layer, userDefined=True) or list():
                try:
                    value = cmds.getAttr(layer + "." + attr)
                except Exception:
                    # Some attributes cannot be read directly,
                    # such as mesh and color attributes. These
                    # are considered non-essential to this
                    # particular publishing pipeline.
                    value = None

                data[attr] = value

            instance = context.create_instance(data.get("name", layer))
            instance.data.update(data)
