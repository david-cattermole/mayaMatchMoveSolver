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
# Activates the Python development environment for Maya 2025.
#
# This script should be sourced, NOT called, for example:
# $ source scripts/python_venv_activate_maya2025.bash
#

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

PROJECT_ROOT=`pwd`

MAYA_VERSION=2026

# Python executable - edit this to point to an explicit python executable file.
#
# RockyLinux8 has Python 3.6 by default, but we use Python 3.9 because
# it has better support for tools like 'ruff'.
PYTHON_EXE=python3.9

PYTHON_VIRTUAL_ENV_DIR_NAME="python_venv_linux_maya${MAYA_VERSION}"
source "${PROJECT_ROOT}/scripts/internal/python_venv_activate.bash"
