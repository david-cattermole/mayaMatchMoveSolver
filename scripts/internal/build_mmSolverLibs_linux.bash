#!/usr/bin/env bash
#
# Copyright (C) 2022, 2023, 2024 David Cattermole.
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

# Validate required environment variables.
echo "Validating required environment variables..."
for var in MAYA_VERSION CMAKE_EXE RUST_CARGO_EXE VFX_PLATFORM CXX_STANDARD; do
    if [ -z "${!var}" ]; then
        echo "ERROR: Required environment variable '$var' is not set."
        echo "This script must be called by a parent build script that sets all required variables."
        exit 1
    fi
done
echo "All required environment variables are set."

# Store the current working directory, to return to.
CWD=`pwd`

# Path to this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# The root of this project.
PROJECT_ROOT=`readlink -f ${DIR}/../..`
echo "Project Root: ${PROJECT_ROOT}"

# What directory to build the project in?
#
# Note: BUILD_DIR_BASE should already be set by the calling script.
# If not, use default location.
if [ -z "$BUILD_DIR_BASE" ]; then
    BUILD_DIR_BASE="${PROJECT_ROOT}/.."
fi
echo "Build root directory base: ${BUILD_DIR_BASE}"

# OpenColorIO build dir.
BUILD_OCIO_DIR_NAME="build_opencolorio"
BUILD_OCIO_DIR_BASE="${BUILD_DIR_BASE}/${BUILD_OCIO_DIR_NAME}"
echo "Build OpenColorIO directory base: ${BUILD_OCIO_DIR_BASE}"

# mmSolverLibs build dir.
BUILD_MMSOLVERLIBS_DIR_NAME="build_mmsolverlibs"
BUILD_MMSOLVERLIBS_DIR_BASE="${BUILD_DIR_BASE}/${BUILD_MMSOLVERLIBS_DIR_NAME}"
echo "Build mmSolverLibs directory base: ${BUILD_MMSOLVERLIBS_DIR_BASE}"

# What type of build? "Release" or "Debug"?
BUILD_TYPE="Release"
MMSOLVER_DEBUG=1

RELEASE_FLAG=""
BUILD_TYPE_DIR="debug"
if [ ${BUILD_TYPE}=="Release" ]; then
    RELEASE_FLAG="--release"
    BUILD_TYPE_DIR="release"
fi

# Allows you to see the build command lines, to help debugging build
# problems. Set to ON to enable, and OFF to disable.
MMSOLVER_BUILD_VERBOSE=OFF

# Where to find the mmsolverlibs Rust libraries and headers.
MMSOLVERLIBS_INSTALL_PATH="${BUILD_MMSOLVERLIBS_DIR_BASE}/install/maya${MAYA_VERSION}_linux/"
MMSOLVERLIBS_ROOT="${PROJECT_ROOT}/lib"
MMSOLVERLIBS_RUST_ROOT="${MMSOLVERLIBS_ROOT}/mmsolverlibs"
MMSOLVERLIBS_CPP_TARGET_DIR="${BUILD_MMSOLVERLIBS_DIR_BASE}/rust_linux_maya${MAYA_VERSION}"
MMSOLVERLIBS_LIB_DIR="${MMSOLVERLIBS_CPP_TARGET_DIR}/${BUILD_TYPE_DIR}"
MMSOLVERLIBS_INCLUDE_DIR="${MMSOLVERLIBS_ROOT}/include"

# Paths for dependencies.
EXTERNAL_OCIO_BUILD_DIR="${BUILD_OCIO_DIR_BASE}/cmake_linux_maya${MAYA_VERSION}_${BUILD_TYPE}/ext/dist"
OCIO_INSTALL_DIR="${BUILD_OCIO_DIR_BASE}/install/maya${MAYA_VERSION}_linux/"
OCIO_CMAKE_CONFIG_DIR="${OCIO_INSTALL_DIR}/lib64/cmake/OpenColorIO/"
OCIO_CMAKE_FIND_MODULES_DIR="${BUILD_OCIO_DIR_BASE}/source/maya${MAYA_VERSION}_linux/${OPENCOLORIO_TARBALL_EXTRACTED_DIR_NAME}/share/cmake/modules"

expat_DIR="${EXTERNAL_OCIO_BUILD_DIR}/${EXPAT_RELATIVE_CMAKE_DIR}"
expat_INCLUDE_DIR="${EXTERNAL_OCIO_BUILD_DIR}/include/"
expat_LIBRARY="${EXTERNAL_OCIO_BUILD_DIR}/${EXPAT_RELATIVE_LIB_PATH}"

pystring_LIBRARY="${EXTERNAL_OCIO_BUILD_DIR}/${PYSTRING_RELATIVE_LIB_PATH}"
pystring_INCLUDE_DIR="${EXTERNAL_OCIO_BUILD_DIR}/include"

yaml_DIR="${EXTERNAL_OCIO_BUILD_DIR}/${YAML_RELATIVE_CMAKE_DIR}"
yaml_LIBRARY="${EXTERNAL_OCIO_BUILD_DIR}/${YAML_RELATIVE_LIB_PATH}"
yaml_INCLUDE_DIR="${EXTERNAL_OCIO_BUILD_DIR}/include/"

Imath_DIR="${EXTERNAL_OCIO_BUILD_DIR}/lib64/cmake/Imath"

ZLIB_LIBRARY="${EXTERNAL_OCIO_BUILD_DIR}/${ZLIB_RELATIVE_LIB_PATH}"
ZLIB_INCLUDE_DIR="${EXTERNAL_OCIO_BUILD_DIR}/include/"

minizip_DIR="${EXTERNAL_OCIO_BUILD_DIR}/lib64/cmake/minizip-ng"

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
    # './Cargo.toml'
    # './scripts/internal/build_mmSolver_windows64.bat'
    # './scripts/internal/build_mmSolver_linux.bash'
    # './scripts/internal/build_mmSolverLibs_windows64.bat'
    # './scripts/internal/build_mmSolverLibs_linux.bash'
    ${RUST_CARGO_EXE} install cxxbridge-cmd --version 1.0.155
fi
MMSOLVERLIBS_CXXBRIDGE_EXE="${HOME}/.cargo/bin/cxxbridge"

cd ${MMSOLVERLIBS_RUST_ROOT}
${RUST_CARGO_EXE} build ${RELEASE_FLAG} --target-dir ${MMSOLVERLIBS_CPP_TARGET_DIR}

# A local copy of LDPK to reduce the amount of downloads to the
# 3DEqualizer website (LDPK doesn't have a git repo to clone from).
LDPK_URL="${PROJECT_ROOT}/external/archives/ldpk-2.12.0.tar"

# Build project
cd ${BUILD_DIR_BASE}
BUILD_DIR_NAME="cmake_linux_maya${MAYA_VERSION}_${BUILD_TYPE}"
BUILD_DIR="${BUILD_MMSOLVERLIBS_DIR_BASE}/${BUILD_DIR_NAME}"
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}

export MAYA_VERSION=${MAYA_VERSION}
${CMAKE_EXE} \
    -DBUILD_SHARED_LIBS=OFF \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DCMAKE_INSTALL_PREFIX=${MMSOLVERLIBS_INSTALL_PATH} \
    -DCMAKE_POSITION_INDEPENDENT_CODE=1 \
    -DCMAKE_CXX_STANDARD=${CXX_STANDARD} \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -DCMAKE_MODULE_PATH=${OCIO_CMAKE_FIND_MODULES_DIR} \
    -DCMAKE_VERBOSE_MAKEFILE=${MMSOLVER_BUILD_VERBOSE} \
    -DMMSOLVER_VFX_PLATFORM=${VFX_PLATFORM} \
    -DMMSOLVER_DEBUG=${MMSOLVER_DEBUG} \
    -DMMSOLVERLIBS_CXXBRIDGE_EXE=${MMSOLVERLIBS_CXXBRIDGE_EXE} \
    -DMMSOLVERLIBS_BUILD_TESTS=${MMSOLVERLIBS_BUILD_TESTS} \
    -DMMSOLVERLIBS_LIB_DIR=${MMSOLVERLIBS_LIB_DIR} \
    -DMMSOLVER_DOWNLOAD_DEPENDENCIES=ON \
    -Dldpk_URL=${LDPK_URL} \
    -DOpenColorIO_DIR=${OCIO_CMAKE_CONFIG_DIR} \
    -DOCIO_INSTALL_EXT_PACKAGES=NONE \
    -Dexpat_DIR=${expat_DIR} \
    -Dexpat_LIBRARY=${expat_LIBRARY} \
    -Dexpat_INCLUDE_DIR=${expat_INCLUDE_DIR} \
    -Dexpat_USE_STATIC_LIBS=TRUE \
    -Dpystring_LIBRARY=${pystring_LIBRARY} \
    -Dpystring_INCLUDE_DIR=${pystring_INCLUDE_DIR} \
    -Dyaml-cpp_DIR=${yaml_DIR} \
    -Dyaml-cpp_LIBRARY=${yaml_LIBRARY} \
    -Dyaml-cpp_INCLUDE_DIR=${yaml_INCLUDE_DIR} \
    -DImath_DIR=${Imath_DIR} \
    -DZLIB_LIBRARY=${ZLIB_LIBRARY} \
    -DZLIB_INCLUDE_DIR=${ZLIB_INCLUDE_DIR} \
    -DZLIB_STATIC_LIBRARY=ON \
    -Dminizip-ng_DIR=${minizip_DIR} \
    ${MMSOLVERLIBS_ROOT}

${CMAKE_EXE} --build . --parallel
${CMAKE_EXE} --install .

# Return back project root directory.
cd ${CWD}
