# Copyright (C) 2019, 2020, 2025 David Cattermole.
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

include(MMSolverUtils)

# Create Python file for documentation sphinx build with some build
# options baked in.
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/source/conf.py.in
  ${CMAKE_CURRENT_SOURCE_DIR}/source/conf.py
  @ONLY)

find_program(SPHINX_BUILD sphinx-build)
if(SPHINX_BUILD)
    message(STATUS "Found sphinx-build: ${SPHINX_BUILD}")
    set(SPHINX_AVAILABLE TRUE)
else()
    message(WARNING "sphinx-build not found. Documentation will not be built.")
    set(SPHINX_AVAILABLE FALSE)
endif()

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

# Build Documentation (using Python Sphinx)
if(SPHINX_AVAILABLE)
    # Get the location where the build files will be generated.
    get_maya_module_os_name(os_name)
    set(BUILD_DOCS_DIR "build_${os_name}_maya${MAYA_VERSION}")

    set(input_file source/index.html)
    set(output_file ${BUILD_DOCS_DIR}/html/py-modindex.html)
    add_custom_command(
            OUTPUT ${output_file}
            COMMAND ${CMAKE_COMMAND} -E copy ${input_file} ${BUILD_DOCS_DIR}/html/index.html
            COMMAND make html
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            DEPENDS ${input_files}
    )

    add_custom_target(
            build_documentation ALL
            DEPENDS ${output_file}
            COMMENT "Building Documentation (with Sphinx) (${input_file})..."
    )

    if (MMSOLVER_BUILD_PLUGIN)
        add_dependencies(mmSolver build_documentation)
    endif ()

    # Install Documentation
    install(DIRECTORY "${BUILD_DOCS_DIR}/html/"
            DESTINATION "${MODULE_FULL_NAME}/docs/html")
else()
    message(STATUS "Skipping documentation build because sphinx-build is not available")
endif()
