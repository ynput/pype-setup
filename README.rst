Readme
######

This is 2.0 incarnation of setup tool to install **pype**.

usage
*****

command line arguments
======================

Use ``pype`` command to launch and control whole pipeline. Pype is using
following subcommands:

deploy
------

Deploy repositories to ``repos``.

Repositories are defined in ``deploy`` folder in json files and can be
overriden by studio specific configuration. Just create
``deploy/studio/deploy.json`` and it will take precedence over factory
configuration.

Additional options:
  - ``-f`` or ``--force`` will force repositories to be overwritten no matter state
    they are in.

.. note:: It needs git installation in **PATH**.

download
--------

Command to download required packages.

Only packages for current platform will be download. To create
multiplatform packages, run ``download`` on every platform you need and
then merge content of ``vendor/packages``.

eventserver
-----------

This command launches ftrack event server.

This should be ideally used by system service (such us systemd or upstart
on linux and window service).

You have to set either proper environment variables to provide URL and
credentials or use option to specify them. If you use ``--store-credentials``
provided credentials will be stored for later use.

Additional options:
  - ``-d`` or ``--debug`` rill raise debug messages verbosity
  - ``--ftrack-url`` or ``FTRACK_SERVER`` specify URL to Ftrack server
  - ``--ftrack-user`` or ``FTRACK_USER`` specify Ftrack API user name
  - ``--ftrack-api-key`` or ``FTRACK_API_KEY`` specify Ftrack API key
  - ``--ftrack-event-path`` set path to event handlers used by event server
  - ``--no-stored-credentials`` will not use credential saved earlier with option
    bellow. You have to set proper argument options or environment variables.
  - ``--store-credentials`` will save credentials specified by argument options or
    environment variables for later use, so they don't need to be specified
    again.

install
-------

This will install pype virtual environment.

Install destination is ``PYPE_ENV``, defaulting to
``c:\\Users\\Public\\pype_env2`` on Windows and ``/opt/pype/pype_env2`` on
linux. Can be overriden by setting ```PYPE_ENV``.

Offline installation will not download packages from internet but will
look for them in ``vendor/packages``. Those can be downloaded by
``download`` command for every platform needed (pip will download packages
only for current platform).

.. note:: This action is run by default if virtual environment is not
          detected. So running for example event server on machine where
          pype was not installed yet will automatically trigger **install**.

Additional options:
  - ``--offline`` will expect that all required packages in
    ``pypeapp/requirements.txt`` are present in ``vendor/packages`` and will not
    try to look for them on internet.
  - ``--force`` will re-create virtual environment even if it exists


mongodb
-------

Will launch local MongoDB server

.. note:: This requires MongoDB installation. It looks for ``mongod`` either
          in ``PATH`` or in default installation location (on Windows).

publish
-------

CLI publishing.

Publish collects json from paths provided as an argument.
More than one path is allowed. This is running **Pyblish** in ``shell`` host.

Additional options:
  - ``-g`` or ``--gui`` will open **Pyblish** GUI
  - ``-d`` or ``--debug`` rill raise debug messages verbosity

test
----

Will run test suite against pype or pype-setup.

Additional options:
  - ``--pype`` will run tests on pype, otherwise on pype-setup

texturecopy
-----------

Copy specified textures to provided asset path.

It validates if project and asset exists. Then it will use
`speedcopy <https://github.com/antirotor/speedcopy>`_ to
copy all textures found in all directories under ``--path`` to destination
folder, determined by template texture in anatomy. I will use source
filename and automatically rise version number on directory.

Result will be copied without directory structure so it will be flat then.
Nothing is written to database.

Additional options:
  - ``-d`` or ``--debug`` rill raise debug messages verbosity
  - ``-p`` or ``--project`` name of project asset is under
  - ``-a`` or ``--asset`` name of asset to which we want to copy textures
  - ``path`` path where textures are found

tray
----

Run pype tray. This is default action if no subcommand is specified.

update-requirements
-------------------

Update requirements based upon current environment.

This will update ``pypeapp/requirements.txt`` with stuff already installed
in current running python environment. Usefull for developer when adding
some dependency for feature.

.. note:: Shortcut for ``pip freeze > pypeapp/requirements.txt``

validate
--------

This command will validate deployment.

It will check if all repositories in ``repos`` are the same as specified in
``deploy.json``.


You can get help in command line using ``pype --help`` or
``pype <subcommand> --help``.

make-docs
---------

This will generate documentation using apidoc and Sphinx for both **pype-setup**
and **pype**. Generated html documentation can be found in ``docs/build/html``

deployment
==========

Deployment is driven by configuration in ``deploy/deploy.json`` where
repositories are specified and additional dependecies. It can be overridden
by creating directory inside ``deploy`` and adding customized ``deploy.json``
and its schema there.

tests
*****

Test runner is **pytest**. For example of writing test look into tests
already in ``tests`` directory.
See `pytest reference <https://docs.pytest.org/en/latest/reference.html>`_.

Write your tests in ``tests`` directory inside hierarchy (either in top
level ``tests`` directory) or inside your package.

You can then run ``pype test`` or ``run_tests`` to enter virtual environment
and execute **pytest**.

To select specific test, you can use:
``pype test -k "_test_deploy"`` to run just test named so.

.. note::
   ``run_tests`` script is deprecated in favor of ``pype test`` command and
   will be removed in future versions.

coverage
********

To see actual coverage, use ``pytest --cov=pypeapp`` within virtualenv. To
generate html report, use ``pytest --cov=pypeapp --cov-report=html:coverage``.
That will generate html report into ``coverage`` directory. From there, when
you click on file name, it will display parts of code uncovered by tests.

About code coverage see
`here <https://hackingthelibrary.org/posts/2018-02-09-code-coverage/>`_.

Coverage is configured in ``.coveragerc``

.. todo:: add coverage to **pype** command for better control path and
          environment.

documentation
*************

Documentation is generated by Sphinx and autodoc. You can now use pype
command ``pype make-docs`` to generate it.

Autodoc is configured to use **rst** docstyle, but takes **napoleon** too.

- RST [`reference <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_]
- Example of `Google Style Python Docstring <http://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google>`_.
- Example of `NumPy Style Python Docstrings <http://www.sphinx-doc.org/en/master/usage/extensions/example_numpy.html#example-numpy>`_.

todo
****
 - Cover more code with tests
 - Write documentation
 - Increase test coverage
