#!/bin/bash
# part of pype-Setup
#

shared_permission_help () {
  # print help for shared dirname
  cat <<-EOF
    Above error is probably caused by insufficient permissions. For local installation, Pype setup
    requires directory where possibly all relevant users of Avalon on this computer can access data. We also
    do not recommend to setup Pype as a root user. If you do not have rights to setup such shared folder,
    please contact your system administrator.
EOF
}


remote_env_not_exists () {
  # todo: need to check if wget completed sucessfully
  if [ -d "$INSTALLATION_DIRECTORY" ] ; then
    local_env_exists
  fi
  echo -e "${BIYellow}***${RST} Conda installation dir [ ${BIWhite}$INSTALLATION_DIRECTORY${RST} ] is missing ..."
  if [ ! -f "$MINICONDA_DIRECTORY/miniconda.sh" ] ; then
    # miniconda cannot be found, so we download it via wget
    echo -e "${BIYellow}***${RST} ${BIBlue}Miniconda.sh${RST} in [ ${BIWhite}$MINICONDA_DIRECTORY${RST} ] is missing ..."
    /bin/mkdir "$MINICONDA_DIRECTORY"
    echo -e "${BIGreen}>>>${RST} Created dir [ ${BIWhite}$MINICONDA_DIRECTORY${RST} ]"
    CONDA_FILENAME="$MINICONDA_DIRECTORY/miniconda.sh"

    # 64bit version; change if needed
    URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    wget -O "$CONDA_FILENAME" "$URL"
    echo -e "${BIGreen}>>>${RST} ${BIBlue}Miniconda${RST} downloaded to in [ ${BIWhite}$CONDA_FILENAME${RST} ]"
  fi

  # we assume installer now exists
  installer_exists
}

installer_exists () {
  # todo: check if copy was successfull
  # Install miniconda
  echo -e "${BIGreen}>>>${RST} Installing Conda root env. Please wait! :)"
  if [ ! -f "$CONDA_FILENAME" ] ; then
    echo -e "${BIRed}!!!${RST} Miniconda not found at [ ${BIWhite}$CONDA_FILENAME${RST} ]"
    remote_env_not_exists
  fi
  /bin/bash "$CONDA_FILENAME" -b -p "$INSTALLATION_DIRECTORY"
  echo -e "${BIGreen}>>>${RST} Conda created root env in [ ${BIWhite}$INSTALLATION_DIRECTORY${RST} ]"

  # we assume installation now exists
  installation_exists
}

installation_exists () {
  # Ensure Remote Avalon environment is available for copying to local
  if [ -d "$REMOTE_ENV_DIR" ] ; then
    remote_env_exists
  fi
  echo -e "${BIGreen}>>>${RST} Remote environment in [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
  export PATH="$INSTALLATION_DIRECTORY/bin:/bin:/sbin:/usr/bin:/usr/sbin"

  echo -e "${BIGreen}>>>${RST} Activating conda ..."
  # Activate conda by activating the root environment
  . activate root

  # create avalon env into local computer first lately to by coppied back to
  # remote directory for faster distribution to other computers in the network
  if [ -d "$LOCAL_ENV_DIR" ] ; then
    echo -e "${BIGreen}>>>${RST} Removing outdated environment from [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
    rm -rf "$LOCAL_ENV_DIR"
  fi
  echo -e "${BIGreen}>>>${RST} Creating conda env using [ ${BIWhite}$PYPE_SETUP_ROOT/bin/environment.yml${RST} ] ..."
  conda env create -f "$PYPE_SETUP_ROOT/bin/environment.yml" -p "$LOCAL_ENV_DIR"
  if [ $? != 0 ] ; then
    echo -e "${BIRed}!!!${RST} Creating conda env failed."
    shared_permission_help
    exit 1
  fi
  echo -e "${BIGreen}>>>${RST} Conda created [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"

  # activatin the local env for pip updgrading
  . activate "$LOCAL_ENV_DIR"
  python -m pip install --upgrade pip
  echo -e "${BIGreen}>>>${RST} Pip updated to last version to local env"

  # Deactivate avalon_env local environment as it is more save to activate it
  # with feeding it into the path (there was a bug with cPython bynary)
  . deactivate

  # Deactivate root environment to escape completely from conda. We dont need it
  # anymore
  . deactivate

  # creates the local folder for environment
  mkdir -p "$REMOTE_ENV_DIR"

  # copy files into local folder for faster redistribution to other pc in network
  cp -r "$LOCAL_ENV_DIR" "$REMOTE_ENV_DIR"
  echo -e "${BIGreen}>>>${RST} Remote env created in [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"

  # we assume remote env exists
  remote_env_exists

}

remote_env_exists () {
  if [ -d "$LOCAL_ENV_DIR" ] ; then
    local_env_exists
  else
    # if the user's computer doesn't have the local environment yet
    # creates the local folder for environment
    mkdir -p "$LOCAL_ENV_DIR"
    if [ $? != 0 ] ; then
      echo -e "${BIRed}!!!${RST} Cannot create directory [ ${BIWhite}$LOCAL_ENV_DIR${RST} ] !"
      exit 1
    fi

    # copy files into local folder for faster redistribution to other pc in network
    cp -r "$REMOTE_ENV_DIR" "$LOCAL_ENV_DIR"
    echo -e "${BIGreen}>>>${RST} Local env created in [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"

    # assume local environment exists
    local_env_exists
  fi
}

local_env_exists () {
  if [ "$SYNC_ENV" = "1" ] ; then
    if [! -d "$REMOTE_ENV_DIR" ] ; then
      remote_env_not_exists
    else
      echo -e "${BIGreen}>>>${RST} Synchronizing environment from REMOTE to [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
      "$REMOTE_ENV_DIR"/python.exe "$PYPE_SETUP_ROOT/bin/sync_dirs.py" "$REMOTE_ENV_DIR" "$LOCAL_ENV_DIR"
    fi
  fi

  if [ "$REMOTE_ENV_ON" = "1" ] ; then
    export PATH="$REMOTE_ENV_DIR:$REMOTE_ENV_DIR/Scripts:$REMOTE_ENV_DIR/Library/bin:$REMOTE_ENV_DIR/bin:$PATH"
    echo -e "${BIGreen}>>>${RST} Running remote env from: [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
  else
    export PATH="$LOCAL_ENV_DIR:$LOCAL_ENV_DIR/Scripts:$LOCAL_ENV_DIR/Library/bin:$LOCAL_ENV_DIR/bin:$PATH"
    echo -e "${BIGreen}>>>${RST} Running local env from: [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
  fi

  if [ -d "$PYPE_SETUP_ROOT/app/repos/avalon-core/avalon" ] ; then
    submodules_exists
  else

      echo -e "${BIYellow}***${RST} Git submodules in [ ${BIWhite}$PYPE_SETUP_ROOT/app/repos/avalon-core${RST} ] are missing ..."

      # Initialize submodules
      echo -e "${BIGreen}>>>${RST} Running Git initialisation ... "
      if [ ! -d "$PYPE_SETUP_ROOT/.git" ] ; then
        python "$PYPE_SETUP_ROOT/bin/initialize_git.py"
      fi
      git submodule update --init --recursive
      git submodule foreach --recursive git pull origin master
      echo -e "${BIGreen}>>>${RST} Git submodules created and updated"

      # Assume git submodules are initialized

      submodules_exists
   fi


}

submodules_exists () {
  echo -e "${BIWhite}***${RST} All setup and good to go!"
}

export PS1="${BIWhite}Avalon:${RST}${BIGreen}\u@\h \w >${RST} "

# Change the working directory to the conda-git-deployment directory.
# "pushd" is being used so any UNC paths get mapped until a restart happens.

conda_script=`readlink -f "${BASH_SOURCE[0]}" 2>/dev/null||echo $0`
# The directory where current script resides
conda_script_dir=`dirname "${conda_script}"`

CONDA_DIR=$conda_script_dir
pushd $CONDA_DIR > /dev/null

# Make CWD root of avalon-environment repository.
cd ..

# Get installation directory.
MINICONDA_DIRECTORY="$PYPE_SETUP_ROOT/bin/python"
INSTALLATION_DIRECTORY="$MINICONDA_DIRECTORY/__DEV__"

AVALON_ENV_NAME="pype_env"
REMOTE_ENV_DIR="$MINICONDA_DIRECTORY/$AVALON_ENV_NAME"

# create local data disk paths
LOCAL_ENV_DIR="$CONDA_SHARED/$AVALON_ENV_NAME"

if [ -d "$LOCAL_ENV_DIR" ] ; then
  if [ ! "$(ls -A $LOCAL_ENV_DIR)" ] ; then
    remote_env_not_exists
  else
    local_env_exists
  fi
else
  remote_env_not_exists
fi
