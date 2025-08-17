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

# Create Python file with some build options baked in.
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/constant.py
  ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/constant.py
  @ONLY)

# Install generated constant file.
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/constant.py
        DESTINATION "${MODULE_FULL_NAME}/python/mmSolver/")

# Install Python API and tools
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/"
        DESTINATION "${MODULE_FULL_NAME}/python"
        FILES_MATCHING PATTERN "*.py"
        PATTERN "__pycache__" EXCLUDE
        PATTERN "*mmSolver/constant.py" EXCLUDE)


if (MMSOLVER_BUILD_QT_UI)
    include(MMSolverUtils)
    compile_qt_ui_to_python_file("base"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/ui/base.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/ui/ui_base.py
            )

    compile_qt_ui_to_python_file("centertwodee"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/centertwodee/ui/centertwodee_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/centertwodee/ui/ui_centertwodee_layout.py
            )

    compile_qt_ui_to_python_file("channelsen"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/channelsen/ui/channelsen_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/channelsen/ui/ui_channelsen_layout.py
            )

    compile_qt_ui_to_python_file("convertmarker"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/convertmarker/ui/convertmarker_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/convertmarker/ui/ui_convertmarker_layout.py
            )

    compile_qt_ui_to_python_file("raycastmarker"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/raycastmarker/ui/raycastmarker_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/raycastmarker/ui/ui_raycastmarker_layout.py
            )

    compile_qt_ui_to_python_file("reparent2"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/reparent2/ui/reparent2_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/reparent2/ui/ui_reparent2_layout.py
            )

    compile_qt_ui_to_python_file("removesolvernodes"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/removesolvernodes/ui/removesolvernodes_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/removesolvernodes/ui/ui_removesolvernodes_layout.py
            )

    compile_qt_ui_to_python_file("smoothkeyframes"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/smoothkeyframes/ui/smoothkeys_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/smoothkeyframes/ui/ui_smoothkeys_layout.py
            )

    compile_qt_ui_to_python_file("setcameraoriginframe"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/setcameraoriginframe/ui/originframe_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/setcameraoriginframe/ui/ui_originframe_layout.py
            )

    compile_qt_ui_to_python_file("loadmarker"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/loadmarker/ui/loadmarker_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/loadmarker/ui/ui_loadmarker_layout.py
            )

    compile_qt_ui_to_python_file("solver_layout"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/ui/solver_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/solver/ui/ui_solver_layout.py
            )

    compile_qt_ui_to_python_file("solver_nodebrowser_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/nodebrowser_widget.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/solver/widget/ui_nodebrowser_widget.py
            )

    compile_qt_ui_to_python_file("solver_framerange_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/framerange_widget.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/solver/widget/ui_framerange_widget.py
            )

    compile_qt_ui_to_python_file("solver_collection_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/collection_widget.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/solver/widget/ui_collection_widget.py
            )

    compile_qt_ui_to_python_file("solver_rootframe_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/rootframe_widget.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/solver/widget/ui_rootframe_widget.py
            )

    compile_qt_ui_to_python_file("solver_solver_basic_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/solver_basic_widget.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/solver/widget/ui_solver_basic_widget.py
            )

    compile_qt_ui_to_python_file("solver_solver_standard_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/solver_standard_widget.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/solver/widget/ui_solver_standard_widget.py
            )

    compile_qt_ui_to_python_file("solver_solver_camera_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/solver_camera_widget.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/solver/widget/ui_solver_camera_widget.py
            )

    compile_qt_ui_to_python_file("solver_solverstate_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/solverstate_widget.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/solver/widget/ui_solverstate_widget.py
            )

    compile_qt_ui_to_python_file("solver_solver_widget"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/solver/widget/solver_widget.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/solver/widget/ui_solver_widget.py
            )

    compile_qt_ui_to_python_file("solver_about"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/aboutwindow/ui/about_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/aboutwindow/ui/ui_about_layout.py
            )

    compile_qt_ui_to_python_file("sysinfo"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/sysinfowindow/ui/sysinfo_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/sysinfowindow/ui/ui_sysinfo_layout.py
            )

    compile_qt_ui_to_python_file("setattributedetails"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/setattributedetails/ui/dialog.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/setattributedetails/ui/ui_dialog.py
            )

    compile_qt_ui_to_python_file("preferences_window"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/userprefswindow/ui/pref_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/userprefswindow/ui/ui_pref_layout.py
            )

    compile_qt_ui_to_python_file("attrbake"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/attributebake/ui/attrbake_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/attributebake/ui/ui_attrbake_layout.py
          )

    compile_qt_ui_to_python_file("attributecurvefilterpops"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/attributecurvefilterpops/ui/attrcurvefilterpops_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/attributecurvefilterpops/ui/ui_attrcurvefilterpops_layout.py
            )

    compile_qt_ui_to_python_file("attributecurvesimplify"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/attributecurvesimplify/ui/attrcurvesimplify_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/attributecurvesimplify/ui/ui_attrcurvesimplify_layout.py
            )

    compile_qt_ui_to_python_file("createcontroller2"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/createcontroller2/ui/createcontroller_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/createcontroller2/ui/ui_createcontroller_layout.py
            )

    compile_qt_ui_to_python_file("createcontroller3beta"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/createcontroller3beta/ui/createcontroller_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/createcontroller3beta/ui/ui_createcontroller_layout.py
            )

    compile_qt_ui_to_python_file("cameraobjectscaleadjust"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/cameraobjectscaleadjust/ui/cameraobjectscaleadjust_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/cameraobjectscaleadjust/ui/ui_cameraobjectscaleadjust_layout.py
            )

    compile_qt_ui_to_python_file("screenspacerigbake"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/screenspacerigbake/ui/screenspacerigbake_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/screenspacerigbake/ui/ui_screenspacerigbake_layout.py
            )

    compile_qt_ui_to_python_file("surfacecluster"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/surfacecluster/ui/surfacecluster_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/surfacecluster/ui/ui_surfacecluster_layout.py
            )

    compile_qt_ui_to_python_file("meshfrompoints"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/meshfrompoints/ui/meshfrompoints_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/meshfrompoints/ui/ui_meshfrompoints_layout.py
            )

    compile_qt_ui_to_python_file("imagecacheprefs"
            ${CMAKE_CURRENT_SOURCE_DIR}/mmSolver/tools/imagecacheprefs/ui/imagecacheprefs_layout.ui
            ${CMAKE_CURRENT_BINARY_DIR}/mmSolver/tools/imagecacheprefs/ui/ui_imagecacheprefs_layout.py
            )

    # Install generated Python UI files
    install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/"
            DESTINATION "${MODULE_FULL_NAME}/python"
            FILES_MATCHING PATTERN "ui_*.py"
            PATTERN "__pycache__" EXCLUDE
            PATTERN "CMakeFiles" EXCLUDE
            )
endif ()
