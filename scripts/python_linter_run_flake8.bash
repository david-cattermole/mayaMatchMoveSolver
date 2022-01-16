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
# Runs Flake8 for the project.

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

PROJECT_ROOT=`pwd`

python -m flake8 \
       "${PROJECT_ROOT}/3dequalizer/python" \
       "${PROJECT_ROOT}/3dequalizer/scriptdb" \
       "${PROJECT_ROOT}/mel" \
       "${PROJECT_ROOT}/python" \
       "${PROJECT_ROOT}/tests"

cd ${PROJECT_ROOT}
