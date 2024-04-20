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
# Runs PyLint for the project.

PROJECT_ROOT=`pwd`

python -m pylint -j 4 \
       "${PROJECT_ROOT}/share/3dequalizer/python" \
       "${PROJECT_ROOT}/share/3dequalizer/scriptdb" \
       "${PROJECT_ROOT}/mel" \
       "${PROJECT_ROOT}/python" \
       "${PROJECT_ROOT}/tests"

cd ${PROJECT_ROOT}
