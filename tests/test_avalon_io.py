import os

from avalon import io as avalon


os.environ["AVALON_PROJECTS"] = r""
os.environ["AVALON_PROJECT"] = "temp"
os.environ["AVALON_ASSET"] = "temp"
os.environ["AVALON_SILO"] = "temp"
os.environ["AVALON_CONFIG"] = "temp"


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

print("existing_projects:\n\t\t{}\n".format(existing_projects))
print("existing_objects:\n\t\t{}\n".format(existing_objects))
