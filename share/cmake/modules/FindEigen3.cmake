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
# - Eigen3 finder module
# This module will look for Eigen3, using the predefined variable
# Eigen3_ROOT. Eigen is a header-only library, and therefore does not
# define any libraries.
#
# Uses Variables:
# - Eigen3_ROOT_PATH - Directory for the Eigen install root.
# - Eigen3_INCLUDE_PATH - Directory for the header files.
#
# Defines Variables:
# - Eigen3_FOUND
# - Eigen3_DIR
# - Eigen3_INCLUDE_DIRS
#

function(find_Eigen3_find_with_paths
    Eigen3_root
    Eigen3_include_path
    out_Eigen3_dir
    out_Eigen3_include_dirs)

    find_path(Eigen3_include_dir eigen3/Eigen/src/Core/util/Macros.h
      HINTS
        ${Eigen3_include_path}
        ${Eigen3_root}
        /usr/local/include
        /usr/include
      PATH_SUFFIXES
        include/
    )

    find_path(Eigen3_include_dir eigen3/Eigen/src/Core/util/Macros.h
      HINTS
        ${Eigen3_include_path}
        ${Eigen3_root}
        /usr/local/include
        /usr/include
      PATH_SUFFIXES
        include/
    )

    find_path(Eigen3_dir
      NAMES
        Eigen3Config.cmake
        Eigen3ConfigVersion.cmake
      HINTS
        ${Eigen3_include_path}/../share/eigen3/cmake
        ${Eigen3_root}
        /usr/share
        /usr/local/share
    )

    if(Eigen3_include_dir AND Eigen3_dir)
      set(${out_Eigen3_include_dirs} ${Eigen3_include_dir} PARENT_SCOPE)
      set(${out_Eigen3_dir} ${Eigen3_dir} PARENT_SCOPE)
    endif()

endfunction()


function(find_Eigen3_create_target)
  add_library(Eigen3::Eigen INTERFACE IMPORTED GLOBAL)
endfunction()


function(find_Eigen3_set_target Eigen3_include_dir)

  set_target_properties(Eigen3::Eigen PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES ${Eigen3_include_dir}
    )

endfunction()


option(Eigen3_ALLOW_DOWNLOAD
  "Allow automatically downloading and building EIGEN3?" ON)

# Check for vendored Eigen first
if(NOT Eigen3_FOUND)
  message(STATUS "Looking for vendored Eigen3...")
  find_path(Eigen3_VENDORED_DIR
    NAMES Eigen/Core
    PATHS ${CMAKE_CURRENT_SOURCE_DIR}/lib/thirdparty/eigen
          ${CMAKE_CURRENT_SOURCE_DIR}/../lib/thirdparty/eigen
          ${CMAKE_SOURCE_DIR}/lib/thirdparty/eigen
    NO_DEFAULT_PATH
  )

  if(Eigen3_VENDORED_DIR)
    set(Eigen3_FOUND TRUE)
    set(Eigen3_DIR "${Eigen3_VENDORED_DIR}")
    set(Eigen3_INCLUDE_DIR "${Eigen3_VENDORED_DIR}")
    set(Eigen3_INCLUDE_DIRS "${Eigen3_VENDORED_DIR}")
    set(Eigen3_VERSION "3.4.0")
    message(STATUS "Found vendored Eigen3: ${Eigen3_VENDORED_DIR}")
  endif()
endif()

if(NOT Eigen3_FOUND AND (NOT MMSOLVER_DOWNLOAD_DEPENDENCIES OR NOT Eigen3_ALLOW_DOWNLOAD))

  if(NOT DEFINED Eigen3_ROOT)
    # Search for "Eigen3-config.cmake" given on the command line.
    find_package(Eigen3 ${Eigen3_FIND_VERSION} CONFIG QUIET)
  endif()

  if(Eigen3_FOUND)
    message(FATAL_ERROR "Not Implemented. Eigen has been found from the Eigen3-config.cmake file")
  else()
    # Fallback and try to find the package.
    find_Eigen3_find_with_paths(
      ${Eigen3_ROOT}
      ${Eigen3_INCLUDE_PATH}
      Eigen3_DIR
      Eigen3_INCLUDE_DIRS
      )
  endif()

  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(Eigen3
    REQUIRED_VARS
      Eigen3_DIR
      Eigen3_INCLUDE_DIRS
  )

  if(Eigen3_FOUND)
    message(STATUS "Eigen3: Found=${Eigen3_FOUND}")
    message(STATUS "Eigen3: Config=${Eigen3_DIR}")
    message(STATUS "Eigen3: Include=${Eigen3_INCLUDE_DIRS}")
  endif()

endif()


# Ensure a target for Eigen3 is created.
if(NOT TARGET Eigen3::Eigen)
  find_Eigen3_create_target()
  if(Eigen3_FOUND)
    find_Eigen3_set_target(${Eigen3_INCLUDE_DIR})
  else()
    set(_Eigen3_TARGET_CREATE TRUE)
  endif()
endif()


# Download, Build and Install.
if(NOT Eigen3_FOUND AND MMSOLVER_DOWNLOAD_DEPENDENCIES AND Eigen3_ALLOW_DOWNLOAD)
  include(ExternalProject)
  include(GNUInstallDirs)

  set(_EXTERNAL_INSTALL_DIR "${CMAKE_BINARY_DIR}/ext/install")
  set(_EXTERNAL_BUILD_DIR "${CMAKE_BINARY_DIR}/ext/build")

  # Fill in the expected values/paths that will exist when the build
  # and install of Eigen3 actually happens.
  set(Eigen3_FOUND TRUE)
  set(Eigen3_VERSION ${Eigen3_FIND_VERSION})

  set(Eigen3_DIR "${_EXTERNAL_INSTALL_DIR}/Eigen3/share/eigen3/cmake")
  set(Eigen3_INCLUDE_DIR "${_EXTERNAL_INSTALL_DIR}/Eigen3/${CMAKE_INSTALL_INCLUDEDIR}/eigen3")

  set(Eigen3_URL
    "https://gitlab.com/libeigen/eigen.git"
    CACHE STRING
    "The URL for the Eigen3 git repository.")

  set(Eigen3_GIT_TAG "${Eigen3_VERSION}"
    CACHE STRING
    "The Git Tag for the Eigen3 git repository.")

  set(Eigen3_INSTALL_PATH ${_EXTERNAL_INSTALL_DIR}/Eigen3)
  set(Eigen3_PREFIX ${_EXTERNAL_BUILD_DIR}/Eigen3)
  set(Eigen3_SOURCE_DIR ${_EXTERNAL_BUILD_DIR}/Eigen3/src/Eigen3)

  set(Eigen3_CMAKE_ARGS
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
    -DCMAKE_INSTALL_PREFIX=${Eigen3_INSTALL_PATH}
    -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
    -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
    -DCMAKE_POSITION_INDEPENDENT_CODE=${CMAKE_POSITION_INDEPENDENT_CODE}
    -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
    -DCMAKE_CXX_EXTENSIONS=${CXX_EXTENSIONS}
    -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}

    -DINCLUDE_INSTALL_DIR=${Eigen3_INCLUDE_DIR}
  )

  # Hack to let imported target be built from ExternalProject_Add
  file(MAKE_DIRECTORY ${Eigen3_INCLUDE_DIR})

  ExternalProject_Add(Eigen3
    PREFIX ${Eigen3_PREFIX}
    GIT_REPOSITORY ${Eigen3_URL}
    GIT_TAG ${Eigen3_GIT_TAG}
    INSTALL_DIR ${Eigen3_INSTALL_PATH}
    BUILD_BYPRODUCTS ${Eigen3_INCLUDE_DIR}
    CMAKE_ARGS ${Eigen3_CMAKE_ARGS}
    EXCLUDE_FROM_ALL TRUE
    BUILD_COMMAND ""
    INSTALL_COMMAND ${CMAKE_COMMAND} --build . --config ${CMAKE_BUILD_TYPE} --target install --parallel
  )

  add_dependencies(Eigen3::Eigen Eigen3)
  message(STATUS "Installing Eigen3 (version \"${Eigen3_VERSION}\")")
  message(STATUS "Eigen3: Config=${Eigen3_DIR}")
  message(STATUS "Eigen3: Include=${Eigen3_INCLUDE_DIR}")

else()

  # Placeholder target that does nothing.
  if(NOT TARGET Eigen3)
    add_custom_target(Eigen3)
  endif()

endif()


if(_Eigen3_TARGET_CREATE)
  find_Eigen3_set_target(${Eigen3_INCLUDE_DIR})
  mark_as_advanced(
    Eigen3_DIR
    Eigen3_INCLUDE_DIR
    Eigen3_VERSION
  )
endif()
