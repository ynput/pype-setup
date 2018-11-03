import sys
import os
import subprocess
import toml
import git

from .utils import (
    forward,
    get_conf_file
)

from .pype_logging import (
    Logger
)

log = Logger.getLogger(__name__)
PYPE_DEBUG = os.getenv("PYPE_DEBUG") is "1"

# TODO: updating repositories into defined branches from .gitmodules
# TODO: write our own gitmodules and ensure it will install all
# submodules at first run in case the .gitmodules got lostself.
# TODO: checking out into defined branches in case branch is
# different from the one in .gitmodules and activated


def git_make_repository():
    repos = get_pype_repos_file_content()

    project_root = os.environ["PYPE_SETUP_ROOT"]
    for repo, conf in repos.items():
        log.debug("\n\n`{}`: processing...".format(conf["name"]))
        git_set_repository(project_root, conf)


def git_set_repository(cd=None, rep_dict=None):
    assert cd or rep_dict, "Need to input [cd] and [rep_dict]"
    assert isinstance(rep_dict, dict), "[rep_dict] must be dictionary "
    "with repository data"
    assert "@" in rep_dict['url'], "[rep_dict['url']] must be ssh url "
    "path (make sure your rsa key is installed in .ssh and related public "
    "key in github)"

    repo_path = os.path.normpath(
        os.path.join(
            cd,
            rep_dict['submodule_root'],
            rep_dict['name']
        )
    )

    try:
        # perhaps the repository not cloned yet
        repo = git.Repo.clone_from(
            rep_dict['url'],
            repo_path,
            branch=rep_dict['branch'])
        log.info("[git] rep' `{}` cloned to `{}`".format(
            rep_dict['name'], repo_path)
        )
    except Exception:
        repo = git.Repo(
            repo_path,
            # branch=repo['branch']
        )
        log.debug("[git] getting into `{}` in `{}`".format(
            rep_dict['name'], repo_path)
        )

    try:
        origin = repo.create_remote('origin', repo.remotes.origin.url)
    except Exception:
        origin = repo.remotes['origin']
    assert origin.exists(), "[git] origin doesn't exists"
    assert origin == repo.remotes.origin == repo.remotes['origin']

    if rep_dict['branch'] not in [head.name for head in repo.heads]:

        origin.fetch()

        if "origin/{}".format(rep_dict['branch']) in [head.name for head in origin.refs]:
            try:
                checkout = repo.create_head(
                    rep_dict['branch'],
                    origin.refs[rep_dict['branch']]
                ).set_tracking_branch(
                    origin.refs[rep_dict['branch']]
                ).checkout()

                log.info("[git] rep' `{}` checkout to `{}`".format(rep_dict['name'], checkout))

            except Exception:

                log.debug("[git] rep' `{}` already in `{}`".format(
                    rep_dict['name'], rep_dict['branch']))
            origin.pull()
        else:
            log.debug("[git] available remote branches: {}".format(
                [head.name.split("/")[1] for head in origin.refs
                 if 'HEAD' not in head.name]
            ))
            log.debug("[git] remote branches for `{}` not having defined branch `{}`".format(
                rep_dict['name'], rep_dict['branch']))
    else:
        try:
            checkout = repo.create_head(
                rep_dict['branch'],
                origin.refs[rep_dict['branch']]
            ).set_tracking_branch(
                origin.refs[rep_dict['branch']]
            ).checkout()

            log.info("[git] rep' `{}` checkout to `{}`".format(rep_dict['name'], checkout))

        except Exception:
            log.debug("[git] rep' `{}` already in `{}`".format(
                rep_dict['name'], rep_dict['branch']))
            pass
        origin.pull()


def _add_config(dir_name):
    '''adding config name of module'''
    # print("adding AVALON_CONFIG: '{}'".format(dir_name))
    os.environ['AVALON_CONFIG'] = dir_name


def _test_module_import(module_path, module_name):
    ''' test import module see if all is set correctly'''
    if subprocess.call([
        sys.executable, "-c",
        "import {}".format(module_name)
    ]) != 0:
        log.critical("ERROR: '{}' not found, check your "
                     "PYTHONPATH for '{}'.".format(module_name, module_path))
        sys.exit(1)


def _add_to_path(add_to_path):
    # Append to PATH
    # print("---------1", os.environ["PATH"])
    os.environ["PATH"] = os.pathsep.join(
        [add_to_path] +
        os.getenv("PATH", "").split(os.pathsep)
    )


def _add_to_pythonpath(add_to_pythonpath):
    # Append to PYTHONPATH
    # print("---------2", os.environ["PYTHONPATH"])
    os.environ["PYTHONPATH"] = os.pathsep.join(
        [add_to_pythonpath] +
        os.getenv("PYTHONPATH", "").split(os.pathsep)
    )


def _setup_environment(repos=None):
    '''Sets all environment variables regarding attributes found
    studio-templates/install/config-repos..default.toml

    '''
    assert isinstance(repos, dict), "`repos` must be <dict>"

    testing_list = list()
    for key, value in repos.items():

        if key not in list(os.environ.keys()):
            print("Adding '{}'...".format(key))
            path = os.path.normpath(
                os.path.join(
                    os.environ['PYPE_SETUP_ROOT'],
                    value['submodule_root'],
                    value['name']
                )
            )
            # print("Checking path '{}'...".format(path))
            if value['env'] in "path":
                path = os.path.normpath(
                    os.path.join(path, value['subdir'])
                )
                _add_to_path(path)
            else:
                # for PYTHONPATH
                if "config" in value['name']:
                    _add_config(value['subdir'])
                    # print("Config added...")
                _add_to_pythonpath(path)
                # print("/// added to pythonpath")
                # add to list for testing
                testing_list.append(
                    {
                        "path": path,
                        "subdir": value['subdir']
                    }
                )
            os.environ[key] = path

    if testing_list:
        for m in testing_list:
            print("Testing module: {}".format(m["subdir"]))
            _test_module_import(m["path"], m["subdir"])


def get_pype_repos_file_content():
    assert os.environ["PYPE_STUDIO_TEMPLATES"], "set PYPE_STUDIO_TEMPLATES before this script is executed"

    install_dir = os.path.join(os.environ["PYPE_STUDIO_TEMPLATES"], "install")
    repos_config_file = get_conf_file(install_dir, "pype-repos")
    repos_config_path = os.path.join(
        install_dir,
        repos_config_file
    )
    print("Pype-repos path: {}".format(repos_config_path))

    config_content = toml.load(
        repos_config_path
    )
    return config_content


def solve_dependecies():
    # getting content of pype-repo toml config
    config_content = get_pype_repos_file_content()
    # adding stuff to environment variables
    _setup_environment(config_content)
    print("All pype, avalon, pyblish environment variables are set")
