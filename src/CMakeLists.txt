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
# Building the C++ code for mmSolver.
#

# Explicitly enable features
set(CMAKE_MACOSX_RPATH 1)


# Default Solver to use.
set(PREFERRED_SOLVER "cminpack_lmder"
  CACHE STRING
  "Choices are cminpack_lm, cminpack_lmder or ceres. Which solver is used by default?")


# Set a default solver
set(DEFAULT_SOLVER ${PREFERRED_SOLVER})

# Source
set(SOURCE_FILES
  utilities/debug_utils.cpp
  utilities/number_utils.cpp
  utilities/string_utils.cpp
  adjust/adjust_base.cpp
  adjust/adjust_cminpack_base.cpp
  adjust/adjust_cminpack_lmder.cpp
  adjust/adjust_cminpack_lmdif.cpp
  adjust/adjust_relationships.cpp
  adjust/adjust_solveFunc.cpp
  calibrate/calibrate_common.cpp
  calibrate/vanishing_point.cpp
  lens/lens_model_3de_classic.cpp
  lens/lens_model_basic.cpp
  core/mmcamera.cpp
  core/mmcoord.cpp
  core/mmdata.cpp
  core/mmmath.cpp
  core/reprojection.cpp
  shape/ShapeDrawUtils.cpp
  shape/MarkerShapeNode.cpp
  shape/MarkerDrawOverride.cpp
  shape/BundleShapeNode.cpp
  shape/BundleDrawOverride.cpp
  shape/SkyDomeShapeNode.cpp
  shape/SkyDomeDrawOverride.cpp
  shape/LineShapeNode.cpp
  shape/LineDrawOverride.cpp
  render/HudRender.cpp
  render/MMRendererCmd.cpp
  render/PresentTarget.cpp
  render/QuadRenderBase.cpp
  render/QuadRenderBlend.cpp
  render/QuadRenderCopy.cpp
  render/QuadRenderEdgeDetect.cpp
  render/QuadRenderInvert.cpp
  render/RenderGlobalsNode.cpp
  render/RenderOverride.cpp
  render/SceneRender.cpp
  mayahelper/maya_camera.cpp
  mayahelper/maya_marker.cpp
  mayahelper/maya_bundle.cpp
  mayahelper/maya_attr.cpp
  mayahelper/maya_scene_graph.cpp
  mayahelper/maya_utils.cpp
  common_arg_flags.cpp
  MMCameraCalibrateNode.cpp
  MMCameraRelativePoseCmd.cpp
  MMCameraSolveCmd.cpp
  MMLensData.cpp
  MMLensDeformerNode.cpp
  MMLensEvaluateNode.cpp
  MMLensModel3deClassicNode.cpp
  MMLensModelBasicNode.cpp
  MMLensModelToggleNode.cpp
  MMLineIntersectNode.cpp
  MMMarkerGroupTransformNode.cpp
  MMMarkerScaleNode.cpp
  MMMarkerTransformMatrix.cpp
  MMMarkerTransformNode.cpp
  MMReprojectionCmd.cpp
  MMReprojectionNode.cpp
  MMSolverAffectsCmd.cpp
  MMSolverCmd.cpp
  MMSolverTypeCmd.cpp
  MMTestCameraMatrixCmd.cpp
  pluginMain.cpp
)

include(MMSolverUtils)

# 'mmSolver' maya plugin library
add_library_maya_plugin(mmSolver "${SOURCE_FILES}")
set_target_maya_plugin_compile_options(mmSolver)
target_include_directories(mmSolver
  PRIVATE ../include
  PRIVATE .
  )
# On Linux the 'm' library is required.
if(CMAKE_SYSTEM_NAME STREQUAL Linux)
  target_link_libraries(mmSolver PUBLIC m)
endif ()


if (BUILD_MMSCENEGRAPH)
  add_subdirectory(mmscenegraph)
  if(MMSCENEGRAPH_INCLUDE_DIR)
    target_link_libraries(mmSolver
      PRIVATE
      mmscenegraph
      )
    target_include_directories(mmSolver
      PRIVATE ${MMSCENEGRAPH_INCLUDE_DIR}
      )
    target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_MMSCENEGRAPH)
  endif()
endif ()

set_global_treat_warnings_as_errors()
set_global_maya_plugin_compile_options()


find_package(Maya REQUIRED)
message(STATUS "MAYA: ${MAYA_FOUND}")
message(STATUS "MAYA: Root=${MAYA_LOCATION}")
message(STATUS "MAYA: API=${MAYA_API_VERSION}")
message(STATUS "MAYA: Maya Executable=${MAYA_EXECUTABLE}")
message(STATUS "MAYA: Python Executable=${MAYA_PYTHON_EXECUTABLE}")
message(STATUS "MAYA: Includes=${MAYA_INCLUDE_DIRS}")
message(STATUS "MAYA: Libraries=${MAYA_LIBRARIES}")
if(MAYA_FOUND)
  target_include_directories(mmSolver
    PRIVATE ${MAYA_INCLUDE_DIRS}
    )
  target_link_libraries(mmSolver
    PUBLIC
    ${MAYA_OpenMaya_LIBRARY}
    ${MAYA_OpenMayaAnim_LIBRARY}
    ${MAYA_OpenMayaRender_LIBRARY}
    ${MAYA_OpenMayaUI_LIBRARY}
    ${MAYA_Foundation_LIBRARY}
    )
endif()


find_package(CMinpack REQUIRED)
message(STATUS "CMINPACK: ${CMINPACK_FOUND}")
message(STATUS "CMINPACK: Root=${CMINPACK_ROOT}")
message(STATUS "CMINPACK: Include=${CMINPACK_INCLUDE_DIRS}")
message(STATUS "CMINPACK: Library=${CMINPACK_LIBRARIES}")
message(STATUS "CMINPACK: Library DLL=${CMINPACK_LIBRARY_DLL}")
if(CMINPACK_FOUND)
  target_include_directories(mmSolver
    PRIVATE ${CMINPACK_INCLUDE_DIRS}
    )
  target_link_libraries(mmSolver
    PRIVATE
    ${CMINPACK_LIBRARIES}
    )
  target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_CMINPACK)
  install_shared_library(
    ${CMINPACK_LIBRARY}
    ${CMINPACK_LIBRARY_DLL}
    "${MODULE_FULL_NAME}/lib/")
endif()


find_package(Eigen3 REQUIRED)
message(STATUS "EIGEN3: ${EIGEN3_FOUND}")
message(STATUS "EIGEN3: Version=${EIGEN3_VERSION_STRING}")
message(STATUS "EIGEN3: Root=${Eigen3_DIR}")
message(STATUS "EIGEN3: Include=${EIGEN3_INCLUDE_DIRS}")
if(EIGEN3_FOUND)
  target_link_libraries(mmSolver
    PRIVATE
    Eigen3::Eigen
    )
  target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_EIGEN)
endif()


find_package(Cxsparse REQUIRED)
message(STATUS "CXSPARSE: ${CXSPARSE_FOUND}")
message(STATUS "CXSPARSE: Root=${CXSPARSE_ROOT}")
message(STATUS "CXSPARSE: Include=${CXSPARSE_INCLUDE_DIRS}")
message(STATUS "CXSPARSE: Library=${CXSPARSE_LIBRARIES}")
if(CXSPARSE_FOUND)
  target_include_directories(mmSolver
    PRIVATE ${CXSPARSE_INCLUDE_DIRS}
    )
  target_link_libraries(mmSolver
    PRIVATE
    ${CXSPARSE_LIBRARIES}
    )
  target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_CXSPARSE)
endif()


# find_package(Gflags REQUIRED)
message(STATUS "GFLAGS: ${GFLAGS_FOUND}")
message(STATUS "GFLAGS: Include=${GFLAGS_INCLUDE_DIRS}")
message(STATUS "GFLAGS: Library=${GFLAGS_LIBRARIES}")
if(GFLAGS_FOUND)
  target_include_directories(mmSolver
    PRIVATE ${GFLAGS_INCLUDE_DIRS}
    )
  target_link_libraries(mmSolver
    PRIVATE
    ${GFLAGS_LIBRARIES}
    )
  target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_GFLAGS)
  install_shared_library(
    ${GFLAGS_LIBRARY}
    ${GFLAGS_LIBRARY_DLL}
    "${MODULE_FULL_NAME}/lib/")
endif()


# find_package(Glog REQUIRED)
message(STATUS "GLOG: ${GLOG_FOUND}")
message(STATUS "GLOG: Include=${GLOG_INCLUDE_DIRS}")
message(STATUS "GLOG: Library=${GLOG_LIBRARIES}")
if(GLOG_FOUND)
  target_include_directories(mmSolver
    PRIVATE ${GLOG_INCLUDE_DIRS}
    )
  target_link_libraries(mmSolver
    PRIVATE
    ${GLOG_LIBRARIES}
    )
  target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_GLOG)
  install_shared_library(
    ${GLOG_LIBRARY}
    ${GLOG_LIBRARY_DLL}
    "${MODULE_FULL_NAME}/lib/")
endif()


find_package(Ceres REQUIRED)
message(STATUS "CERES: ${CERES_FOUND}")
message(STATUS "CERES: Version=${CERES_VERSION}")
message(STATUS "CERES: Root=${CERES_ROOT}")
message(STATUS "CERES: Include=${CERES_INCLUDE_DIRS}")
message(STATUS "CERES: Library=${CERES_LIBRARIES}")
if(CERES_FOUND)
  target_include_directories(mmSolver
    PRIVATE ${CERES_INCLUDE_DIRS}
    )
  target_link_libraries(mmSolver
    PRIVATE
    ceres
    )
  target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_CERES)
endif()


# find_package(Libmv REQUIRED)
message(STATUS "LIBMV: ${LIBMV_FOUND}")
message(STATUS "LIBMV: Root=${LIBMV_ROOT}")
message(STATUS "LIBMV: Include=${LIBMV_INCLUDE_DIRS}")
message(STATUS "LIBMV: Library=${LIBMV_LIBRARIES}")
if(LIBMV_FOUND)
  target_include_directories(mmSolver
    PRIVATE ${LIBMV_INCLUDE_DIRS}
    )
  target_link_libraries(mmSolver
    PRIVATE
    ${LIBMV_LIBRARIES}
    )
  target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_LIBMV)
endif()


find_package(OpenMVG REQUIRED)
message(STATUS "OPENMVG: ${OPENMVG_FOUND}")
message(STATUS "OPENMVG: Version=${OPENMVG_VERSION}")
message(STATUS "OPENMVG: Root=${OPENMVG_ROOT}")
message(STATUS "OPENMVG: Include=${OPENMVG_INCLUDE_DIRS}")
message(STATUS "OPENMVG: Library=${OPENMVG_LIBRARIES}")
if(OPENMVG_FOUND)
  target_link_libraries(mmSolver
    PRIVATE
    OpenMVG::openMVG_camera
    OpenMVG::openMVG_exif
    OpenMVG::openMVG_features
    OpenMVG::openMVG_geodesy
    OpenMVG::openMVG_geometry
    OpenMVG::openMVG_graph
    OpenMVG::openMVG_image
    OpenMVG::openMVG_linearProgramming
    OpenMVG::openMVG_matching
    OpenMVG::openMVG_matching_image_collection
    OpenMVG::openMVG_multiview
    OpenMVG::openMVG_numeric
    OpenMVG::openMVG_robust_estimation
    OpenMVG::openMVG_sfm
    OpenMVG::openMVG_system
    )
  target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_OPENMVG)
endif()


if(WIN32)
  find_package(Dlfcn REQUIRED)
  message(STATUS "DLFCN ${DLFCN_FOUND}")
  message(STATUS "DLFCN Root=${DLFCN_ROOT}")
  message(STATUS "DLFCN Libraries=${DLFCN_LIBRARIES}")
  message(STATUS "DLFCN Library DLL=${DLFCN_LIBRARY_DLL}")
  message(STATUS "DLFCN Include=${DLFCN_INCLUDE_DIRS}")
  target_include_directories(mmSolver
    PRIVATE ${DLFCN_INCLUDE_DIRS}
    )
  target_link_libraries(mmSolver
    PRIVATE
    ${DLFCN_LIBRARIES}
    )
  install_shared_libraries(
    ${DLFCN_LIBRARY}
    ${DLFCN_LIBRARY_DLL}
    "${MODULE_FULL_NAME}/lib/")
endif()


find_package(LDPK REQUIRED)
message(STATUS "LDPK ${LDPK_FOUND}")
message(STATUS "LDPK Root=${LDPK_ROOT}")
message(STATUS "LDPK Libraries=${LDPK_LIBRARIES}")
message(STATUS "LDPK Include=${LDPK_INCLUDE_DIRS}")
if(LDPK_FOUND)
  target_include_directories(mmSolver
    PRIVATE ${LDPK_INCLUDE_DIRS}
    )
  target_link_libraries(mmSolver
    PRIVATE
    ${LDPK_LIBRARIES}
    )
  target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_LDPK)
endif()


install_target_plugin_to_module(mmSolver "${MODULE_FULL_NAME}")
