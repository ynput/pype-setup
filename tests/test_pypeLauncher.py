import os
import pytest
from pypeapp.pypeLauncher import PypeLauncher


class TestPypeLauncher():

    @pytest.mark.skip(reason="tests of PypeLauncher not ready yet")
    def test_traydebug_env(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'PYPE_SETUP_PATH', os.path.abspath('.'))

        PypeLauncher(['--traydebug'])

        assert os.environ.get('PYPE_DEBUG') == '3'
