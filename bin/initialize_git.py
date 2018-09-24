import os
import shutil
import subprocess
import tempfile
import sys

IS_WIN32 = sys.platform == "win32"

if __name__ == "__main__":

    repository_path = os.getcwd()
    branch = 'dir-rework'
    repository_url = "git@github.com:pypeclub/pype-setup.git"
	
    print("Making \"{0}\" into git repository.".format(repository_path))

    if IS_WIN32:
        _env = {
            key: os.getenv(key)
            for key in ("USERNAME",
                        "SYSTEMROOT",
                        "PYTHONPATH",
                        "PATH")
            if os.getenv(key)
        }
    else:
    # OSX and Linux users are left to fend for themselves.
        _env = os.environ.copy()


    for key in _env.items():
        print(key)
        if key in ("PATH","PYTHONPATH"):
            print(key, value)

    # Copy .git directory from cloned repository
    tempdir = tempfile.mkdtemp()
    git_clone = subprocess.Popen(["git", "clone", "-b", branch, repository_url], cwd=tempdir, env=_env, shell=True)
    print("git_clone: ", git_clone)
    src = os.path.join(tempdir, "avalon-environment", ".git")
    dst = os.path.join(repository_path, ".git")
    if not os.path.exists(dst):
        shutil.copytree(src, dst)

    # Initialising git repository
    git_init = subprocess.Popen(["git", "init"], env=_env, shell=True)
    git_checkout = subprocess.Popen(["git", "checkout", branch], env=_env, shell=True)
    print("git_checkout: ", git_checkout)
    print("git_init: ", git_init)
    git_add = subprocess.Popen(["git", "add", "."], env=_env, shell=True)
    print("git_add: ", git_add)
