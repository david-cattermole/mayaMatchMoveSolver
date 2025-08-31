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
# Cleans the OpenColorIO build directories for Maya 2019.

# Build location - where to clean the project build files.
#
# Defaults to ${PROJECT_ROOT}/.. if not set.
if [ -z "$BUILD_DIR_BASE" ]; then
    BUILD_DIR_BASE="$(pwd)/.."
fi

# Maya
MAYA_VERSION=2019

CWD=`pwd`

# Path to this script.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "${DIR}/internal/clean_openColorIO_linux.bash"

cd ${CWD}
