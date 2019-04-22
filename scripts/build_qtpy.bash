#!/usr/bin/env bash
# Downloads and installs Qt.py file.

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

INSTALL_DIR="${ROOT}/install/qtpy"

# Extract Qt.py
python "${THIS_DIR}/get_qtpy.py" "${ROOT}/archives" "${ROOT}/working" "${ROOT}/patches"

# Copy file to install
mkdir -p ${INSTALL_DIR}
cp ${ROOT}/working/Qt.py-1.1.0/Qt.py ${INSTALL_DIR}

# Return back project root directory.
cd ${CWD}
