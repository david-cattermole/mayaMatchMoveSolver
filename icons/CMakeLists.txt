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

get_maya_module_os_name(os_name)
set(input_file ${CMAKE_CURRENT_SOURCE_DIR}/resources.qrc)
set(output_file ${CMAKE_CURRENT_BINARY_DIR}/resources_${os_name}_maya${MAYA_VERSION}.rcc)
compile_qt_resources_qrc_to_rcc_file("qt_resources" ${input_file} ${output_file})

# Install Icons.
install(FILES
  ${output_file}
  DESTINATION "${MODULE_FULL_NAME}/resources")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/"
  DESTINATION "${MODULE_FULL_NAME}/icons"
  FILES_MATCHING
        PATTERN "*.png"
        PATTERN "*.svg"
  PATTERN "edit" EXCLUDE
  PATTERN "library" EXCLUDE
  PATTERN "ui" EXCLUDE)
