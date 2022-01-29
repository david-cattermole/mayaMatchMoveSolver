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
# Builds the third-party dependencies needed in mmSolver.

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

CWD=`pwd`

# Path to this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PACKAGE_ROOT=`readlink -f ${DIR}/../../external`
echo "Package Root: ${PACKAGE_ROOT}"
cd "${PACKAGE_ROOT}"

# Common arguments
INSTALL_DIR="${PACKAGE_ROOT}/install/maya${MAYA_VERSION}_linux"
WORKING_DIR="${PACKAGE_ROOT}/working/maya${MAYA_VERSION}_linux"
SOURCE_DIR="${PACKAGE_ROOT}"

# Build
BUILD_DIR_NAME="build_maya${MAYA_VERSION}_linux"
mkdir -p "${INSTALL_DIR}"
mkdir -p "${WORKING_DIR}"
cd "${WORKING_DIR}"
mkdir -p "${BUILD_DIR_NAME}"
cd "${BUILD_DIR_NAME}"
rm --force -R *

# Number of CPUs
CPU_NUM=`nproc --all`

${CMAKE_EXE} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POSITION_INDEPENDENT_CODE=1 \
    -DCMAKE_CXX_STANDARD=${CXX_STANDARD} \
    -DTHIRDPARTY_BASE_INSTALL_DIR=${INSTALL_DIR} \
    -DTHIRDPARTY_BASE_WORKING_DIR=${WORKING_DIR} \
    ${SOURCE_DIR}

${CMAKE_EXE} --build . --parallel ${CPU_NUM}
${CMAKE_EXE} --install .

# Return back project root directory.
cd "${PACKAGE_ROOT}"
