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
        COMMENT "Compiling Qt UI file (${input_file})..."
)
add_dependencies(mmSolver build_documentation)
