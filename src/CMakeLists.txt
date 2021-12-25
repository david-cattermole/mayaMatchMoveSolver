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
  core/mmcamera.cpp
  core/mmcoord.cpp
  core/mmdata.cpp
  core/mmmath.cpp
  core/reprojection.cpp
  Camera.cpp
  Marker.cpp
  Bundle.cpp
  Attr.cpp
  mayaUtils.cpp
  commonArgFlags.cpp
  MMSolverAffectsCmd.cpp
  MMMarkerScaleNode.cpp
  MMReprojectionNode.cpp
  MMMarkerGroupTransformNode.cpp
  MMCameraCalibrateNode.cpp
  MMLineIntersectNode.cpp
  MMTestCameraMatrixCmd.cpp
  MMSolverCmd.cpp
  MMSolverTypeCmd.cpp
  MMReprojectionCmd.cpp
  MMCameraSolveCmd.cpp
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

message(STATUS "CMINPACK: ${CMINPACK_FOUND}"
  " Root=${CMINPACK_ROOT}"
  " Include=${CMINPACK_INCLUDE_DIRS}"
  " Library=${CMINPACK_LIBRARIES}")

message(STATUS "GFLAGS: ${GFLAGS_FOUND}"
  " Include=${GFLAGS_INCLUDE_DIRS}"
  " Library=${GFLAGS_LIBRARIES}")

message(STATUS "GLOG: ${GLOG_FOUND}"
  " Include=${GLOG_INCLUDE_DIRS}"
  " Library=${GLOG_LIBRARIES}")



message(STATUS "EIGEN3: ${EIGEN3_FOUND}"
  " Root=${Eigen3_DIR}"
  " Include=${EIGEN3_INCLUDE_DIRS}")


message(STATUS "CERES: ${CERES_FOUND}"
  " Root=${CERES_ROOT}"
  " Include=${CERES_INCLUDE_DIRS}"
  " Library=${CERES_LIBRARIES}")

message(STATUS "LIBMV: ${LIBMV_FOUND}"
  " Root=${LIBMV_ROOT}"
  " Include=${LIBMV_INCLUDE_DIRS}"
  " Library=${LIBMV_LIBRARIES}")

# Treat warnings as errors.
if(MSVC)
  add_compile_options(/W4 /WX)
else()
  add_compile_options(-W -Wall -Werror -Wpedantic)
endif()

include(MMSolverUtils)

set_global_maya_plugin_compile_options()

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
  )
target_link_libraries(mmSolver
  PUBLIC
  ${MAYA_OpenMaya_LIBRARY}
  ${MAYA_OpenMayaAnim_LIBRARY}
  ${MAYA_Foundation_LIBRARY}
  )
target_link_libraries(mmSolver
  PRIVATE
  ${GFLAGS_LIBRARIES}
  ${GLOG_LIBRARIES}
  ${CMINPACK_LIBRARIES}
  ${CERES_LIBRARIES}
  ${LIBMV_LIBRARIES}
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
