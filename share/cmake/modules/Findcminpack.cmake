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
# - cminpack finder module
# This module will look for cminpack, using the predefined variable
# cminpack_ROOT.
#
# Uses Variables:
# - cminpack_ROOT_PATH - Directory for the cminpack install root.
# - cminpack_INCLUDE_PATH - Directory for the header files.
# - cminpack_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - cminpack_FOUND
# - cminpack_LIBRARIES
# - cminpack_INCLUDE_DIRS
#

function(find_cminpack_find_with_paths
  cminpack_root
  cminpack_include_path
  cminpack_lib_path
  out_cminpack_include_dirs
  out_cminpack_libraries)

    find_path(cminpack_include_dir cminpack.h
      HINTS
        ${cminpack_include_path}
        ${cminpack_root}
        /usr/local/include
        /usr/include
      PATH_SUFFIXES
        include/
        cminpack-1/
        include/cminpack-1/
    )

    find_library(cminpack_library
      NAMES
        libcminpack.1
        libcminpack.so.1
        libcminpack.1.dylib
        libcminpack
        cminpack
        libcminpack_s
        libcminpack_s_d
        cminpack_s
        cminpack_s_d
      HINTS
        ${cminpack_lib_path}
        ${cminpack_root}
        /usr/lib
        /usr/local/lib
      PATH_SUFFIXES
        bin/
        lib/
        lib64/
    )

    if(cminpack_include_dir AND cminpack_library)
      set(${out_cminpack_include_dirs} ${cminpack_include_dir} PARENT_SCOPE)
      set(${out_cminpack_libraries} ${cminpack_library} PARENT_SCOPE)
    endif()

endfunction()


function(find_cminpack_create_target)
  add_library(cminpack::cminpack UNKNOWN IMPORTED GLOBAL)
endfunction()


function(find_cminpack_set_target cminpack_library cminpack_include_dir)

  set_target_properties(cminpack::cminpack PROPERTIES
    IMPORTED_LOCATION ${cminpack_library}
    IMPORTED_LINK_INTERFACE_LANGUAGES "C"
    INTERFACE_INCLUDE_DIRECTORIES ${cminpack_include_dir}
    )

  if (WIN32)
    set_target_properties(cminpack::cminpack PROPERTIES
      INTERFACE_COMPILE_DEFINITIONS "CMINPACK_NO_DLL"
      )
  endif ()

endfunction()


option(cminpack_ALLOW_DOWNLOAD
  "Allow automatically downloading and building CMinpack?" ON)


if(NOT MMSOLVER_DOWNLOAD_DEPENDENCIES OR NOT cminpack_ALLOW_DOWNLOAD)

  if(NOT DEFINED cminpack_ROOT)
    # Search for "cminpack-config.cmake" given on the command line.
    find_package(cminpack ${cminpack_FIND_VERSION} CONFIG QUIET)
  endif()

  if(cminpack_FOUND)
    message(FATAL_ERROR "Not Implemented. cminpack has been found from the cminpack-config.cmake file")
  else()
    # Fallback and try to find the package.
    find_cminpack_find_with_paths(
      "${cminpack_ROOT}"
      "${cminpack_INCLUDE_PATH}"
      "${cminpack_LIB_PATH}"
      cminpack_INCLUDE_DIRS
      cminpack_LIBRARIES
      )
  endif()

  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(cminpack
    REQUIRED_VARS
      cminpack_LIBRARIES
      cminpack_INCLUDE_DIRS
  )

  if(cminpack_FOUND)
    message(STATUS "cminpack: Found=${cminpack_FOUND}")
    message(STATUS "cminpack: Include=${cminpack_INCLUDE_DIRS}")
    message(STATUS "cminpack: Library=${cminpack_LIBRARIES}")
  endif()

endif()


# Ensure a target for cminpack is created.
if(NOT TARGET cminpack::cminpack)
  find_cminpack_create_target()
  if(cminpack_FOUND)
    find_cminpack_set_target(${cminpack_LIBRARY} ${cminpack_INCLUDE_DIR})
  else()
    set(_cminpack_TARGET_CREATE TRUE)
  endif()
endif()


# Download, Build and Install.
if(NOT cminpack_FOUND AND MMSOLVER_DOWNLOAD_DEPENDENCIES AND cminpack_ALLOW_DOWNLOAD)
  include(ExternalProject)
  include(GNUInstallDirs)

  set(_EXTERNAL_INSTALL_DIR "${CMAKE_BINARY_DIR}/ext/install")
  set(_EXTERNAL_BUILD_DIR "${CMAKE_BINARY_DIR}/ext/build")

  # Fill in the expected values/paths that will exist when the build
  # and install of cminpack actually happens.
  set(cminpack_FOUND TRUE)
  set(cminpack_VERSION ${cminpack_FIND_VERSION})

  set(cminpack_INCLUDE_DIR "${_EXTERNAL_INSTALL_DIR}/cminpack/${CMAKE_INSTALL_INCLUDEDIR}/cminpack-1")
  set(cminpack_LIBRARY_DIR "${_EXTERNAL_INSTALL_DIR}/cminpack/${CMAKE_INSTALL_LIBDIR}")

  set(cminpack_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}cminpack_s${CMAKE_STATIC_LIBRARY_SUFFIX}")
  if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(cminpack_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}cminpack_s_d${CMAKE_STATIC_LIBRARY_SUFFIX}")
  endif()
  set(cminpack_LIBRARY "${cminpack_LIBRARY_DIR}/${cminpack_LIBRARY_NAME}")

  set(cminpack_URL
    "https://github.com/devernay/cminpack.git"
    CACHE STRING
    "The URL for the CMinpack git repository.")

  set(cminpack_GIT_TAG "v${cminpack_VERSION}" CACHE STRING
    "The Git tag for the CMinpack git repository.")

  set(cminpack_INSTALL_PATH ${_EXTERNAL_INSTALL_DIR}/cminpack)
  set(cminpack_PREFIX ${_EXTERNAL_BUILD_DIR}/cminpack)
  set(cminpack_SOURCE_DIR ${_EXTERNAL_BUILD_DIR}/cminpack/src/cminpack)

  set(cminpack_CMAKE_ARGS
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
    -DCMAKE_INSTALL_PREFIX=${cminpack_INSTALL_PATH}
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

    -DCMINPACK_PRECISION=d  # d=double precision, s=single precision
    -DBUILD_SHARED_LIBS=0
    -DBUILD_EXAMPLES=0
    -DUSE_BLAS=0
  )

  # Hack to let imported target be built from ExternalProject_Add
  file(MAKE_DIRECTORY ${cminpack_INCLUDE_DIR})

  ExternalProject_Add(cminpack
    PREFIX ${cminpack_PREFIX}
    GIT_REPOSITORY ${cminpack_URL}
    GIT_TAG "${cminpack_GIT_TAG}"
    INSTALL_DIR ${cminpack_INSTALL_PATH}
    BUILD_BYPRODUCTS ${cminpack_LIBRARY}
    CMAKE_ARGS ${cminpack_CMAKE_ARGS}
    EXCLUDE_FROM_ALL TRUE
    BUILD_COMMAND ""
    INSTALL_COMMAND ${CMAKE_COMMAND} --build . --config ${CMAKE_BUILD_TYPE} --target install --parallel
  )

  add_dependencies(cminpack::cminpack cminpack)
  message(STATUS "Installing cminpack (version \"${cminpack_VERSION}\")")
  message(STATUS "cminpack: Include=${cminpack_INCLUDE_DIR}")
  message(STATUS "cminpack: Library=${cminpack_LIBRARY}")

else()

  # Placeholder target that does nothing.
  add_custom_target(cminpack)

endif()


if(_cminpack_TARGET_CREATE)
  find_cminpack_set_target(${cminpack_LIBRARY} ${cminpack_INCLUDE_DIR})
  mark_as_advanced(
    cminpack_INCLUDE_DIR
    cminpack_LIBRARY
    cminpack_VERSION
  )
endif()
