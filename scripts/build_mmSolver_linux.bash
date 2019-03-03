#!/usr/bin/env bash
# Builds the Maya MatchMove Solver project.

# Maya
MAYA_VERSION=2017
MAYA_LOCATION=/usr/autodesk/maya2017/

# Clear all build information before re-compiling.
# Turn this off when wanting to make small changes and recompile.
FRESH_BUILD=1

# Run the Python API and Solver tests inside Maya, after a
# successfully build an install process.
RUN_TESTS=0

# Use CMinpack?
# CMinpack is the recommended solving library.
WITH_CMINPACK=1

# WARNING: Would you like to use GPL-licensed code? If so you will not
# be able to distribute binary copies of mmSolver.
WITH_GPL_CODE=0

# Where to install the module?
#
# The "$HOME/maya/2017/modules" directory is automatically searched
# for Maya module (.mod) files. Therefore we can install directly.
#
# INSTALL_MODULE_DIR=${PROJECT_ROOT}/modules
INSTALL_MODULE_DIR=${HOME}/maya/2017/modules

# Build ZIP Package.
# For developer use. Make ZIP packages ready to distribute to others.
BUILD_PACKAGE=0

# Do not edit below, unless you know what you're doing.
###############################################################################

# Store the current working directory, to return to.
CWD=`pwd`

# Path to this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# The root of this project.
PROJECT_ROOT=`readlink -f ${DIR}/..`

# Number of CPUs
CPU_NUM=`nproc --all`

# Build mmSolver project
mkdir -p build
cd build
if [ ${FRESH_BUILD} -eq 1 ]; then
    rm --force -R *
fi
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=${INSTALL_MODULE_DIR} \
      -DUSE_GPL_LEVMAR=${WITH_GPL_CODE} \
      -DUSE_CMINPACK=${WITH_CMINPACK} \
      -DCMINPACK_ROOT=${PROJECT_ROOT}/external/install/cminpack \
      -DLEVMAR_ROOT=${PROJECT_ROOT}/external/install/levmar \
      -DMAYA_VERSION=${MAYA_VERSION} \
      -DMAYA_LOCATION=${MAYA_LOCATION} \
      ..
make clean
make -j${CPU_NUM}
make install

# Run tests
if [ ${RUN_TESTS} -eq 1 ]; then
    make test
fi

# Build ZIP package.
if [ ${BUILD_PACKAGE} -eq 1 ]; then
    make package
fi

# Return back project root directory.
cd ${CWD}
