#!/usr/bin/env bash
# part of pype-Setup
# ----------------------------------------------------------------------------
# 1] check for existance of local and remote env
# 2] if local not exists and SYNC is on, sync remote -> local
# 3] if remote not exists or its integrity is invalid, create remote and local
# 4] when above done, set environment
# 5] run it with --pushtoremote to sync local -> remote

rsync_command='rsync -arh'
if [ "$RSYNC_PROGRESS" = "1" ] ; then
  rsync_command='rsync -arh --info=progress2'
fi

check_if_env_match () {
  # is there difference between both dirs?
  echo -e "${BIGreen}>>>${RST} Checking difference between local and remote env (this can take a momet) ..."
  diff -qr $LOCAL_ENV_DIR $REMOTE_ENV_DIR
  if [ $? != 0 ] ; then
    echo -e "${BIYellow}***${RST} local and remote environment are not in sync"
    # if so, REMOTE_ENV_DIR is considered authoritative
    if [ "$SYNC_ENV" = "1" ] ; then
      # sync dir remote -> local
      sync_remote_to_local
      if [ $? = 1 ] ; then
        return 1
      fi
    fi
  fi
  return 0
}

sync_remote_to_local () {
  echo -e "${BIGreen}-->${RST} Syncing [ ${BIWhite}REMOTE${RST} ] -> [ ${BIWhite}LOCAL${RST} ] "
  rcmd="$rsync_command $REMOTE_ENV_DIR/ $LOCAL_ENV_DIR"
  ${rcmd}
  if [ $? != 0 ] ; then
    echo -e "${BIRed}!!!${RST} Sync failed."
    cat <<-EOF
      Syncing of both environment has failed. Please, consult output above for error messages.
EOF
    return 1
  fi
  return 0
}

compute_remote_checksum () {
  echo -e "${BIGreen}>>>${RST} Computing checksum for [ ${BIWhite}$REMOTE_ENV_DIR${RST} ] ..."
  grep -ar -e . "$REMOTE_ENV_DIR" | md5sum | cut -c-32 >> "$REMOTE_ENV_DIR/checksum"
}

compute_local_checksum () {
  echo -e "${BIGreen}>>>${RST} Computing checksum for [ ${BIWhite}$LOCAL_ENV_DIR${RST} ] ..."
  grep -ar -e . "$LOCAL_ENV_DIR" | md5sum | cut -c-32 >> "$LOCAL_ENV_DIR/checksum"
}

check_local_validity () {
  if [ ! -f "$LOCAL_ENV_DIR/checksum" ] ; then
    echo -e "${BIRed}!!!${RST} Checksum file is missing [ ${BIWhite}$LOCAL_ENV_DIR/checksum${RST} ]"
    cat <<-EOF
      Checksum file must be present in environment. Either remote environment is invalid (empty or otherwise),
      or sync didn't finish properly. Check remote environment, delete it if necessary and run installer again.
EOF
    return 1
  fi
  echo -e "${BIGreen}>>>${RST} Computing checksum for [ ${BIWhite}$LOCAL_ENV_DIR${RST} ] ..."
  grep -ar -e . "$LOCAL_ENV_DIR" | md5sum | cut -c-32 | diff -q "$LOCAL_ENV_DIR/checksum" -
  if [ $? != 0 ] ; then
    echo -e "${BIRed}!!!${RST} Checksum is invalid."
    cat <<-EOF
      We've synced either invalid environment or sync failed. Delete both local and remote and run installer again.
EOF
    return 1
  fi
  return 0
}

create_installer () {
  if [ ! -f "$CONDA_FILENAME" ] ; then
    # miniconda cannot be found, so we download it via wget
    echo -e "${BIYellow}***${RST} ${BIBlue}Miniconda.sh${RST} in [ ${BIWhite}$MINICONDA_DIRECTORY${RST} ] is missing ..."
    /bin/mkdir "$MINICONDA_DIRECTORY"
    if [ $? != 0 ] ; then
      echo -e "${BIRed}!!!${RST} Cannot create directory for Miniconda installer."
      return 1
    fi
    # 64bit version; change if needed
    URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    echo -e "${BIGreen}>>>${RST} Downloading Miniconda [ ${BIWhite}$MINICONDA_DIRECTORY${RST} ] ..."
    wget -O "$CONDA_FILENAME" "$URL"
    if [ $? != 0 ] ; then
      echo -e "${BIRed}!!!${RST} Cannot download Miniconda."
      return 1
    fi
    echo -e "${BIGreen}>>>${RST} ${BIBlue}Miniconda${RST} downloaded to in [ ${BIWhite}$CONDA_FILENAME${RST} ]"
  fi
  return 0
}

run_installer () {
    if [ -d "$INSTALLATION_DIRECTORY" ] ; then
      echo -e "${BIGreen}>>>${RST} Updating Conda root env. Please wait ..."
      /bin/bash "$CONDA_FILENAME" -b -u -p "$INSTALLATION_DIRECTORY"
    else
      echo -e "${BIGreen}>>>${RST} Installing Conda root env. Please wait ..."
      /bin/bash "$CONDA_FILENAME" -b -p "$INSTALLATION_DIRECTORY"
    fi

    echo -e "${BIGreen}>>>${RST} Conda created root env in [ ${BIWhite}$INSTALLATION_DIRECTORY${RST} ]"
    return 0
}

create_local_env () {
  # if we disabled sync and are not running from remote
  if [ "$REMOTE_ENV_ON" != "1" ] ; then
    if [ "$SYNC_ENV" != "1" ] ; then
      echo -e "${BIRed}!!!${RST} Sync is disabled and we are forcing local environment."
      echo -e "${BIRed}!!!${RST} Forcing sync"
    fi
  fi
  # check if we have remote env
  if [ -d "$REMOTE_ENV_DIR" ] ; then
    if [ "$REMOTE_ENV_ON" != "1" ] ; then
      # we have, so we'll sync and test later
      sync_remote_to_local
      if [ $? = 1 ] ; then
        return 1
      fi
      # check if we have checksum file
      check_local_validity
      if [ $? = 1 ] ; then
        return 1
      fi
    fi
  else
    if [ "$REMOTE_ENV_ON" == "1" ] ; then
      echo -e "${BIRed}!!!${RST} Forcing remote environment use but it is missing."
      cat <<-EOF
We are forcing use of remote environment, but it wasn't found. If you want
to create new one, delete local environment too and run installer again, or
manually copy existing local environment to remote destination.
EOF
      return 1
    fi
  fi
  # no remote and local is empty
  # run full install
  create_installer
  if [ $? = 1 ] ; then
    return 1
  fi
  run_installer
  if [ $? = 1 ] ; then
    return 1
  fi
  create_remote_env
  if [ $? = 1 ] ; then
    return 1
  fi
  return 0
}

create_remote_env () {
  echo -e "${BIGreen}>>>${RST} Installing remote environment to [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
  export PATH="$INSTALLATION_DIRECTORY/bin:/bin:/sbin:/usr/bin:/usr/sbin"

  echo -e "${BIGreen}>>>${RST} Activating conda ..."
  # Activate conda by activating the root environment
  . activate root

  # create avalon env into local computer first lately to by coppied back to
  # remote directory for faster distribution to other computers in the network
  if [ -d "$LOCAL_ENV_DIR" ] ; then
    echo -e "${BIGreen}>>>${RST} Removing outdated local environment from [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
    rm -rf "$LOCAL_ENV_DIR"
    if [ $? != 0 ] ; then
      echo -e "${BIRed}!!!${RST} Cannot remove local environment."
      cat <<-EOF
Cannot remove directory containing local environment. It could be caused by
permissions or process still running from within. Please consult error messages
above.
EOF
      return 1
    fi
  fi
  echo -e "${BIGreen}>>>${RST} Processing environment for [ ${BIWhite}python 2${RST} ] ..."
  echo -e "${BIGreen}---${RST} Creating conda environment using [ ${BIWhite}$PYPE_SETUP_ROOT/bin/environment2.yml${RST} ] ..."
  conda env create -f "$PYPE_SETUP_ROOT/bin/environment2.yml" -p "$LOCAL_ENV_DIR/python2"
  if [ $? != 0 ] ; then
    echo -e "${BIRed}!!!${RST} Creating conda env failed."
    cat <<-EOF
Unable to create Conda environment. Usually this is caused by insufficient permissions
on local environment directory or some dependency issues in Conda. Please consult error
messages above.
EOF
    exit 1
  fi
  echo -e "${BIGreen}>>>${RST} Conda created [ ${BIWhite}$LOCAL_ENV_DIR/python2${RST} ]"

  echo -e "${BIGreen}>>>${RST} Processing environment for [ ${BIWhite}python 3${RST} ] ..."
  echo -e "${BIGreen}---${RST} Creating conda environment using [ ${BIWhite}$PYPE_SETUP_ROOT/bin/environment3.yml${RST} ] ..."
  conda env create -f "$PYPE_SETUP_ROOT/bin/environment3.yml" -p "$LOCAL_ENV_DIR/python3"
  if [ $? != 0 ] ; then
    echo -e "${BIRed}!!!${RST} Creating conda env failed."
    cat <<-EOF
Unable to create Conda environment. Usually this is caused by insufficient permissions
on local environment directory or some dependency issues in Conda. Please consult error
messages above.
EOF
    exit 1
  fi
  echo -e "${BIGreen}>>>${RST} Conda created [ ${BIWhite}$LOCAL_ENV_DIR/python3${RST} ]"

  # activatin the local env for pip updgrading
  echo -e "${BICyan}-->${RST} Entering local environment ..."
  . activate "$LOCAL_ENV_DIR/python2"
  echo -e "${BIGreen}>>>${RST} Updating PIP to latest version ..."
  python -m pip install --upgrade pip
  if [ $? != 0 ] ; then
    echo -e "${BIRed}!!!${RST} PIP wasn't updated successfully."
    cat <<-EOF
This is not fatal error, but using outdated PIP version can result in many
different compatibility issues later on while installing pipeline dependencies.
EOF
  else
    echo -e "${BIGreen}>>>${RST} Pip updated ..."
  fi

  # Deactivate avalon_env local environment as it is more safe to activate it
  # with feeding it into the path (there was a bug with cPython binary)
  echo -e "${BICyan}<--${RST} Leaving local environment ..."
  . deactivate

  # Deactivate root environment to escape completely from conda. We dont need it
  # anymore
  echo -e "${BICyan}<--${RST} Leaving root environment ..."
  . deactivate

  # create checksum file
  compute_local_checksum

  # creates remote environment dir if not exists
  if [ ! -d "$REMOTE_ENV_DIR" ] ; then
    mkdir -p "$REMOTE_ENV_DIR"
  fi
  # checks if it is not empty
  if [ "$(ls -A $REMOTE_ENV_DIR)" ] ; then
    echo -e "${BIRed}!!!${RST} Remote environment dir exists and is not empty."
    echo -e "${BIRed}!!!${RST} [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
    cat <<-EOF
As a safety measure, we will not install environment to already existing one.
You should check this directory and remove it. After that run installation again.
EOF
      return 1
    fi

  # sync fresh local environment to remote one
  echo -e "${BIGreen}-->${RST} Copying [ ${BIWhite}$LOCAL_ENV_DIR${RST} ] -> [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
  rcmd="$rsync_command $LOCAL_ENV_DIR/ $REMOTE_ENV_DIR"
  ${rcmd}
  if [ $? != 0 ] ; then
    echo -e "${BIRed}!!!${RST} Sync failed."
    cat <<-EOF
Syncing of both environment has failed. Please, consult output above for error messages.
EOF
      return 1
    fi
    echo -e "${BIGreen}>>>${RST} Remote environment created in [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
    return 0
}

main () {
  if [ "$ARGS" = "--pushtoremote" ] ; then
    if [ ! -d "$REMOTE_ENV_DIR" ] ; then
      mkdir -p "$REMOTE_ENV_DIR"
    fi
    if [ $? != 0 ] ; then
      echo -e "${BIRed}!!!${RST} Cannot create remote environment directory [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]."
      return 1
    fi
    echo -e "${BIGreen}-->${RST} Copying [ ${BIWhite}$LOCAL_ENV_DIR${RST} ] -> [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
    rcmd="$rsync_command $LOCAL_ENV_DIR/ $REMOTE_ENV_DIR"
    ${rcmd}
    if [ $? != 0 ] ; then
      echo -e "${BIRed}!!!${RST} Sync failed."
      cat <<-EOF
Syncing of both environment has failed. Please, consult output above for error messages.
EOF
      return 1
    fi
    echo -e "${BIGreen}>>>${RST} Remote environment created in [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
  fi

  if [ "$ARGS" = "--sync" ] ; then
    if [ ! -d "$REMOTE_ENV_DIR" ] ; then
      echo -e "${BIRed}!!!${RST} Cannot sync, remote environment is missing."
      exit 1
    fi
    sync_remote_to_local
    if [ $? = 0 ] ; then
      cho -e "${BIRed}!!!${RST} Sync failed."
      cat <<-EOF
  Syncing of both environment has failed. Please, consult output above for error messages.
EOF
      return 1
    fi
  fi

  # check if local env exist and is not empty
  if [ -d "$LOCAL_ENV_DIR" ] ; then
    # we have local env dir
    if [ ! "$(ls -A $LOCAL_ENV_DIR)" ] ; then
      # but it is empty
      create_local_env
      if [ $? = 1 ] ; then
        return 1
      fi
    else
      # local env exists
      # print warning if remote doesn't exist
      if [ ! -d "$REMOTE_ENV_DIR" ] ; then
        if [ "$SYNC_ENV" = "1" ] ; then
          echo -e "${BIRed}!!!${RST} Cannot sync, remote environment is missing."
          return 1
        else
          if [ "$REMOTE_ENV_ON" = "1" ] ; then
            echo -e "${BIRed}!!!${RST} Cannot use remote environment as it is missing."
            cat <<-EOF
We are forcing use of remote environment, but it wasn't found. If you want
to create new one, delete local environment too and run installer again, or
manually copy existing local environment to remote destination.
EOF
            return 1
          fi
          echo -e "${BIYellow}!!!${RST} Remote environment is missing."
        fi
      else
        # remote env exists
        if [ "$SYNC_ENV" = "1" ] ; then
          # sync to local
          sync_remote_to_local
          if [ $? = 1 ] ; then
            return 1
          fi
          # check if we have checksum file
          check_local_validity
          if [ $? = 1 ] ; then
            return 1
          fi
        fi
      fi
    # end local not empty
    fi
  else
    # local env doesn't exist
    echo -e "${BIYellow}>>>${RST} Local environment not exists: [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
    create_local_env
    if [ $? = 1 ] ; then
      return 1
    fi
  fi

  # now we should have checked environments. Set variables
  if [ "$REMOTE_ENV_ON" = "1" ] ; then
    export PYTHON_ENV="$REMOTE_ENV_DIR"
    echo -e "${BIGreen}>>>${RST} Running remote environment from: [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
  else
    export PYTHON_ENV="$LOCAL_ENV_DIR"
    echo -e "${BIGreen}>>>${RST} Running local environment from: [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
  fi

  export PATH="$PYTHON_ENV/python3/bin:$PATH"
  # hardwired path to python should be changed as conda is updgrading
  # TODO: better handling of python version in path.
  export PYTHONPATH="$PYPE_SETUP_ROOT:$PYTHON_ENV/lib/python3.6/site-packages"
  export GIT_PYTHON_GIT_EXECUTABLE="$PYTHON_ENV/python3/bin/git"
  if [ ! -d "$PYPE_SETUP_ROOT/repos/pype-templates" ] ; then
    echo -e "${BIYellow}***${RST} Git repositories in [ ${BIWhite}$PYPE_SETUP_ROOT/app/repos${RST} ] are missing ..."

    # Initialize submodules
    echo -e "${BIGreen}>>>${RST} Running Git initialization ... "
    #echo -e "${BICyan}DBG${RST} $PYTHONPATH"
    python "$PYPE_SETUP_ROOT/bin/initialize_git.py"
    if [ $? != "0" ] ; then
      echo -e "${BIRed}!!!${RST} Cannot use initialize git repositories."
      cat <<-EOF
Initialization of git repositories essential for pype correct function has failed.
Please check any error messages above.
EOF
      return 1
    fi

    echo -e "${BIGreen}>>>${RST} Git repositories created and updated"
  fi
  return 0
}


MINICONDA_DIRECTORY="$PYPE_SETUP_ROOT/bin/python"
CONDA_FILENAME="$MINICONDA_DIRECTORY/miniconda.sh"
INSTALLATION_DIRECTORY="$MINICONDA_DIRECTORY/__DEV__"
AVALON_ENV_NAME="pype_env"
REMOTE_ENV_DIR="$MINICONDA_DIRECTORY/$AVALON_ENV_NAME"
LOCAL_ENV_DIR="$CONDA_SHARED/$AVALON_ENV_NAME"

# main entry
# -----------------------------

# don't do it as it mess with terminal control
# export PS1="${BIWhite}Avalon:${RST}${BIGreen}\u@\h \w >${RST} "
export PS1="Avalon: \u@\h \w > "

# Change the working directory to the conda-git-deployment directory.
# "pushd" is being used so any UNC paths get mapped until a restart happens.

conda_script=`readlink -f "${BASH_SOURCE[0]}" 2>/dev/null||echo $0`
# The directory where current script resides
conda_script_dir=`dirname "${conda_script}"`

CONDA_DIR=$conda_script_dir
pushd $CONDA_DIR > /dev/null

# Make CWD root of repository.
cd ..

main "$@"
return $?
