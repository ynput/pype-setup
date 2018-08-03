import pyblish.api


class CollectAvalonTime(pyblish.api.ContextPlugin):
    """Store global time at the time of publish"""

    label = "Time"
    order = pyblish.api.CollectorOrder

    def process(self, context):
        from avalon import api
        context.data["time"] = api.time()
