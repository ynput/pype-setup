import avalon.maya


class RigLoader(avalon.maya.Loader):
    """Specific loader for rigs

    This automatically creates an instance for animators upon load.

    """

    families = ["mindbender.rig"]
    representations = ["ma"]

    def process(self, name, namespace, context, data):
        from maya import cmds

        nodes = cmds.file(self.fname,
                          namespace=namespace,
                          reference=True,
                          returnNewNodes=True,
                          groupReference=True,
                          groupName=namespace + ":" + name)

        # Store for post-process
        self[:] = nodes

        # Trigger post process only if it's not been set to disabled
        if data.get("post_process", True):
            # TODO(marcus): We are hardcoding the name "out_SET" here.
            #   Better register this keyword, so that it can be used
            #   elsewhere, such as in the Integrator plug-in,
            #   without duplication.
            output = next(
                (node for node in self
                    if node.endswith("out_SET")), None)
            controls = next(
                (node for node in self
                    if node.endswith("controls_SET")), None)

            assert output, "No out_SET in rig, this is a bug."
            assert controls, "No controls_SET in rig, this is a bug."

            with avalon.maya.maintained_selection():
                cmds.select([output, controls], noExpand=True)

                dependencies = [context["representation"]["_id"]]
                asset = context["asset"]["name"] + "_"

                avalon.maya.create(
                    name=avalon.maya.unique_name(asset, suffix="_SET"),

                    # Publish to the currently set asset, and not the
                    # asset from which the Rig was produced.
                    asset=context["asset"],

                    family="mindbender.animation",
                    options={"useSelection": True},
                    data={
                        "dependencies": " ".join(str(d) for d in dependencies)
                    })
