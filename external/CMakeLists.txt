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
# This CMake script is for building and organising the 'external' dependancies
# for Maya MatchMove Solver.
#
cmake_minimum_required(VERSION 2.8)
find_package(Python2 COMPONENTS Interpreter REQUIRED)

set(ARCHIVES_DIR "${CMAKE_SOURCE_DIR}/archives")
set(WORKING_DIR "${CMAKE_SOURCE_DIR}/working")
set(PATCHES_DIR "${CMAKE_SOURCE_DIR}/patches")

set(CMINPACK_DOWNLOAD_FILE "${ARCHIVES_DIR}/cminpack-1.3.6.tar.gz")
set(CMINPACK_EXTRACTED_FILE "${WORKING_DIR}/cminpack-1.3.6")

set(LEVMAR_DOWNLOAD_FILE "${ARCHIVES_DIR}/levmar-2.6.tgz")
set(LEVMAR_EXTRACTED_FILE "${WORKING_DIR}/levmar-2.6")


# Extract CMinpack
set(PY_SCRIPT "${CMAKE_SOURCE_DIR}/../scripts/get_cminpack.py")
add_custom_command(
    OUTPUT ${CMINPACK_EXTRACTED_FILE}
    COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMINPACK_EXTRACTED_FILE}
    COMMAND python ${PY_SCRIPT} ${ARCHIVES_DIR} ${WORKING_DIR} ${PATCHES_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    DEPENDS ${CMINPACK_DOWNLOAD_FILE}
    )
add_custom_target(
    cminpack_package ALL
    DEPENDS ${CMINPACK_EXTRACTED_FILE}
    COMMENT "Unpacking CMinpack package..."
    )


# Extract Levmar
set(PY_SCRIPT "${CMAKE_SOURCE_DIR}/../scripts/get_levmar.py")
add_custom_command(
        OUTPUT ${LEVMAR_EXTRACTED_FILE}
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${LEVMAR_EXTRACTED_FILE}
        COMMAND python ${PY_SCRIPT} ${ARCHIVES_DIR} ${WORKING_DIR} ${PATCHES_DIR}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        DEPENDS ${LEVMAR_DOWNLOAD_FILE}
)
add_custom_target(
        levmar_package ALL
        DEPENDS ${LEVMAR_EXTRACTED_FILE}
        COMMENT "Unpacking LevMar package..."
)
