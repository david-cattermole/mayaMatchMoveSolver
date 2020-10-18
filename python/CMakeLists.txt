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
# Configure and install Python scripts and Qt .ui files.
#

find_package(Maya REQUIRED)

# Create Python file with some build options baked in.
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/constant.py.in
  ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/constant.py
  @ONLY)


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
            mmSolver/ui/base.ui
            mmSolver/ui/ui_base.py
            )

    add_ui_compile("channelsen"
            mmSolver/tools/channelsen/ui/channelsen_layout.ui
            mmSolver/tools/channelsen/ui/ui_channelsen_layout.py
            )

    add_ui_compile("smoothkeyframes"
            mmSolver/tools/smoothkeyframes/ui/smoothkeys_layout.ui
            mmSolver/tools/smoothkeyframes/ui/ui_smoothkeys_layout.py
            )

    add_ui_compile("loadmarker"
            mmSolver/tools/loadmarker/ui/loadmarker_layout.ui
            mmSolver/tools/loadmarker/ui/ui_loadmarker_layout.py
            )

    add_ui_compile("solver_layout"
            mmSolver/tools/solver/ui/solver_layout.ui
            mmSolver/tools/solver/ui/ui_solver_layout.py
            )

    add_ui_compile("solver_widgets"
            mmSolver/tools/solver/widget/nodebrowser_widget.ui
            mmSolver/tools/solver/widget/ui_nodebrowser_widget.py
            )

    add_ui_compile("solver_about"
            mmSolver/tools/aboutwindow/ui/about_layout.ui
            mmSolver/tools/aboutwindow/ui/ui_about_layout.py
            )

    add_ui_compile("sysinfo"
            mmSolver/tools/sysinfowindow/ui/sysinfo_layout.ui
            mmSolver/tools/sysinfowindow/ui/ui_sysinfo_layout.py
            )

    add_ui_compile("setattributedetails"
            mmSolver/tools/setattributedetails/ui/dialog.ui
            mmSolver/tools/setattributedetails/ui/ui_dialog.py
            )
endif ()


# Install Python API and tools
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/"
        DESTINATION "${MODULE_FULL_NAME}/python"
        FILES_MATCHING PATTERN "*.py")
