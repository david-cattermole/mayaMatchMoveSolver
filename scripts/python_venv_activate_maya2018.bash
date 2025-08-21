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
# Activates the Python development environment for Maya 2018.
#
# This script should be sourced, NOT called, for example:
# $ source scripts/python_venv_activate_maya2018.bash
#

# Set Maya version for the common venv activation script.
export MAYA_VERSION=2018

# Call the common venv activation script.
source "$(pwd)/scripts/internal/python_venv_activate_common.bash"
