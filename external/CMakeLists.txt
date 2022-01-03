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

# find_package() will use <PackageName>_ROOT variables.
#
# https://cmake.org/cmake/help/latest/policy/CMP0074.html
cmake_policy(SET CMP0074 NEW)

# The "project" command will overwrite the "VERSION" variables. We set
# the VERSION variables after the "project" command, so it should not
# affect us.
#
# https://cmake.org/cmake/help/latest/policy/CMP0048.html
cmake_policy(SET CMP0048 NEW)

# Options
set(THIRDPARTY_BASE_INSTALL_DIR "${CMAKE_CURRENT_SOURCE_DIR}/install"
  CACHE PATH "Base directory to install the thirdparty projects into.")
set(THIRDPARTY_BASE_WORKING_DIR "${CMAKE_CURRENT_SOURCE_DIR}/working"
  CACHE PATH "Base directory to download the thirdparty projects into.")


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
# CMinpack - Minimizer Package
#########################################################
set(CMINPACK_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/cminpack)
set(CMINPACK_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/cminpack)
set(CMINPACK_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/cminpack/src/cminpack)
set(CMINPACK_PATCH_SRC_1 ${CMAKE_CURRENT_SOURCE_DIR}/patches/cminpack/CMakeLists.txt)
set(CMINPACK_PATCH_DST_1 ${CMINPACK_SOURCE_DIR})
ExternalProject_Add(cminpack
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
        -DBUILD_SHARED_LIBS=1
        -DBUILD_EXAMPLES=0
        -DUSE_FPIC=1
        -DUSE_BLAS=0
        -DMKLROOT=${MKL_DIR}
)


#########################################################
# Eigen - Linear Alegbra library
#########################################################
#
# TODO: Only enable FFTW if our project actually uses it.
#
set(EIGEN_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/eigen)
set(EIGEN_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/eigen)
set(EIGEN_INCLUDE_DIR ${EIGEN_INSTALL_PATH}/include/eigen3)

ExternalProject_Add(eigen
    PREFIX ${EIGEN_PREFIX}
    GIT_REPOSITORY "https://gitlab.com/libeigen/eigen.git"
    GIT_TAG "3.2.7"  # was "3.3.9"
    INSTALL_DIR ${EIGEN_INSTALL_PATH}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${EIGEN_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DBLAS_VERBOSE=1
        -DCHOLMOD_INCLUDES=${SUITESPARSE_INCLUDE_DIR}/suitesparse/
        -DCHOLMOD_LIBRARIES=${SUITESPARSE_LIBRARY_DIR}/libcholmod.lib
        -DUMFPACK_INCLUDES=${SUITESPARSE_INCLUDE_DIR}/suitesparse/
        -DUMFPACK_LIBRARIES=${SUITESPARSE_LIBRARY_DIR}/libumfpack.lib
        -DSPQR_INCLUDES=${SUITESPARSE_INCLUDE_DIR}/suitesparse/
        -DSPQR_LIBRARIES=${SUITESPARSE_LIBRARY_DIR}/libspqr.lib
        -DEIGEN_USE_MKL_ALL=1
        # -DFFTW_DIR=${FFTW_INSTALL_PATH}
)




#########################################################
# libmv - Multiple View library
#########################################################
set(LIBMV_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/libmv)
set(LIBMV_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/libmv)
set(LIBMV_DOWNLOAD_DIR ${THIRDPARTY_BASE_WORKING_DIR}/libmv/src)
set(LIBMV_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/libmv/src/libmv)

# Main patches
set(LIBMV_PATCH_SRC_1 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/CMakeLists.txt)
set(LIBMV_PATCH_DST_1 ${LIBMV_SOURCE_DIR})
set(LIBMV_PATCH_SRC_2 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/Installation.cmake)
set(LIBMV_PATCH_DST_2 ${LIBMV_SOURCE_DIR}/src/CMake)
set(LIBMV_PATCH_SRC_3 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/reconstruction_tools.h)
set(LIBMV_PATCH_DST_3 ${LIBMV_SOURCE_DIR}/src/libmv/reconstruction/tools.h)

# Third party patches
set(LIBMV_PATCH_SRC_4 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/third_party_CMakeLists.txt)
set(LIBMV_PATCH_DST_4 ${LIBMV_SOURCE_DIR}/src/third_party/CMakeLists.txt)
set(LIBMV_PATCH_SRC_5 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/third_party_ssba_CMakeLists.txt)
set(LIBMV_PATCH_DST_5 ${LIBMV_SOURCE_DIR}/src/third_party/ssba/CMakeLists.txt)
set(LIBMV_PATCH_SRC_6 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_CMakeLists.txt)
set(LIBMV_PATCH_DST_6 ${LIBMV_SOURCE_DIR}/src/libmv/CMakeLists.txt)
set(LIBMV_PATCH_SRC_21 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/third_party_pthreads-w32_CMakeLists.txt)
set(LIBMV_PATCH_DST_21 ${LIBMV_SOURCE_DIR}/src/third_party/pthreads-w32/CMakeLists.txt)
set(LIBMV_PATCH_SRC_22 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/third_party_ceres_CMakeLists.txt)
set(LIBMV_PATCH_DST_22 ${LIBMV_SOURCE_DIR}/src/third_party/ceres/CMakeLists.txt)

# LibMV patches
set(LIBMV_PATCH_SRC_8 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_autotrack_CMakeLists.txt)
set(LIBMV_PATCH_DST_8 ${LIBMV_SOURCE_DIR}/src/libmv/autotrack/CMakeLists.txt)
set(LIBMV_PATCH_SRC_9 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_base_CMakeLists.txt)
set(LIBMV_PATCH_DST_9 ${LIBMV_SOURCE_DIR}/src/libmv/base/CMakeLists.txt)
set(LIBMV_PATCH_SRC_10 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_camera_CMakeLists.txt)
set(LIBMV_PATCH_DST_10 ${LIBMV_SOURCE_DIR}/src/libmv/camera/CMakeLists.txt)
set(LIBMV_PATCH_SRC_11 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_correspondence_CMakeLists.txt)
set(LIBMV_PATCH_DST_11 ${LIBMV_SOURCE_DIR}/src/libmv/correspondence/CMakeLists.txt)
set(LIBMV_PATCH_SRC_12 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_descriptor_CMakeLists.txt)
set(LIBMV_PATCH_DST_12 ${LIBMV_SOURCE_DIR}/src/libmv/descriptor/CMakeLists.txt)
set(LIBMV_PATCH_SRC_13 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_detector_CMakeLists.txt)
set(LIBMV_PATCH_DST_13 ${LIBMV_SOURCE_DIR}/src/libmv/detector/CMakeLists.txt)
set(LIBMV_PATCH_SRC_14 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_image_CMakeLists.txt)
set(LIBMV_PATCH_DST_14 ${LIBMV_SOURCE_DIR}/src/libmv/image/CMakeLists.txt)
set(LIBMV_PATCH_SRC_15 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_multiview_CMakeLists.txt)
set(LIBMV_PATCH_DST_15 ${LIBMV_SOURCE_DIR}/src/libmv/multiview/CMakeLists.txt)
set(LIBMV_PATCH_SRC_16 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_numeric_CMakeLists.txt)
set(LIBMV_PATCH_DST_16 ${LIBMV_SOURCE_DIR}/src/libmv/numeric/CMakeLists.txt)
set(LIBMV_PATCH_SRC_17 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_reconstruction_CMakeLists.txt)
set(LIBMV_PATCH_DST_17 ${LIBMV_SOURCE_DIR}/src/libmv/reconstruction/CMakeLists.txt)
set(LIBMV_PATCH_SRC_18 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_simple_pipeline_CMakeLists.txt)
set(LIBMV_PATCH_DST_18 ${LIBMV_SOURCE_DIR}/src/libmv/simple_pipeline/CMakeLists.txt)
set(LIBMV_PATCH_SRC_19 ${CMAKE_CURRENT_SOURCE_DIR}/patches/libmv/libmv_tracking_CMakeLists.txt)
set(LIBMV_PATCH_DST_19 ${LIBMV_SOURCE_DIR}/src/libmv/tracking/CMakeLists.txt)

ExternalProject_Add(libmv
    DEPENDS eigen
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
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_5} ${LIBMV_PATCH_DST_5}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_6} ${LIBMV_PATCH_DST_6}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_8} ${LIBMV_PATCH_DST_8}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_9} ${LIBMV_PATCH_DST_9}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_10} ${LIBMV_PATCH_DST_10}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_11} ${LIBMV_PATCH_DST_11}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_12} ${LIBMV_PATCH_DST_12}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_13} ${LIBMV_PATCH_DST_13}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_14} ${LIBMV_PATCH_DST_14}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_15} ${LIBMV_PATCH_DST_15}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_16} ${LIBMV_PATCH_DST_16}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_17} ${LIBMV_PATCH_DST_17}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_18} ${LIBMV_PATCH_DST_18}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_19} ${LIBMV_PATCH_DST_19}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_21} ${LIBMV_PATCH_DST_21}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LIBMV_PATCH_SRC_22} ${LIBMV_PATCH_DST_22}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${LIBMV_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DEIGEN_INCLUDE_DIR=${EIGEN_INCLUDE_DIR}
        #
        # WARNING: Enabling "EIGENSPARSE" results in an LGPL licensed
        # Ceres.
        -DEIGENSPARSE=1
        -DCXSPARSE=0  # Disabled because it's slower than SuiteSparse.
        -DLAPACK=0
        -DSUITESPARSE=0
        -DSCHUR_SPECIALIZATIONS=1  # Enable this for more optimizations.
        -DWITH_FAST_DETECTOR=1
        -DBUILD_SHARED_LIBS=0
        -DBUILD_TESTS=0
        -DBUILD_GUI=0
        -DBUILD_TOOLS=0
        #
        # TODO: Install Doxygen and fill this out.
        # -DDOXYGEN_EXECUTABLE
)
