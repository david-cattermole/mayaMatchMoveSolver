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

# Normalize the path to avoid escape sequence issues on Windows.
file(TO_CMAKE_PATH "${BUILD_DOCS_DIR_BASE}" BUILD_DOCS_DIR_BASE)

set(DOCS_LOCAL_DIR "${CMAKE_CURRENT_SOURCE_DIR}/build/")
set(DOCS_MODULE_DIR "${MODULE_FULL_NAME}/docs/")

message(STATUS "Documentation local directory: ${DOCS_LOCAL_DIR}")
message(STATUS "Documentation build directory: ${BUILD_DOCS_DIR_BASE}")
message(STATUS "Documentation module directory: ${DOCS_MODULE_DIR}")

# Ensure the external build directory exists.
file(MAKE_DIRECTORY ${BUILD_DOCS_DIR_BASE})

# Build Documentation (using Python Sphinx)
set(input_file "${CMAKE_CURRENT_SOURCE_DIR}/source/index.html")
set(output_file "${BUILD_DOCS_DIR_BASE}/html/py-modindex.html")
if(SPHINX_AVAILABLE)
    if(WIN32)
        set(DOCS_WRAPPER_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/build_docs_with_venv.bat)
    else()
        set(DOCS_WRAPPER_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/build_docs_with_venv.bash)
    endif()

    add_custom_command(
            OUTPUT ${output_file}
            COMMAND ${CMAKE_COMMAND} -E copy ${input_file} ${BUILD_DOCS_DIR_BASE}/html/index.html
            COMMAND ${CMAKE_COMMAND} -E env BUILD_DOCS_DIR_BASE=${BUILD_DOCS_DIR_BASE} MAYA_VERSION=${MAYA_VERSION} ${DOCS_WRAPPER_SCRIPT}
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            DEPENDS ${input_files}
    )
    add_custom_target(
            build_documentation ALL
            # TODO: Can we be smarter about what the documentation
            # target depends on? For example listing all the Python
            # code and the HTML and images for the site?
            DEPENDS ${output_file}
            COMMENT "Building Documentation (with Sphinx) (${input_file})..."
    )
else()
    # Without Sphinx, we just copy the placeholder page, so our
    # installed package always has a file it can open.
    add_custom_command(
            OUTPUT ${output_file}
            COMMAND ${CMAKE_COMMAND} -E copy ${input_file} ${BUILD_DOCS_DIR_BASE}/html/index.html
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            DEPENDS ${input_files}
    )
    add_custom_target(
            build_documentation ALL
            # TODO: Can we be smarter about what the documentation
            # target depends on? For example listing all the Python
            # code and the HTML and images for the site?
            DEPENDS ${output_file}
            COMMENT "Building Documentation (with placeholder file) (${input_file})..."
    )
endif()

if (MMSOLVER_BUILD_PLUGIN)
    add_dependencies(mmSolver build_documentation)
endif ()

# Install Documentation.
if(EXISTS "${BUILD_DOCS_DIR_BASE}")
    # NOTE: We already copied the placeholder file above, so we can
    # install that, even if nothing else exists.
    install(DIRECTORY "${BUILD_DOCS_DIR_BASE}/"
        DESTINATION "${DOCS_MODULE_DIR}")
elseif(EXISTS "${DOCS_LOCAL_DIR}")
    # Install fallback documentation if sphinx-build is not available.
    message(STATUS "Installing fallback documentation from ${CMAKE_CURRENT_SOURCE_DIR}/docs/build/")
    install(DIRECTORY "${DOCS_LOCAL_DIR} "
        DESTINATION "${DOCS_MODULE_DIR}")
else()
  message(WARNING "No documentation found to install. Skipping documentation installation.")
endif()
