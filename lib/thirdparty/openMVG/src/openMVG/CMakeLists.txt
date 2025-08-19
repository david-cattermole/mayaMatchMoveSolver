# Copyright (C) 2022 David Cattermole.
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
# CMake build for (a reduced version of) OpenMVG.
#

set(OPENMVG_SOURCE_FILES

  features/feature.cpp

  geometry/Similarity3.cpp
  geometry/Similarity3_Kernel.cpp
  geometry/rigid_transformation3D_srt.cpp

  multiview/conditioning.cpp
  multiview/essential.cpp
  multiview/motion_from_essential.cpp
  multiview/projection.cpp
  multiview/solver_affine.cpp
  multiview/solver_essential_eight_point.cpp
  multiview/solver_essential_five_point.cpp
  multiview/solver_essential_kernel.cpp
  multiview/solver_essential_three_point.cpp
  multiview/solver_fundamental_kernel.cpp
  multiview/solver_homography_kernel.cpp
  multiview/solver_resection_kernel.cpp
  multiview/solver_resection_p3p_nordberg.cpp
  multiview/triangulation.cpp
  multiview/triangulation_nview.cpp

  numeric/nullspace.cpp
  numeric/numeric.cpp

  sfm/pipelines/sfm_robust_model_estimation.cpp
  sfm/sfm_data_BA_ceres.cpp
  sfm/sfm_data_transform.cpp
  sfm/sfm_data_triangulation.cpp
  sfm/sfm_data_utils.cpp
)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

add_library(openMVG ${OPENMVG_SOURCE_FILES})

target_link_libraries(openMVG PRIVATE
  glog::glog
)

target_link_libraries(openMVG PUBLIC
  Eigen3::Eigen
  ceres
)

set(include_dir "${CMAKE_CURRENT_SOURCE_DIR}/../")
target_include_directories(openMVG PUBLIC
  $<BUILD_INTERFACE:${include_dir}>
  $<INSTALL_INTERFACE:include/>)

# Add miniglog include directory for Ceres builds with miniglog.
if(TARGET ceres)
  get_target_property(CERES_INCLUDE_DIR ceres INTERFACE_INCLUDE_DIRECTORIES)
  if(NOT CERES_INCLUDE_DIR)
    # If Ceres doesn't have INTERFACE_INCLUDE_DIRECTORIES, find the
    # Ceres headers manually.
    find_path(CERES_INCLUDE_DIR ceres/ceres.h)
  endif()
  if(CERES_INCLUDE_DIR)
    target_include_directories(openMVG PRIVATE
      ${CERES_INCLUDE_DIR}/ceres/internal/miniglog)
  endif()
endif()

if (openMVG_USE_AVX2)
  target_compile_options(openMVG PUBLIC "-DOPENMVG_USE_AVX2")
  if (UNIX)
    target_compile_options(openMVG PUBLIC "-mavx2")
  endif ()
endif ()

if (openMVG_USE_AVX)
  target_compile_options(openMVG PUBLIC "-DOPENMVG_USE_AVX")
  if (UNIX)
    target_compile_options(openMVG PUBLIC "-mavx")
  endif ()
endif ()


if(MSVC)
  set_target_properties(openMVG PROPERTIES COMPILE_FLAGS "/bigobj")
  target_compile_options(openMVG PUBLIC "-D_USE_MATH_DEFINES")
endif()
