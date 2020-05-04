# -*- coding: utf-8 -*-
"""Main entry point for Pype command."""
from . import cli
import sys
import traceback

if __name__ == '__main__':
    try:
        cli.main(obj={}, prog_name="pype")
    except Exception as e:
        print("!!! Pype crashed:")
        traceback.print_exception(type(e), e, e.__traceback__)
        sys.exit(1)
