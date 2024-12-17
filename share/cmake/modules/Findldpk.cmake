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
# - ldpk finder module
# This module will look for ldpk, using the predefined variable
# ldpk_ROOT.
#
# Uses Variables:
# - ldpk_ROOT_PATH - Directory for the ldpk install root.
# - ldpk_INCLUDE_PATH - Directory for the header files.
#
# Defines Variables:
# - ldpk_FOUND
# - ldpk_INCLUDE_DIRS
#

function(find_ldpk_find_with_paths
    ldpk_root
    ldpk_include_path
    out_ldpk_dir
    out_ldpk_include_dirs)

    find_path(ldpk_include_dir ldpk/ldpk.h
      HINTS
        ${ldpk_include_path}
        ${ldpk_root}
        /usr/local/include
        /usr/include
      PATH_SUFFIXES
        include/
    )

    find_path(ldpk_dir
      NAMES
        ldpkConfig.cmake
        ldpkConfigVersion.cmake
      HINTS
        ${ldpk_include_path}/../share/ldpk/cmake
        ${ldpk_root}
        /usr/share
        /usr/local/share
    )

    if(ldpk_include_dir AND ldpk_dir)
      set(${out_ldpk_include_dirs} ${ldpk_include_dir} PARENT_SCOPE)
      set(${out_ldpk_dir} ${ldpk_dir} PARENT_SCOPE)
    endif()

endfunction()


function(find_ldpk_create_target)
  add_library(ldpk::ldpk INTERFACE IMPORTED GLOBAL)
endfunction()


function(find_ldpk_set_target ldpk_include_dir)

  set_target_properties(ldpk::ldpk PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES ${ldpk_include_dir}
  )

endfunction()


option(ldpk_ALLOW_DOWNLOAD
  "Allow automatically downloading and building LDPK?" ON)


if(NOT MMSOLVER_DOWNLOAD_DEPENDENCIES OR NOT ldpk_ALLOW_DOWNLOAD)

  if(NOT DEFINED ldpk_ROOT)
    # Search for "ldpk-config.cmake" given on the command line.
    find_package(ldpk ${ldpk_FIND_VERSION} CONFIG QUIET)
  endif()

  if(ldpk_FOUND)
    message(FATAL_ERROR "Not Implemented. ldpk has been found from the ldpk-config.cmake file")
  else()
    # Fallback and try to find the package.
    find_ldpk_find_with_paths(
      ${ldpk_ROOT}
      ${ldpk_INCLUDE_PATH}
      ldpk_DIR
      ldpk_INCLUDE_DIRS
      )
  endif()

  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(ldpk
    REQUIRED_VARS
      ldpk_DIR
      ldpk_INCLUDE_DIRS
  )

  if(ldpk_FOUND)
    message(STATUS "ldpk: Found=${ldpk_FOUND}")
    message(STATUS "ldpk: Config=${ldpk_DIR}")
    message(STATUS "ldpk: Include=${ldpk_INCLUDE_DIRS}")
  endif()

endif()


# Ensure a target for ldpk is created.
if(NOT TARGET ldpk::ldpk)
  find_ldpk_create_target()
  if(ldpk_FOUND)
    find_ldpk_set_target(# ${ldpk_LIBRARY}
      ${ldpk_INCLUDE_DIR})
  else()
    set(_ldpk_TARGET_CREATE TRUE)
  endif()
endif()


# Download, Build and Install.
if(NOT ldpk_FOUND AND MMSOLVER_DOWNLOAD_DEPENDENCIES AND ldpk_ALLOW_DOWNLOAD)
  include(ExternalProject)
  include(GNUInstallDirs)

  set(_EXTERNAL_INSTALL_DIR "${CMAKE_BINARY_DIR}/ext/install")
  set(_EXTERNAL_BUILD_DIR "${CMAKE_BINARY_DIR}/ext/build")

  # Fill in the expected values/paths that will exist when the build
  # and install of ldpk actually happens.
  set(ldpk_FOUND TRUE)
  set(ldpk_VERSION ${ldpk_FIND_VERSION})

  set(ldpk_DIR "${_EXTERNAL_INSTALL_DIR}/ldpk/share/ldpk/cmake")
  set(ldpk_INCLUDE_DIR "${_EXTERNAL_INSTALL_DIR}/ldpk/${CMAKE_INSTALL_INCLUDEDIR}")

  set(ldpk_URL
    "https://www.3dequalizer.com/user_daten/sections/tech_docs/archives/ldpk-${ldpk_VERSION}.tgz"
    CACHE STRING
    "The URL for the ldpk tar-ball.")

  set(ldpk_INSTALL_PATH ${_EXTERNAL_INSTALL_DIR}/ldpk)
  set(ldpk_PREFIX ${_EXTERNAL_BUILD_DIR}/ldpk)
  set(ldpk_SOURCE_DIR ${_EXTERNAL_BUILD_DIR}/ldpk/src/ldpk)

  # Patches
  #
  # ${CMAKE_SOURCE_DIR} is expected to be '$PROJECT_ROOT/lib'.
  set(ldpk_PATCH_DIR ${CMAKE_SOURCE_DIR}/../external/patches/ldpk)
  set(ldpk_PATCH_SRC_1 ${ldpk_PATCH_DIR}/CMakeLists.txt)
  set(ldpk_PATCH_SRC_2 ${ldpk_PATCH_DIR}/ldpk-config.cmake.in)
  set(ldpk_PATCH_DST_1 ${ldpk_SOURCE_DIR}/CMakeLists.txt)
  set(ldpk_PATCH_DST_2 ${ldpk_SOURCE_DIR}/ldpk-config.cmake.in)

  set(ldpk_CMAKE_ARGS
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
    -DCMAKE_INSTALL_PREFIX=${ldpk_INSTALL_PATH}
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

    -DINCLUDE_INSTALL_DIR=${ldpk_INCLUDE_DIR}
  )

  # Hack to let imported target be built from ExternalProject_Add
  file(MAKE_DIRECTORY ${ldpk_INCLUDE_DIR})

  ExternalProject_Add(ldpk
    PREFIX ${ldpk_PREFIX}
    URL "${ldpk_URL}"
    INSTALL_DIR ${ldpk_INSTALL_PATH}
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${ldpk_PATCH_SRC_1} ${ldpk_PATCH_DST_1}
    COMMAND       ${CMAKE_COMMAND} -E copy ${ldpk_PATCH_SRC_2} ${ldpk_PATCH_DST_2}
    BUILD_BYPRODUCTS "${ldpk_INCLUDE_DIR}/ldpk/ldpk_vec2d.h"
    CMAKE_ARGS ${ldpk_CMAKE_ARGS}
    EXCLUDE_FROM_ALL TRUE
    BUILD_COMMAND ""
    INSTALL_COMMAND ${CMAKE_COMMAND} --build . --config ${CMAKE_BUILD_TYPE} --target install --parallel
  )

  add_dependencies(ldpk::ldpk ldpk)
  message(STATUS "Installing ldpk (version \"${ldpk_VERSION}\")")
  message(STATUS "ldpk: Config=${ldpk_DIR}")
  message(STATUS "ldpk: Include=${ldpk_INCLUDE_DIR}")

else()

  # Placeholder target that does nothing.
  add_custom_target(ldpk)

endif()


if(_ldpk_TARGET_CREATE)
  find_ldpk_set_target(${ldpk_INCLUDE_DIR})
  mark_as_advanced(
    ldpk_DIR
    ldpk_INCLUDE_DIR
    ldpk_VERSION
  )
endif()
