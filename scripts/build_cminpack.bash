#!/usr/bin/env bash
#
# Copyright (C) 2019 David Cattermole.
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
# Builds the cminpack shared library.

# Store the current working directory, to return to.
CWD=`pwd`

# Path to this script.
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# The root of this project.
PROJECT_ROOT=${THIS_DIR}/..

# The root of the project external directory.
ROOT=${THIS_DIR}/../external/
echo Package Root: ${ROOT}
cd ${ROOT}

INSTALL_DIR="${ROOT}/install/cminpack"

# Extract LevMar
python "${THIS_DIR}/get_cminpack.py" "${ROOT}/archives" "${ROOT}/working" "${ROOT}/patches"

# Build Library
mkdir -p build
cd build
rm -f -R *
cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR} \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_EXAMPLES=OFF \
    -DUSE_FPIC=ON \
    -DUSE_BLAS=0 \
    ../working/cminpack-1.3.6
make clean
make all
make install

# Return back project root directory.
cd ${CWD}
