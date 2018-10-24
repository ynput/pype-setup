import os
import shutil
import subprocess
import tempfile
import sys
from app.lib.repos import (
    git_set_repository,
    git_make_repository
)

IS_WIN32 = sys.platform == "win32"

repository_path = os.environ["PYPE_SETUP_ROOT"]
rep_git_url = os.getenv(
    "PYPE_SETUP_GIT_URL",
    "git@github.com:pypeclub/pype-setup.git"
)
rep_git_branch = os.getenv(
    "PYPE_SETUP_GIT_BRANCH",
    "master"
)
# studio templates repository setting
studio_templates_name = os.getenv(
    "PYPE_STUDIO_TEMPLATES_NAME",
    "studio-templates"
)
studio_templates_url = os.getenv(
    "PYPE_STUDIO_TEMPLATES_URL",
    "git@github.com:pypeclub/studio-templates.git"
)
studio_templates_submodule_root = os.getenv(
    "PYPE_STUDIO_TEMPLATES_SUBM_PATH",
    "studio"
)
studio_templates_branch = os.getenv(
    "PYPE_STUDIO_TEMPLATES_BRANCH",
    "master"
)

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

    for key, value in _env.items():
        print(key)
        if key in ("PATH", "PYTHONPATH"):
            print(key, value)

    # Copy .git directory from cloned repository
    tempdir = tempfile.mkdtemp()
    subprocess.call(["git", "clone", rep_git_url], cwd=tempdir, shell=True)
    src = os.path.join(tempdir, "pype-setup", ".git")
    dst = os.path.join(repository_path, ".git")

    if not os.path.exists(dst):
        os.makedirs(dst)

    shutil.rmtree(dst, ignore_errors=False, onerror=None)
    if not os.path.exists(dst):
        shutil.copytree(src, dst)

    # Initialising git repository
    subprocess.Popen(["git", "init"], shell=True)
    subprocess.Popen(["git", "fetch"], shell=True)
    subprocess.Popen(["git", "checkout", rep_git_branch], shell=True)
    

    repos_data = {
        "name": studio_templates_name,
        "url": studio_templates_url,
        "submodule_root": studio_templates_submodule_root,
        "branch": studio_templates_branch
    }

    # install studio-templates repository
    git_set_repository(repository_path, repos_data)

    # install rest of dependent repositories from
    # /studio/<studio>-templates/install/pype-repos.toml
    git_make_repository()

    subprocess.call(["git", "add", "."], shell=True)
