# Copyright (C) 2019 David Cattermole.
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
# This CMake script is for building and organising the 'external'
# dependancies for Maya MatchMove Solver.
#
cmake_minimum_required(VERSION 2.8.12)


# Install Qt.py, if exists.
set(QTPY_FILE "${CMAKE_CURRENT_SOURCE_DIR}/install/qtpy/Qt.py")
if (EXISTS ${QTPY_FILE})
  install(FILES ${QTPY_FILE}
    DESTINATION "${MODULE_FULL_NAME}/python_qtpy/")
endif ()
