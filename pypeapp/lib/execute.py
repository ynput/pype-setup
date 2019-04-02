import subprocess
import os
from .. import Logger

log_levels = {
    'info': ">>> [",
    'warning': "*** WRN:",
    'error': "--- ERR:",
    'critical': "!!! CRI:",
    'debug': "  - {"
}
log_levels_debug = [
    'DEBUG:', 'INFO:', 'ERROR:', 'WARNING:', 'CRITICAL:']

log = Logger().get_logger('api')


def execute(args,
            silent=False,
            cwd=None,
            env=None,
            shell=None):
    """ Execute command as process.

        This will execute given command as process, monitor its output
        and log it appropriately.

        .. seealso:: :mod:`subprocess` module in Python

        :param args: list of arguments passed to process
        :type args: list
        :param silent: control ouput of executed process
        :type silent: bool
        :param cwd: current working directory for process
        :type cwd: string
        :param env: environment variables for process
        :type env: dict
        :param shell: use shell to execute, default is no
        :type shell: bool
        :returns: return code of process
        :rtype: int
    """
    log.info("Executing '%s'.." % " ".join(args))
    popen = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        cwd=cwd,
        env=env or os.environ,
        shell=shell
    )

    # Blocks until finished
    while True:
        line = popen.stdout.readline()
        if line != '':
            if not silent:
                line_test = False
                for funct, test_string in log_levels.items():
                    if test_string in line:
                        getattr(log, funct)(
                            "Exe: {}".format(
                                line[:-2]
                            ).replace(
                                test_string,
                                ""
                            )
                        )
                        line_test = True
                        break
                for test_string in log_levels_debug:
                    if line.startswith(test_string):
                        line_test = True
                        break

                if (int(os.getenv("PYPE_DEBUG", "0")) == 3 and
                        not line_test):
                    print(line[:-1])
        else:
            break

    log.info("Execution is finishing up ...")

    popen.wait()
    return popen.returncode
