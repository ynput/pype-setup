# pype-setup 2.0

This is 2.0 incarnation of setup tool to install **pype**.

### usage:

Use `pype` command to launch and control whole pipeline. Available command
line arguments are:

**--install**: This will install **pype** if it's environment wasn't found. When something is
detected in environment destination directory, installation will abort unless used with **--force**. That will force install to clean destination environment.

Installation will download and setup python dependencies and then it will load `deploy/deploy.json`. Using this file setup will populate repositories in `repos`. If they exists but differs with specified ones (they are on different branch for example), setup will switch them to
correct one. Only if their working tree is clean. If there is another directory in `deploy` containing `deploy.json`, it is then considered as an override and setup will use that.

You can use **--download** to just download required python packages to `vendor/packages` to be
used later with **--offline** switch that will use those downloaded without connecting to internet. Useful in scenarios where internet connection is unavailable.

**--ignore** switch can be used to ignore inconsistent setup of repositories when launching **pype**. Useful during development, but dangerous as it can result in crashes and malfunctions.

### tests:

Write your tests in `tests` directory inside hierarchy (either in top level `tests` directory) or inside your package. Then run `run_tests` to enter virtual environment and execute **pytest**.

### todo:

 - Implement rest of pype-setup 1.0
 - Cover more code with tests
