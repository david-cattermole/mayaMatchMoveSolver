# Copyright (C) 2019, 2021 David Cattermole, Kazuma Tonegawa.
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
# Configure and install Python scripts and Qt .ui files.
#

find_package(Maya REQUIRED)

# Create Python file with some build options baked in.
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/constant.py.in
  ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/constant.py
  @ONLY)


# Compile a .ui file into a .py file using 'mayapy' command.
function(add_ui_compile
         name
         input_file
         output_file)

    set(EXEC_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/../scripts/compileUI.py)

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

    if (BUILD_PLUGIN)
        add_dependencies(mmSolver compile_ui_${name})
    endif ()

endfunction()


if (BUILD_QT_UI)
    add_ui_compile("base"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/ui/base.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/ui/ui_base.py
            )

    add_ui_compile("centertwodee"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/centertwodee/ui/centertwodee_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/centertwodee/ui/ui_centertwodee_layout.py
            )

    add_ui_compile("channelsen"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/channelsen/ui/channelsen_layout.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/channelsen/ui/ui_channelsen_layout.py
            )

    add_ui_compile("convertmarker"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/convertmarker/ui/convertmarker_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/convertmarker/ui/ui_convertmarker_layout.py
            )

    add_ui_compile("raycastmarker"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/raycastmarker/ui/raycastmarker_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/raycastmarker/ui/ui_raycastmarker_layout.py
            )

    add_ui_compile("reparent2"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/reparent2/ui/reparent2_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/reparent2/ui/ui_reparent2_layout.py
            )

    add_ui_compile("removesolvernodes"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/removesolvernodes/ui/removesolvernodes_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/removesolvernodes/ui/ui_removesolvernodes_layout.py
            )

    add_ui_compile("smoothkeyframes"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/smoothkeyframes/ui/smoothkeys_layout.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/smoothkeyframes/ui/ui_smoothkeys_layout.py
            )

    add_ui_compile("loadmarker"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/loadmarker/ui/loadmarker_layout.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/loadmarker/ui/ui_loadmarker_layout.py
            )

    add_ui_compile("solver_layout"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/ui/solver_layout.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/ui/ui_solver_layout.py
            )

    add_ui_compile("solver_nodebrowser_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/nodebrowser_widget.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/ui_nodebrowser_widget.py
            )

    add_ui_compile("solver_framerange_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/framerange_widget.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/ui_framerange_widget.py
            )

    add_ui_compile("solver_collection_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/collection_widget.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/ui_collection_widget.py
            )

    add_ui_compile("solver_rootframe_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/rootframe_widget.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/ui_rootframe_widget.py
            )

    add_ui_compile("solver_solver_basic_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/solver_basic_widget.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/ui_solver_basic_widget.py
            )

    add_ui_compile("solver_solver_legacy_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/solver_legacy_widget.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/ui_solver_legacy_widget.py
            )

    add_ui_compile("solver_solver_standard_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/solver_standard_widget.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/ui_solver_standard_widget.py
            )


    add_ui_compile("solver_solverstate_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/solverstate_widget.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/ui_solverstate_widget.py
            )

    add_ui_compile("solver_solver_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/solver_widget.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/ui_solver_widget.py
            )

    add_ui_compile("solver_about"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/aboutwindow/ui/about_layout.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/aboutwindow/ui/ui_about_layout.py
            )

    add_ui_compile("sysinfo"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/sysinfowindow/ui/sysinfo_layout.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/sysinfowindow/ui/ui_sysinfo_layout.py
            )

    add_ui_compile("setattributedetails"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/setattributedetails/ui/dialog.ui
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/setattributedetails/ui/ui_dialog.py
            )

    add_ui_compile("preferences_window"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/userprefswindow/ui/pref_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/userprefswindow/ui/ui_pref_layout.py
            )

    add_ui_compile("fastbake"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/attributebake/ui/attrbake_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/attributebake/ui/ui_attrbake_layout.py
            )

    add_ui_compile("createcontroller2"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/createcontroller2/ui/createcontroller_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/createcontroller2/ui/ui_createcontroller_layout.py
            )

endif ()


# Install Python API and tools
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/"
        DESTINATION "${MODULE_FULL_NAME}/python"
        FILES_MATCHING PATTERN "*.py")
