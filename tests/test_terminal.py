"""
This is jus sample test
TODO: make it real.
"""
import pytest
from pypeapp import Terminal
from colorama import Fore, Style, init


class TestTerminal(object):
    def test_log(self):
        init()
        t = Terminal()
        test_1 = r">>> blabla"
        res_1 = (Style.BRIGHT + Fore.GREEN +
                 r">>> " + Style.RESET_ALL + "blabla" + Style.RESET_ALL)

        assert t.log(test_1) == res_1
        pass

    def test_echo(self):
        pass
