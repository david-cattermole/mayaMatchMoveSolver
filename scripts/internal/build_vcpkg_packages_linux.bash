#!/usr/bin/env bash
#
# Copyright (C) 2026 David Cattermole.
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
# Installs OpenBLAS and SuiteSparse (CHOLMOD) using vcpkg.
#
# OpenBLAS is built single-threaded as a shared library.
# SuiteSparse CHOLMOD is built without GPL components and without CUDA.
#
# This script is assumed to be called with a number of variables
# already set:
#
# - MAYA_VERSION
# - CMAKE_EXE
#
# The following variables are set by `build_config_linux.bash`:
#
# - BUILD_VCPKG_DIR_BASE
# - BUILD_VCPKG_INSTALL_DIR

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

# Source centralised build configuration.
source "${PROJECT_ROOT}/scripts/internal/build_config_linux.bash"

# Directory configuration handled by centralised `build_config_linux.bash`.
echo "Build vcpkg directory base: ${BUILD_VCPKG_DIR_BASE}"
echo "vcpkg install path: ${BUILD_VCPKG_INSTALL_DIR}"

# Set up vcpkg directory.
VCPKG_DIR="${BUILD_VCPKG_DIR_BASE}/vcpkg"
if [ ! -d "${VCPKG_DIR}" ]; then
    echo "Cloning vcpkg..."
    mkdir -p "${BUILD_VCPKG_DIR_BASE}"
    git clone https://github.com/microsoft/vcpkg.git "${VCPKG_DIR}"
fi

# Bootstrap vcpkg if needed.
if [ ! -f "${VCPKG_DIR}/vcpkg" ]; then
    echo "Bootstrapping vcpkg..."
    "${VCPKG_DIR}/bootstrap-vcpkg.sh" -disableMetrics
fi

VCPKG_EXE="${VCPKG_DIR}/vcpkg"

# Use the x64-linux-dynamic triplet which builds shared libraries.
VCPKG_TRIPLET="x64-linux-dynamic"

# Install OpenBLAS (single-threaded, shared library).
#
# The default OpenBLAS port in vcpkg builds without the 'threads'
# feature, which gives us single-threaded code. The x64-linux-dynamic
# triplet builds shared libraries.
echo "Installing OpenBLAS via vcpkg..."
${VCPKG_EXE} install openblas:${VCPKG_TRIPLET} \
    --x-install-root="${BUILD_VCPKG_INSTALL_DIR}"

# Install SuiteSparse CHOLMOD (no GPL, no CUDA, shared library).
#
# By installing suitesparse-cholmod without the 'gpl' feature on
# the top-level suitesparse port, we get only LGPL-licensed
# components. CUDA is also off by default.
echo "Installing SuiteSparse CHOLMOD via vcpkg..."
${VCPKG_EXE} install suitesparse-cholmod:${VCPKG_TRIPLET} \
    --x-install-root="${BUILD_VCPKG_INSTALL_DIR}"

echo "vcpkg packages installed successfully."
echo "Install root: ${BUILD_VCPKG_INSTALL_DIR}"

# Return back project root directory.
cd ${CWD}
