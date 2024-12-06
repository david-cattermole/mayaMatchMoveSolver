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
# This CMake script is for building the 'external' dependancies for
# Maya MatchMove Solver Core ("mmcore").


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

# LDPK (Lens Distortion Plug-in Kit)
#
# Provides "industry standard" lens distortion models that mmSolver
# uses internally.
#
# LDPK is not used by any other libraries (eg. OpenMVG or Ceres).
#
# https://www.3dequalizer.com
find_package(ldpk 2.12.0 REQUIRED)
