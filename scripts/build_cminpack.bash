#!/usr/bin/env bash
# Builds the cminpack shared library.

# Store the current working directory, to return to.
CWD=`pwd`

# Path to this script.
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# The root of this project.
PROJECT_ROOT=`readlink -f ${THIS_DIR}/..`

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
rm --force -R *
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
