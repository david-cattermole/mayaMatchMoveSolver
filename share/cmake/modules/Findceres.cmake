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
# - ceres finder module
# This module will look for ceres, using the predefined variable
# ceres_ROOT.
#
# Uses Variables:
# - ceres_ROOT_PATH - Directory for the ceres install root.
# - ceres_INCLUDE_PATH - Directory for the header files.
# - ceres_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - ceres_FOUND
# - ceres_LIBRARIES
# - ceres_INCLUDE_DIRS
#

function(find_ceres_find_with_paths ceres_root ceres_include_path ceres_lib_path)

    find_path(ceres_include_dir ceres/ceres.h
      HINTS
        ${ceres_include_path}
        ${ceres_root}
        /usr/local/include
        /usr/include
      PATH_SUFFIXES
        include/
    )

    find_library(ceres_library
      NAMES
        libceres
        libceres-debug
        ceres
        ceres-debug
      HINTS
        ${ceres_lib_path}
        ${ceres_root}
        /usr/lib
        /usr/local/lib
      PATH_SUFFIXES
        bin/
        lib/
        lib64/
    )

    find_path(ceres_dir
      NAMES
        CeresConfig.cmake
        CeresConfigVersion.cmake
      HINTS
        ${ceres_lib_path}/../CMake
        ${ceres_root}
        /usr/share
        /usr/local/share
    )

    if(ceres_include_dir AND ceres_library AND ceres_dir)
      set(${out_ceres_include_dirs} ${ceres_include_dir} PARENT_SCOPE)
      set(${out_ceres_libraries} ${ceres_library} PARENT_SCOPE)
      set(${out_ceres_dir} ${ceres_dir} PARENT_SCOPE)
    endif()

endfunction()


function(find_ceres_create_target)
  add_library(ceres UNKNOWN IMPORTED GLOBAL)
endfunction()


function(find_ceres_set_target ceres_library ceres_include_dir)

  set_target_properties(ceres PROPERTIES
    IMPORTED_LOCATION ${ceres_library}
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    INTERFACE_INCLUDE_DIRECTORIES ${ceres_include_dir}
  )

  if(NOT WIN32)
    # 'gomp' is GNU OpenMP for GCC.
    set_target_properties(ceres PROPERTIES IMPORTED_LINK_INTERFACE_LIBRARIES "gomp")
  endif()

endfunction()


option(ceres_ALLOW_DOWNLOAD
  "Allow automatically downloading and building ceres solver?" ON)


if(NOT MMSOLVER_DOWNLOAD_DEPENDENCIES OR NOT ceres_ALLOW_DOWNLOAD)

  if(NOT DEFINED ceres_ROOT)
    # Search for "ceres-config.cmake" given on the command line.
    find_package(ceres ${ceres_FIND_VERSION} CONFIG QUIET)
  endif()

  if(ceres_FOUND)
    message(FATAL_ERROR "Not Implemented. ceres has been found from the ceres-config.cmake file")
  else()
    # Fallback and try to find the package.
    find_ceres_find_with_paths(
      ${ceres_ROOT}
      ${ceres_INCLUDE_PATH}
      ${ceres_LIB_PATH}
      ceres_DIR
      ceres_INCLUDE_DIRS
      ceres_LIBRARIES
      )
  endif()

  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(ceres
    REQUIRED_VARS
      ceres_DIR
      ceres_LIBRARIES
      ceres_INCLUDE_DIRS
  )

  if(ceres_FOUND)
    message(STATUS "ceres: Found=${ceres_FOUND}")
    message(STATUS "ceres: Config=${ceres_DIR}")
    message(STATUS "ceres: Include=${ceres_INCLUDE_DIRS}")
    message(STATUS "ceres: Library=${ceres_LIBRARIES}")
  endif()

endif()


# Ensure a target for ceres is created.
if(NOT TARGET ceres)
  find_ceres_create_target()
  if(ceres_FOUND)
    find_ceres_set_target(${ceres_LIBRARY} ${ceres_INCLUDE_DIR})
  else()
    set(_ceres_TARGET_CREATE TRUE)
  endif()
endif()


# Download, Build and Install.
if(NOT ceres_FOUND AND MMSOLVER_DOWNLOAD_DEPENDENCIES AND ceres_ALLOW_DOWNLOAD)
  include(ExternalProject)
  include(GNUInstallDirs)

  set(_EXTERNAL_INSTALL_DIR "${CMAKE_BINARY_DIR}/ext/install")
  set(_EXTERNAL_BUILD_DIR "${CMAKE_BINARY_DIR}/ext/build")

  # Fill in the expected values/paths that will exist when the build
  # and install of ceres actually happens.
  set(ceres_FOUND TRUE)
  set(ceres_VERSION ${ceres_FIND_VERSION})

  set(ceres_INCLUDE_DIR "${_EXTERNAL_INSTALL_DIR}/ceres/${CMAKE_INSTALL_INCLUDEDIR}")
  set(ceres_LIBRARY_DIR "${_EXTERNAL_INSTALL_DIR}/ceres/${CMAKE_INSTALL_LIBDIR}")

  set(ceres_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}ceres${CMAKE_STATIC_LIBRARY_SUFFIX}")
  if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(ceres_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}ceres-debug${CMAKE_STATIC_LIBRARY_SUFFIX}")
  endif()
  set(ceres_LIBRARY "${ceres_LIBRARY_DIR}/${ceres_LIBRARY_NAME}")

  if(WIN32)
    set(ceres_DIR "${_EXTERNAL_INSTALL_DIR}/ceres/CMake")
  else()
    set(ceres_DIR "${ceres_LIBRARY_DIR}/cmake/Ceres/")
  endif()

  set(ceres_URL
    "https://github.com/ceres-solver/ceres-solver.git"
    CACHE STRING
    "The URL for the ceres-solver git repository.")

  set(ceres_GIT_TAG "${ceres_VERSION}" CACHE STRING
    "The Git tag for the ceres-solver git repository.")

  set(ceres_INSTALL_PATH ${_EXTERNAL_INSTALL_DIR}/ceres)
  set(ceres_PREFIX ${_EXTERNAL_BUILD_DIR}/ceres)

  # The full 'glog' library is faster than the cut-down 'miniglog'
  # embedded in Ceres. Different platforms enable/disable this because
  # of build issues.
  #
  set(ceres_USE_MINIGLOG 0)
  if (WIN32 AND NOT UNIX)
    # 'miniglog' is disabled on Windows because of build errors on MSVC
    # with a conflict of the 'ERROR' severity identifer clashing with
    # something else in mmSolver.
    set(ceres_USE_MINIGLOG 0)
  else()
    # 'glog' is disabled on Linux because of linking/build errors.
    set(ceres_USE_MINIGLOG 1)
  endif()

  set(ceres_CMAKE_ARGS
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
    -DCMAKE_INSTALL_PREFIX=${ceres_INSTALL_PATH}
    -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
    -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
    -DCMAKE_POSITION_INDEPENDENT_CODE=${CMAKE_POSITION_INDEPENDENT_CODE}
    -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
    -DCMAKE_CXX_EXTENSIONS=${CXX_EXTENSIONS}
    -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
    -DCMAKE_FIND_PACKAGE_NO_PACKAGE_REGISTRY=1
    -DCMAKE_FIND_PACKAGE_NO_SYSTEM_PACKAGE_REGISTRY=1
    -DCMAKE_FIND_USE_PACKAGE_REGISTRY=0

    -DEIGEN_INCLUDE_DIR_HINTS=${Eigen3_INCLUDE_DIR}

    -DGLOG_INCLUDE_DIR=${glog_INCLUDE_DIR}
    -DGLOG_LIBRARY=${glog_LIBRARY}
    -DGLOG_INCLUDE_DIR_HINTS=${glog_INCLUDE_DIR}
    -DGLOG_LIBRARY_DIR_HINTS=${glog_LIBRARY}

    -DBUILD_TESTING=0
    -DBUILD_DOCUMENTATION=0
    -DBUILD_EXAMPLES=0
    -DBUILD_BENCHMARKS=0
    -DBUILD_SHARED_LIBS=0
    -DCXX11=ON

    -DMINIGLOG=${ceres_USE_MINIGLOG}
    # WARNING: Enabling "EIGENSPARSE" results in an LGPL licensed
    # Ceres.
    -DEIGENSPARSE=ON
    -DLAPACK=OFF
    -DSUITESPARSE=OFF
    -DGFLAGS=OFF
    -DCUSTOM_BLAS=OFF

    # Enable SCHUR_SPECIALIZATIONS for more optimizations at the
    # cost of compile time.
    -DSCHUR_SPECIALIZATIONS=OFF

    # Use OpenMP, TBB (with C++11) or C++11 Thread primitives?
    # Only one should be enabled.
    -DOPENMP=ON
    -DTBB=OFF
    -DCXX11_THREADS=OFF

    # For Microsoft Visual Studio: Use static C-Run Time Library
    # in place of shared.
    -DMSVC_USE_STATIC_CRT=OFF
  )

  # Hack to let imported target be built from ExternalProject_Add
  file(MAKE_DIRECTORY ${ceres_INCLUDE_DIR})

  ExternalProject_Add(ceres_install
    DEPENDS Eigen3 glog
    PREFIX ${ceres_PREFIX}
    GIT_REPOSITORY ${ceres_URL}
    GIT_TAG "${ceres_GIT_TAG}"
    INSTALL_DIR ${ceres_INSTALL_PATH}
    BUILD_BYPRODUCTS ${ceres_LIBRARY}
    CMAKE_ARGS ${ceres_CMAKE_ARGS}
    EXCLUDE_FROM_ALL TRUE
    BUILD_COMMAND ""
    INSTALL_COMMAND ${CMAKE_COMMAND} --build . --config ${CMAKE_BUILD_TYPE} --target install --parallel
  )

  add_dependencies(ceres ceres_install)
  message(STATUS "Installing ceres (version \"${ceres_VERSION}\")")
  message(STATUS "ceres: Config=${ceres_DIR}")
  message(STATUS "ceres: Include=${ceres_INCLUDE_DIR}")
  message(STATUS "ceres: Library=${ceres_LIBRARY}")

else()

  # Placeholder target that does nothing.
  add_custom_target(ceres_install)

endif()


if(_ceres_TARGET_CREATE)
  find_ceres_set_target(${ceres_LIBRARY} ${ceres_INCLUDE_DIR})
  mark_as_advanced(
    ceres_DIR
    ceres_INCLUDE_DIR
    ceres_LIBRARY
    ceres_VERSION
  )
endif()
