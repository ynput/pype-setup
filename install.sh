#!/usr/bin/env bash
#
# Pype install
#

# Full path of the current script
THIS=`readlink -f "${BASH_SOURCE[0]}" 2>/dev/null||echo $0`
# The directory where current script resides
DIR=`dirname "${THIS}"`

ARG=$1

print_dependency_help () {
  cat <<-EOF
    Successfull installation of Pype needs few system tools already installed.
    We need wget, git, gcc, md5sum and rsync. Please refer to your system's user guide how
    to install them. To make all more readable, update rsync to > 3.1.0.
EOF
}
# subshell will not work for symlinks. Use readlink then.
export PYPE_SETUP_ROOT="$(cd $DIR; pwd)"
export PYPE_STUDIO_TEMPLATES="$PYPE_SETUP_ROOT/repos/pype-templates"

# basic Setup
export PYPE_SETUP_GIT_URL="git@bitbucket.org:pypeclub/pype-setup.git"
export PYPE_SETUP_GIT_BRANCH="master"
export PYPE_STUDIO_TEMPLATES_NAME="pype-templates"
export PYPE_STUDIO_TEMPLATES_URL="git@bitbucket.org:pypeclub/pype-templates.git"
export PYPE_STUDIO_TEMPLATES_SUBM="repos"
export PYPE_STUDIO_TEMPLATES_BRANCH="master"
# Directory, where will be local evironment. Should be accessible for all
CONDA_SHARED="/tmp"

# debugging
export PYPE_DEBUG=1

# maintain python environment
# will synchronize remote with local
SYNC_ENV=0
# will switch to remote
REMOTE_ENV_ON=0

# Load colors definitions for easy output coloring
source "$PYPE_SETUP_ROOT/bin/colors.sh"

echo -e "${IGreen}>>>${RST} ${BIWhite}Welcome to Pipe Club${RST}"

# test system dependencies
echo -e "${IGreen}>>>${RST} Checking for dependencies ..."
echo -e "${BIYellow}---${RST} looking for ${BIWhite}[ wget ]${RST} ... \c"
command -v wget >/dev/null 2>&1 || { echo -e "${BIRed}FAILED${RST}"; print_dependency_help; exit 1; }
echo -e "${BIGreen}OK${RST}"
echo -e "${BIYellow}---${RST} looking for ${BIWhite}[ git ]${RST} ... \c"
command -v git >/dev/null 2>&1 || { echo -e "${BIRed}FAILED${RST}"; print_dependency_help; exit 1; }
echo -e "${BIGreen}OK${RST}"
echo -e "${BIYellow}---${RST} looking for ${BIWhite}[ rsync ]${RST} ... \c"
command -v wget >/dev/null 2>&1 || { echo -e "${BIRed}FAILED${RST}"; print_dependency_help; exit 1; }
echo -e "${BIGreen}OK${RST}"
echo -e "${BIYellow}---${RST} checking ${BIWhite}[ rsync ]${RST} version ... \c"
RSYNC_VERSION="$(rsync --version | awk 'NR==1 {print $3}')"
oIFS="$IFS"
IFS=.
set -- $RSYNC_VERSION
IFS="$oIFS"
RSYNC_PROGRESS=0
if [ "$1" -ge "3" ] && [ "$2" -ge "1" ] && [ "$3" -ge "0" ] ; then
echo -e "${BIGreen}$1.$2.$3${RST}"
RSYNC_PROGRESS=1
else
echo -e "${BIYellow}old - $1.$2.$3${RST}"
fi
echo -e "${BIYellow}---${RST} looking for ${BIWhite}[ gcc ]${RST} ... \c"
command -v gcc >/dev/null 2>&1 || { echo -e "${BIRed}FAILED${RST}"; print_dependency_help; exit 1; }
echo -e "${BIGreen}OK${RST}"
echo -e "${BIYellow}---${RST} looking for ${BIWhite}[ md5sum ]${RST} ... \c"
command -v md5sum >/dev/null 2>&1 || { echo -e "${BIRed}FAILED${RST}"; print_dependency_help; exit 1; }
echo -e "${BIGreen}OK${RST}"


echo -e "${IGreen}>>>${RST} launching Conda ..."

# Launch Conda
source "$PYPE_SETUP_ROOT/bin/launch_conda.sh"
