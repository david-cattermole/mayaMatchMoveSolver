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
# ----------------------------------------------------------------------
#
# Define the tests for mmSolver.

find_package(Maya REQUIRED)

set(EXEC_SCRIPT ${CMAKE_SOURCE_DIR}/tests/runTests.py)

## API Tests
#set(suffix api)
#add_test(
#   NAME
#       test_python_${suffix}
#   COMMAND
#       ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT} ${CMAKE_SOURCE_DIR}/tests/test/test_${suffix}
#   WORKING_DIRECTORY
#       ${CMAKE_SOURCE_DIR}
#)

## Solver Tests
#set(suffix solver)
#add_test(
#       NAME
#       test_python_${suffix}
#       COMMAND
#       ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT} ${CMAKE_SOURCE_DIR}/tests/test/test_${suffix}
#       WORKING_DIRECTORY
#       ${CMAKE_SOURCE_DIR}
#)

## Tools Tests
#set(suffix tools)
#add_test(
#       NAME
#       test_python_${suffix}
#       COMMAND
#       ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT} ${CMAKE_SOURCE_DIR}/tests/test/test_${suffix}
#       WORKING_DIRECTORY
#       ${CMAKE_SOURCE_DIR}
#)

## Utilities Tests
#set(suffix utils)
#add_test(
#       NAME
#       test_python_${suffix}
#       COMMAND
#       ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT} ${CMAKE_SOURCE_DIR}/tests/test/test_${suffix}
#       WORKING_DIRECTORY
#       ${CMAKE_SOURCE_DIR}
#)

# API Tests
add_test(
        NAME
        test_python
        COMMAND
        ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT}
        WORKING_DIRECTORY
        ${CMAKE_SOURCE_DIR}
)
