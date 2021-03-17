#!/usr/bin/env bash

realpath () {
  echo $(cd $(dirname "$1") || return; pwd)/$(basename "$1")
}

export PYPE_LOG_NO_COLORS="1"
echo ">>> running as: $(who)"

echo ">>> launching mayabatch via pype with arguments $@"
export PYPE_SETUP_PATH=$(dirname $(dirname "$(realpath ${BASH_SOURCE[0]})"))
source "$PYPE_SETUP_PATH/pype" launch --app mayabatch_$PYPE_MAYA_VERSION $@
