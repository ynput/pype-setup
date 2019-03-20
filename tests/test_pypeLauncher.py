import os
import pytest
from .test_deployment import TestDeployment
from pypeapp.pypeLauncher import PypeLauncher


class TestPypeLauncher():

    def test_traydebug_env(self, monkeypatch):
        # d = TestDeployment().setup_deployment(tmp_path)
        monkeypatch.setitem(os.environ, 'PYPE_ROOT', os.path.abspath('.'))

        PypeLauncher(['--traydebug'])
        assert os.environ.get('PYPE_DEBUG') == '3'
