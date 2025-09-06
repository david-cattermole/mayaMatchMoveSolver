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
# Internal script to clean mmSolver build directories.
#
# NOTE: Do not call this script directly! This file should be called by
# the clean_mmSolver_linux_mayaXXXX.bash files.
#
# This script assumes MAYA_VERSION has been set by the calling script.

# Validate that MAYA_VERSION is set.
if [ -z "$MAYA_VERSION" ]; then
    echo "ERROR: MAYA_VERSION environment variable is not set."
    echo "This script should be called from a Maya version-specific wrapper script."
    exit 1
fi

# Path to this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# The root of this project.
PROJECT_ROOT=`readlink -f ${DIR}/../..`

# Source centralised build configuration.
source "${PROJECT_ROOT}/scripts/internal/build_config_linux.bash"

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

CWD=`pwd`

echo "Cleaning mmSolver build directories for Maya ${MAYA_VERSION}..."
echo "Build directory base: ${BUILD_DIR_BASE}"

# Remove mmSolver-specific build directories
BUILD_DIRS=(
    "${BUILD_MMSOLVER_CMAKE_DIR}"
    "${BUILD_MMSOLVER_PYTHON_VENV_DIR}"
    "${BUILD_MMSOLVER_RUST_DIR}"
    "${BUILD_DOCS_DIR_BASE}"
)

for dir in "${BUILD_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "Removing directory: $dir"
        rm -rf "$dir"
    else
        echo "Directory does not exist (skipping): $dir"
    fi
done

echo "mmSolver build cleanup completed for Maya ${MAYA_VERSION}."

cd ${CWD}
