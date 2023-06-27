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

# Where to find the mmsolverlibs Rust libraries and headers.
MMSOLVERLIBS_INSTALL_PATH="${BUILD_DIR_BASE}/build_mmsolverlibs/install/maya${MAYA_VERSION}_linux/"
MMSOLVERLIBS_ROOT="${PROJECT_ROOT}/lib"
MMSOLVERLIBS_RUST_ROOT="${MMSOLVERLIBS_ROOT}/mmsolverlibs"
MMSOLVERLIBS_CPP_TARGET_DIR="${BUILD_DIR_BASE}/build_mmsolverlibs/rust_linux_maya${MAYA_VERSION}"
MMSOLVERLIBS_LIB_DIR="${MMSOLVERLIBS_CPP_TARGET_DIR}/${BUILD_TYPE_DIR}"
MMSOLVERLIBS_INCLUDE_DIR="${MMSOLVERLIBS_ROOT}/include"

MMSOLVERLIBS_BUILD_TESTS=1

echo "Building mmsolverlibs... (${MMSOLVERLIBS_ROOT})"

# Check if 'cxxbridge.exe' is installed or not, and then install it if
# not.
#
# https://stackoverflow.com/questions/592620/how-can-i-check-if-a-program-exists-from-a-bash-script
if ! command -v cxxbridge &> /dev/null
then
    # Install the needed 'cxxbridge' command.
    #
    # NOTE: When changing this version number, make sure to update the
    # CXX version used in the C++ buildings, and all the build scripts
    # using this value:
    # './rust/cppbind/mmscenegraph/Cargo.toml'
    # './rust/cppbind/mmimage/Cargo.toml'
    # './scripts/internal/build_rust_library_windows64.bat'
    ${RUST_CARGO_EXE} install cxxbridge-cmd --version 1.0.75
fi
MMSOLVERLIBS_CXXBRIDGE_EXE="${HOME}\.cargo\bin\cxxbridge"

cd ${MMSOLVERLIBS_RUST_ROOT}
${RUST_CARGO_EXE} build ${RELEASE_FLAG} --target-dir ${MMSOLVERLIBS_CPP_TARGET_DIR}

# A local copy of LDPK to reduce the amount of downloads to the
# 3DEqualizer website (LDPK doesn't have a git repo to clone from).
LDPK_URL="${PROJECT_ROOT}/external/archives/ldpk-2.8.tar"

# Build project
cd ${BUILD_DIR_BASE}
BUILD_DIR_NAME="cmake_linux_maya${MAYA_VERSION}_${BUILD_TYPE}"
BUILD_DIR="${BUILD_DIR_BASE}/build_mmsolverlibs/${BUILD_DIR_NAME}"
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}

export MAYA_VERSION=${MAYA_VERSION}
${CMAKE_EXE} \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DCMAKE_INSTALL_PREFIX=${MMSOLVERLIBS_INSTALL_PATH} \
    -DCMAKE_POSITION_INDEPENDENT_CODE=1 \
    -DCMAKE_CXX_STANDARD=${CXX_STANDARD} \
    -DMMSOLVERLIBS_CXXBRIDGE_EXE=${MMSOLVERLIBS_CXXBRIDGE_EXE} \
    -DMMSOLVERLIBS_BUILD_TESTS=${MMSOLVERLIBS_BUILD_TESTS} \
    -DMMSOLVERLIBS_LIB_DIR=${MMSOLVERLIBS_LIB_DIR} \
    -Dldpk_URL=${LDPK_URL} \
    -DBUILD_SHARED_LIBS=OFF \
    ${MMSOLVERLIBS_ROOT}

${CMAKE_EXE} --build . --parallel
${CMAKE_EXE} --install .

# Return back project root directory.
cd ${CWD}
