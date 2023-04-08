#!/usr/bin/env bash
#
# Copyright (C) 2019, 2022 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------
#
# Builds the Maya MatchMove Solver project.
#
# This script is assumed to be called with a number of variables
# already set:
#
# - MAYA_VERSION
# - MAYA_LOCATION
# - PYTHON_EXE
# - CMAKE_EXE

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

# Store the current working directory, to return to.
CWD=`pwd`

# Clear all build information before re-compiling.
# Turn this off when wanting to make small changes and recompile.
FRESH_BUILD=1

# Run the Python API and Solver tests inside Maya, after a
# successfully build an install process.
RUN_TESTS=0

# Where to install the module?
#
# The "$HOME/maya/2018/modules" directory is automatically searched
# for Maya module (.mod) files. Therefore we can install directly.
#
INSTALL_MODULE_DIR="${HOME}/maya/${MAYA_VERSION}/modules"

# Build ZIP Package.
# For developer use. Make ZIP packages ready to distribute to others.
BUILD_PACKAGE=1

# What directory to build the project in?
BUILD_DIR_BASE="${PROJECT_ROOT}/../"

# What type of build? "Release" or "Debug"?
BUILD_TYPE=Release

# Build options, to allow faster compilation times. (not to be used by
# users wanting to build this project.)
MMSOLVER_BUILD_PLUGIN=1
MMSOLVER_BUILD_PYTHON=1
MMSOLVER_BUILD_MEL=1
MMSOLVER_BUILD_3DEQUALIZER=1
MMSOLVER_BUILD_SYNTHEYES=1
MMSOLVER_BUILD_BLENDER=1
MMSOLVER_BUILD_QT_UI=1
MMSOLVER_BUILD_RENDERER=1
MMSOLVER_BUILD_DOCS=1
MMSOLVER_BUILD_ICONS=1
MMSOLVER_BUILD_CONFIG=1
MMSOLVER_BUILD_TESTS=0

# Path to this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# The root of this project.
PROJECT_ROOT=`readlink -f ${DIR}/../..`
echo "Project Root: ${PROJECT_ROOT}"

# Set up Python environment.
PYTHON_VIRTUAL_ENV_DIR_NAME="python_venv_linux_maya${MAYA_VERSION}"
source "${PROJECT_ROOT}/scripts/internal/python_venv_activate.bash"

# Paths for dependencies.
MMSCENEGRAPH_INSTALL_DIR="${BUILD_DIR_BASE}/build_mmscenegraph/install/maya${MAYA_VERSION}_linux/"
MMSCENEGRAPH_CMAKE_CONFIG_DIR="${MMSCENEGRAPH_INSTALL_DIR}/lib/cmake/mmscenegraph"

# We don't want to find system packages.
CMAKE_IGNORE_PATH="/lib;/lib64;/usr;/usr/lib;/usr/lib64;/usr/local;/usr/local/lib;/usr/local/lib64;"

# A local copy of LDPK to reduce the amount of downloads to the
# 3DEqualizer website (LDPK doesn't have a git repo to clone from).
LDPK_URL="${PROJECT_ROOT}/external/archives/ldpk-2.8.tar"

# Build mmSolver project
cd ${BUILD_DIR_BASE}
BUILD_DIR_NAME="cmake_linux_maya${MAYA_VERSION}_${BUILD_TYPE}"
BUILD_DIR="${BUILD_DIR_BASE}/build_mmsolver/${BUILD_DIR_NAME}"
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}

export MAYA_VERSION=${MAYA_VERSION}
${CMAKE_EXE} \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DCMAKE_INSTALL_PREFIX=${INSTALL_MODULE_DIR} \
    -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH} \
    -DCMAKE_POSITION_INDEPENDENT_CODE=1 \
    -DCMAKE_CXX_STANDARD=${CXX_STANDARD} \
    -DOPENGL_INCLUDE_DIR=${OPENGL_INCLUDE_DIR} \
    -DMMSOLVER_BUILD_PLUGIN=${MMSOLVER_BUILD_PLUGIN} \
    -DMMSOLVER_BUILD_PYTHON=${MMSOLVER_BUILD_PYTHON} \
    -DMMSOLVER_BUILD_MEL=${MMSOLVER_BUILD_MEL} \
    -DMMSOLVER_BUILD_3DEQUALIZER=${MMSOLVER_BUILD_3DEQUALIZER} \
    -DMMSOLVER_BUILD_SYNTHEYES=${MMSOLVER_BUILD_SYNTHEYES} \
    -DMMSOLVER_BUILD_BLENDER=${MMSOLVER_BUILD_BLENDER} \
    -DMMSOLVER_BUILD_QT_UI=${MMSOLVER_BUILD_QT_UI} \
    -DMMSOLVER_BUILD_RENDERER=${MMSOLVER_BUILD_RENDERER} \
    -DMMSOLVER_BUILD_DOCS=${MMSOLVER_BUILD_DOCS} \
    -DMMSOLVER_BUILD_ICONS=${MMSOLVER_BUILD_ICONS} \
    -DMMSOLVER_BUILD_CONFIG=${MMSOLVER_BUILD_CONFIG} \
    -DMMSOLVER_BUILD_TESTS=${MMSOLVER_BUILD_TESTS} \
    -DMAYA_LOCATION=${MAYA_LOCATION} \
    -DMAYA_VERSION=${MAYA_VERSION} \
    -Dldpk_URL=${LDPK_URL} \
    -Dmmscenegraph_DIR=${MMSCENEGRAPH_CMAKE_CONFIG_DIR} \
    ${PROJECT_ROOT}

${CMAKE_EXE} --build . --parallel

# Comment this line out to stop the automatic install into the home directory.
${CMAKE_EXE} --install .

# Run tests
if [ ${RUN_TESTS} -eq 1 ]; then
    ${CMAKE_EXE} --build . --target test
fi

# Build ZIP package.
if [ ${BUILD_PACKAGE} -eq 1 ]; then
    ${CMAKE_EXE} --build . --target package
fi

# Return back project root directory.
cd ${CWD}
