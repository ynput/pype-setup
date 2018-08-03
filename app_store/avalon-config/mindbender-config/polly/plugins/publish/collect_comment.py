import pyblish.api


class CollectAvalonComment(pyblish.api.ContextPlugin):
    """This plug-ins displays the comment dialog box per default"""

    label = "Comment"
    order = pyblish.api.CollectorOrder

    def process(self, context):
        context.data["comment"] = ""
