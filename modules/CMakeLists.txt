# Copyright (C) 2019, 2020 David Cattermole.
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
# Configure the Maya module file.


# Module paths
set(MODULE_OS_NAME "unknown")
if(CMAKE_SYSTEM_NAME STREQUAL Darwin)
    set(MODULE_OS_NAME "mac")
elseif(CMAKE_SYSTEM_NAME STREQUAL Linux)
    set(MODULE_OS_NAME "linux")
elseif(CMAKE_SYSTEM_NAME STREQUAL Windows)
    set(MODULE_OS_NAME "win64")
else ()
    message(FATAL_ERROR "Only Linux, MacOS and Windows are supported.")
endif ()

# Module names
set(MODULE_NAME "${PROJECT_NAME}-${PROJECT_VERSION}")
set(MODULE_FULL_NAME "${MODULE_NAME}-maya${MAYA_VERSION}-${MODULE_OS_NAME}")
set(MODULE_BUILD_DIR "${CMAKE_BINARY_DIR}/${MODULE_FULL_NAME}")

# Create Module Description file.
if(CMAKE_SYSTEM_NAME STREQUAL Darwin)
    configure_file(
            ${CMAKE_CURRENT_SOURCE_DIR}/mayaMatchMoveSolver_mac.mod
            ${CMAKE_BINARY_DIR}/${MODULE_FULL_NAME}.mod
            @ONLY)
elseif(CMAKE_SYSTEM_NAME STREQUAL Linux)
    configure_file(
            ${CMAKE_CURRENT_SOURCE_DIR}/mayaMatchMoveSolver_linux.mod
            ${CMAKE_BINARY_DIR}/${MODULE_FULL_NAME}.mod
            @ONLY)
elseif(CMAKE_SYSTEM_NAME STREQUAL Windows)
    configure_file(
            ${CMAKE_CURRENT_SOURCE_DIR}/mayaMatchMoveSolver_windows.mod
            ${CMAKE_BINARY_DIR}/${MODULE_FULL_NAME}.mod
            @ONLY)
else ()
    message(FATAL_ERROR "Only Linux, MacOS and Windows are supported.")
endif ()

# Install the Module Description file.
install(FILES
        "${CMAKE_BINARY_DIR}/${MODULE_FULL_NAME}.mod"
        DESTINATION "./")

# Set variables in parent scope (directory above).
set(MODULE_OS_NAME "${MODULE_OS_NAME}" PARENT_SCOPE)
set(MODULE_NAME "${MODULE_NAME}" PARENT_SCOPE)
set(MODULE_FULL_NAME "${MODULE_FULL_NAME}" PARENT_SCOPE)
set(MODULE_BUILD_DIR "${MODULE_BUILD_DIR}" PARENT_SCOPE)
