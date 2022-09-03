#!/usr/bin/env bash
#
# Copyright (C) 2022 David Cattermole.
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
# Builds the mmscenegraph library.
#
# This script is assumed to be called with a number of variables
# already set:
#
# - MAYA_VERSION
# - RUST_CARGO_EXE

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

# Store the current working directory, to return to.
CWD=`pwd`

# Path to this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# The root of this project.
PROJECT_ROOT=`readlink -f ${DIR}/../..`
echo "Project Root: ${PROJECT_ROOT}"

# What type of build? "Release" or "Debug"?
BUILD_TYPE="Release"

RELEASE_FLAG=""
BUILD_TYPE_DIR="debug"
if [ ${BUILD_TYPE}=="Release" ]; then
    RELEASE_FLAG="--release"
    BUILD_TYPE_DIR="release"
fi

# Where to find the mmSceneGraph Rust libraries and headers.
MMSCENEGRAPH_INSTALL_PATH="${PROJECT_ROOT}/external/install/maya${MAYA_VERSION}_windows64/mmscenegraph/"
MMSCENEGRAPH_ROOT="${PROJECT_ROOT}/mmscenegraph"
MMSCENEGRAPH_RUST_DIR="${MMSCENEGRAPH_ROOT}/rust"
MMSCENEGRAPH_CPP_DIR="${MMSCENEGRAPH_ROOT}/cppbind"
MMSCENEGRAPH_RUST_TARGET_DIR="${PROJECT_ROOT}/build_mmscenegraph_rust_linux_maya${MAYA_VERSION}"
MMSCENEGRAPH_CPP_TARGET_DIR="${PROJECT_ROOT}/build_mmscenegraph_rust_linux_maya${MAYA_VERSION}"
MMSCENEGRAPH_LIB_DIR="${MMSCENEGRAPH_CPP_TARGET_DIR}/${BUILD_TYPE_DIR}"
MMSCENEGRAPH_INCLUDE_DIR="${MMSCENEGRAPH_CPP_DIR}/include"

echo "Building mmSceneGraph... (${MMSCENEGRAPH_ROOT})"

# Install the needed 'cxxbridge' command.
#
# NOTE: When chaging this version number, make sure to update the
# CXX version used in the C++ buildings, and all the build scripts
# using this value:
# './mmscenegraph/cppbind/Cargo.toml'
# './scripts/internal/build_mmscenegraph_windows64.bat'
${RUST_CARGO_EXE} install cxxbridge-cmd --version 1.0.72

echo "Building C++ Bindings... (${MMSCENEGRAPH_CPP_DIR})"
cd "${MMSCENEGRAPH_CPP_DIR}"
# Assumes 'cxxbridge' (cxxbridge-cmd) is installed.
echo "Generating C++ Headers..."
cxxbridge --header --output "${MMSCENEGRAPH_CPP_DIR}/include/mmscenegraph/_cxx.h"
${RUST_CARGO_EXE} build ${RELEASE_FLAG} --target-dir "${MMSCENEGRAPH_CPP_TARGET_DIR}"

# Build project
cd "${PROJECT_ROOT}"
mkdir -p build_mmscenegraph_linux_maya${MAYA_VERSION}_${BUILD_TYPE}
cd build_mmscenegraph_linux_maya${MAYA_VERSION}_${BUILD_TYPE}

export MAYA_VERSION=${MAYA_VERSION}
${CMAKE_EXE} \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DCMAKE_INSTALL_PREFIX=${INSTALL_MODULE_DIR} \
    -DCMAKE_POSITION_INDEPENDENT_CODE=1 \
    -DCMAKE_CXX_STANDARD=${CXX_STANDARD} \
    -DMMSCENEGRAPH_CXXBRIDGE_EXE=${MMSCENEGRAPH_BUILD_TESTS} \
    -DMMSCENEGRAPH_BUILD_TESTS=${MMSCENEGRAPH_BUILD_TESTS} \
    -DMMSCENEGRAPH_LIB_DIR=${MMSCENEGRAPH_LIB_DIR} \
    -DMMSCENEGRAPH_INCLUDE_DIR=${MMSCENEGRAPH_INCLUDE_DIR} \
    -DBUILD_SHARED_LIBS=OFF \
    ${MMSCENEGRAPH_ROOT}

${CMAKE_EXE} --build . --parallel
${CMAKE_EXE} --install .

# Return back project root directory.
cd ${CWD}
