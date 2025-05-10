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
# Ceres_ROOT.
#
# Uses Variables:
# - Ceres_ROOT_PATH - Directory for the ceres install root.
# - Ceres_INCLUDE_PATH - Directory for the header files.
# - Ceres_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - Ceres_FOUND
# - Ceres_LIBRARIES
# - Ceres_INCLUDE_DIRS
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


option(Ceres_ALLOW_DOWNLOAD
  "Allow automatically downloading and building Ceres solver?" ON)


if(NOT MMSOLVER_DOWNLOAD_DEPENDENCIES OR NOT Ceres_ALLOW_DOWNLOAD)

  if(NOT DEFINED Ceres_ROOT)
    # Search for "ceres-config.cmake" given on the command line.
    find_package(Ceres ${Ceres_FIND_VERSION} CONFIG QUIET)
  endif()

  if(Ceres_FOUND)
    message(FATAL_ERROR "Not Implemented. Ceres has been found from the ceres-config.cmake file")
  else()
    # Fallback and try to find the package.
    find_ceres_find_with_paths(
      ${Ceres_ROOT}
      ${Ceres_INCLUDE_PATH}
      ${Ceres_LIB_PATH}
      Ceres_DIR
      Ceres_INCLUDE_DIRS
      Ceres_LIBRARIES
      )
  endif()

  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(ceres
    REQUIRED_VARS
      Ceres_DIR
      Ceres_LIBRARIES
      Ceres_INCLUDE_DIRS
  )

  if(Ceres_FOUND)
    message(STATUS "Ceres: Found=${Ceres_FOUND}")
    message(STATUS "Ceres: Config=${Ceres_DIR}")
    message(STATUS "Ceres: Include=${Ceres_INCLUDE_DIRS}")
    message(STATUS "Ceres: Library=${Ceres_LIBRARIES}")
  endif()

endif()


# Ensure a target for Ceres is created.
if(NOT TARGET ceres)
  find_ceres_create_target()
  if(Ceres_FOUND)
    find_ceres_set_target(${Ceres_LIBRARY} ${Ceres_INCLUDE_DIR})
  else()
    set(_ceres_TARGET_CREATE TRUE)
  endif()
endif()


# Download, Build and Install.
if(NOT Ceres_FOUND AND MMSOLVER_DOWNLOAD_DEPENDENCIES AND Ceres_ALLOW_DOWNLOAD)
  include(ExternalProject)
  include(GNUInstallDirs)

  set(_EXTERNAL_INSTALL_DIR "${CMAKE_BINARY_DIR}/ext/install")
  set(_EXTERNAL_BUILD_DIR "${CMAKE_BINARY_DIR}/ext/build")

  # Fill in the expected values/paths that will exist when the build
  # and install of Ceres actually happens.
  set(Ceres_FOUND TRUE)
  set(Ceres_VERSION ${Ceres_FIND_VERSION})

  set(Ceres_INCLUDE_DIR "${_EXTERNAL_INSTALL_DIR}/ceres/${CMAKE_INSTALL_INCLUDEDIR}")
  set(Ceres_LIBRARY_DIR "${_EXTERNAL_INSTALL_DIR}/ceres/${CMAKE_INSTALL_LIBDIR}")

  set(Ceres_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}ceres${CMAKE_STATIC_LIBRARY_SUFFIX}")
  if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(Ceres_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}ceres-debug${CMAKE_STATIC_LIBRARY_SUFFIX}")
  endif()
  set(Ceres_LIBRARY "${Ceres_LIBRARY_DIR}/${Ceres_LIBRARY_NAME}")

  if(WIN32)
    set(Ceres_DIR "${_EXTERNAL_INSTALL_DIR}/ceres/CMake")
  else()
    set(Ceres_DIR "${Ceres_LIBRARY_DIR}/cmake/Ceres/")
  endif()

  set(Ceres_URL
    "https://github.com/ceres-solver/ceres-solver.git"
    CACHE STRING
    "The URL for the ceres-solver git repository.")

  set(Ceres_GIT_TAG "${Ceres_VERSION}" CACHE STRING
    "The Git tag for the ceres-solver git repository.")

  set(Ceres_INSTALL_PATH ${_EXTERNAL_INSTALL_DIR}/ceres)
  set(Ceres_PREFIX ${_EXTERNAL_BUILD_DIR}/ceres)

  # The full 'glog' library is faster than the cut-down 'miniglog'
  # embedded in Ceres, but it also adds a dependency.
  if (MMSOLVER_USE_GLOG)
    set(Ceres_USE_MINIGLOG 0)
  else()
    set(Ceres_USE_MINIGLOG 1)
  endif()

  set(Ceres_CMAKE_ARGS
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
    -DCMAKE_INSTALL_PREFIX=${Ceres_INSTALL_PATH}
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

    -DMINIGLOG=${Ceres_USE_MINIGLOG}
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
  file(MAKE_DIRECTORY ${Ceres_INCLUDE_DIR})

  set(Ceres_dependencies "Eigen3 glog")
  if(NOT MMSOLVER_USE_GLOG)
    # No need to use 'glog' if 'miniglog' feature is enabled.
    set(Ceres_dependencies "Eigen3")
  endif()

  ExternalProject_Add(ceres_install
    DEPENDS ${Ceres_dependencies}
    PREFIX ${Ceres_PREFIX}
    GIT_REPOSITORY ${Ceres_URL}
    GIT_TAG "${Ceres_GIT_TAG}"
    INSTALL_DIR ${Ceres_INSTALL_PATH}
    BUILD_BYPRODUCTS ${Ceres_LIBRARY}
    CMAKE_ARGS ${Ceres_CMAKE_ARGS}
    EXCLUDE_FROM_ALL TRUE
    BUILD_COMMAND ""
    INSTALL_COMMAND ${CMAKE_COMMAND} --build . --config ${CMAKE_BUILD_TYPE} --target install --parallel
  )

  add_dependencies(ceres ceres_install)
  message(STATUS "Installing Ceres (version \"${Ceres_VERSION}\")")
  message(STATUS "Ceres: Config=${Ceres_DIR}")
  message(STATUS "Ceres: Include=${Ceres_INCLUDE_DIR}")
  message(STATUS "Ceres: Library=${Ceres_LIBRARY}")

else()

  # Placeholder target that does nothing.
  if(NOT TARGET ceres_install)
    add_custom_target(ceres_install)
  endif()

endif()


if(_ceres_TARGET_CREATE)
  find_ceres_set_target(${Ceres_LIBRARY} ${Ceres_INCLUDE_DIR})
  mark_as_advanced(
    Ceres_DIR
    Ceres_INCLUDE_DIR
    Ceres_LIBRARY
    Ceres_VERSION
  )
endif()
