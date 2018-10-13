#!/usr/bin/env python3
import os
import ftrack_api


ftrack_envs = {
    "FTRACK_SERVER": "https://pype.ftrackapp.com",
    "FTRACK_API_KEY": "e27c2606-ff78-4ccc-8463-f3a3e560604a",
    "FTRACK_API_USER": "jakub.jezek",
    "FTRACK_EVENT_PLUGIN_PATH": ""
}

for k, v in ftrack_envs.items():
    os.environ[k] = v

session = ftrack_api.Session()

print(session)
