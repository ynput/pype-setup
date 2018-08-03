"""Use Mayapy for testing

Usage:
    $ mayapy run_maya_tests.py

"""

if __name__ == "__main__":
    import sys
    import nose
    import logging
    import warnings

    from nose_exclude import NoseExclude

    from maya import standalone
    standalone.initialize()

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    log = logging.getLogger()

    # Discard default Maya logging handler
    log.handlers[:] = []

    argv = sys.argv[:]
    argv.extend([

        # Sometimes, files from Windows accessed
        # from Linux cause the executable flag to be
        # set, and Nose has an aversion to these
        # per default.
        "--exe",

        "--verbose",
        "--with-doctest",

        "--with-coverage",
        "--cover-html",
        "--cover-tests",
        "--cover-erase",

        "--exclude-dir=polly/nuke",
        "--exclude-dir=polly/houdini",
        "--exclude-dir=polly/schema",
    ])

    nose.main(argv=argv,
              addplugins=[NoseExclude()])
