import pyblish.api


class ValidateMindbenderDeadlineDone(pyblish.api.InstancePlugin):
    """Ensure render is finished before publishing the resulting images"""

    label = "Rendered Successfully"
    order = pyblish.api.ValidatorOrder
    hosts = ["shell"]
    families = ["mindbender.imagesequence"]
    optional = True

    def process(self, instance):
        import os
        import json

        from avalon import api
        from avalon.vendor import requests, clique

        # From Deadline documentation
        # https://docs.thinkboxsoftware.com/products/deadline/8.0/
        # 1_User%20Manual/manual/rest-jobs.html#job-property-values
        states = {
            0: "Unknown",
            1: "Active",
            2: "Suspended",
            3: "Completed",
            4: "Failed",
            6: "Pending",
        }

        collection = clique.parse(instance.name)
        context = instance.context
        workspace = context.data["workspaceDir"]
        metadata = os.path.join(workspace, collection.head + "json")

        try:
            with open(metadata) as f:
                metadata = json.load(f)
        except OSError:
            raise Exception("%s was not published correctly "
                            "(missing metadata)" % instance)

        url = api.Session["AVALON_DEADLINE"] + "/api/jobs?JobID=%s"
        response = requests.get(url % metadata["job"]["_id"])

        if response.ok:
            data = response.json()[0]
            state = states.get(data["Stat"])

            if state in (None, "Unknown"):
                raise Exception("State of this render is unknown")

            elif state == "Active":
                raise Exception("This render is still currently active")

            elif state == "Suspended":
                raise Exception("This render is suspended")

            elif state == "Failed":
                raise Exception("This render was not successful")

            elif state == "Pending":
                raise Exception("This render is pending")
            else:
                self.log.info("%s was rendered successfully" % instance)

        else:
            raise Exception("Could not determine the current status "
                            " of this render")
