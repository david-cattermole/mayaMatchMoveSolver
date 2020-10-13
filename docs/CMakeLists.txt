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


# Build Documentation (using Python Sphinx)

set(input_files
        ${CMAKE_SOURCE_DIR}/docs/source/index.rst
        ${CMAKE_SOURCE_DIR}/docs/source/introduction.rst
        ${CMAKE_SOURCE_DIR}/docs/source/commands.rst
        ${CMAKE_SOURCE_DIR}/docs/source/nodes.rst
        ${CMAKE_SOURCE_DIR}/docs/source/tools.rst
        ${CMAKE_SOURCE_DIR}/docs/source/tutorial.rst
        ${CMAKE_SOURCE_DIR}/docs/source/solver_design.rst
        ${CMAKE_SOURCE_DIR}/docs/source/references.rst
        ${CMAKE_SOURCE_DIR}/docs/source/mmSolver.api.rst
        ${CMAKE_SOURCE_DIR}/docs/source/mmSolver.logger.rst
        ${CMAKE_SOURCE_DIR}/docs/source/mmSolver.tools.rst
        ${CMAKE_SOURCE_DIR}/docs/source/mmSolver.ui.rst
        ${CMAKE_SOURCE_DIR}/docs/source/mmSolver.utils.rst
        )
set(output_file ${CMAKE_SOURCE_DIR}/docs/build/html/py-modindex.html)
add_custom_command(
        OUTPUT ${output_file}
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/docs/source/index.html ${CMAKE_SOURCE_DIR}/docs/build/html/index.html
        COMMAND make html
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/docs
        DEPENDS ${input_files}
)
add_custom_target(
        build_documentation ALL
        DEPENDS ${output_file}
        COMMENT "Building Documentation (with Sphinx) (${input_file})..."
)
if (BUILD_PLUGIN)
    add_dependencies(mmSolver build_documentation)
endif ()

# Install Documentation
if (BUILD_DOCS)
    install(DIRECTORY "docs/build/html/"
            DESTINATION "${MODULE_FULL_NAME}/docs/html")
endif ()
