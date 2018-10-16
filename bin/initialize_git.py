import os
import shutil
import subprocess
import tempfile
import sys

IS_WIN32 = sys.platform == "win32"

repository_path = os.environ["PYPE_SETUP_ROOT"]
REP_GIT_URL = os.environ["PYPE_SETUP_GIT_URL"]
REP_GIT_BRANCH = os.environ["PYPE_SETUP_GIT_BRANCH"]

if __name__ == "__main__":

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
        if key in ("PATH", "PYTHONPATH"):
            print(key, value)

    # Copy .git directory from cloned repository
    tempdir = tempfile.mkdtemp()
    subprocess.call(["git", "clone", REP_GIT_URL], cwd=tempdir, shell=True)
    src = os.path.join(tempdir, "pype-setup", ".git")
    dst = os.path.join(repository_path, ".git")

    shutil.rmtree(dst, ignore_errors=False, onerror=None)
    if not os.path.exists(dst):
        shutil.copytree(src, dst)

    # Initialising git repository
    subprocess.Popen(["git", "init"], shell=True)
    subprocess.Popen(["git", "checkout", REP_GIT_BRANCH], shell=True)
    subprocess.call(["git", "add", "."], shell=True)
