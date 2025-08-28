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
# Runs tests via the Maya Python Interpreter (mayapy).

# The root of this project.
PROJECT_ROOT="$(pwd)"
echo "Project Root: ${PROJECT_ROOT}"

# Path to Maya Python interpreter.
MAYA_EXE="/usr/autodesk/maya2022/bin/mayapy"

# Run tests.
"${MAYA_EXE}" "${PROJECT_ROOT}/tests/runTests.py" "$@"
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "mmSolver tests failed!"
    exit 1
fi

# Successful return.
exit 0
