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

    def test_mongo_settings(self, monkeypatch, printer):
        from pypeapp.lib.log import _mongo_settings
        test_url_1 = 'mongodb://host:1111'
        printer("testing {}".format(test_url_1))
        monkeypatch.setitem(os.environ, 'PYPE_LOG_MONGO_URL', test_url_1)
        with pytest.raises(RuntimeError) as excinfo:
            host, port, database, username, password, collection, auth_db = _mongo_settings()
        assert "missing database" in str(excinfo.value)

        test_url_2 = 'mongodb://host:1111/database'
        printer("testing {}".format(test_url_2))
        monkeypatch.setitem(os.environ, 'PYPE_LOG_MONGO_URL', test_url_2)
        host, port, database, username, password, collection, auth_db = _mongo_settings()
        assert host == 'host'
        assert port == 1111
        assert database == 'database'
        assert collection is None
        assert username is None
        assert password is None
        assert auth_db == ''

        test_url_3 = 'mongodb://host:1111/database/collection'
        printer("testing {}".format(test_url_3))
        monkeypatch.setitem(os.environ, 'PYPE_LOG_MONGO_URL', test_url_3)
        host, port, database, username, password, collection, auth_db = _mongo_settings()
        assert host == 'host'
        assert port == 1111
        assert database == 'database'
        assert collection == 'collection'
        assert username is None
        assert password is None
        assert auth_db == ''

        test_url_4 = 'mongodb://user@host:1111/database/collection'
        printer("testing {}".format(test_url_4))
        monkeypatch.setitem(os.environ, 'PYPE_LOG_MONGO_URL', test_url_4)
        host, port, database, username, password, collection, auth_db = _mongo_settings()
        assert host == 'host'
        assert port == 1111
        assert database == 'database'
        assert collection == 'collection'
        assert username == 'user'
        assert password is None
        assert auth_db == ''

        test_url_5 = 'mongodb://user:password@host:1111/database/collection?authSource=auth'
        printer("testing {}".format(test_url_5))
        monkeypatch.setitem(os.environ, 'PYPE_LOG_MONGO_URL', test_url_5)
        host, port, database, username, password, collection, auth_db = _mongo_settings()
        assert host == 'host'
        assert port == 1111
        assert database == 'database'
        assert collection == 'collection'
        assert username == 'user'
        assert password == 'password'
        assert auth_db == 'auth'

        test_url_6 = 'mongodb://host:1d'
        printer("testing {}".format(test_url_6))
        monkeypatch.setitem(os.environ, 'PYPE_LOG_MONGO_URL', test_url_6)
        with pytest.raises(RuntimeError) as excinfo:
            host, port, database, username, password, collection, auth_db = _mongo_settings()
        assert "invalid port" in str(excinfo.value)
