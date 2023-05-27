#!/usr/bin/env bash
#
# Copyright (C) 2022, 2023 David Cattermole.
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
# Builds a rust-based library.
#
# This script is assumed to be called with a number of variables
# already set:
#
# - MAYA_VERSION
# - RUST_CARGO_EXE

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

# Name of the rust library that will be built.
PROJECT_NAME=$1

# Store the current working directory, to return to.
CWD=`pwd`

# Path to this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# The root of this project.
PROJECT_ROOT=`readlink -f ${DIR}/../..`
echo "Project Root: ${PROJECT_ROOT}"

# What directory to build the project in?
BUILD_DIR_BASE="${PROJECT_ROOT}/../"

# What type of build? "Release" or "Debug"?
BUILD_TYPE="Release"

RELEASE_FLAG=""
BUILD_TYPE_DIR="debug"
if [ ${BUILD_TYPE}=="Release" ]; then
    RELEASE_FLAG="--release"
    BUILD_TYPE_DIR="release"
fi

# Where to find the ${PROJECT_NAME} Rust libraries and headers.
MM_LIBRARY_INSTALL_PATH="${BUILD_DIR_BASE}/build_${PROJECT_NAME}/install/maya${MAYA_VERSION}_linux/"
MM_LIBRARY_ROOT="${PROJECT_ROOT}/rust/cppbind/${PROJECT_NAME}"
MM_LIBRARY_RUST_DIR="${MM_LIBRARY_ROOT}/rust/src/${PROJECT_NAME}"
MM_LIBRARY_CPP_DIR="${MM_LIBRARY_ROOT}"
MM_LIBRARY_RUST_TARGET_DIR="${BUILD_DIR_BASE}/build_${PROJECT_NAME}/rust_linux_maya${MAYA_VERSION}"
MM_LIBRARY_CPP_TARGET_DIR="${BUILD_DIR_BASE}/build_${PROJECT_NAME}/rust_linux_maya${MAYA_VERSION}"
MM_LIBRARY_LIB_DIR="${MM_LIBRARY_CPP_TARGET_DIR}/${BUILD_TYPE_DIR}"
MM_LIBRARY_INCLUDE_DIR="${MM_LIBRARY_CPP_DIR}/include"

MM_LIBRARY_BUILD_TESTS=0

echo "Building ${PROJECT_NAME}... (${MM_LIBRARY_ROOT})"

# Install the needed 'cxxbridge' command.
#
# NOTE: When changing this version number, make sure to update the
# CXX version used in the C++ buildings, and all the build scripts
# using this value:
# './rust/cppbind/mmscenegraph/Cargo.toml'
# './rust/cppbind/mmimage/Cargo.toml'
# './scripts/internal/build_rust_library_windows64.bat'
${RUST_CARGO_EXE} install cxxbridge-cmd --version 1.0.75
MM_LIBRARY_CXXBRIDGE_EXE="${HOME}\.cargo\bin\cxxbridge"

echo "Building C++ Bindings... (${MM_LIBRARY_CPP_DIR})"
cd "${MM_LIBRARY_CPP_DIR}"
# Assumes 'cxxbridge' (cxxbridge-cmd) is installed.
echo "Generating C++ Headers..."
cxxbridge --header --output "${MM_LIBRARY_CPP_DIR}/include/${PROJECT_NAME}/_cxx.h"
${RUST_CARGO_EXE} build ${RELEASE_FLAG} --target-dir "${MM_LIBRARY_CPP_TARGET_DIR}"

# Build project
cd ${BUILD_DIR_BASE}
BUILD_DIR_NAME="cmake_linux_maya${MAYA_VERSION}_${BUILD_TYPE}"
BUILD_DIR="${BUILD_DIR_BASE}/build_${PROJECT_NAME}/${BUILD_DIR_NAME}"
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}

export MAYA_VERSION=${MAYA_VERSION}
${CMAKE_EXE} \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DCMAKE_INSTALL_PREFIX=${MM_LIBRARY_INSTALL_PATH} \
    -DCMAKE_POSITION_INDEPENDENT_CODE=1 \
    -DCMAKE_CXX_STANDARD=${CXX_STANDARD} \
    -DMM_LIBRARY_CXXBRIDGE_EXE=${MM_LIBRARY_CXXBRIDGE_EXE} \
    -DMM_LIBRARY_BUILD_TESTS=${MM_LIBRARY_BUILD_TESTS} \
    -DMM_LIBRARY_LIB_DIR=${MM_LIBRARY_LIB_DIR} \
    -DMM_LIBRARY_INCLUDE_DIR=${MM_LIBRARY_INCLUDE_DIR} \
    -DBUILD_SHARED_LIBS=OFF \
    ${MM_LIBRARY_ROOT}

${CMAKE_EXE} --build . --parallel
${CMAKE_EXE} --install .

# Return back project root directory.
cd ${CWD}
