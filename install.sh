#!/bin/bash
#
# Pype-setup
# Linux server launcher
#

# Full path of the current script
THIS=`readlink -f "${BASH_SOURCE[0]}" 2>/dev/null||echo $0`
# The directory where current script resides
DIR=`dirname "${THIS}"`

print_dependency_help () {
  cat <<-EOF
    Successfull installation of Pype needs few system tools already installed.
    We need wget, git, gcc and rsync. Please refer to your system's user guide how
    to install them.
EOF
}
# subshell will not work for symlinks. Use readlink then.
export PYPE_SETUP_ROOT="$(cd $DIR; pwd)"
export PYPE_STUDIO_TEMPLATES="$(cd $PYPE_SETUP_ROOT/studio/studio-templates; pwd)"

# basic Setup
export PYPE_SETUP_GIT_URL="git@github.com:pypeclub/pype-setup.git"
export PYPE_SETUP_GIT_BRANCH="master"
export PYPE_STUDIO_TEMPLATES_URL="git@github.com:pypeclub/studio-templates.git"
export PYPE_STUDIO_TEMPLATES_BRANCH="master"
# Directory, where will be local evironment. Should be accessible for all
CONDA_SHARED="/tmp"

# debugging
export PYPE_DEBUG=1
export PYPE_DEBUG_STDOUT=1

# maintain python environment
# will synchronize remote with local
SYNC_ENV=1
# will switch to remote
REMOTE_ENV_ON=1

# Load colors definitions for easy output coloring
source "$PYPE_SETUP_ROOT/bin/colors.sh"

echo -e "${IGreen}>>>${RST} ${BIWhite}Welcome to Pipe Club${RST}"

# test system dependencies
echo -e "${BIYellow}---${RST} looking for ${BIWhite}[ wget ]${RST} ... \c"
command -v wget >/dev/null 2>&1 || { echo -e "${BIRed}FAILED${RST}"; print_dependency_help; exit 1; }
echo -e "${BIGreen}OK${RST}"
echo -e "${BIYellow}---${RST} looking for ${BIWhite}[ git ]${RST} ... \c"
command -v git >/dev/null 2>&1 || { echo -e "${BIRed}FAILED${RST}"; print_dependency_help; exit 1; }
echo -e "${BIGreen}OK${RST}"
echo -e "${BIYellow}---${RST} looking for ${BIWhite}[ rsync ]${RST} ... \c"
command -v wget >/dev/null 2>&1 || { echo -e "${BIRed}FAILED${RST}"; print_dependency_help; exit 1; }
echo -e "${BIGreen}OK${RST}"
echo -e "${BIYellow}---${RST} looking for ${BIWhite}[ gcc ]${RST} ... \c"
command -v gcc >/dev/null 2>&1 || { echo -e "${BIRed}FAILED${RST}"; print_dependency_help; exit 1; }
echo -e "${BIGreen}OK${RST}"


echo -e "${IGreen}>>>${RST} launching Conda ..."

# Launch Conda
source "$PYPE_SETUP_ROOT/bin/launch_conda.sh"

export PYTHONPATH="$PYPE_SETUP_ROOT"
