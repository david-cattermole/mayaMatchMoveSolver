# Copyright (C) 2019, 2021 David Cattermole.
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
# This CMake script is for building and organising the 'external'
# dependancies for Maya MatchMove Solver.

cmake_minimum_required(VERSION 3.12.0)

# Project configuration.
project(Project)

# Include the CMake "ExternalProject" tools, otherwise nothing will
# work.
include(ExternalProject)

# Options
set(THIRDPARTY_BASE_INSTALL_DIR "${CMAKE_CURRENT_SOURCE_DIR}/install"
  CACHE PATH "Base directory to install the thirdparty projects into.")
set(USE_GPL_LEVMAR 0
  CACHE BOOL "Compile with the GPL-licensed Lev-Mar library?")


#########################################################
# Google Flags (gflags)
#########################################################
set(GFLAGS_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/gflags)
set(GFLAGS_PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/working/gflags)
ExternalProject_Add(gflags
    PREFIX ${GFLAGS_PREFIX}
    GIT_REPOSITORY "https://github.com/gflags/gflags.git"
    GIT_TAG "v2.2.2"
    INSTALL_DIR ${GFLAGS_INSTALL_PATH}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${GFLAGS_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
)


#########################################################
# Google Log (glog)
#########################################################
set(GLOG_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/glog)
set(GLOG_PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/working/glog)
ExternalProject_Add(glog
    PREFIX ${GLOG_PREFIX}
    GIT_REPOSITORY "https://github.com/google/glog.git"
    GIT_TAG "v0.5.0"
    INSTALL_DIR ${GLOG_INSTALL_PATH}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${GLOG_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
)


#########################################################
# LevMar
#########################################################
#
# NOTE: LevMar is licensed under the GNU Public License (GPL). If this
# library used, the project is considered GPL licensed.
#
if(USE_GPL_LEVMAR)
  set(LEVMAR_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/levmar)
  set(LEVMAR_PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/working/levmar)
  set(LEVMAR_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/working/levmar/src/levmar)
  set(LEVMAR_PATCH_CMAKELIST_FILE ${CMAKE_CURRENT_SOURCE_DIR}/patches/levmar/CMakeLists.txt)
  ExternalProject_Add(levmar
      PREFIX ${LEVMAR_PREFIX}
      URL "http://users.ics.forth.gr/~lourakis/levmar/levmar-2.6.tgz"
      INSTALL_DIR ${LEVMAR_INSTALL_PATH}
      PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${LEVMAR_PATCH_CMAKELIST_FILE} ${LEVMAR_SOURCE_DIR}
      CMAKE_ARGS
          -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
          -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
          -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
          -DCMAKE_INSTALL_PREFIX=${LEVMAR_INSTALL_PATH}
          -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
          -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
          -DBUILD_SHARED_LIBS=1
          -DBUILD_DEMO=0
          -DHAVE_LAPACK=0
          -DNEED_F2C=0
          -DLM_SNGL_PREC=0
      )
endif()


#########################################################
# CMinpack
#########################################################
set(CMINPACK_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/cminpack)
set(CMINPACK_PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/working/cminpack)
set(CMINPACK_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/working/cminpack/src/cminpack)
set(CMINPACK_PATCH_CMAKELIST_FILE ${CMAKE_CURRENT_SOURCE_DIR}/patches/cminpack/CMakeLists.txt)
ExternalProject_Add(cminpack
    PREFIX ${CMINPACK_PREFIX}
    URL "https://github.com/devernay/cminpack/archive/v1.3.8.tar.gz"
    INSTALL_DIR ${CMINPACK_INSTALL_PATH}
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${CMINPACK_PATCH_CMAKELIST_FILE} ${CMINPACK_SOURCE_DIR}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${CMINPACK_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DBUILD_SHARED_LIBS=1
        -DBUILD_EXAMPLES=0
        -DUSE_FPIC=1
        -DUSE_BLAS=0
)


#########################################################
# SuiteSparse - Sparse Matrix Algorithms
#########################################################
#
# Note: SuiteSparse here contains pre-compiled files for LAPACK and
# BLAS, so we don't need to compile them ourselves.
#
set(SUITESPARSE_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/suitesparse)
set(SUITESPARSE_PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/working/suitesparse)
set(SUITESPARSE_LAPACK_DIR ${CMAKE_CURRENT_SOURCE_DIR}/working/suitesparse/src/suitesparse/lapack_windows/x64)
set(SUITESPARSE_LIBRARY_DIR ${SUITESPARSE_INSTALL_PATH}/lib)
set(SUITESPARSE_INCLUDE_DIR ${SUITESPARSE_INSTALL_PATH}/include)
ExternalProject_Add(suitesparse
    PREFIX ${SUITESPARSE_PREFIX}
    GIT_REPOSITORY "https://github.com/jlblancoc/suitesparse-metis-for-windows.git"
    GIT_TAG "v1.5.0"
    INSTALL_DIR ${SUITESPARSE_INSTALL_PATH}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${SUITESPARSE_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DLAPACK_DIR=${SUITESPARSE_LAPACK_DIR}
        -DBUILD_METIS=1
        -DSHARED=0
        -DSUITESPARSE_DL_LAST=0
        -DWITH_CUDA=0
        -DOPENMP=0
        -DPCRE=0
)


#########################################################
# Eigen - Vector, Matrix and Mathematics library
#########################################################
set(EIGEN_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/eigen)
set(EIGEN_PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/working/eigen)
set(EIGEN_INCLUDE_DIR ${EIGEN_INSTALL_PATH}/include)
ExternalProject_Add(eigen
    PREFIX ${EIGEN_PREFIX}
    GIT_REPOSITORY "https://gitlab.com/libeigen/eigen.git"
    GIT_TAG "3.3.9"
    INSTALL_DIR ${EIGEN_INSTALL_PATH}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${EIGEN_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
)


#########################################################
# Ceres Solver - Non-Linear Least-Squares Fits solver
#########################################################
set(CERES_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/ceres)
set(CERES_PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/working/ceres)
set(CERES_DOWNLOAD_DIR ${CMAKE_CURRENT_SOURCE_DIR}/working/ceres/src)
set(CERES_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/working/ceres/src/ceres)
ExternalProject_Add(ceres
    DEPENDS gflags glog eigen
    PREFIX ${CERES_PREFIX}
    GIT_REPOSITORY "https://github.com/ceres-solver/ceres-solver.git"
    GIT_TAG "1.14.0"
    INSTALL_DIR ${CERES_INSTALL_PATH}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${CERES_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DEigen3_DIR=${EIGEN_INSTALL_PATH}/share/eigen3/cmake
        -DGLOG_INCLUDE_DIR_HINTS=${GLOG_INSTALL_PATH}/include
        -DGLOG_LIBRARY_DIR_HINTS=${GLOG_INSTALL_PATH}/lib
        -Dgflags_DIR=${GFLAGS_INSTALL_PATH}/lib/cmake/gflags
        -DSUITESPARSE_INCLUDE_DIR_HINTS=${SUITESPARSE_INCLUDE_DIR}
        -DSUITESPARSE_LIBRARY_DIR_HINTS=${SUITESPARSE_LIBRARY_DIR}
        # -DCXSPARSE_INCLUDE_DIR_HINTS
        # -DCXSPARSE_LIBRARY_DIR_HINTS
        #
        # WARNING: Enabling "EIGENSPARSE" results in an LGPL licensed
        # Ceres.
        # -DEIGENSPARSE=1
)
set(CERES_LIBRARY ${CERES_INSTALL_PATH}/lib/ceres.lib)
set(CERES_INCLUDE_DIR ${CERES_INSTALL_PATH}/include)


#########################################################
# libmv - Multiple View library
#########################################################
set(LIBMV_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/libmv)
set(LIBMV_PREFIX ${CMAKE_CURRENT_SOURCE_DIR}/working/libmv)
set(LIBMV_DOWNLOAD_DIR ${CMAKE_CURRENT_SOURCE_DIR}/working/libmv/src)
set(LIBMV_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/working/libmv/src/libmv)
set(LIBMV_PATCH_CMAKELIST_FILE ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/CMakeLists.txt)
set(LIBMV_PATCH_INSTALLATION_CMAKE_FILE ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/Installation.cmake)
set(LIBMV_PATCH_RECONSTRUCTION_TOOLS_HEADER_FILE ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/reconstruction_tools.h)
ExternalProject_Add(libmv
    DEPENDS ceres
    PREFIX ${LIBMV_PREFIX}
    GIT_REPOSITORY "git://git.blender.org/libmv.git"
    GIT_TAG "f701b2b9fbc641b3252b3513239eeb14477ed5e1"
    DOWNLOAD_DIR ${LIBMV_DOWNLOAD_DIR}
    SOURCE_DIR ${LIBMV_SOURCE_DIR}
    INSTALL_DIR ${LIBMV_INSTALL_PATH}
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_CMAKELIST_FILE} ${LIBMV_SOURCE_DIR}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_INSTALLATION_CMAKE_FILE} ${LIBMV_SOURCE_DIR}/src/CMake
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_RECONSTRUCTION_TOOLS_HEADER_FILE} ${LIBMV_SOURCE_DIR}/src/libmv/reconstruction/tools.h
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${LIBMV_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DWITH_SYSTEM_CERES=1
        -DCERES_LIBRARY=${CERES_LIBRARY}
        -DCERES_INCLUDE_DIR=${CERES_INCLUDE_DIR}
        -DEIGEN_INCLUDE_DIR=${LIBMV_EIGEN_INCLUDE_DIR}
        -DWITH_FAST_DETECTOR=1
        -DBUILD_SHARED_LIBS=0
        -DBUILD_TESTS=0
        -DBUILD_GUI=0
        -DBUILD_TOOLS=1
        #
        # TODO: Install Doxygen and fill this out.
        # -DDOXYGEN_EXECUTABLE
)
