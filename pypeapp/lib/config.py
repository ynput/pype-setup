import os
import json
from .log import PypeLogger

log = PypeLogger().get_logger(__name__)


def collect_json_path(input_path):
    output = None
    if os.path.isdir(input_path):
        output = {}
        for file in os.listdir(input_path):
            full_path = os.path.sep.join([input_path, file])
            if os.path.isdir(full_path):
                loaded = collect_json_path(full_path)
                if loaded:
                    output[file] = loaded
            else:
                basename, ext = os.path.splitext(os.path.basename(file))
                if ext == '.json':
                    with open(full_path, "r") as f:
                        output[basename] = json.load(f)
    else:
        basename, ext = os.path.splitext(os.path.basename(input_path))
        if ext == '.json':
            with open(input_path, "r") as f:
                output = json.load(f)

    return output
