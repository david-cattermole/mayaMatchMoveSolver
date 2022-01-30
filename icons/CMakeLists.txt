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

include(MMSolverUtils)

# This section sets a hard location to the rcc  
# executable file to prevent any errors of 
# likes of 'rcc command not found'
find_program(MAYA_RCC_EXECUTABLE
        rcc
    HINTS
        "${MAYA_LOCATION}"
        "$ENV{MAYA_LOCATION}"
        "${MAYA_BASE_DIR}"
    PATH_SUFFIXES
        MacOS
        bin3/  # Use Python 3.x location, in Maya 2022.
        bin/
    DOC
        "Maya's Qt resource compiler (rcc) executable path"
)

get_maya_module_os_name(os_name)
set(input_file resources.qrc)
set(output_file resources_${os_name}_maya${MAYA_VERSION}.rcc)
message(STATUS "resources output_file: ${output_file}")
add_custom_command(
        OUTPUT ${output_file}
        COMMAND ${MAYA_RCC_EXECUTABLE} -binary ${input_file} -o ${output_file}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS ${input_file}
)
add_custom_target(
        build_icons ALL
        DEPENDS ${output_file}
        COMMENT "Building Icons (with Qt Resource Compiler) (${input_file})..."
)


# Install Icons.
install(FILES
  ${output_file}
  DESTINATION "${MODULE_FULL_NAME}/resources")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/"
  DESTINATION "${MODULE_FULL_NAME}/icons"
  FILES_MATCHING PATTERN "*.png"
  PATTERN "edit" EXCLUDE
  PATTERN "library" EXCLUDE
  PATTERN "ui" EXCLUDE)
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/"
  DESTINATION "${MODULE_FULL_NAME}/icons"
  FILES_MATCHING PATTERN "*.svg"
  PATTERN "edit" EXCLUDE
  PATTERN "library" EXCLUDE
  PATTERN "ui" EXCLUDE)
