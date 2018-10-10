#!/usr/bin/env python3
import ftrack_api

session = ftrack_api.Session(
    server_url="https://pype.ftrackapp.com",
    api_key="e27c2606-ff78-4ccc-8463-f3a3e560604a",
    api_user="jakub.jezek"
)

print(session)

# from app.api import (
#     solve_dependecies,
#     Templates
# )
#
# solve_dependecies()
# t = Templates()
