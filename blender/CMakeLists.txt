# Copyright (C) 2021 David Cattermole.
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
# Generate and install the mmSolver addon for Blender.
#

function(zip_up_blender_addon
        name
        input_directory
        output_file
        working_dir)
    add_custom_command(
            COMMAND ${CMAKE_COMMAND} -E tar "cf" "${output_file}" --format=zip -- ${input_directory}
            WORKING_DIRECTORY "${working_dir}"
            OUTPUT  "${output_file}"
            DEPENDS ${input_files}
            COMMENT "Zipping ${name} to ${output_file}."
    )
    add_custom_target(
            create_zip_${name} ALL
            DEPENDS ${output_file}
            COMMENT "Zipping ${name}"
    )
endfunction()

zip_up_blender_addon(
        mmSolver_blender_addon
        ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver_blender_addon
        ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver_blender_addon.zip
        ${CMAKE_CURRENT_SOURCE_DIR}
)

# Install Blender addon.
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/mmSolver_blender_addon.zip"
        DESTINATION "${MODULE_FULL_NAME}/blender/")
