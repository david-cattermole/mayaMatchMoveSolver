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

set(input_file resources.qrc)
set(output_file resources.rcc)

# This section checks to see if `rcc` is a recognized command 
# on the user's Windows OS, and if not, use the `rcc.exe` 
# file found under the given Maya version.
find_program(RCC_EXISTS "rcc")
if(RCC_EXISTS)
    set(RCC_CMD rcc -binary resources.qrc -o resources.rcc)
else()
    set(RCC_CMD "${MAYA_LOCATION}/bin/rcc.exe" -o resources.rcc resources.qrc)
endif()

add_custom_command(
        OUTPUT ${output_file}
        COMMAND ${RCC_CMD}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS ${input_file}
)
add_custom_target(
        build_icons ALL
        DEPENDS ${output_file}
        COMMENT "Building Icons (with Qt Resource Compiler) (${input_file})..."
)


# Install Icons.
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/"
  DESTINATION "${MODULE_FULL_NAME}/resources"
  FILES_MATCHING PATTERN "*.rcc"
  PATTERN "edit" EXCLUDE
  PATTERN "library" EXCLUDE
  PATTERN "ui" EXCLUDE)
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
