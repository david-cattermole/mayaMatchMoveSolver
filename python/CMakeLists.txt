# Copyright (C) 2019 David Cattermole.
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
# Generate .py files from Qt .ui

find_package(Maya REQUIRED)

function(add_ui_compile
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
    if (BUILD_PLUGIN)
        add_dependencies(mmSolver compile_ui_${name})
    endif ()
endfunction()


if (BUILD_QT_UI)
    add_ui_compile("base"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/ui/base.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/ui/ui_base.py
            )

    add_ui_compile("channelsen"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/channelsen/ui/channelsen_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/channelsen/ui/ui_channelsen_layout.py
            )

    add_ui_compile("raycastmarker"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/raycastmarker/ui/raycastmarker_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/raycastmarker/ui/ui_raycastmarker_layout.py
            )

    add_ui_compile("removesolvernodes"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/removesolvernodes/ui/removesolvernodes_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/removesolvernodes/ui/ui_removesolvernodes_layout.py
            )

    add_ui_compile("smoothkeyframes"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/smoothkeyframes/ui/smoothkeys_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/smoothkeyframes/ui/ui_smoothkeys_layout.py
            )

    add_ui_compile("loadmarker"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/loadmarker/ui/loadmarker_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/loadmarker/ui/ui_loadmarker_layout.py
            )

    add_ui_compile("solver_layout"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/solver/ui/solver_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/solver/ui/ui_solver_layout.py
            )

    add_ui_compile("solver_widgets"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/solver/widget/nodebrowser_widget.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/solver/widget/ui_nodebrowser_widget.py
            )

    add_ui_compile("solver_about"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/aboutwindow/ui/about_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/aboutwindow/ui/ui_about_layout.py
            )

    add_ui_compile("sysinfo"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/sysinfowindow/ui/sysinfo_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/sysinfowindow/ui/ui_sysinfo_layout.py
            )

    add_ui_compile("setattributedetails"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/setattributedetails/ui/dialog.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/setattributedetails/ui/ui_dialog.py
            )

    add_ui_compile("preferences_window"
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/userprefswindow/ui/pref_layout.ui
            ${CMAKE_SOURCE_DIR}/python/mmSolver/tools/userprefswindow/ui/ui_pref_layout.py
            )
endif ()
