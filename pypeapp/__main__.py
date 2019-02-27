import argparse
import os
import sys

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
parser.add_argument("--skipmissing", help=("Skip missing repos during"
                                           "validation"), action="store_true")

kwargs, args = parser.parse_known_args()

if kwargs.install:
    from install_env import install
    install(kwargs.force)

if kwargs.validate:
    from deployment import Deployment, DeployException
    d = Deployment(os.environ.get('PYPE_ROOT', None))
    try:
        d.validate(kwargs.skipmissing)
    except DeployException:
        sys.exit(200)

if kwargs.deploy:
    from deployment import Deployment, DeployException
    d = Deployment(os.environ.get('PYPE_ROOT', None))
    try:
        d.deploy()
    except DeployException:
        sys.exit(200)
    pass
