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
# Configure the Documentation building system.


# Create Python file for documentation sphinx build with some build
# options baked in.
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/source/conf.py.in
  ${CMAKE_CURRENT_SOURCE_DIR}/source/conf.py
  @ONLY)


# Build Documentation (using Python Sphinx)
set(input_files
        source/index.rst
        source/introduction.rst
        source/commands.rst
        source/nodes.rst
        source/tools.rst
        source/tutorial.rst
        source/solver_design.rst
        source/references.rst
        source/mmSolver.api.rst
        source/mmSolver.logger.rst
        source/mmSolver.tools.rst
        source/mmSolver.ui.rst
        source/mmSolver.utils.rst
        )

# Get the location where the build files will be generated
set(BUILD_OS_NAME "unknown")
if(MSVC)
  set(BUILD_OS_NAME "windows64")
elseif(MACOS)
  set(BUILD_OS_NAME "mac")
else()
  set(BUILD_OS_NAME "linux")
endif()
set(BUILD_DOCS_DIR "build_${BUILD_OS_NAME}_maya${MAYA_VERSION}")

set(output_file ${BUILD_DOCS_DIR}/html/py-modindex.html)


add_custom_command(
        OUTPUT ${output_file}
        COMMAND ${CMAKE_COMMAND} -E copy source/index.html ${BUILD_DOCS_DIR}/html/index.html
        COMMAND make html
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
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
install(DIRECTORY "${BUILD_DOCS_DIR}/html/"
        DESTINATION "${MODULE_FULL_NAME}/docs/html")
