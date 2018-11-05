import os
import pprint

import avalon.lib as lib


# TODO: Remove redundant hack
import sys
# sys.path.append(r"P:\pipeline\dev\git\env_prototype")
import acre


templates_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.api import Templates

t = Templates()
# os.environ["TOOL_ENV"] = os.path.join(templates_root, "studio-templates", "environments")

# print(os.environ["TOOL_ENV"])


def launch(tools, executable, args):

    tools_env = acre.get_tools(tools.split(";"))
    env = acre.compute(tools_env)
    env = acre.merge(env, current_env=dict(os.environ))
    print("Environment:\n%s" % pprint.pformat(env, indent=4))

    # Search for the executable within the tool's environment
    # by temporarily taking on its `PATH` settings
    original = os.environ["PATH"]
    os.environ["PATH"] = env.get("PATH", os.environ.get("PATH", ""))
    exe = lib.which(executable)
    os.environ["PATH"] = original

    if not exe:
        raise ValueError("Unable to find executable: %s" % executable)

    print("Launching: %s" % exe)
    lib.launch(exe,
               environment=env,
               args=args)



launch(tools="global;maya_2018;mtoa_3.1.1",
       executable="maya",
       args=[])
