#!/bin/bash
#
# Copyright (C) 2022, 2024, 2025 David Cattermole.
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
# Common Python virtual environment activation script for Linux.
#
# This script expects MAYA_VERSION to be set before calling.
# It reads configuration from scripts/config/maya_settings.py

# Validate that MAYA_VERSION is set.
if [ -z "$MAYA_VERSION" ]; then
    echo "ERROR: MAYA_VERSION must be set before calling this script"
    return 1
fi

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

PROJECT_ROOT=$(pwd)

# Use Python to get configuration settings
PYTHON_CONFIG_SCRIPT="${PROJECT_ROOT}/scripts/config/maya_settings.py"
if [ ! -f "$PYTHON_CONFIG_SCRIPT" ]; then
    echo "ERROR: Configuration file not found: $PYTHON_CONFIG_SCRIPT"
    return 1
fi

# Get settings using Python configuration.
eval $(python3 -c "
import sys
import os
sys.path.insert(0, os.path.join('$PROJECT_ROOT', 'scripts', 'config'))
from maya_settings import MayaConfig

config = MayaConfig('linux')
python_exe = config.get_python_exe('$MAYA_VERSION')
venv_dir_name = config.get_python_venv_dir_name('$MAYA_VERSION')

print(f'PYTHON_EXE={python_exe}')
print(f'PYTHON_VIRTUAL_ENV_DIR_NAME={venv_dir_name}')
")

# Validate that we got the required settings.
if [ -z "$PYTHON_EXE" ]; then
    echo "ERROR: PYTHON_EXE not found for Maya version $MAYA_VERSION"
    return 1
fi

if [ -z "$PYTHON_VIRTUAL_ENV_DIR_NAME" ]; then
    echo "ERROR: PYTHON_VIRTUAL_ENV_DIR_NAME not found for Maya version $MAYA_VERSION"
    return 1
fi

# Export variables and call the existing internal script.
export PYTHON_EXE
export PYTHON_VIRTUAL_ENV_DIR_NAME

echo "Maya Version: $MAYA_VERSION"
echo "Python Executable: $PYTHON_EXE"
echo "Virtual Environment: $PYTHON_VIRTUAL_ENV_DIR_NAME"

source "${PROJECT_ROOT}/scripts/internal/python_venv_activate.bash"
