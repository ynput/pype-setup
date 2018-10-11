import os

import gazu
from avalon import io as avalon


def main():
    projects = {}
    objects = {}
    objects_count = 0
    tasks = [{"name": task["name"]} for task in gazu.task.all_task_types()]

    for project in gazu.project.all_projects():
        # Remove spaces for compatibility, lowercase for consistentcy
        project_name = project["name"].replace(" ", "_").lower()

        assets = gazu.asset.all_assets_for_project(project)
        episodes = []
        sequences = []
        shots = []
        for episode in gazu.shot.all_episodes_for_project(project):
            episode["parent"] = project
            episodes.append(episode)
            for sequence in gazu.shot.all_sequences_for_episode(episode):
                sequence["parent"] = episode
                sequence["label"] = sequence["name"]
                sequence["name"] = "{0}_{1}".format(
                    episode["name"], sequence["name"]
                )
                sequence["visualParent"] = episode["name"]
                sequences.append(sequence)
                for shot in gazu.shot.all_shots_for_sequence(sequence):
                    shot["parent"] = sequence
                    shot["label"] = shot["name"]
                    shot["name"] = "{0}_{1}".format(
                        sequence["name"], shot["name"]
                    )
                    shot["visualParent"] = sequence["name"]
                    shot["tasks"] = gazu.task.all_tasks_for_shot(shot)
                    shots.append(shot)

        silos = [
            [assets, "assets"],
            [episodes, "shots"],
            [sequences, "shots"],
            [shots, "shots"]
        ]
        entities = {}
        for assets, silo in silos:
            for asset in assets:
                entity_type = gazu.entity.get_entity_type(
                    asset["entity_type_id"]
                )
                # Remove spaces for compatibility, lowercase for consistentcy
                name = asset["name"].replace(" ", "_").lower()
                data = {
                    "schema": "avalon-core:asset-2.0",
                    "name": name,
                    "silo": silo,
                    "type": "asset",
                    "parent": project_name,
                    "data": {
                        "label": asset.get("label", asset["name"]),
                        "group": entity_type["name"]
                    }
                }

                if asset.get("visualParent"):
                    data["data"]["visualParent"] = asset["visualParent"]

                if asset.get("tasks"):
                    data["data"]["tasks"] = [
                        task["task_type_name"] for task in asset["tasks"]
                    ]

                entities[name] = data

                objects_count += 1

        objects[project_name] = entities

        projects[project_name] = {
            "schema": "avalon-core:project-2.0",
            "type": "project",
            "name": project_name,
            "data": {
                "label": project["name"]
            },
            "parent": None,
            "config": {
                "schema": "avalon-core:config-1.0",
                "apps": [
                    {
                        "name": "maya2015",
                        "label": "Autodesk Maya 2015"
                    },
                    {
                        "name": "maya2016",
                        "label": "Autodesk Maya 2016"
                    },
                    {
                        "name": "maya2017",
                        "label": "Autodesk Maya 2017"
                    },
                    {
                        "name": "nuke10",
                        "label": "The Foundry Nuke 10.0"
                    }
                ],
                "tasks": tasks,
                "template": {
                    "work":
                        "{root}/{project}/{silo}/{asset}/work/"
                        "{task}/{app}",
                    "publish":
                        "{root}/{project}/{silo}/{asset}/publish/"
                        "{subset}/v{version:0>3}/{subset}.{representation}"
                }
            }
        }

    print("Found:")
    print("- %d projects" % len(projects))
    print("- %d assets" % objects_count)

    os.environ["AVALON_PROJECTS"] = r""
    os.environ["AVALON_PROJECT"] = "temp"
    os.environ["AVALON_ASSET"] = "bruce"
    os.environ["AVALON_SILO"] = "assets"
    os.environ["AVALON_CONFIG"] = "polly"
    os.environ["AVALON_MONGO"] = "mongodb://192.168.99.100:27017"

    print("Fetching Avalon data..")
    avalon.install()

    existing_projects = {}
    existing_objects = {}

    for project in avalon.projects():
        existing_projects[project["name"]] = project

        # Update project
        os.environ["AVALON_PROJECT"] = project["name"]
        avalon.uninstall()
        avalon.install()

        # Collect assets
        assets = {}
        for asset in avalon.find({"type": "asset"}):
            assets[asset["name"]] = asset

        existing_objects[project["name"]] = assets

    print("Synchronising..")
    for name, project in projects.items():
        if project["name"] in existing_projects:
            # Update task types
            existing_project = existing_projects[project["name"]]
            existing_project_task_types = existing_project["config"]["tasks"]
            if existing_project_task_types != tasks:
                print(
                    "Updating tasks types on \"{0}\" to:\n{1}".format(
                        project["name"], tasks
                    )
                )
                existing_project["config"]["tasks"] = tasks
                os.environ["AVALON_PROJECT"] = project["name"]
                avalon.uninstall()
                avalon.install()
                avalon.replace_one({"type": "project"}, existing_project)

            continue

        print("Installing project: %s" % project["name"])
        os.environ["AVALON_PROJECT"] = project["name"]
        avalon.uninstall()
        avalon.install()

        avalon.insert_one(project)

    for project_name, assets in objects.items():
        os.environ["AVALON_PROJECT"] = project_name
        avalon.uninstall()
        avalon.install()

        for asset_name, asset in assets.items():
            if asset_name in existing_objects.get(project_name, {}):
                # Update tasks
                if asset["data"].get("tasks"):
                    existing_asset = existing_objects[project_name][asset_name]
                    existing_tasks = existing_asset["data"].get("tasks", [])
                    if existing_tasks != asset["data"]["tasks"]:
                        tasks = asset["data"]["tasks"]
                        print(
                            "Updating tasks on \"{0} / {1}\" to:\n{2}".format(
                                project_name, asset_name, tasks
                            )
                        )
                        existing_asset["data"]["tasks"] = tasks
                        avalon.replace_one(
                            {"type": "asset", "name": asset_name},
                            existing_asset
                        )

                continue

            asset["parent"] = avalon.locate([asset["parent"]])

            if asset["data"].get("visualParent"):
                asset["data"]["visualParent"] = avalon.find_one(
                    {"type": "asset", "name": asset["data"]["visualParent"]}
                )["_id"]
            print(
                "Installing asset: \"{0} / {1}\"".format(
                    project_name, asset_name
                )
            )
            avalon.insert_one(asset)

    print("Success")


if __name__ == '__main__':
    import time

    print("Logging in..")
    gazu.client.set_host("http://192.168.99.100/api")
    gazu.log_in("admin@example.com", "default")
    print("Logged in..")

    while True:
        print("Syncing..")
        main()
        print("Sleeping for 10 seconds..")
        time.sleep(10)
