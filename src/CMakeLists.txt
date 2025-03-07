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

# This allows us to use the 'RPATH' embedded in a shared object to
# find binaries releative to the current binary.
set(CMAKE_MACOSX_RPATH 1)

# Source
set(SOURCE_FILES
  mmSolver/adjust/adjust_base.cpp
  mmSolver/adjust/adjust_ceres_base.cpp
  mmSolver/adjust/adjust_ceres_lmder.cpp
  mmSolver/adjust/adjust_ceres_lmdif.cpp
  mmSolver/adjust/adjust_cminpack_base.cpp
  mmSolver/adjust/adjust_cminpack_lmder.cpp
  mmSolver/adjust/adjust_cminpack_lmdif.cpp
  mmSolver/adjust/adjust_measureErrors.cpp
  mmSolver/adjust/adjust_relationships.cpp
  mmSolver/adjust/adjust_results_helpers.cpp
  mmSolver/adjust/adjust_results_setMarkerData.cpp
  mmSolver/adjust/adjust_results_setSolveData.cpp
  mmSolver/adjust/adjust_setParameters.cpp
  mmSolver/adjust/adjust_solveFunc.cpp
  mmSolver/calibrate/calibrate_common.cpp
  mmSolver/calibrate/vanishing_point.cpp
  mmSolver/cmd/MMAnimCurveFilterPopsCmd.cpp
  # mmSolver/cmd/MMAnimCurveSimplifyCmd.cpp
  mmSolver/cmd/MMBestFitPlaneCmd.cpp
  mmSolver/cmd/MMCameraPoseFromPointsCmd.cpp
  mmSolver/cmd/MMCameraRelativePoseCmd.cpp
  mmSolver/cmd/MMCameraSolveCmd.cpp
  mmSolver/cmd/MMColorIOCmd.cpp
  mmSolver/cmd/MMConvertImageCmd.cpp
  mmSolver/cmd/MMImageCacheCmd.cpp
  mmSolver/cmd/MMMarkerHomographyCmd.cpp
  mmSolver/cmd/MMMemoryGPUCmd.cpp
  mmSolver/cmd/MMMemorySystemCmd.cpp
  mmSolver/cmd/MMReadImageCmd.cpp
  mmSolver/cmd/MMReprojectionCmd.cpp
  mmSolver/cmd/MMSolver2Cmd.cpp
  mmSolver/cmd/MMSolverAffectsCmd.cpp
  mmSolver/cmd/MMSolverCmd.cpp
  mmSolver/cmd/MMSolverSceneGraphCmd.cpp
  mmSolver/cmd/MMSolverTypeCmd.cpp
  mmSolver/cmd/MMTestCameraMatrixCmd.cpp
  mmSolver/cmd/arg_flags_attr_details.cpp
  mmSolver/cmd/arg_flags_attr_details.h
  mmSolver/cmd/arg_flags_solve_frames.cpp
  mmSolver/cmd/arg_flags_solve_frames.h
  mmSolver/cmd/arg_flags_solve_info.cpp
  mmSolver/cmd/arg_flags_solve_info.h
  mmSolver/cmd/arg_flags_solve_log.cpp
  mmSolver/cmd/arg_flags_solve_log.h
  mmSolver/cmd/arg_flags_solve_object.cpp
  mmSolver/cmd/arg_flags_solve_object.h
  mmSolver/cmd/arg_flags_solve_scene_graph.cpp
  mmSolver/cmd/arg_flags_solve_scene_graph.h
  mmSolver/core/array_mask.cpp
  mmSolver/core/reprojection.cpp
  mmSolver/image/ImageCache.cpp
  mmSolver/image/ImagePixelData.cpp
  mmSolver/image/PixelDataType.cpp
  mmSolver/image/TextureData.cpp
  mmSolver/image/image_convert.cpp
  mmSolver/image/image_io.cpp
  mmSolver/mayahelper/maya_attr.cpp
  mmSolver/mayahelper/maya_bundle.cpp
  mmSolver/mayahelper/maya_camera.cpp
  mmSolver/mayahelper/maya_lens_model_utils.cpp
  mmSolver/mayahelper/maya_marker.cpp
  mmSolver/mayahelper/maya_marker_group.cpp
  mmSolver/mayahelper/maya_scene_graph.cpp
  mmSolver/mayahelper/maya_utils.cpp
  mmSolver/node/MMCameraCalibrateNode.cpp
  mmSolver/node/MMImagePlaneTransformNode.cpp
  mmSolver/node/MMImageSequenceFrameLogicNode.cpp
  mmSolver/node/MMLensData.cpp
  mmSolver/node/MMLensDeformerNode.cpp
  mmSolver/node/MMLensEvaluateNode.cpp
  mmSolver/node/MMLensModel3deNode.cpp
  mmSolver/node/MMLensModelToggleNode.cpp
  mmSolver/node/MMLineBestFitNode.cpp
  mmSolver/node/MMLineIntersectNode.cpp
  mmSolver/node/MMLinePointIntersectNode.cpp
  mmSolver/node/MMMarkerGroupTransformNode.cpp
  mmSolver/node/MMMarkerScaleNode.cpp
  mmSolver/node/MMMarkerTransformMatrix.cpp
  mmSolver/node/MMMarkerTransformNode.cpp
  mmSolver/node/MMReprojectionNode.cpp
  mmSolver/node/node_line_utils.cpp
  mmSolver/pluginMain.cpp
  mmSolver/sfm/camera_from_known_points.cpp
  mmSolver/sfm/camera_relative_pose.cpp
  mmSolver/sfm/homography.cpp
  mmSolver/sfm/sfm_utils.cpp
  mmSolver/shape/BundleDrawOverride.cpp
  mmSolver/shape/BundleShapeNode.cpp
  mmSolver/shape/ImagePlaneGeometry2Override.cpp
  mmSolver/shape/ImagePlaneGeometryOverride.cpp
  mmSolver/shape/ImagePlaneShape2Node.cpp
  mmSolver/shape/ImagePlaneShapeNode.cpp
  mmSolver/shape/ImagePlaneUtils.cpp
  mmSolver/shape/LineDrawOverride.cpp
  mmSolver/shape/LineShapeNode.cpp
  mmSolver/shape/MarkerDrawOverride.cpp
  mmSolver/shape/MarkerShapeNode.cpp
  mmSolver/shape/ShapeDrawUtils.cpp
  mmSolver/shape/SkyDomeDrawOverride.cpp
  mmSolver/shape/SkyDomeShapeNode.cpp
  mmSolver/utilities/assert_utils.cpp
  mmSolver/utilities/debug_utils.cpp
  mmSolver/utilities/memory_gpu_utils.cpp
  mmSolver/utilities/memory_system_utils.cpp
  mmSolver/utilities/memory_utils.cpp
  mmSolver/utilities/number_utils.cpp
  mmSolver/utilities/path_utils.cpp
  mmSolver/utilities/string_utils.cpp
)

if (MMSOLVER_BUILD_RENDERER)
  set(SOURCE_FILES
    ${SOURCE_FILES}
    mmSolver/render/MMRendererStandardCmd.cpp
    mmSolver/render/MMRendererSilhouetteCmd.cpp
    mmSolver/render/RenderOverrideStandard.cpp
    mmSolver/render/RenderGlobalsStandardNode.cpp
    mmSolver/render/RenderGlobalsSilhouetteNode.cpp
    mmSolver/render/RenderOverrideSilhouette.cpp
    mmSolver/render/ops/ClearOperation.cpp
    mmSolver/render/ops/HudRender.cpp
    mmSolver/render/ops/PresentTarget.cpp
    mmSolver/render/ops/SceneRender.cpp
    mmSolver/render/ops/SceneRenderBase.cpp
    mmSolver/render/ops/SilhouetteRender.cpp
    mmSolver/render/ops/scene_utils.cpp
    mmSolver/render/shader/shader_utils.cpp
  )

  # Allow C++ source code to query the defined 'WITH_MM_RENDERER'
  # value to test if the MM Renderer will be compiled.
  add_compile_definitions(MMSOLVER_BUILD_RENDERER=1)
endif ()

include(MMSolverUtils)

# 'mmSolver' maya plugin library
add_library_maya_plugin(mmSolver "${SOURCE_FILES}")
set_target_maya_plugin_compile_options(mmSolver)
target_include_directories(mmSolver
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../include
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../external/openMVG/src/

  # For generated 'buildConstant.h' file.
  PRIVATE ${CMAKE_BINARY_DIR}/include
)

# On Linux the 'm' library is required.
if(CMAKE_SYSTEM_NAME STREQUAL Linux)
  target_link_libraries(mmSolver PRIVATE m)
endif ()

# Set global flags and options that need to apply to the Maya
# plug-in. See 'MMSolverUtils' CMake module for more information.
include(MMCommonUtils)
mm_common_set_global_treat_warnings_as_errors()
option(MMSOLVER_DEBUG "Enable mmSolver debug mode; prints details and enables debug assertions." OFF)
mm_common_set_global_compile_options(MMSOLVER_DEBUG)

# MM Solver standalone libraries.
find_package(mmsolverlibs_cpp REQUIRED)
find_package(mmsolverlibs_rust REQUIRED)

target_link_libraries(mmSolver
  # The order of these libraries ('mmsolverlibs_cpp' and
  # 'mmsolverlibs_rust') matters when linking GCC on Linux.
  #
  # 'mmsolverlibs_cpp' and 'mmsolverlibs_rust' both use functions from
  # each other and so there is a cyclic dependency. On Windows the
  # order doesn't matter because the linker is "dumb", however the GCC
  # linker is "smart" and automatically discards symbols that are not
  # used from preceeding libraries. This causes the issue, and so we
  # must control the linking order:
  #
  # See more information:
  # https://stackoverflow.com/questions/45135/why-does-the-order-in-which-libraries-are-linked-sometimes-cause-errors-in-gcc
  PUBLIC mmsolverlibs_rust::mmsolverlibs_rust
  PUBLIC mmsolverlibs_cpp::mmsolverlibs_cpp
)

find_package(Maya REQUIRED)
message(STATUS "Maya: Found=${MAYA_FOUND}")
message(STATUS "Maya: Root=${MAYA_LOCATION}")
message(STATUS "Maya: API=${MAYA_API_VERSION}")
message(STATUS "Maya: Maya Executable=${MAYA_EXECUTABLE}")
message(STATUS "Maya: Python Executable=${MAYA_PYTHON_EXECUTABLE}")
message(STATUS "Maya: Includes=${MAYA_INCLUDE_DIRS}")
message(STATUS "Maya: Libraries=${MAYA_LIBRARIES}")
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

# MM Color IO dependencies
include(MMColorIOUtils)
mmcolorio_find_packages()
mmcolorio_target_link_packages(mmSolver)

# Link all libraries.
target_link_libraries(mmSolver
  PRIVATE cminpack::cminpack
  PRIVATE glog::glog
  PRIVATE Eigen3::Eigen
  PRIVATE ceres
  PRIVATE openMVG
)

target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_CMINPACK)
target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_OPENMVG)
target_compile_definitions(mmSolver PRIVATE MMSOLVER_USE_CERES)

install_target_plugin_to_module(mmSolver "${MODULE_FULL_NAME}")


# TODO: Extract this logic into a reusable function/macro in a CMake
# module.
if (WIN32)
  get_target_property(OpenColorIO_IMPLIB_RELEASE
    OpenColorIO::OpenColorIO
    IMPORTED_IMPLIB_RELEASE)
  message(STATUS
    "OpenColorIO_IMPLIB_RELEASE: ${OpenColorIO_IMPLIB_RELEASE}")

  get_target_property(OpenColorIO_LOCATION_RELEASE
    OpenColorIO::OpenColorIO
    IMPORTED_LOCATION_RELEASE)
  message(STATUS
    "OpenColorIO_LOCATION_RELEASE: ${OpenColorIO_LOCATION_RELEASE}")

  install_shared_library(
    ${OpenColorIO_IMPLIB_RELEASE}
    ${OpenColorIO_LOCATION_RELEASE}
    "${MODULE_FULL_NAME}/lib")
elseif (UNIX)

  get_target_property(OpenColorIO_LOCATION_RELEASE
    OpenColorIO::OpenColorIO
    IMPORTED_LOCATION_RELEASE)
  message(STATUS
    "OpenColorIO_LOCATION_RELEASE: ${OpenColorIO_LOCATION_RELEASE}")

    get_target_property(OpenColorIO_SONAME_RELEASE
      OpenColorIO::OpenColorIO
      IMPORTED_SONAME_RELEASE)
    message(STATUS
      "OpenColorIO_SONAME_RELEASE: ${OpenColorIO_SONAME_RELEASE}")

  install_shared_library_with_name(
    ${OpenColorIO_LOCATION_RELEASE}
    ${OpenColorIO_LOCATION_RELEASE}
    ${OpenColorIO_SONAME_RELEASE}
    "${MODULE_FULL_NAME}/lib")
endif ()
