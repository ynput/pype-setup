import pyblish.api


class CollectMindbenderImageSequences(pyblish.api.ContextPlugin):
    """Gather image sequnences from working directory"""

    order = pyblish.api.CollectorOrder
    hosts = ["shell"]
    label = "Image Sequences"

    def process(self, context):
        import os
        from avalon.vendor import clique

        workspace = context.data["workspaceDir"]

        base, dirs, _ = next(os.walk(workspace))
        for renderlayer in dirs:
            abspath = os.path.join(base, renderlayer)
            files = os.listdir(abspath)
            collections, remainder = clique.assemble(files, minimum_items=1)
            assert not remainder, (
                "There shouldn't have been a remainder for '%s': "
                "%s" % (renderlayer, remainder))

            for collection in collections:
                instance = context.create_instance(str(collection))

                data = {
                    "family": "Image Sequences",
                    "families": ["mindbender.imagesequence"],
                    "subset": collection.head[:-1],
                    "isSeries": True,
                    "stagingDir": os.path.join(workspace, renderlayer),
                    "files": list(collection),
                }

                instance.data.update(data)
