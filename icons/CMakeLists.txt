# Copyright (C) 2020 David Cattermole.
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
# Build Icons (using Qt Resource Compiler)

set(input_file ${CMAKE_SOURCE_DIR}/icons/resources.qrc)
set(output_file ${CMAKE_SOURCE_DIR}/icons/resources.rcc)

find_program(QT_RESOURCE_COMPILER_EXECUTABLE
        rcc
    HINTS
        "${MAYA_LOCATION}"
        "$ENV{MAYA_LOCATION}"
        "${MAYA_BASE_DIR}"
    PATH_SUFFIXES
        MacOS/
        bin3/  # Use Python 3.x location, in Maya 2022.
        bin/
    DOC
        "Maya provided Qt RCC's executable path"
)

add_custom_command(
        OUTPUT ${output_file}
        COMMAND ${QT_RESOURCE_COMPILER_EXECUTABLE} -binary resources.qrc -o resources.rcc
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/icons
        DEPENDS ${input_file}
)
add_custom_target(
        build_icons ALL
        DEPENDS ${output_file}
        COMMENT "Building Icons (with Qt Resource Compiler) (${input_file})..."
)
