# Copyright (C) 2025 David Cattermole.
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
# CMakeLists.txt for vendored Eigen.
#
# Eigen is a header-only C++ template library for linear algebra:
# matrices, vectors, numerical solvers, and related algorithms.
#
# This vendored copy ensures consistent version across all build environments
# and eliminates external dependency management.
#

# Eigen is a header-only library, so we create an INTERFACE target
# Create 'eigen' target (Eigen3 target may already exist from parent CMake)
add_library(eigen INTERFACE)

# Only create Eigen3 target if it doesn't already exist
if(NOT TARGET Eigen3)
  add_library(Eigen3 INTERFACE)
endif()

# Only create Eigen3::Eigen alias if it doesn't already exist
if(NOT TARGET Eigen3::Eigen)
  add_library(Eigen3::Eigen ALIAS eigen)
endif()

# Set the include directory for the Eigen headers
set(eigen_include_dir "${CMAKE_CURRENT_SOURCE_DIR}")

# Set interface include directories for eigen target
target_include_directories(eigen INTERFACE
  $<BUILD_INTERFACE:${eigen_include_dir}>
  $<INSTALL_INTERFACE:include/>
)

# Set interface include directories for Eigen3 target if we created it here
# (If it was created earlier, it should already have the correct paths)
get_target_property(eigen3_include_dirs Eigen3 INTERFACE_INCLUDE_DIRECTORIES)
if(NOT eigen3_include_dirs OR eigen3_include_dirs STREQUAL "eigen3_include_dirs-NOTFOUND")
  target_include_directories(Eigen3 INTERFACE
    $<BUILD_INTERFACE:${eigen_include_dir}>
    $<INSTALL_INTERFACE:include/>
  )
endif()

# Set C++ standard requirement (Eigen 3.4.0 requires C++14 minimum)
target_compile_features(eigen INTERFACE cxx_std_14)

# Set C++ standard for Eigen3 if we created it here
get_target_property(eigen3_cxx_features Eigen3 INTERFACE_COMPILE_FEATURES)
if(NOT eigen3_cxx_features OR eigen3_cxx_features STREQUAL "eigen3_cxx_features-NOTFOUND")
  target_compile_features(Eigen3 INTERFACE cxx_std_14)
endif()

# Set export name.
set_target_properties(eigen PROPERTIES
  EXPORT_NAME "Eigen3::Eigen"
)

# Set properties for Eigen3 if we created it here
if(TARGET Eigen3)
  get_target_property(eigen3_export_name Eigen3 EXPORT_NAME)
  if(NOT eigen3_export_name OR eigen3_export_name STREQUAL "eigen3_export_name-NOTFOUND")
    set_target_properties(Eigen3 PROPERTIES
      EXPORT_NAME "Eigen3"
    )
  endif()
endif()
