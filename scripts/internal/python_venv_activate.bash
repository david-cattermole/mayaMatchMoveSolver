#!/bin/bash
#
# Copyright (C) 2022 David Cattermole.
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
# Activates (and sets up) the Python development environment.
#
# Warning: This file expects the variables "PYTHON_VIRTUAL_ENV_DIR_NAME"
# and "PYTHON_EXE" to be defined in the calling environment, if this is
# not done, undefined behaviour will happen (likely an error).


# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

PROJECT_ROOT=`pwd`

# What directory to build the environment in?
BASE_DIR="${PROJECT_ROOT}/.."

# Clear the currently generated Python virtual environment before
# running the build process (including Python commands).
#
# The generation of a Python Virtual Environment slow to run and should
# be reused if possible; therefore leave this off for normal usage.
FRESH_PYTHON_VIRTUAL_ENV=0

# Full directory path to environment.
PYTHON_VIRTUAL_ENV_DIR="${BASE_DIR}/build_mmsolver/${PYTHON_VIRTUAL_ENV_DIR_NAME}"

# Activate script file name.
PYTHON_VIRTUAL_ENV_ACTIVATE_SCRIPT="${PYTHON_VIRTUAL_ENV_DIR}/bin/activate"

# Delete any existing Python virtual environment, if it exists.
if [ ${FRESH_PYTHON_VIRTUAL_ENV} -eq 1 ]; then
    mkdir -p "${PYTHON_VIRTUAL_ENV_DIR}"
    cd "${PYTHON_VIRTUAL_ENV_DIR}"
    rm -f -R *
fi

# Ensure Python Virtual Environment is setup.
REQUIRE_PACKAGE_INSTALL=0
if [ ! -f "${PYTHON_VIRTUAL_ENV_ACTIVATE_SCRIPT}" ]; then
    echo "Setting up Python Virtual Environment ${PYTHON_VIRTUAL_ENV_DIR_NAME}"
    ${PYTHON_EXE} -m venv ${PYTHON_VIRTUAL_ENV_DIR}
    REQUIRE_PACKAGE_INSTALL=1
fi

# Activate!
echo "Activating Python Virtual Environment ${PYTHON_VIRTUAL_ENV_DIR_NAME}"
cd "${PYTHON_VIRTUAL_ENV_DIR}"
source "${PYTHON_VIRTUAL_ENV_ACTIVATE_SCRIPT}"

# Install requirements
if [ ${REQUIRE_PACKAGE_INSTALL} -eq 1 ]; then
    ${PYTHON_EXE} -m pip install --upgrade pip

    REQUIRE_DEV_MAYA_VERSION_FILE="${PROJECT_ROOT}/share/requirements-dev-maya${MAYA_VERSION}.txt"
    REQUIRE_DOC_MAYA_VERSION_FILE="${PROJECT_ROOT}/share/requirements-doc-maya${MAYA_VERSION}.txt"

    ${PYTHON_EXE} -m pip install -r $REQUIRE_DEV_MAYA_VERSION_FILE
    ${PYTHON_EXE} -m pip install -r $REQUIRE_DOC_MAYA_VERSION_FILE
fi

cd ${PROJECT_ROOT}
