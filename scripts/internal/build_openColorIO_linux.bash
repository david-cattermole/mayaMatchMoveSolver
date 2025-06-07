#!/usr/bin/env bash
#
# Copyright (C) 2019, 2022, 2024 David Cattermole.
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
# Builds the OpenColorIO project.
#
# By default the minimal build is performed that will give us the
# library.  This is not a "full" build with all features, bindings and
# programs.
#
# A static library is also preferred, to avoid shipping shared/dynamic
# libraries with mmSolver (which is a pain when dealing with a
# third-party studio's environment - it's easiest to embed everything
# and be done with it).
#
# This script is assumed to be called with a number of variables
# already set:
#
# - MAYA_VERSION
# - MAYA_LOCATION
# - PYTHON_EXE
# - CMAKE_EXE
# - CXX_STANDARD
# - OPENCOLORIO_TARBALL_NAME
# - OPENCOLORIO_TARBALL_EXTRACTED_DIR_NAME

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

# Store the current working directory, to return to.
CWD=`pwd`

# What directory to build the project in?
#
# Note: BUILD_DIR_BASE should already be set by the calling script.
# If not, use default location.
if [ -z "$BUILD_DIR_BASE" ]; then
    BUILD_DIR_BASE="${PROJECT_ROOT}/.."
fi
echo "Build root directory base: ${BUILD_DIR_BASE}"

# OpenColorIO build related stuff will go here.
BUILD_OCIO_DIR_NAME="build_opencolorio"
BUILD_OCIO_DIR_BASE="${BUILD_OCIO_DIR_BASE}/${BUILD_OCIO_DIR_NAME}"
echo "Build OpenColorIO directory base: ${BUILD_OCIO_DIR_BASE}"

# Install directory.
OCIO_INSTALL_PATH="${BUILD_OCIO_DIR_BASE}/install/maya${MAYA_VERSION}_linux/"

# What type of build? "Release" or "Debug"?
BUILD_TYPE=Release

# Allows you to see the build command lines, to help debugging build
# problems. Set to ON to enable, and OFF to disable.
MMSOLVER_BUILD_VERBOSE=OFF

# Path to this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# The root of this project.
PROJECT_ROOT=`readlink -f ${DIR}/../..`
echo "Project Root: ${PROJECT_ROOT}"

# We don't want to find system packages.
CMAKE_IGNORE_PATH="/lib;/lib64;/usr;/usr/lib;/usr/lib64;/usr/local;/usr/local/lib;/usr/local/lib64;"

# Build OpenColorIO project
cd ${BUILD_DIR_BASE}
BUILD_DIR_NAME="cmake_linux_maya${MAYA_VERSION}_${BUILD_TYPE}"
BUILD_DIR="${BUILD_OCIO_DIR_BASE}/${BUILD_DIR_NAME}"
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}

# Make sure source code archive is downloaded and exists.
SOURCE_TARBALL="${PROJECT_ROOT}/external/archives/${OPENCOLORIO_TARBALL_NAME}"
if [ ! -f "${SOURCE_TARBALL}" ]; then
    echo "${SOURCE_TARBALL} does not exist."
    echo "Please download the tar.gz file from https://github.com/AcademySoftwareFoundation/OpenColorIO/releases"
    exit 1
fi

# Extract the OpenColorIO archive.
EXTRACT_OUT_DIR="${BUILD_OCIO_DIR_BASE}/source/maya${MAYA_VERSION}_linux"
if [ ! -d "${EXTRACT_OUT_DIR}" ]; then
    echo "${EXTRACT_OUT_DIR} does not exist, creating it..."
    mkdir -p "${EXTRACT_OUT_DIR}"
fi
SOURCE_ROOT="${EXTRACT_OUT_DIR}/${OPENCOLORIO_TARBALL_EXTRACTED_DIR_NAME}/"
if [ ! -d "${SOURCE_ROOT}" ]; then
    echo "${SOURCE_ROOT} does not exist, extracting tarball..."
    # NOTE: Uses CMake to mirror the Windows build script. 'tar' is
    # unlikely to be available on Windows.
    ${CMAKE_EXE} -E chdir ${EXTRACT_OUT_DIR} tar xf ${SOURCE_TARBALL}
fi

echo "Building opencolorio... (${SOURCE_ROOT})"

# Renaming the library name and C++ namespace, is so that software
# looking for the "regular" OpenColorIO will not conflict with the
# mmSolver library.
MMSOLVER_OCIO_LIBNAME_SUFFIX="_mmSolver"
MMSOLVER_OCIO_NAMESPACE="OpenColorIO_mmSolver"

${CMAKE_EXE} \
    -DBUILD_SHARED_LIBS=OFF \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DCMAKE_INSTALL_PREFIX=${OCIO_INSTALL_PATH} \
    -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH} \
    -DCMAKE_POSITION_INDEPENDENT_CODE=1 \
    -DCMAKE_CXX_STANDARD=${CXX_STANDARD} \
    -DCMAKE_VERBOSE_MAKEFILE=${MMSOLVER_BUILD_VERBOSE} \
    -DOCIO_INSTALL_EXT_PACKAGES=ALL \
    -DOCIO_USE_OIIO_FOR_APPS=OFF \
    -DOCIO_BUILD_APPS=OFF \
    -DOCIO_BUILD_TESTS=OFF \
    -DOCIO_BUILD_GPU_TESTS=OFF \
    -DOCIO_BUILD_DOCS=OFF \
    -DOCIO_BUILD_FROZEN_DOCS=OFF \
    -DOCIO_BUILD_PYTHON=OFF \
    -DOCIO_BUILD_OPENFX=OFF \
    -DOCIO_LIBNAME_SUFFIX=${MMSOLVER_OCIO_LIBNAME_SUFFIX} \
    -DOCIO_NAMESPACE=${MMSOLVER_OCIO_NAMESPACE} \
    ${SOURCE_ROOT}

${CMAKE_EXE} --build . --parallel
${CMAKE_EXE} --install .

# Return back project root directory.
cd ${CWD}
