#!/bin/bash
#
# Pype command
#

# Full path of the current script
THIS=`readlink -f "${BASH_SOURCE[0]}" 2>/dev/null||echo $0`
# The directory where current script resides
DIR=`dirname "${THIS}"`

export PYPE_SETUP_ROOT="$(cd $DIR; pwd)"

source "$PYPE_SETUP_ROOT/bin/colors.sh"

echo -e "${IGreen}>>>${RST} ${BIWhite}Welcome to Pipe Club${RST}"

python "$PYPE_SETUP_ROOT/app/pype-start.py" "$@"
