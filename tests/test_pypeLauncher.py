import os
import pytest
from pypeapp.pypeLauncher import PypeLauncher
from .test_storage import TestStorage


class TestPypeLauncher():

    @pytest.mark.skip(reason="tests of PypeLauncher not ready yet")
    def test_traydebug_env(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'PYPE_ROOT', os.path.abspath('.'))

        PypeLauncher(['--traydebug'])

        assert os.environ.get('PYPE_DEBUG') == '3'

    def test_path_remapping(self, tmp_path, monkeypatch):
        test_env = {
            "FOO": "orange:apple",
            "BAR": "K:\\Windows\\Path\\Pear",
            "BAZ": "/mnt/path/Pear",
            "GOO": [
                "/mnt/path/banana",
                {"BOO": "/mnt/path/kiwi"}
            ]
        }

        test_storage = """\
{
    "test": {
        "dog": {
            "path": {
                "windows": "//store/mnt/path",
                "linux": "/mnt/path",
                "darwin": "/Volumes/path"
            },
            "mount": {
                "windows": "K:\\\\Windows\\\\Path",
                "linux": "/mnt/path",
                "darwin": "/Volumes/path"
            }
        }
    }
}
"""

        TestStorage().setup_storage(test_storage, tmp_path, monkeypatch)
        result = PypeLauncher().path_remapper(test_env, "windows", "linux")
        assert result.get("BAR") == "/mnt/path/Pear"

        result = PypeLauncher().path_remapper(test_env, "linux", "windows")
        assert result.get("BAZ") == r"\\store\mnt\path\Pear"
        assert result.get("BAR") == r"K:\Windows\Path\Pear"
        assert result.get("FOO") == "orange:apple"
        assert result.get("GOO")[0] == r"\\store\mnt\path\banana"
        assert result.get("GOO")[1].get("BOO") == r"\\store\mnt\path\kiwi"
