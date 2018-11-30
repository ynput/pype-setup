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


create_install () {
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
}


remote_env_not_exists () {
  # todo: need to check if wget completed sucessfully
  if [ -d "$INSTALLATION_DIRECTORY" ] ; then
    if [ ! "$(ls -A $INSTALLATION_DIRECTORY)" ] ; then
      create_install
    else
      remote_env_exists
      CONDA_FILENAME="$MINICONDA_DIRECTORY/miniconda.sh"
    fi
  else
    create_install
  fi
}

installer_exists () {
  # todo: check if copy was successfull
  # Install miniconda
  echo -e "${BIGreen}>>>${RST} Installing Conda root env. Please wait! :)"
  if [ ! -f "$CONDA_FILENAME" ] ; then
    echo -e "${BIRed}!!!${RST} Miniconda not found at [ ${BIWhite}$CONDA_FILENAME${RST} ]"
    exit 1
  fi
  /bin/bash "$CONDA_FILENAME" -b -p "$INSTALLATION_DIRECTORY"
  echo -e "${BIGreen}>>>${RST} Conda created root env in [ ${BIWhite}$INSTALLATION_DIRECTORY${RST} ]"

  # we assume installation now exists

}

installation_exists () {
  # Ensure Remote Avalon environment is available for copying to local
  if [ ! -d "$REMOTE_ENV_DIR" ] ; then
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

    # Deactivate avalon_env local environment as it is more safe to activate it
    # with feeding it into the path (there was a bug with cPython bynary)
    . deactivate

    # Deactivate root environment to escape completely from conda. We dont need it
    # anymore
    . deactivate

    # creates the local folder for environment
    mkdir -p "$REMOTE_ENV_DIR"

    # copy files into local folder for faster redistribution to other pc in network
    echo -e "${BIGreen}>>>${RST} Copying [ ${BIWhite}$LOCAL_ENV_DIR${RST} ] -> [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
    rsync -arh --info=progress2 "$LOCAL_ENV_DIR/" "$REMOTE_ENV_DIR"
    echo -e "${BIGreen}>>>${RST} Remote env created in [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
  fi
}

remote_env_exists () {
  echo -e "-----"
  if [ ! -d "$LOCAL_ENV_DIR" ] ; then
    # if the user's computer doesn't have the local environment yet
    # creates the local folder for environment
    echo -e "${BIGreen}>>>${RST} Creating local env [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
    mkdir -p "$LOCAL_ENV_DIR"
    if [ $? != 0 ] ; then
      echo -e "${BIRed}!!!${RST} Cannot create directory [ ${BIWhite}$LOCAL_ENV_DIR${RST} ] !"
      exit 1
    fi

    # copy files into local folder for faster redistribution to other pc in network
    echo -e "${BIGreen}>>>${RST} Copying [ ${BIWhite}$REMOTE_ENV_DIR${RST} ] -> [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
    rsync -arh --info=progress2 "$REMOTE_ENV_DIR/" "$LOCAL_ENV_DIR"
    echo -e "${BIGreen}>>>${RST} Local env created in [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
  fi
}

local_env_exists () {
  if [ "$SYNC_ENV" = "1" ] ; then
    if [ ! -d "$REMOTE_ENV_DIR" ] ; then
      echo -e "${BIYellow}!!!${RST} Synchronizing is enabled but remote env doesn't exists [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
      echo -e "${BIGreen}>>>${RST} Creating remote env [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
      remote_env_not_exists
      installer_exists
      installation_exists
      remote_env_exists
    fi
    # remote should now exist. Check again and fail miserably if not found
    if [ ! -d "$REMOTE_ENV_DIR" ] ; then
      echo -e "${BIRed}!!!${RST} We couldn't create remote env [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
      echo -e "${BIRed}!!!${RST} Check all output to see what can cause trouble."
      exit 1
    fi
    echo -e "${BIGreen}>>>${RST} Synchronizing environment from REMOTE to [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
    "$REMOTE_ENV_DIR"/bin/python "$PYPE_SETUP_ROOT/bin/sync_dirs.py" "$REMOTE_ENV_DIR" "$LOCAL_ENV_DIR"
  fi
  if [ ! -d "$LOCAL_ENV_DIR" ] ; then
    echo -e "${BIRed}!!!${RST} Local env [ ${BIWhite}$REMOTE_ENV_DIR${RST} ] doesn't exists but it should by this point."
    echo -e "${BIRed}!!!${RST} Something is terribly wrong."
    exit 1
  fi
  if [ "$REMOTE_ENV_ON" = "1" ] ; then
    export PYTHON_ENV="$REMOTE_ENV_DIR"
    echo -e "${BIGreen}>>>${RST} Running remote env from: [ ${BIWhite}$REMOTE_ENV_DIR${RST} ]"
  else
    export PYTHON_ENV="$LOCAL_ENV_DIR"
    echo -e "${BIGreen}>>>${RST} Running local env from: [ ${BIWhite}$LOCAL_ENV_DIR${RST} ]"
    # echo -e "${BICyan}DBG${RST} $PYTHONPATH"
  fi

  export PATH="$PYTHON_ENV:$PYTHON_ENV/Scripts:$PYTHON_ENV/Library/bin:$PYTHON_ENV/bin:$PATH"
  export PYTHONPATH="$PYTHONPATH:$PYPE_SETUP_ROOT:$PYTHON_ENV/Lib/site-packages"
  export GIT_PYTHON_GIT_EXECUTABLE="$PYTHON_ENV/bin/git"

  if [ ! -d "$PYPE_SETUP_ROOT/repos/avalon-core/avalon" ] ; then
    echo -e "${BIYellow}***${RST} Git submodules in [ ${BIWhite}$PYPE_SETUP_ROOT/app/repos/avalon-core${RST} ] are missing ..."

    # Initialize submodules
    echo -e "${BIGreen}>>>${RST} Running Git initialisation ... "
    #echo -e "${BICyan}DBG${RST} $PYTHONPATH"
    python "$PYPE_SETUP_ROOT/bin/initialize_git.py"

    # git submodule update --init --recursive
    # git submodule foreach --recursive git pull origin master
    echo -e "${BIGreen}>>>${RST} Git submodules created and updated"
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
  # we have local env dir
  if [ ! "$(ls -A $LOCAL_ENV_DIR)" ] ; then
    # and it is empty
    remote_env_not_exists
    installer_exists
    installation_exists
    remote_env_exists
    local_env_exists
  else
    # it is not empty
    local_env_exists
    submodules_exists
  fi
else
  #we don't have local env dir
  remote_env_not_exists
  installer_exists
  installation_exists
  remote_env_exists
  local_env_exists
  submodules_exists
fi
