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

# Do not allow using GNU extensions (such as '-std=g++11'), because
# it's not compatible with Maya.
set(CXX_EXTENSIONS OFF)

# Use the older C++11 ABI for std::string and std::list, to be
# compatible with RHEL/CentOS 7, Maya and the VFX Platform.
#
# https://vfxplatform.com/#footnote-gcc6
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_GLIBCXX_USE_CXX11_ABI=0")
endif()

#########################################################
# Google Log (glog)
#########################################################
set(GLOG_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/glog)
set(GLOG_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/glog)
# set(GLOG_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/glog/src/glog)
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
        -DBUILD_SHARED_LIBS=0
        -DBUILD_TESTING=0
        -DWITH_GTEST=0
        -DWITH_GFLAGS=0
        -DWITH_PKGCONFIG=0
        -DWITH_THREADS=0
        -DWITH_SYMBOLIZE=0
        -DWITH_TLS=0
        -DWITH_UNWIND=0
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
    PREFIX ${CMINPACK_PREFIX}
    URL "https://github.com/devernay/cminpack/archive/v1.3.8.tar.gz"
    URL_HASH MD5=8fa8ae3c7a3e6259f26c51c62045af99
    INSTALL_DIR ${CMINPACK_INSTALL_PATH}
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${CMINPACK_PATCH_SRC_1} ${CMINPACK_PATCH_DST_1}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${CMINPACK_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DCMAKE_POSITION_INDEPENDENT_CODE=${CMAKE_POSITION_INDEPENDENT_CODE}
        -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
        -DCMAKE_CXX_EXTENSIONS=${CXX_EXTENSIONS}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DBUILD_SHARED_LIBS=1
        -DBUILD_EXAMPLES=0
        -DUSE_FPIC=1
        -DUSE_BLAS=0
)


#########################################################
# CXSparse - Sparse Matrix algorithms
#########################################################
set(CXSPARSE_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/cxsparse)
set(CXSPARSE_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/cxsparse)
set(CXSPARSE_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/cxsparse/src/cxsparse)
set(CXSPARSE_PATCH_SRC_1 ${CMAKE_CURRENT_SOURCE_DIR}/patches/cxsparse/CMakeLists.txt)
set(CXSPARSE_PATCH_DST_1 ${CXSPARSE_SOURCE_DIR})
ExternalProject_Add(cxsparse
    PREFIX ${CXSPARSE_PREFIX}
    GIT_REPOSITORY "https://github.com/TheFrenchLeaf/CXSparse.git"
    GIT_TAG "26040d5425fc5300b8e0a40b212ff1846b073629"
    INSTALL_DIR ${CXSPARSE_INSTALL_PATH}
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${CXSPARSE_PATCH_SRC_1} ${CXSPARSE_PATCH_DST_1}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${CXSPARSE_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DCMAKE_POSITION_INDEPENDENT_CODE=${CMAKE_POSITION_INDEPENDENT_CODE}
        -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
        -DCMAKE_CXX_EXTENSIONS=${CXX_EXTENSIONS}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DBUILD_SHARED_LIBS=0
)


#########################################################
# Eigen - Linear Alegbra library
#########################################################
set(EIGEN_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/eigen)
set(EIGEN_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/eigen)
set(EIGEN_INCLUDE_DIR ${EIGEN_INSTALL_PATH}/include/eigen3)
set(EIGEN_DIR ${EIGEN_INSTALL_PATH}/share/eigen3/cmake)
ExternalProject_Add(eigen
    PREFIX ${EIGEN_PREFIX}
    GIT_REPOSITORY "https://gitlab.com/libeigen/eigen.git"
    GIT_TAG "3.4.0"  # matches the version used by OpenMVG.
    INSTALL_DIR ${EIGEN_INSTALL_PATH}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${EIGEN_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DCMAKE_POSITION_INDEPENDENT_CODE=${CMAKE_POSITION_INDEPENDENT_CODE}
        -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
        -DCMAKE_CXX_EXTENSIONS=${CXX_EXTENSIONS}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DINCLUDE_INSTALL_DIR=${EIGEN_INCLUDE_DIR}
)


#########################################################
# Ceres Solver - Non-Linear Least-Squares Fits solver
#########################################################
set(CERES_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/ceres)
set(CERES_LIBRARY_DIR ${CERES_INSTALL_PATH}/lib)
set(CERES_INCLUDE_DIR ${CERES_INSTALL_PATH}/include)
set(CERES_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/ceres)
set(CERES_DOWNLOAD_DIR ${THIRDPARTY_BASE_WORKING_DIR}/ceres/src)
set(CERES_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/ceres/src/ceres)

set(CERES_BUILD_SHARED 0)
set(CERES_BUILD_TESTS 0)
set(CERES_BUILD_DOC 0)
set(CERES_BUILD_EXAMPLES 0)

ExternalProject_Add(ceres
    DEPENDS cxsparse eigen glog
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
        -DEigen3_DIR=${EIGEN_DIR}
        -Dglog_DIR=${GLOG_INSTALL_PATH}
        -DCXSPARSE_INCLUDE_DIR_HINTS=${CXSPARSE_INSTALL_PATH}
        -DCXSPARSE_LIBRARY_DIR_HINTS=${CXSPARSE_INSTALL_PATH}
        -DBUILD_TESTING=${CERES_BUILD_TESTS}
        -DBUILD_DOCUMENTATION=${CERES_BUILD_DOC}
        -DBUILD_EXAMPLES=${CERES_BUILD_EXAMPLES}
        -DBUILD_BENCHMARKS=0
        -DBUILD_SHARED_LIBS=${CERES_BUILD_SHARED}
        # Use the full 'glog' library, rather than the cut-down
        # 'miniglog' embedded in Ceres. 'glog' is faster than
        # 'miniglog', but increases the build complexity.
        #
        # 'miniglog' is disabled because of build errors on MSVC with
        # a conflict of the 'ERROR' severity identifer clashing with
        # something else in mmSolver.
        -DMINIGLOG=OFF
        # WARNING: Enabling "EIGENSPARSE" results in an LGPL licensed
        # Ceres.
        -DEIGENSPARSE=ON
        -DCXSPARSE=ON
        -DLAPACK=OFF
        -DSUITESPARSE=OFF
        -DGFLAGS=OFF
        -DCUSTOM_BLAS=OFF
        # Enable SCHUR_SPECIALIZATIONS for more optimizations at the
        # cost of compile time.
        -DSCHUR_SPECIALIZATIONS=ON
        -DCXX11=ON
        # Use OpenMP, TBB (with C++11) or C++11 Thread primitives?
        # Only one should be enabled.
        -DOPENMP=ON
        -DTBB=OFF
        -DCXX11_THREADS=OFF
        # For Microsoft Visual Studio: Use static C-Run Time Library
        # in place of shared.
        -DMSVC_USE_STATIC_CRT=OFF
)


#########################################################
# openMVG - Multiple View library
#########################################################
set(OPENMVG_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/openMVG)
set(OPENMVG_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/openMVG)
set(OPENMVG_DOWNLOAD_DIR ${THIRDPARTY_BASE_WORKING_DIR}/openMVG/src)
set(OPENMVG_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/openMVG/src/openMVG)

# Choose components based on OS
set(OpenMVG_BUILD_SHARED 0)
set(OpenMVG_BUILD_TESTS 0)
set(OpenMVG_BUILD_DOC 0)
set(OpenMVG_BUILD_EXAMPLES 0)
set(OpenMVG_BUILD_OPENGL_EXAMPLES 0)
set(OpenMVG_BUILD_SOFTWARES 0)
set(OpenMVG_BUILD_GUI_SOFTWARES 0)
set(OpenMVG_BUILD_COVERAGE 0)
if (MSVC)
  # This specific set of flags has been tested to work with
  # MSVC. Using different flags, although faster/better to compile,
  # might result in a failed build.
  set(OpenMVG_BUILD_SHARED 0)
  set(OpenMVG_BUILD_TESTS 0)
  set(OpenMVG_BUILD_DOC 1)
  set(OpenMVG_BUILD_EXAMPLES 1)
  set(OpenMVG_BUILD_OPENGL_EXAMPLES 0)
  set(OpenMVG_BUILD_SOFTWARES 1)
  set(OpenMVG_BUILD_GUI_SOFTWARES 0)
  set(OpenMVG_BUILD_COVERAGE 0)
endif()

ExternalProject_Add(openMVG
    PREFIX ${OPENMVG_PREFIX}
    DEPENDS eigen ceres
    GIT_REPOSITORY "https://github.com/openMVG/openMVG.git"
    GIT_TAG "v2.0"
    DOWNLOAD_DIR ${OPENMVG_DOWNLOAD_DIR}
    SOURCE_DIR ${OPENMVG_SOURCE_DIR}
    SOURCE_SUBDIR src/
    INSTALL_DIR ${OPENMVG_INSTALL_PATH}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${OPENMVG_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${EIGEN_INSTALL_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DCMAKE_POSITION_INDEPENDENT_CODE=${CMAKE_POSITION_INDEPENDENT_CODE}
        -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
        -DCMAKE_CXX_EXTENSIONS=${CXX_EXTENSIONS}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DOpenMVG_BUILD_SHARED=${OpenMVG_BUILD_SHARED}
        -DOpenMVG_BUILD_TESTS=${OpenMVG_BUILD_TESTS}
        -DOpenMVG_BUILD_DOC=${OpenMVG_BUILD_DOC}
        -DOpenMVG_BUILD_EXAMPLES=${OpenMVG_BUILD_EXAMPLES}
        -DOpenMVG_BUILD_OPENGL_EXAMPLES=${OpenMVG_BUILD_OPENGL_EXAMPLES}
        -DOpenMVG_BUILD_SOFTWARES=${OpenMVG_BUILD_SOFTWARES}
        -DOpenMVG_BUILD_GUI_SOFTWARES=${OpenMVG_BUILD_GUI_SOFTWARES}
        -DOpenMVG_BUILD_COVERAGE=${OpenMVG_BUILD_COVERAGE}
        -DOpenMVG_USE_OPENMP=1
        -DOpenMVG_USE_OPENCV=0
        -DOpenMVG_USE_OCVSIFT=0
        -DEigen3_DIR=${EIGEN_DIR}
        # WARNING: Enabling "EIGENSPARSE" results in an LGPL licensed
        # Ceres.
        -DEIGENSPARSE=1
        -DCeres_DIR=${CERES_INSTALL_PATH}
        -DCERES_DIR_HINTS=${CERES_INSTALL_PATH}
)


##################
# dlfcn
##################
#
# dlfcn is required for the LDPK on Windows only.
set(LDPK_DEPENDS "")
set(DLFCN_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/dlfcn)
set(DLFCN_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/dlfcn)
if (WIN32 AND NOT UNIX)
  set(LDPK_DEPENDS "dlfcn")
  ExternalProject_Add(dlfcn
    PREFIX ${DLFCN_PREFIX}
    GIT_REPOSITORY "https://github.com/dlfcn-win32/dlfcn-win32.git"
    GIT_TAG "v1.2.0"
    INSTALL_DIR ${DLFCN_INSTALL_PATH}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${DLFCN_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DCMAKE_POSITION_INDEPENDENT_CODE=${CMAKE_POSITION_INDEPENDENT_CODE}
        -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
        -DCMAKE_CXX_EXTENSIONS=${CXX_EXTENSIONS}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DBUILD_SHARED_LIBS=ON
        -DBUILD_TESTS=OFF
    )
endif()


##################
# LDPK (Lens Distortion Plug-in Kit)
##################
#
# The LDPK from Science-d-Visions is used to deform images using lens
# models.
set(LDPK_INSTALL_PATH ${THIRDPARTY_BASE_INSTALL_DIR}/ldpk)
set(LDPK_PREFIX ${THIRDPARTY_BASE_WORKING_DIR}/ldpk)
set(LDPK_DOWNLOAD_DIR ${THIRDPARTY_BASE_WORKING_DIR}/ldpk/src)
set(LDPK_SOURCE_DIR ${THIRDPARTY_BASE_WORKING_DIR}/ldpk/src/ldpk)

# Patches
set(LDPK_PATCH_DIR ${CMAKE_CURRENT_SOURCE_DIR}/patches/ldpk)
set(LDPK_PATCH_SRC_1 ${LDPK_PATCH_DIR}/CMakeLists.txt)
set(LDPK_PATCH_DST_1 ${LDPK_SOURCE_DIR}/CMakeLists.txt)
set(LDPK_PATCH_SRC_2 ${LDPK_PATCH_DIR}/ldpk-config.cmake.in)
set(LDPK_PATCH_DST_2 ${LDPK_SOURCE_DIR}/ldpk-config.cmake.in)

ExternalProject_Add(ldpk
    PREFIX ${LDPK_PREFIX}
    DEPENDS ${LDPK_DEPENDS}
    URL "https://www.3dequalizer.com/user_daten/sections/tech_docs/archives/ldpk-2.7.tgz"
    URL_HASH MD5=4b8eb9cd970c671f5ef37e5001979bf2
    DOWNLOAD_DIR ${LDPK_DOWNLOAD_DIR}
    SOURCE_DIR ${LDPK_SOURCE_DIR}
    INSTALL_DIR ${LDPK_INSTALL_PATH}
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${LDPK_PATCH_SRC_1} ${LDPK_PATCH_DST_1}
    COMMAND       ${CMAKE_COMMAND} -E copy ${LDPK_PATCH_SRC_2} ${LDPK_PATCH_DST_2}
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
        -DCMAKE_INSTALL_PREFIX=${LDPK_INSTALL_PATH}
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
        -DCMAKE_POSITION_INDEPENDENT_CODE=${CMAKE_POSITION_INDEPENDENT_CODE}
        -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
        -DCMAKE_CXX_EXTENSIONS=${CXX_EXTENSIONS}
        -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
        -DDLFCN_LOCATION=${DLFCN_INSTALL_PATH}
)
