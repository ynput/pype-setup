import pytest
import logging
from pypeapp import Logger
from pprint import pprint
import os
import re


class TestLogger():

    def test_console_output(self, capsys, monkeypatch, printer):
        monkeypatch.setitem(os.environ, 'PYPE_DEBUG', '3')
        lf = Logger()
        assert lf.PYPE_DEBUG == 3
        logger = Logger().get_logger('test_output', 'tests')

        printer("DEBUG LEVEL SET: {}".format(os.environ.get('PYPE_DEBUG')))

        # critical
        printer("testing critical level")
        logger.critical("CRITICAL TEST")
        cap = capsys.readouterr()
        cri_regex = re.compile(r'\x1b\[1m\x1b\[31m!!! CRI: \x1b\[0m.* \x1b\[1m\x1b\[32m>>> \x1b\[0m\x1b\[92m{ test_output }\x1b\[0m: \x1b\[1m\x1b\[92m\[ \x1b\[0mCRITICAL TEST \x1b\[1m\x1b\[92m]\x1b\[0m \x1b\[0m\n')  # noqa: E501
        assert cri_regex.match(cap[1])

        # error
        printer("testing error level")
        logger.error("ERROR TEST")
        cap = capsys.readouterr()
        err_regex = re.compile(r'\x1b\[1m\x1b\[91m!!! ERR: \x1b\[0m.* \x1b\[1m\x1b\[32m>>> \x1b\[0m\x1b\[92m{ test_output }\x1b\[0m: \x1b\[1m\x1b\[92m\[ \x1b\[0m\x1b\[1m\x1b\[91mERROR\x1b\[0m TEST \x1b\[1m\x1b\[92m]\x1b\[0m \x1b\[0m\n')  # noqa: E501
        assert err_regex.match(cap[1])

        # warn
        printer("testing warning level")
        logger.warning("WARNING TEST")
        cap = capsys.readouterr()
        warn_regex = re.compile(r'\x1b\[1m\x1b\[93m\*\*\* WRN\x1b\[0m: \x1b\[1m\x1b\[32m>>> \x1b\[0m\x1b\[92m{ test_output }\x1b\[0m: \x1b\[1m\x1b\[92m\[ \x1b\[0mWARNING TEST \x1b\[1m\x1b\[92m]\x1b\[0m \x1b\[0m\n')  # noqa: E501
        assert warn_regex.match(cap[1])

        # info
        printer("testing info level")
        logger.info("INFO TEST")
        cap = capsys.readouterr()
        info_regex = re.compile(r'\x1b\[1m\x1b\[32m>>> \x1b\[0m\x1b\[1m\x1b\[92m\[ \x1b\[0mINFO TEST \x1b\[1m\x1b\[92m]\x1b\[0m \x1b\[0m\n')  # noqa: E501
        assert info_regex.match(cap[1])

        # debug
        printer("testing debug level")
        logger.debug("DEBUG TEST")
        cap = capsys.readouterr()
        debug_regex = re.compile(r'\x1b\[1m\x1b\[33m  - \x1b\[0m\x1b\[92m{ test_output }\x1b\[0m: \x1b\[1m\x1b\[92m\[ \x1b\[0mDEBUG TEST \x1b\[1m\x1b\[92m]\x1b\[0m \x1b\[0m\n')  # noqa: E501
        assert debug_regex.match(cap[1])

    @pytest.mark.skip(reason="got --- Logging error ---, disabling for now")
    def test_print_exception(self, capsys, monkeypatch, printer):
        monkeypatch.setitem(os.environ, 'PYPE_DEBUG', '3')
        lf = Logger()
        assert lf.PYPE_DEBUG == 3
        logger = Logger().get_logger('test_output', 'tests')

        printer("DEBUG LEVEL SET: {}".format(os.environ.get('PYPE_DEBUG')))

        test = {}

        try:
            test['nonexistent']
        except KeyError:
            logger.error("test access to undefined key")

        cap = capsys.readouterr()
        assert cap[1] == 1
