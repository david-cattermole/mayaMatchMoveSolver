#!/usr/bin/env bash
#
# Copyright (C) 2025 David Cattermole.
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
# Internal script to clean OpenColorIO build directories.
#
# NOTE: Do not call this script directly! This file should be called by
# the clean_openColorIO_linux_mayaXXXX.bash files.
#
# This script assumes MAYA_VERSION has been set by the calling script.

# Validate that MAYA_VERSION is set.
if [ -z "$MAYA_VERSION" ]; then
    echo "ERROR: MAYA_VERSION environment variable is not set."
    echo "This script should be called from a Maya version-specific wrapper script."
    exit 1
fi

# Build location - where to clean the project build files.
BUILD_DIR_BASE="$(pwd)/.."

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

CWD=`pwd`

echo "Cleaning OpenColorIO build directories for Maya ${MAYA_VERSION}..."
echo "Build directory base: ${BUILD_DIR_BASE}"

# OpenColorIO build directory
OCIO_BUILD_DIR="${BUILD_DIR_BASE}/build_opencolorio"

# Remove OpenColorIO-specific build directories for this Maya version
BUILD_DIRS=(
    "${OCIO_BUILD_DIR}/cmake_linux_maya${MAYA_VERSION}_Release"
    "${OCIO_BUILD_DIR}/cmake_win64_maya${MAYA_VERSION}_Release"
    "${OCIO_BUILD_DIR}/install/maya${MAYA_VERSION}_linux"
    "${OCIO_BUILD_DIR}/install/maya${MAYA_VERSION}_windows64"
    "${OCIO_BUILD_DIR}/source/maya${MAYA_VERSION}_linux"
    "${OCIO_BUILD_DIR}/source/maya${MAYA_VERSION}_windows64"
)

for dir in "${BUILD_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "Removing directory: $dir"
        rm -rf "$dir"
    else
        echo "Directory does not exist (skipping): $dir"
    fi
done

echo "OpenColorIO build cleanup completed for Maya ${MAYA_VERSION}."

cd ${CWD}