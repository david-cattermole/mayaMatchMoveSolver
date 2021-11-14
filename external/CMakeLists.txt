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
set(THIRDPARTY_BASE_WORKING_DIR "${CMAKE_CURRENT_SOURCE_DIR}/working"
  CACHE PATH "Base directory to download the thirdparty projects into.")

set(USE_GPL_LEVMAR 0
  CACHE BOOL "Compile with the GPL-licensed Lev-Mar library?")


# #########################################################
# # ATLAS
# #########################################################
# set(ATLAS_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/atlas)
# set(ATLAS_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/atlas)
# ExternalProject_Add(atlas
#     PREFIX ${ATLAS_PREFIX}
#     GIT_REPOSITORY "https://sourceforge.net/projects/math-atlas/files/Stable/3.10.3/atlas3.10.3.tar.bz2/download"
#     GIT_TAG "v3.10.0"
#     INSTALL_DIR ${ATLAS_INSTALL_PATH}
#     CMAKE_ARGS
#         -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
#         -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
#         -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
#         -DCMAKE_INSTALL_PREFIX=${ATLAS_INSTALL_PATH}
#         -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
#         -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
# )


# #########################################################
# # LAPACK
# #########################################################
# set(LAPACK_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/lapack)
# set(LAPACK_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/lapack)
# ExternalProject_Add(lapack
#     PREFIX ${LAPACK_PREFIX}
#     GIT_REPOSITORY "https://github.com/Reference-LAPACK/lapack.git"
#     GIT_TAG "v3.10.0"
#     INSTALL_DIR ${LAPACK_INSTALL_PATH}
#     CMAKE_ARGS
#         -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
#         -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
#         -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
#         -DCMAKE_INSTALL_PREFIX=${LAPACK_INSTALL_PATH}
#         -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
#         -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
#         # -DBUILD_SHARED_LIBS=1
#         # -DBUILD_TESTS=0
#         # -DENABLE_OPENMP=0
#         # -DENABLE_THREADS=0  # use 'pthread'?
#         # -DWITH_COMBINED_THREADS=0
#         # -DENABLE_FLOAT=0
#         # -DENABLE_LONG_DOUBLE=0
#         # -DENABLE_QUAD_PRECISION=0
#         # -DENABLE_SSE=0
#         # -DENABLE_SSE2=0
#         # -DENABLE_AVX=0
#         # -DENABLE_AVX2=0
#         # -DDISABLE_FORTRAN=0
# )


# #########################################################
# # LevMar
# #########################################################
# #
# # NOTE: LevMar is licensed under the GNU Public License (GPL). If this
# # library used, the project is considered GPL licensed.
# #
# if(USE_GPL_LEVMAR)
#   set(LEVMAR_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/levmar)
#   set(LEVMAR_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/levmar)
#   set(LEVMAR_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/levmar/src/levmar)
#   set(LEVMAR_PATCH_CMAKELIST_FILE ${CMAKE_CURRENT_SOURCE_DIR}/patches/levmar/CMakeLists.txt)
#   ExternalProject_Add(levmar
#       PREFIX ${LEVMAR_PREFIX}
#       URL "http://users.ics.forth.gr/~lourakis/levmar/levmar-2.6.tgz"
#       INSTALL_DIR ${LEVMAR_INSTALL_PATH}
#       PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${LEVMAR_PATCH_CMAKELIST_FILE} ${LEVMAR_SOURCE_DIR}
#       CMAKE_ARGS
#           -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
#           -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
#           -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
#           -DCMAKE_INSTALL_PREFIX=${LEVMAR_INSTALL_PATH}
#           -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
#           -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
#           -DBUILD_SHARED_LIBS=1
#           -DBUILD_DEMO=0
#           -DHAVE_LAPACK=0
#           -DNEED_F2C=0
#           -DLM_SNGL_PREC=0
#       )
# endif()


# #########################################################
# # FFTW (Fastest Fourier Transform in the West)
# #########################################################
# #
# # TODO: Eigen can use FFTW, but right now I'm not sure if Ceres or
# # libmv are using FFT features of Eigen, therefore it could be a waste
# # of time and space to compile this.
# #
# set(FFTW_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/fftw)
# set(FFTW_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/fftw)
# ExternalProject_Add(fftw
#     PREFIX ${FFTW_PREFIX}
#     URL "https://fftw.org/fftw-3.3.10.tar.gz"
#     INSTALL_DIR ${FFTW_INSTALL_PATH}
#     CMAKE_ARGS
#         -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
#         -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
#         -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
#         -DCMAKE_INSTALL_PREFIX=${FFTW_INSTALL_PATH}
#         -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
#         -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
#         -DBUILD_SHARED_LIBS=0
#         -DBUILD_TESTS=0
#         -DENABLE_OPENMP=0
#         -DENABLE_THREADS=0  # use 'pthread'?
#         -DWITH_COMBINED_THREADS=0
#         -DENABLE_FLOAT=0
#         -DENABLE_LONG_DOUBLE=0
#         -DENABLE_QUAD_PRECISION=0
#         -DENABLE_SSE=0
#         -DENABLE_SSE2=0
#         -DENABLE_AVX=0
#         -DENABLE_AVX2=0
#         -DDISABLE_FORTRAN=0
# )




#########################################################
# Google Test (gtest)
#########################################################
set(GTEST_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/gtest)
set(GTEST_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/gtest)
ExternalProject_Add(gtest
    PREFIX ${GTEST_PREFIX}
    GIT_REPOSITORY "https://github.com/google/googletest.git"
    GIT_TAG "release-1.11.0"
    INSTALL_DIR ${GTEST_INSTALL_PATH}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${GTEST_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
)


#########################################################
# Google Flags (gflags)
#########################################################
set(GFLAGS_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/gflags)
set(GFLAGS_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/gflags)
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
set(GLOG_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/glog)
ExternalProject_Add(glog
    DEPENDS gtest gflags
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
        -DBUILD_SHARED_LIBS=0
        -DWITH_GTEST=1
        -DWITH_GFLAGS=1
        -DGTest_DIR=${GTEST_INSTALL_PATH}
        -Dgflags=${GFLAGS_INSTALL_PATH}
)

#########################################################
# SuiteSparse - Sparse Matrix Algorithms
#########################################################
#
# Note: SuiteSparse here contains pre-compiled files for LAPACK and
# BLAS, so we don't need to compile them ourselves.
#
set(SUITESPARSE_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/suitesparse)
set(SUITESPARSE_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/suitesparse)
set(SUITESPARSE_LAPACK_DIR ${THIRDPARTY_BASE_WORKING_DIR}/suitesparse/src/suitesparse/lapack_windows/x64)
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
# CMinpack - Minimizer Package
#########################################################
set(CMINPACK_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/cminpack)
set(CMINPACK_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/cminpack)
set(CMINPACK_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/cminpack/src/cminpack)
set(CMINPACK_PATCH_SRC_1 ${CMAKE_CURRENT_SOURCE_DIR}/patches/cminpack/CMakeLists.txt)
set(CMINPACK_PATCH_DST_1 ${CMINPACK_SOURCE_DIR})
ExternalProject_Add(cminpack
    DEPENDS suitesparse
    PREFIX ${CMINPACK_PREFIX}
    URL "https://github.com/devernay/cminpack/archive/v1.3.8.tar.gz"
    INSTALL_DIR ${CMINPACK_INSTALL_PATH}
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${CMINPACK_PATCH_SRC_1} ${CMINPACK_PATCH_DST_1}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${CMINPACK_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DBUILD_SHARED_LIBS=1  # TODO: See if we can make this 'static'.
        -DBUILD_EXAMPLES=0
        -DUSE_FPIC=1
        -DUSE_BLAS=1
)


#########################################################
# Eigen - Linear Alegbra library
#########################################################
#
# TODO: Only enable FFTW if our project actually uses it.
#
set(EIGEN_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/eigen)
set(EIGEN_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/eigen)
set(EIGEN_INCLUDE_DIR ${EIGEN_INSTALL_PATH}/include)
ExternalProject_Add(eigen
    DEPENDS
        suitesparse
        # fftw
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
        -DBLAS_VERBOSE=ON
        -DBLAS_LIBDIR=${SUITESPARSE_LAPACK_DIR}
        -DCHOLMOD_DIR=${SUITESPARSE_LAPACK_DIR}
        # -DFFTW_DIR=${FFTW_INSTALL_PATH}
)


#########################################################
# Ceres Solver - Non-Linear Least-Squares Fits solver
#########################################################
set(CERES_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/ceres)
set(CERES_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/ceres)
set(CERES_DOWNLOAD_DIR ${THIRDPARTY_BASE_WORKING_DIR}/ceres/src)
set(CERES_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/ceres/src/ceres)
ExternalProject_Add(ceres
    DEPENDS gflags glog eigen suitesparse
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
        -DCXSPARSE_INCLUDE_DIR_HINTS=${SUITESPARSE_INCLUDE_DIR}
        -DCXSPARSE_LIBRARY_DIR_HINTS=${SUITESPARSE_LIBRARY_DIR}
        -DBUILD_TESTING=0
        -DBUILD_DOCUMENTATION=0
        -DBUILD_EXAMPLES=0
        -DBUILD_BENCHMARKS=0
        -DBUILD_SHARED_LIBS=0
        #
        # WARNING: Enabling "EIGENSPARSE" results in an LGPL licensed
        # Ceres.
        -DEIGENSPARSE=0
        -DLAPACK=1
        -DCXSPARSE=1
        -DSUITESPARSE=1
        -DGFLAGS=1
        -DCUSTOM_BLAS=1
        -DSCHUR_SPECIALIZATIONS=1
        -DCXX11=1
        -DOPENMP=1
        -DTBB=0
        -DCXX11_THREADS=0
)
set(CERES_LIBRARY ${CERES_INSTALL_PATH}/lib/ceres.lib)
set(CERES_INCLUDE_DIR ${CERES_INSTALL_PATH}/include)


#########################################################
# libmv - Multiple View library
#########################################################
set(LIBMV_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/libmv)
set(LIBMV_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/libmv)
set(LIBMV_DOWNLOAD_DIR ${THIRDPARTY_BASE_WORKING_DIR}/libmv/src)
set(LIBMV_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/libmv/src/libmv)
set(LIBMV_PATCH_SRC_1 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/CMakeLists.txt)
set(LIBMV_PATCH_DST_1 ${LIBMV_SOURCE_DIR})
set(LIBMV_PATCH_SRC_2 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/Installation.cmake)
set(LIBMV_PATCH_DST_2 ${LIBMV_SOURCE_DIR}/src/CMake)
set(LIBMV_PATCH_SRC_3 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/reconstruction_tools.h)
set(LIBMV_PATCH_DST_3 ${LIBMV_SOURCE_DIR}/src/libmv/reconstruction/tools.h)
set(LIBMV_PATCH_SRC_4 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/third_party_CMakeLists.txt)
set(LIBMV_PATCH_DST_4 ${LIBMV_SOURCE_DIR}/src/third_party/CMakeLists.txt)
ExternalProject_Add(libmv
    DEPENDS gtest glog gflags suitesparse ceres
    PREFIX ${LIBMV_PREFIX}
    GIT_REPOSITORY "git://git.blender.org/libmv.git"
    GIT_TAG "f701b2b9fbc641b3252b3513239eeb14477ed5e1"
    DOWNLOAD_DIR ${LIBMV_DOWNLOAD_DIR}
    SOURCE_DIR ${LIBMV_SOURCE_DIR}
    INSTALL_DIR ${LIBMV_INSTALL_PATH}
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_1} ${LIBMV_PATCH_DST_1}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_2} ${LIBMV_PATCH_DST_2}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_3} ${LIBMV_PATCH_DST_3}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_4} ${LIBMV_PATCH_DST_4}
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
        -DBUILD_TOOLS=0
        #
        # TODO: Install Doxygen and fill this out.
        # -DDOXYGEN_EXECUTABLE
)
