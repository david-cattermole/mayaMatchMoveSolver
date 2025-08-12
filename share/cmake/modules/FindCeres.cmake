# Copyright (C) 2022, 2025 David Cattermole.
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
# - ceres finder module
# This module sets up the vendored Ceres Solver library.
#
# Defines Variables:
# - Ceres_FOUND
# - Ceres_LIBRARIES
# - Ceres_INCLUDE_DIRS
# - Ceres_VERSION
#

# Always use vendored Ceres.
message(STATUS "Ceres: Using vendored Ceres Solver library")
set(Ceres_FOUND TRUE)
set(Ceres_VERSION "1.14.0")

# Set up paths for the vendored library.
set(Ceres_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/lib/thirdparty/ceres/include")
set(Ceres_LIBRARY "ceres::ceres")
set(Ceres_LIBRARIES "ceres::ceres")

# Set legacy variables for compatibility.
set(CERES_FOUND TRUE)
set(CERES_INCLUDE_DIRS ${Ceres_INCLUDE_DIR})
set(CERES_LIBRARIES ${Ceres_LIBRARY})
set(CERES_VERSION ${Ceres_VERSION})

# Display configuration.
if(Ceres_FOUND)
  message(STATUS "Ceres: Found=${Ceres_FOUND} (vendored)")
  message(STATUS "Ceres: Version=${Ceres_VERSION}")
  message(STATUS "Ceres: Include=${Ceres_INCLUDE_DIR}")
  message(STATUS "Ceres: Library=${Ceres_LIBRARY}")
endif()

# Mark variables as advanced for GUI CMake tools.
mark_as_advanced(
  Ceres_INCLUDE_DIR
  Ceres_LIBRARY
  Ceres_VERSION
)
