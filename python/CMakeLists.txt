# Generate .py files from Qt .ui

find_package(Maya REQUIRED)

function (add_ui_compile
        name
        input_file
        output_file)
    set(EXEC_SCRIPT ${CMAKE_SOURCE_DIR}/scripts/compileUI.py)
    add_custom_command(
            OUTPUT ${output_file}
            COMMAND ${MAYA_PYTHON_EXECUTABLE} ${EXEC_SCRIPT} ${input_file}
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
            DEPENDS ${input_file}
    )
    add_custom_target(
            compile_ui_${name} ALL
            DEPENDS ${output_file}
            COMMENT "Compiling Qt UI file (${input_file})..."
    )
    add_dependencies(mmSolver compile_ui_${name})
endfunction()


add_ui_compile("base"
    ${CMAKE_SOURCE_DIR}/python/mmSolver/ui/base.ui
    ${CMAKE_SOURCE_DIR}/python/mmSolver/ui/ui_base.py
)

add_ui_compile("channelsen"
    ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/channelsen/ui/channelsen_layout.ui
    ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/channelsen/ui/ui_channelsen_layout.py
)

add_ui_compile("smoothkeyframes"
    ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/smoothkeyframes/ui/smoothkeys_layout.ui
    ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/smoothkeyframes/ui/ui_smoothkeys_layout.py
)

add_ui_compile("loadmarker"
    ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/loadmarker/ui/loadmarker_layout.ui
    ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/loadmarker/ui/ui_loadmarker_layout.py
)

add_ui_compile("solver"
    ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/solver/ui/solver_layout.ui
    ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/solver/ui/ui_solver_layout.py
)
