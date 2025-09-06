#!/bin/bash
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
# Wrapper script to build documentation with proper Python virtual environment.
#

# Get the project root (one level up from docs directory).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# Activate the Python virtual environment for the specified Maya version.
source "scripts/python_venv_activate_maya${MAYA_VERSION}.bash"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate Python virtual environment!"
    exit 1
fi

# Change back to docs directory.
cd "${PROJECT_ROOT}/docs"

# Run the make command with environment variables.
make html
