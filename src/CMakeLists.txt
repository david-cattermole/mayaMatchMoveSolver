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
  core/bundleAdjust_base.cpp
  core/bundleAdjust_relationships.cpp
  core/bundleAdjust_solveFunc.cpp
  core/bundleAdjust_cminpack_base.cpp
  core/bundleAdjust_cminpack_lmdif.cpp
  core/bundleAdjust_cminpack_lmder.cpp
  core/calibrate/common.cpp
  core/calibrate/vanishingPoint.cpp
  core/lensModelBasic.cpp
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
  Camera.cpp
  Marker.cpp
  Bundle.cpp
  Attr.cpp
  mayaSceneGraph.cpp
  mayaUtils.cpp
  commonArgFlags.cpp
  MMSolverAffectsCmd.cpp
  MMMarkerScaleNode.cpp
  MMReprojectionNode.cpp
  MMMarkerGroupTransformNode.cpp
  MMCameraCalibrateNode.cpp
  MMCameraRelativePoseCmd.cpp
  MMLineIntersectNode.cpp
  MMMarkerTransformMatrix.cpp
  MMMarkerTransformNode.cpp
  MMTestCameraMatrixCmd.cpp
  MMSolverCmd.cpp
  MMSolverTypeCmd.cpp
  MMReprojectionCmd.cpp
  MMCameraSolveCmd.cpp
  MMLensDeformerNode.cpp
  MMLensModelBasicNode.cpp
  MMLensModelToggleNode.cpp
  MMLensData.cpp
  MMLensEvaluateNode.cpp
  pluginMain.cpp
)


# Find external packages
find_package(Maya REQUIRED)
find_package(CMinpack REQUIRED)
find_package(Gflags REQUIRED)
find_package(Glog REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Ceres REQUIRED)
find_package(Libmv REQUIRED)
find_package(OpenMVG REQUIRED)

message(STATUS "MAYA: ${MAYA_FOUND}")
message(STATUS "MAYA: Root=${MAYA_LOCATION}")
message(STATUS "MAYA: API=${MAYA_API_VERSION}")
message(STATUS "MAYA: Maya Executable=${MAYA_EXECUTABLE}")
message(STATUS "MAYA: Python Executable=${MAYA_PYTHON_EXECUTABLE}")
message(STATUS "MAYA: Includes=${MAYA_INCLUDE_DIRS}")
message(STATUS "MAYA: Libraries=${MAYA_LIBRARIES}")

message(STATUS "CMINPACK: ${CMINPACK_FOUND}")
message(STATUS "CMINPACK: Root=${CMINPACK_ROOT}")
message(STATUS "CMINPACK: Include=${CMINPACK_INCLUDE_DIRS}")
message(STATUS "CMINPACK: Library=${CMINPACK_LIBRARIES}")

message(STATUS "GFLAGS: ${GFLAGS_FOUND}")
message(STATUS "GFLAGS: Include=${GFLAGS_INCLUDE_DIRS}")
message(STATUS "GFLAGS: Library=${GFLAGS_LIBRARIES}")

message(STATUS "GLOG: ${GLOG_FOUND}")
message(STATUS "GLOG: Include=${GLOG_INCLUDE_DIRS}")
message(STATUS "GLOG: Library=${GLOG_LIBRARIES}")

message(STATUS "EIGEN3: ${EIGEN3_FOUND}")
message(STATUS "EIGEN3: Root=${Eigen3_DIR}")
message(STATUS "EIGEN3: Include=${EIGEN3_INCLUDE_DIRS}")

message(STATUS "CERES: ${CERES_FOUND}")
message(STATUS "CERES: Root=${CERES_ROOT}")
message(STATUS "CERES: Include=${CERES_INCLUDE_DIRS}")
message(STATUS "CERES: Library=${CERES_LIBRARIES}")

message(STATUS "LIBMV: ${LIBMV_FOUND}")
message(STATUS "LIBMV: Root=${LIBMV_ROOT}")
message(STATUS "LIBMV: Include=${LIBMV_INCLUDE_DIRS}")
message(STATUS "LIBMV: Library=${LIBMV_LIBRARIES}")

message(STATUS "OPENMVG: ${OPENMVG_FOUND}")
message(STATUS "OPENMVG: Root=${OPENMVG_ROOT}")
message(STATUS "OPENMVG: Include=${OPENMVG_INCLUDE_DIRS}")
message(STATUS "OPENMVG: Library=${OPENMVG_LIBRARIES}")

# Treat warnings as errors.
if(MSVC)
  add_compile_options(/W4 /WX)
else()
  add_compile_options(-W -Wall -Werror -Wpedantic)
endif()

include(MMSolverUtils)

set_global_maya_plugin_compile_options()

if (BUILD_MMSCENEGRAPH)
  add_subdirectory(mmscenegraph)
endif ()

# 'mmSolver' maya plugin library
if (APPLE)
  add_library(mmSolver MODULE ${SOURCE_FILES})
else ()
  add_library(mmSolver SHARED ${SOURCE_FILES})
endif ()
set_target_maya_plugin_compile_options(mmSolver)
target_include_directories(mmSolver
  PRIVATE ../include
  PRIVATE .
  PRIVATE ${MAYA_INCLUDE_DIRS}
  PRIVATE ${GFLAGS_INCLUDE_DIRS}
  PRIVATE ${GLOG_INCLUDE_DIRS}
  PRIVATE ${CMINPACK_INCLUDE_DIRS}
  PRIVATE ${EIGEN3_INCLUDE_DIRS}
  PRIVATE ${CERES_INCLUDE_DIRS}
  PRIVATE ${LIBMV_INCLUDE_DIRS}
  PRIVATE ${OPENMVG_INCLUDE_DIRS}
  )
target_link_libraries(mmSolver
  PRIVATE
  mmscenegraph
)
target_include_directories(mmSolver
  PRIVATE ${MMSCENEGRAPH_INCLUDE_DIR}
  )
target_link_libraries(mmSolver
  PUBLIC
  ${MAYA_OpenMaya_LIBRARY}
  ${MAYA_OpenMayaAnim_LIBRARY}
  ${MAYA_OpenMayaRender_LIBRARY}
  ${MAYA_OpenMayaUI_LIBRARY}
  ${MAYA_Foundation_LIBRARY}
  )
target_link_libraries(mmSolver
  PRIVATE
  ${GFLAGS_LIBRARIES}
  ${GLOG_LIBRARIES}
  ${CMINPACK_LIBRARIES}
  ${CERES_LIBRARIES}
  ${LIBMV_LIBRARIES}
  ${OPENMVG_LIBRARIES}
)
target_compile_definitions(mmSolver PRIVATE USE_SOLVER_CMINPACK)
target_compile_definitions(mmSolver PRIVATE USE_SOLVER_CERES)
target_compile_definitions(mmSolver PRIVATE USE_SOLVER_LIBMV)

# On Linux the 'm' library is required.
if(CMAKE_SYSTEM_NAME STREQUAL Linux)
  target_link_libraries(mmSolver PUBLIC m)
endif ()

install_target_plugin_to_module(mmSolver "${MODULE_FULL_NAME}")

# Install dynamic libraries; cminpack
if (CMINPACK_FOUND)
  install_library(
    ${CMINPACK_LIBRARY}
    ${CMINPACK_LIBRARY_DLL}
    "${MODULE_FULL_NAME}/lib/")
endif ()
