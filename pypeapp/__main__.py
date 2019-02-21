import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--install", help="Install environment",
                    action="store_true")
parser.add_argument("--force",
                    help=("Used with --install will force "
                          "installation of environment into destination "
                          "directory even if it exists and is not empty. "
                          "Content will be erased and replaced by "
                          "new environment"),
                    action="store_true"
                    )
parser.add_argument("--deploy", help="Deploy Pype repos and dependencies",
                    action="store_true")
parser.add_argument("--validate", help="Validate Pype deployment",
                    action="store_true")

kwargs, args = parser.parse_known_args()

if kwargs.install:
    from install_env import install
    install(kwargs.force)

if kwargs.validate:
    from deployment import Deployment
    d = Deployment(os.environ.get('PYPE_ROOT', None))
    if (not d.validate()):
        exit(1)
    pass

if kwargs.deploy:
    from deployment import Deployment
    d = Deployment(os.environ.get('PYPE_ROOT', None))
    pass
