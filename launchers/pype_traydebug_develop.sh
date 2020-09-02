#!/usr/bin/env bash
#     ____________  ____      ____  ____________  ____________
#   / \           \/\   \    /\   \/\           \/\           \
#   \  \      ---  \ \   \___\_\   \ \      ---  \ \     ------\
#    \  \     _____/  \____     ____\ \     _____/  \    \___\
#     \  \    \__/  \____/ \    \__/\  \    \__/  \  \    -------\
#      \  \____\         \  \____\   \  \____\     \  \___________\
#       \/____/           \/____/     \/____/       \/___________/
#
#                    ...  █░░ --=[ CLuB ]]=-- ░░█ ...

# Full path of the current script
THIS=`readlink -f "${BASH_SOURCE[0]}" 2>/dev/null||echo $0`
# The directory where current script resides
DIR=`dirname "${THIS}"`
export PYPE_SETUP_PATH="$(cd $DIR/../ ; pwd)"
export PYPE_DEBUG=3

gnome-terminal -- "$PYPE_SETUP_PATH/pype" tray --debug
