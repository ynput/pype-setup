import os
import sys
from pypeLauncher import PypeLauncher

# add forcefully click from vendor in case we didn't installed pype yet
try:
    import click
except ImportError:
    click_path = os.path.join(os.environ['PYPE_SETUP_PATH'],
                              'vendor', 'python', 'click')
    sys.path.append(click_path)
    import click


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    Pype is main command serving as entry point to pipeline system. It wraps
    different commands together.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(tray)


@main.command()
@click.option("-d", "--debug",
              is_flag=True, help=("Run pype tray in debug mode"))
def tray(debug):
    """
    Launch pype tray.

    Default action of pype command is to launch tray widget to control basic
    aspects of pype. See documentation for more information.

    Running pype with `--debug` will result in lot of information useful for
    debugging to be shown in console.
    """
    PypeLauncher().launch_tray(debug)


@main.command()
@click.option("--offline", is_flag=True, help="Do offline installation.")
@click.option("--force", is_flag=True,
              help="Force overwrite of existing installation")
def install(offline, force):
    """
    This will install pype virtual env.

    Install destination is `PYPE_ENV`, defaulting to
    `c:\\Users\\Public\\pype_env2` on Windows and `/opt/pype/pype_env2` on
    linux. Can be overriden by setting `PYPE_ENV`.

    Offline installation will not download packages from internet but will
    look for them in `vendor/packages`. Those can be downloaded by
    `download` command for every platform needed (pip will download packages
    only for current platform).
    """
    # offline is ignored as it is used only by shell script during bootstrap
    PypeLauncher().install(force)


@main.command()
def update_requirements():
    """
    Update requirements based upon current environment.

    This will update `pypeapp/requirements.txt` with stuff already installed
    in current running python environment. Usefull for developer when adding
    some dependency for feature.

    Shortcut for `pip freeze > pypeapp/requirements.txt`
    """
    # done by shell script.
    pass


@main.command()
def download():
    """
    Command to download required packages.

    Only packages for current platform will be download. To create
    multiplatform packages, run `download` on every platform you need and
    then merge content of `vendor/packages`.
    """
    # This is implemented purely in shell script
    pass


@main.command()
@click.option("-f", "--force", is_flag=True,
              help=("This will force repositories to be overwritten"))
def deploy(force):
    """
    Deploy repositories to `repos`.

    Repositories are defined in `deploy` folder in json files and can be
    overriden by studio specific configuration. Just create
    `deploy/studio/deploy.json` and it will take precedence over factory
    configuration.

    It needs git installation.
    """
    PypeLauncher().deploy(force)


@main.command()
def validate():
    """
    This command will validate deployment.

    It needs git installation.
    """
    PypeLauncher().validate()


@main.command()
def mongodb():
    """
    This will launch local mongodb server. Useful for development.
    """
    PypeLauncher().launch_local_mongodb()


@main.command()
@click.option("-d", "--develop", is_flag=True, help="Adds develop buttons.")
def settings(develop):
    """
    This will launch local mongodb server. Useful for development.
    """
    PypeLauncher().launch_settings_gui(develop)


@main.command()
@click.option("-d", "--debug", is_flag=True, help="Print debug messages")
@click.option("--ftrack-url", envvar="FTRACK_SERVER",
              help="Ftrack server url")
@click.option("--ftrack-user", envvar="FTRACK_API_USER",
              help="Ftrack api user")
@click.option("--ftrack-api-key", envvar="FTRACK_API_KEY",
              help="Ftrack api key")
@click.option("--ftrack-events-path",
              envvar="FTRACK_EVENTS_PATH",
              help=("path to ftrack event handlers"))
@click.option("--no-stored-credentials", is_flag=True,
              help="dont use stored credentials")
@click.option("--store-credentials", is_flag=True,
              help="store provided credentials")
@click.option("--legacy", is_flag=True,
              help="run event server without mongo storing")
@click.option("--clockify-api-key", envvar="CLOCKIFY_API_KEY",
              help="Clockify API key.")
@click.option("--clockify-workspace", envvar="CLOCKIFY_WORKSPACE",
              help="Clockify workspace")
def eventserver(debug,
                ftrack_url,
                ftrack_user,
                ftrack_api_key,
                ftrack_events_path,
                no_stored_credentials,
                store_credentials,
                legacy,
                clockify_api_key,
                clockify_workspace):
    """
    This command launches ftrack event server.

    This should be ideally used by system service (such us systemd or upstart
    on linux and window service).

    You have to set either proper environment variables to provide URL and
    credentials or use option to specify them. If you use --store_credentials
    provided credentials will be stored for later use.
    """
    if debug:
        os.environ['PYPE_DEBUG'] = "3"
    # map eventserver options
    # TODO: switch eventserver to click, normalize option names
    args = []
    if ftrack_url:
        args.append('-ftrackurl')
        args.append(ftrack_url)

    if ftrack_user:
        args.append('-ftrackuser')
        args.append(ftrack_user)

    if ftrack_api_key:
        args.append('-ftrackapikey')
        args.append(ftrack_api_key)

    if ftrack_events_path:
        args.append('-ftrackeventpaths')
        args.append(ftrack_events_path)

    if no_stored_credentials:
        args.append('-noloadcred')

    if store_credentials:
        args.append('-storecred')

    if legacy:
        args.append('-legacy')

    if clockify_api_key:
        args.append('-clockifyapikey')
        args.append(clockify_api_key)

    if clockify_workspace:
        args.append('-clockifyworkspace')
        args.append(clockify_workspace)

    PypeLauncher().launch_eventservercli(args)


@main.command()
@click.argument("paths", nargs=-1)
@click.option("-g", "--gui", is_flag=True, help="Run pyblish GUI")
@click.option("-d", "--debug", is_flag=True, help="Print debug messages")
def publish(gui, debug, paths):
    """
    Starts CLI publishing.

    Publish collects json from paths provided as an argument.
    More than one path is allowed.
    """
    if debug:
        os.environ['PYPE_DEBUG'] = '3'
    PypeLauncher().publish(gui, list(paths))


@main.command()
@click.option("-d", "--debug", is_flag=True, help="Print debug messages")
@click.option("-p", "--project", required=True,
              help="name of project asset is under")
@click.option("-a", "--asset", required=True,
              help="name of asset to which we want to copy textures")
@click.option("--path", required=True,
              help="path where textures are found",
              type=click.Path(exists=True))
def texturecopy(debug, project, asset, path):
    """
    Copy specified textures to provided asset path.

    It validates if project and asset exists. Then it will use speedcopy to
    copy all textures found in all directories under --path to destination
    folder, determined by template texture in anatomy. I will use source
    filename and automatically rise version number on directory.

    Result will be copied without directory structure so it will be flat then.
    Nothing is written to database.
    """
    if debug:
        os.environ['PYPE_DEBUG'] = '3'
    PypeLauncher().texture_copy(project, asset, path)


@main.command()
@click.option("--pype", is_flag=True, help="Run tests on pype")
@click.option("-k", "--keyword", help="select tests by keyword to run",
              type=click.STRING)
@click.argument("id", nargs=-1, type=click.STRING)
def test(pype, keyword, id):
    """
    Run test suite. If --pype is not specified, tests are run against
    pype-setup.
    """
    if pype:
        PypeLauncher().run_pype_tests(keyword, id)
    else:
        PypeLauncher().run_pype_setup_tests(keyword, id)


@main.command()
def make_docs():
    """
    This will generate documentation with Sphinx into `docs/build`
    """
    PypeLauncher().make_docs()


@main.command()
@click.option("--pype", is_flag=True, help="Run tests on pype")
def coverage(pype):
    """
    Generate code coverage report. If --pype is not specified,
    tests are run against pype-setup.
    """

    if pype:
        PypeLauncher().pype_setup_coverage("pype")
    else:
        PypeLauncher().pype_setup_coverage("pypeapp")


@main.command()
def clean():
    """
    This command deletes pyc python bytecode files.

    Working throughout Pype directory, it will remove all pyc bytecode files.
    This is normally not needed but there are cases when update of repostories
    caused errors thanks to these files. If you encounter errors complaining
    about `magic number`, run this command.
    """
    # This is implemented purely in shell script
    pass


@main.command(context_settings={"ignore_unknown_options": True})
@click.option("--app", help="Registered application name")
@click.option("--project", help="Project name",
              default=lambda: os.environ.get('AVALON_PROJECT', ''))
@click.option("--asset", help="Asset name",
              default=lambda: os.environ.get('AVALON_ASSET', ''))
@click.option("--task", help="Task name",
              default=lambda: os.environ.get('AVALON_TASK', ''))
@click.option("--tools", help="List of tools to add")
@click.option("--user", help="Pype user name",
              default=lambda: os.environ.get('PYPE_USERNAME', ''))
@click.option("-fs",
              "--ftrack-server",
              help="Registered application name",
              default=lambda: os.environ.get('FTRACK_SERVER', ''))
@click.option("-fu",
              "--ftrack-user",
              help="Registered application name",
              default=lambda: os.environ.get('FTRACK_API_USER', ''))
@click.option("-fk",
              "--ftrack-key",
              help="Registered application name",
              default=lambda: os.environ.get('FTRACK_API_KEY', ''))
@click.argument('arguments', nargs=-1)
def launch(app, project, asset, task,
           ftrack_server, ftrack_user, ftrack_key, tools, arguments, user):
    """
    Launch registered application name in Pype context.

    You can define applications in pype-config toml files. Project, asset name
    and task name must be provided (even if they are not used by app itself).
    Optionally you can specify ftrack credentials if needed.

    ARGUMENTS are passed to launched application.
    """
    if ftrack_server:
        os.environ["FTRACK_SERVER"] = ftrack_server

    if ftrack_server:
        os.environ["FTRACK_API_USER"] = ftrack_user

    if ftrack_server:
        os.environ["FTRACK_API_KEY"] = ftrack_key

    if user:
        os.environ["PYPE_USERNAME"] = user

    # test required
    if not project or not asset or not task:
        print("!!! Missing required arguments")
        return

    PypeLauncher().run_application(app, project, asset, task, tools, arguments)


@main.command()
def validate_config():
    """
    This will validate all json configuration files for errors.
    """

    PypeLauncher().validate_jsons()
