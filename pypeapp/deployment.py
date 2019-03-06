#         ______                          ______          _____
#   _____|\     \  ______   _____   _____|\     \    _____\    \
#  /     / |     ||\     \ |     | /     / |     |  /    / |    |
# |      |/     /|\ \     \|     ||      |/     /| /    /  /___/|
# |      |\____/ | \ \           ||      |\____/ ||    |__ |___|/
# |\     \    | /   \ \____      ||\     \    | / |       \
# | \     \___|/     \|___/     /|| \     \___|/  |     __/ __
# |  \     \             /     / ||  \     \      |\    \  /  \
# \  \_____\           /_____/  / \  \_____\     | \____\/    |
#  \ |     |           |     | /   \ |     |     | |    |____/|
#   \|_____|           |_____|/     \|_____|      \|____|   | |
#                                                       |___|/
#              ..---===[[ PyP3 Setup ]]===---...

import json
import os
import sys
import subprocess
import jsonschema
# from pprint import pprint
from pypeapp import Logger
from pypeapp.lib.Terminal import Terminal
import git
import shutil
from tqdm import tqdm


class DeployException(Exception):
    """ Wraps exceptions raised from Deployment.
        Logs them via logger facility
    """
    _code = 0

    def __init__(self, message, code=0):
        super().__init__(message)
        log = Logger().get_logger('deployment')
        self._code = code
        log.error(message)

    def get_code(self):
        return self._code


class _GitProgress(git.remote.RemoteProgress):
    """ Class handling displaying progress during git operations.

        This is using **tqdm** for showing progress bars. As **GitPython**
        is parsing progress directly from git command, it is somehow unreliable
        as in some operations it is difficult to get total count of iterations
        to display meaningful progress bar.

    """
    _t = None
    _code = 0
    _current_status = ''
    _current_max = ''

    _description = {
        256: "Checking out files",
        4: "Counting objects",
        128: "Finding sources",
        32: "Receiving objects",
        64: "Resolving deltas",
        16: "Writing objects"
    }

    def __init__(self):
        super().__init__()

    def __del__(self):
        if self._t is not None:
            self._t.close()

    def _detroy_tqdm(self):
        """ Used to close tqdm when opration ended.

        """
        if self._t is not None:
            self._t.close()
            self._t = None

    def _check_mask(self, opcode):
        """" Add meaningful description to **GitPython** opcodes.

            :param opcode: OP_MASK opcode
            :type opcode: int
            :return: String description of opcode
            :rtype: string

            .. seealso:: For opcodes look at :class:`git.RemoteProgress`

        """
        if opcode & self.COUNTING:
            return self._description.get(self.COUNTING)
        elif opcode & self.CHECKING_OUT:
            return self._description.get(self.CHECKING_OUT)
        elif opcode & self.WRITING:
            return self._description.get(self.WRITING)
        elif opcode & self.RECEIVING:
            return self._description.get(self.RECEIVING)
        elif opcode & self.RESOLVING:
            return self._description.get(self.RESOLVING)
        elif opcode & self.FINDING_SOURCES:
            return self._description.get(self.FINDING_SOURCES)
        else:
            return "Processing"

    def update(self, op_code, cur_count, max_count=None, message=''):
        """ Called when git operation update progress.

        .. seealso:: For more details see
                     :func:`git.objects.submodule.base.Submodule.update`
                     `Documentation <https://gitpython.readthedocs.io/en/\
stable/reference.html#git.objects.submodule.base.Submodule.update>`_

        """
        code = self._check_mask(op_code)
        if self._current_status != code or self._current_max != max_count:
            # print("{}-{} | {}-{}".format(code, self._current_status,
            #                              max_count, self._current_max))
            self._current_max = max_count
            self._current_status = code
            self._detroy_tqdm()
            self._t = tqdm(total=max_count)
            self._t.set_description("  . {}".format(code))

        self._t.update(cur_count)


class Deployment(object):
    """ Deployment class will load settings from `deploy/deploy.json` or
        if exists, use `deploy/studio/deploy.json`. Then it will process
        information, create `repos` and setup `vendors`
    """

    _deploy_dir = 'deploy'
    _deploy_file = 'deploy.json'
    _schema_file = 'deploy_schema-1.0.json'
    _pype_root = None
    _log = Logger().get_logger()

    def __init__(self, pype_root: str):
        """ Init deployment object

        This will initialize object and check if **pype_root** is valid
        location. It will normalize path.

        :param pype_root: Path to Pype setup
        :type pype_root: string
        :raises: :class:`DeployException`

        """
        normalized = os.path.normpath(pype_root)
        if not os.path.exists(normalized):
            raise DeployException(
                "PYPE_ROOT {} doesn't exists or wasn't set".format(normalized),
                100)
        self._pype_root = normalized
        pass

    def _read_deployment_file(self, file: str) -> dict:
        """ Just reads deployment file as a json

            :param file: path to json file
            :type file: string
            :return: parsed json
            :rtype: dict

        """
        with open(file) as deployment_file:
            data = json.load(deployment_file)
        return data

    def _read_schema(self, file: str) -> dict:
        """ Reads json schema from file

            :param file: path to schema json
            :type file: string
            :return: parsed json schema
            :rtype: dict
            :raises: :class:`DeployException`

        """
        if (not os.path.exists(file)):
            raise DeployException(
                "Cannot find schema to validate `{}`".format(
                    self._deploy_file), 110)
        with open(file) as schema:
            data = json.load(schema)
        return data

    def _determine_deployment_file(self) -> str:
        """ Determine which deployment file to use.

            We use default one distributed with **Pype**. But if
            under *deploy* directory is another with *deploy.json*, that
            one will take priority.

            :return: Path to deployment file
            :rtype: string
            :raises: :class:`DeployException`

            .. note::
                If there are more then one directory, only first found is used.

        """
        file = os.path.join(self._pype_root,
                            self._deploy_dir, self._deploy_file)
        if (not os.path.exists(file)):
            raise DeployException("Directory `{}` doesn't exist".format(
                self._deploy_file), 120)

        override = None
        deploy_path = os.path.join(self._pype_root, self._deploy_dir)
        with os.scandir(deploy_path) as i:

            for entry in i:
                if entry.is_dir():
                    override = os.path.join(entry.path, self._deploy_file)
                    if (os.path.exists(override)):
                        file = override
                        break
        return os.path.normpath(file)

    def _validate_schema(self, settings: dict) -> bool:
        """ Validate json deployment setting against json schema.

            :param settings: Deployment settings from parsed json
            :type settings: dict
            :return: True if validated, False if not
            :rtype: boolean

            .. seealso::
                :func:`Deployment._read_schema`
                :func:`Deployment.__read_deployment_file`

        """
        schema_file = os.path.join(
            self._pype_root,
            self._deploy_dir,
            self._schema_file
            )
        schema = self._read_schema(schema_file)

        try:
            jsonschema.validate(settings, schema)
        except jsonschema.exceptions.ValidationError as e:
            self._log.error(e)
            return False
        except jsonschema.exceptions.SchemaError as e:
            self._log.error(e)
            return False
        return True

    def validate(self, skip=False) -> bool:
        """ Do deployment setting validation.

            First, deployment settings is determined. It can be default
            provided *deploy.json* or overrided one in
            *deploy/somedir/deploy.json*. This file is then validated against
            json schema. Then it will check, if stuff defined in settings is
            present and deployed.

            :param skip:    if True skip if directory not exists. Used during
                            installation where some directories will be
                            installed nevertheless.
            :type skip: boolean

            :return: True if validated, otherwise throw exception
            :rtype: boolean
            :raises: :class:`DeployException` With info on what is wrong

        """
        settings = self._determine_deployment_file()
        deploy = self._read_deployment_file(settings)
        if (not self._validate_schema(deploy)):
            raise DeployException(
                "Invalid deployment file [ {} ]".format(settings), 200)

        # go throught repositories
        for ritem in deploy.get('repositories'):
            test_path = os.path.join(
                self._pype_root, "repos", ritem.get('name'))
            # does repo directory exist?
            if not os.path.exists(test_path):
                if skip:
                    continue
                raise DeployException(
                    "Repo path doesn't exist [ {} ]".format(test_path), 130)
            try:
                repo = git.Repo(test_path)
            except git.exc.InvalidGitRepositoryError as e:
                raise DeployException(
                    "Path {} exists but it is not valid repository".format(
                        test_path)) from e

            # bare repo isn't allowed
            if repo.bare is True:
                raise DeployException(
                    "Repo on path [ {} ] is bare".format(test_path), 300)

            head = repo.heads[0]
            # check we are on branch
            if ritem.get('branch'):
                if head.name != ritem.get('branch'):
                    raise DeployException(
                        'repo {0} head is not on {1}(!={2}) branch'.format(
                            ritem.get('name'),
                            ritem.get('branch'),
                            head.name
                        ), 210)
            commit = head.commit
            # check we are on ref
            if ritem.get('ref'):
                if not commit.hexsha.startswith(ritem.get('ref')):
                    raise DeployException(
                        'repo {0} head is not on {1}(!={2}) ref'.format(
                            ritem.get('name'),
                            ritem.get('ref'),
                            commit.hexsha
                        ), 220)
            # check tag
            if ritem.get('tag'):
                tag = next(
                    rtag for rtag in head.tags
                    if rtag["tag"] == ritem.get('tag'))
                if tag.commit.hexsha != commit.hexsha:
                    raise DeployException(
                        'repo {0} head is not on {1}(!={2}) tag {3}'.format(
                            ritem.get('name'),
                            tag.commit.hexsha,
                            commit.hexsha,
                            ritem.get('tag')
                        ), 230)

        return True

    def _validate_is_directory(self, path):
        """ Validate if path is directory.

            :param path: string path to test
            :type path: string
            :return: is dir
            :rtype: boolean
        """
        return os.path.isdir(path)

    def _validate_is_empty(self, path):
        """ Validate if directory is empty.

            :param path: string path to test
            :type path: string
            :return: is empty
            :rtype: boolean
        """
        if any(os.scandir(path)):
            return False
        return True

    def _validate_is_repo(self, path):
        """ Validate if directory is git repository.

            :param path: string path to test
            :type path: string
            :return: is repo
            :rtype: boolean
        """
        try:
            git.Repo(path)
        except git.exc.InvalidGitRepositoryError:
            return False
        return True

    def _validate_is_bare(self, path):
        """ Validate if directory is bare git repository.

            :param path: string path to test
            :type path: string
            :return: is bare
            :rtype: boolean
        """
        repo = git.Repo(path)
        return repo.bare

    def _validate_is_dirty(self, path):
        """ Validate if directory is git repository with dirty worktree.

            :param path: string path to test
            :type path: string
            :return: is dirty
            :rtype: boolean
        """
        repo = git.Repo(path)
        print('!-! dirty {}'.format(repo.is_dirty()))
        return repo.is_dirty()

    def _validate_is_branch(self, path, branch):
        """ Validate if directory is git repository with active branch.

            :param path: string path to test
            :type path: string
            :param branch: name of branch
            :type branch: string
            :return: is dir
            :rtype: boolean
        """
        repo = git.Repo(path)
        if str(repo.active_branch) != str(branch):
            print("{} != {}".format(repo.active_branch, branch))
            return False
        return True

    def _validate_origin(self, path: str, origin: str) -> bool:
        """ Validate if directory is git repository remote origin.

            :param path: string path to test
            :type path: string
            :param origin: url of remote origin
            :type branch: string
            :return: is origin
            :rtype: boolean
        """
        repo = git.Repo(path)

        # if there is no origin, repo has no remotes possibly and is invalid
        try:
            if repo.remotes.origin.url != origin:
                return False
        except AttributeError:
            return False
        return True

    def _recreate_repository(self, path, repo):
        """ Recreate (remove and clone) repository on specifed path.

            :param path: string path to repository
            :type path: string
            :param repo: dict representing item from deployment file
            :type repo: dict
            :raises: :class:`DeployException`
        """
        try:
            shutil.rmtree(path)
        except OSError as e:
            raise DeployException(("Cannot remove existing non"
                                   " git repository.{}".format(e))
                                  ) from e
        else:
            # clone repo
            try:
                git.Repo.clone_from(
                    repo.get('url'),
                    path,
                    progress=_GitProgress(),
                    env=None,
                    b=repo.get('branch') or repo.get('tag')
                )
            except git.exc.GitCommandError as e:
                raise DeployException(
                    "Git clone failed for {}".format(
                        repo.get("url"))
                ) from e

    def deploy(self, force=False):
        """ Do repositories deployment and install python dependencies.

            Go throught deployment file and install repositories specified
            there. Also add additional python dependencies with pip.

            :param force:   overwrite existng repos if it's working tree is
                            dirty.
            :type force: boolean
            :raises: :class:`DeployException`

        """
        settings = self._determine_deployment_file()
        deploy = self._read_deployment_file(settings)
        term = Terminal()

        # go throught repositories
        term.echo(">>> Deploying repositories ...")
        for ritem in deploy.get('repositories'):
            path = os.path.join(
                self._pype_root, "repos", ritem.get('name'))

            term.echo(" -- processing [ {} / {} ]".format(
                ritem.get('name'), ritem.get('branch') or ritem.get('tag')))

            if self._validate_is_directory(path):
                # path exists
                # is it repository?
                if not self._validate_is_repo(path):
                    # no, remove dir no matter of content
                    term.echo("  - removing existing directory and cloning...")
                    self._recreate_repository(path, ritem)
                else:
                    # dir is repository
                    repo = git.Repo(path)
                    # is it right one?
                    if not self._validate_origin(path, str(ritem.get('url'))):
                        # repository has different origin then specified
                        term.echo("!!! repository has different origin. ")
                        if (self._validate_is_dirty(path) is True and
                           force is False):
                            raise DeployException(('Invalid repository on '
                                                   'path {}'.format(path)))
                        term.echo(" -> recreating repository. ")
                        self._recreate_repository(path, ritem)
                        pass
                    if (self._validate_is_dirty(path) is True and
                       force is False):
                        raise DeployException(
                            ("Repo on path [ {} ] has dirty"
                             " worktree").format(path), 300)

                    # are we on correct branch?
                    if not self._validate_is_branch(path,
                        ritem.get('branch') or ritem.get('tag')):  # noqa: E128

                        term.echo("  . switching to [ {} ] ...".format(
                            ritem.get('branch') or ritem.get('tag')
                        ))
                        branch = repo.create_head(
                                    ritem.get('branch') or ritem('tag'),
                                    'HEAD')

                        branch.checkout(force=force)

                    # update repo
                    term.echo("  . updating ...")
                    repo.remotes.origin.pull()
            else:
                # path doesn't exist, clone
                try:
                    git.Repo.clone_from(
                        ritem.get('url'),
                        path,
                        progress=_GitProgress(),
                        env=None,
                        b=ritem.get('branch') or ritem.get('tag')
                    )
                except git.exc.GitCommandError as e:
                    raise DeployException(
                        "Git clone failed for {}".format(ritem.get("url"))
                    ) from e

        # install python dependencies
        term.echo(">>> Adding python dependencies ...")
        for pitem in deploy.get('pip'):
            term.echo(" -- processing [ {} ]".format(pitem))
            try:
                out = subprocess.check_output(
                    [sys.executable, '-m', 'pip', 'install', pitem])
            except subprocess.CalledProcessError as e:
                raise DeployException(
                    'PIP command failed with {}'.format(e.returncode)
                    ) from e

        term.echo(">>> Updating requirements ...")
        try:
            out = subprocess.check_output(
                [sys.executable,
                 '-m', 'pip', 'freeze', '--disable-pip-version-check'],
                universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise DeployException(
                'PIP command failed with {}'.format(e.returncode)
                ) from e

        r_path = os.path.join(
            os.path.abspath("."), 'pypeapp', 'requirements.txt')
        with open(r_path, 'w') as r_write:
            r_write.write(out)
        pass
