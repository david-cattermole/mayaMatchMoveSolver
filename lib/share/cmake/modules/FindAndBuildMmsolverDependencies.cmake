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
# This CMake script is for building the 'external' dependencies for
# mmsolverlibs - all third-party dependencies except Maya.


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

# Google Log (glog)
#
# glog is required by Ceres Solver to build and is reponsible for
# logging messages to the terminal. glog is is not used inside
# mmSolver at all.
#
# https://github.com/google/glog
find_package(glog 0.7.1 REQUIRED)

# CMinpack - Minimizer Package (for C)
#
# CMinpack a dense minimizing solver and is the primary minimization
# library used by mmSolver. This is required.
#
# https://github.com/devernay/cminpack
find_package(cminpack 1.3.8 REQUIRED)

# Eigen - Linear Algebra library
#
# https://gitlab.com/libeigen/eigen
#
# Eigen is used by both Ceres and OpenMVG and provides data types
# shared across the ABI boundary and is also used in mmSolver. Eigen
# also supplies a sparse-matrix that is used by Ceres.
#
# v3.4.0 is also the version used by OpenMVG.
find_package(Eigen3 3.4.0 REQUIRED)

# Ceres Solver - Non-Linear Least-Squares Fits solver
#
# Ceres Solver is used by OpenMVG for various least-squares
# minimization solving, with both dense and sparse matrices.
#
# Ceres is not directly used by mmSolver, but is used by OpenMVG,
# which is used by mmSolver. In the future the intention is to use
# Ceres Solver inside mmSolver more.
#
# https://github.com/ceres-solver/ceres-solver
find_package(Ceres 1.14.0 REQUIRED)
