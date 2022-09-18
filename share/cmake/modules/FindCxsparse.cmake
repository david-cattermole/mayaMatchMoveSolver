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
# - cxsparse finder module
# This module will look for cxsparse, using the predefined variable
# cxsparse_ROOT.
#
# Uses Variables:
# - cxsparse_ROOT_PATH - Directory for the cxsparse install root.
# - cxsparse_INCLUDE_PATH - Directory for the header files.
# - cxsparse_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - cxsparse_FOUND
# - cxsparse_LIBRARIES
# - cxsparse_INCLUDE_DIRS
#

function(find_cxsparse_find_with_paths cxsparse_root cxsparse_include_path cxsparse_lib_path)

    find_path(cxsparse_include_dir cs.h
      HINTS
        ${cxsparse_include_path}
        ${cxsparse_root}
        /usr/local/include
        /usr/include
      PATH_SUFFIXES
        include/
    )

    find_library(cxsparse_library
      NAMES
        libcxsparse
        libcxsparse.so
        cxsparse
      HINTS
        ${cxsparse_lib_path}
        ${cxsparse_root}
        /usr/lib
        /usr/local/lib
      PATH_SUFFIXES
        bin/
        lib/
    )

    if(cxsparse_include_dir AND cxsparse_library)
      set(${out_cxsparse_include_dirs} ${cxsparse_include_dir} PARENT_SCOPE)
      set(${out_cxsparse_libraries} ${cxsparse_library} PARENT_SCOPE)
    endif()

endfunction()


function(find_cxsparse_create_target)
  add_library(cxsparse::cxsparse UNKNOWN IMPORTED GLOBAL)
endfunction()


function(find_cxsparse_set_target cxsparse_library cxsparse_include_dir)

  set_target_properties(cxsparse::cxsparse PROPERTIES
    IMPORTED_LOCATION ${cxsparse_library}
    IMPORTED_LINK_INTERFACE_LANGUAGES "C"
    INTERFACE_COMPILE_DEFINITIONS "NCOMPLEX"
    INTERFACE_INCLUDE_DIRECTORIES ${cxsparse_include_dir}
    )

endfunction()


if(NOT MMSOLVER_DOWNLOAD_DEPENDENCIES)

  # TODO: Make CXSparse configurable to find from variables given.
  message(FATAL_ERROR "cxsparse is an internal dependency and must be auto-downloaded and built.")

endif()


# Ensure a target for cxsparse is created.
if(NOT TARGET cxsparse::cxsparse)
  find_cxsparse_create_target()
  if(cxsparse_FOUND)
    find_cxsparse_set_target(${cxsparse_LIBRARY} ${cxsparse_INCLUDE_DIR})
  else()
    set(_cxsparse_TARGET_CREATE TRUE)
  endif()
endif()


# Download, Build and Install.
if(NOT cxsparse_FOUND AND MMSOLVER_DOWNLOAD_DEPENDENCIES)
  include(ExternalProject)
  include(GNUInstallDirs)

  set(_EXTERNAL_INSTALL_DIR "${CMAKE_BINARY_DIR}/ext/install")
  set(_EXTERNAL_BUILD_DIR "${CMAKE_BINARY_DIR}/ext/build")

  # Fill in the expected values/paths that will exist when the build
  # and install of cxsparse actually happens.
  set(cxsparse_FOUND TRUE)
  set(cxsparse_VERSION ${cxsparse_FIND_VERSION})

  set(cxsparse_INCLUDE_DIR "${_EXTERNAL_INSTALL_DIR}/cxsparse/${CMAKE_INSTALL_INCLUDEDIR}")
  set(cxsparse_LIBRARY_DIR "${_EXTERNAL_INSTALL_DIR}/cxsparse/${CMAKE_INSTALL_LIBDIR}")

  set(cxsparse_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}cxsparse${CMAKE_STATIC_LIBRARY_SUFFIX}")
  set(cxsparse_LIBRARY "${cxsparse_LIBRARY_DIR}/${cxsparse_LIBRARY_NAME}")

  set(cxsparse_URL
    "https://github.com/TheFrenchLeaf/CXSparse.git"
    CACHE STRING
    "The URL for the CXSparse git repository.")

  # Unfortunately the Git repo doesn't have version tags at all :(
  set(cxsparse_GIT_TAG "26040d5425fc5300b8e0a40b212ff1846b073629"
    CACHE STRING
    "The Git Tag for the CXSparse git repository.")

  set(cxsparse_INSTALL_PATH ${_EXTERNAL_INSTALL_DIR}/cxsparse)
  set(cxsparse_PREFIX ${_EXTERNAL_BUILD_DIR}/cxsparse)
  set(cxsparse_SOURCE_DIR ${_EXTERNAL_BUILD_DIR}/cxsparse/src/cxsparse)

  set(cxsparse_PATCH_SRC_1 ${CMAKE_SOURCE_DIR}/external/patches/cxsparse/CMakeLists.txt)
  set(cxsparse_PATCH_SRC_2 ${CMAKE_SOURCE_DIR}/external/patches/cxsparse/cxsparse-config.cmake.in)
  set(cxsparse_PATCH_DST_1 ${cxsparse_SOURCE_DIR}/CMakeLists.txt)
  set(cxsparse_PATCH_DST_2 ${cxsparse_SOURCE_DIR}/cxsparse-config.cmake.in)

  set(cxsparse_CMAKE_ARGS
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
    -DCMAKE_INSTALL_PREFIX=${cxsparse_INSTALL_PATH}
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

    -DNCOMPLEX=1
    -DBUILD_SHARED_LIBS=0
  )

  # Hack to let imported target be built from ExternalProject_Add
  file(MAKE_DIRECTORY ${cxsparse_INCLUDE_DIR})

  ExternalProject_Add(cxsparse
    PREFIX ${cxsparse_PREFIX}
    GIT_REPOSITORY ${cxsparse_URL}
    GIT_TAG ${cxsparse_GIT_TAG}
    INSTALL_DIR ${cxsparse_INSTALL_PATH}
    BUILD_BYPRODUCTS ${cxsparse_LIBRARY}
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${cxsparse_PATCH_SRC_1} ${cxsparse_PATCH_DST_1}
    COMMAND       ${CMAKE_COMMAND} -E copy ${cxsparse_PATCH_SRC_2} ${cxsparse_PATCH_DST_2}
    CMAKE_ARGS ${cxsparse_CMAKE_ARGS}
    EXCLUDE_FROM_ALL TRUE
    BUILD_COMMAND ""
    INSTALL_COMMAND ${CMAKE_COMMAND} --build . --config ${CMAKE_BUILD_TYPE} --target install --parallel
  )

  add_dependencies(cxsparse::cxsparse cxsparse)
  message(STATUS "Installing cxsparse (version \"${cxsparse_VERSION}\")")
  message(STATUS "cxsparse: Include=${cxsparse_INCLUDE_DIR}")
  message(STATUS "cxsparse: Library=${cxsparse_LIBRARY}")

else()

  # Placeholder target that does nothing.
  add_custom_target(cxsparse)

endif()


if(_cxsparse_TARGET_CREATE)
  find_cxsparse_set_target(${cxsparse_LIBRARY} ${cxsparse_INCLUDE_DIR})
  mark_as_advanced(
    cxsparse_INCLUDE_DIR
    cxsparse_LIBRARY
    cxsparse_VERSION
  )
endif()
