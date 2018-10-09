#!/usr/bin/env python3
import toml
import app.api as api
import os

# import sys
# sys.path.append(r"C:\Users\hubert\CODE\github\pypeclub\pype-setup")
#
# import app.api as api
#
# data = {
#     "project": {
#         "code": "batman"
#     },
#     "PYPE_CONTEXT_CODE": "sequence_shot",
#     "version": {
#         "main": "v01",
#         "sub": "_p01"
#     },
#     "representation": "exr"
#
# }
# t = api.Loaded_templates
# t.update(
#     one="one_string",
#     two="two_string",
#     three={
#         'one_in_three': '{project.code}_{PYPE_CONTEXT_CODE}<_{subset}>_{version.main}{version.sub}.{representation}',
#         'two_in_three': 'two_in_three_string'}
# )
# print(t.three.one_in_three)
# format = t.format
# print(t.one)
# print(format(t.three.one_in_three, data))
# # anatomy = t.anatomy.data
# # file = format(anatomy.workfiles.file, data)
# # path = format(anatomy.workfiles.path, data)

root = r"C:\Users\hubert\CODE\github\pypeclub\pype-setup\studio\studio-templates\templates"

file = api.get_conf_file(
    dir=root,
    root_file_name="pype-config"
)
# print(file)
path = os.path.join(root, file)
file_content = toml.load(path)
print(file_content['templates'])

process_order = list()
for t in file_content['templates']:
    # print(t)
    if "base" in t['type']:
        try:
            for item in t['order']:
                t_root = os.path.join(root, t['dir'])
                print(os.listdir(t_root))
                t_file = api.get_conf_file(
                    dir=t_root,
                    root_file_name=item
                )
                item_dict = {
                    "path": os.path.join(t_root, t_file),
                    "department": t['dir'],
                    "type": t['type']
                }
                process_order.append(item_dict)
        except KeyError:
            pass
print(process_order)
