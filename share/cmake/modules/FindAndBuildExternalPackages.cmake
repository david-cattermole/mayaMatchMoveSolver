# Copyright (C) 2019, 2021, 2022 David Cattermole.
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
# This CMake script is for building the 'external' dependencies for
# Maya MatchMove Solver - Maya-specific dependencies only.
#
# NOTE: All third-party dependencies (cminpack, glog, Ceres, OpenMVG)
# are handled through the mmsolverlibs sub-project and its Config.cmake.


# Disable Package Registries.
#
# In some cases using the Package Registries is not desirable. CMake
# allows one to disable them. This helps stop packages from
# accidentally linking between unwanted builds.
#
# See this for more information:
# https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html#disabling-the-package-registry
set(CMAKE_FIND_PACKAGE_NO_PACKAGE_REGISTRY ON CACHE BOOL
  "Disable CMake User Package Registry when finding packages")
set(CMAKE_FIND_PACKAGE_NO_SYSTEM_PACKAGE_REGISTRY ON CACHE BOOL
  "Disable CMake System Package Registry when finding packages")
set(CMAKE_FIND_USE_PACKAGE_REGISTRY OFF CACHE BOOL
  "Disable CMake Package Registery entirely (used in CMake 3.16+)")

# Find/build packages - these are required before mmsolverlibs_cpp
# import.
#
# BOOTSTRAP REQUIREMENT: mmsolverlibs handles building all third-party
# dependencies internally. However, the main build must ensure these
# dependencies exist BEFORE importing mmsolverlibs_cpp, since the
# Config.cmake needs to find them transitively. This bootstrap step
# ensures targets exist for the mmsolverlibs Config.cmake to
# reference.
#
# Without this bootstrap, mmsolverlibs_cpp import would fail because
# its Config.cmake cannot find the required dependency targets.
find_package(Threads REQUIRED)
find_package(cminpack 1.3.8 REQUIRED)
find_package(glog 0.7.1 REQUIRED)
find_package(Ceres 1.14.0 REQUIRED)
