import os
import subprocess
from . import (
    Logger
)

log = Logger.getLogger(__name__)


def get_conf_file(
    dir,
    root_file_name,
    preset_name=None,
    split_pattern=None,
    representation=None
):
    '''Gets any available `config template` file from given
    **path** and **name**

    Attributes:
        dir (str): path to root directory where files could be searched
        root_file_name (str): root part of name it is searching for
        preset_name (str): default preset name
        split_pattern (str): default pattern for spliting name and preset
        representation (str): extention of file used for config files
                              can be ".toml" but also ".conf"

    Returns:
        file_name (str): if matching name found or None
    '''

    if not preset_name:
        preset_name = "default"
    if not split_pattern:
        split_pattern = ".."
    if not representation:
        representation = ".toml"

    conf_file = root_file_name + representation

    try:
        preset = os.environ["PYPE_TEMPLATES_PRESET"]
    except KeyError:
        preset = preset_name

    test_files = [
        f for f in os.listdir(dir)
        if split_pattern in f
    ]

    try:
        try:
            conf_file = [
                f for f in test_files
                if preset in os.path.splitext(
                    f)[0].split(
                    split_pattern)[1]
                if root_file_name in os.path.splitext(
                    f)[0].split(
                    split_pattern)[0]
            ][0]
        except IndexError:
            conf_file = [
                f for f in test_files
                if preset_name in os.path.splitext(
                    f)[0].split(
                    split_pattern)[1]
                if root_file_name in os.path.splitext(
                    f)[0].split(
                    split_pattern)[0]
            ][0]
    except IndexError as error:

        log.debug("File is missing '{}' will be"
                  "used basic config file: {}".format(
                      error, conf_file
                  ))
        pass

    return conf_file if os.path.exists(os.path.join(dir, conf_file)) else None


def forward(args,
            silent=False,
            cwd=None,
            env=None,
            executable=None,
            shell=None):
    """Pass `args` to the Avalon CLI, within the Avalon Setup environment

    Arguments:
        args (list): Command-line arguments to run
            within the active environment

    """
    # testing this list to filter stdout line into log.info
    # everything else will be log.debug
    info_log_filter = (
        "Connected to mongodb://",
        ("@", "Using")  # AND condition
    )
    log_levels = {
        log.info: ">>> [",
        log.warning: "*** WRN:",
        log.error: "--- ERR:",
        log.critical: "!!! CRI:",
        log.debug: "  - {"
    }

    def filter_log_line(line, info_log_filter):
        test = False
        for s in info_log_filter:
            if isinstance(s, tuple):
                if len([i for i in s if i in line]) == len(s):
                    test = True
            else:
                if s in line:
                    test = True
        return test

    print("\n")
    log.info("Forwarding '%s'.." % " ".join(args))
    print("\n")

    popen = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        cwd=cwd,
        env=env or os.environ,
        # executable=executable or sys.executable,
        shell=shell
    )

    # Blocks until finished
    while True:
        line = popen.stdout.readline()
        if line != '':
            if not silent:
                # if filter_log_line(line, info_log_filter):
                #     log.info(line[:-2])
                # else:
                for funct, test_string in log_levels.items():
                    if test_string in line:
                        funct(
                            "Fwd: {}".format(
                                line[:-2]
                            ).replace(
                                test_string,
                                ""
                            ).replace("]", "")
                        )
        else:
            break

    log.info("Forward is finishing up..")

    popen.wait()
    return popen.returncode
