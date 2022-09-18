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
# - dlfcn-win32 finder module
# This module will look for dlfcn-win32, using the predefined variable
# dlfcn-win32_ROOT.
#
# Uses Variables:
# - dlfcn-win32_ROOT_PATH - Directory for the dlfcn-win32 install root.
# - dlfcn-win32_INCLUDE_PATH - Directory for the header files.
# - dlfcn-win32_LIB_PATH - Directory for shared libraries (.so and .dll).
# - dlfcn-win32_IMPLIB_PATH - Directory for shared libraries (.lib).
#
# Defines Variables:
# - dlfcn-win32_FOUND
# - dlfcn-win32_DIR
# - dlfcn-win32_LIBRARIES
# - dlfcn-win32_LIBRARIES_DLL
# - dlfcn-win32_INCLUDE_DIRS
#

function(find_dlfcn_win32_find_with_paths dlfcn-win32_root dlfcn-win32_include_path dlfcn-win32_implib_path dlfcn-win32_lib_path)

    find_path(dlfcn-win32_dir dlfcn-win32-config.cmake
      HINTS
        ${dlfcn-win32_lib_path}/../share/dlfcn-win32/
        ${dlfcn-win32_root}
    )

    find_path(dlfcn-win32_include_dir dlfcn-win32.h
      HINTS
        ${dlfcn-win32_include_path}
        ${dlfcn-win32_root}
      PATH_SUFFIXES
        include/
    )

    find_path(dlfcn-win32_library_dir dl.dll
      HINTS
        ${dlfcn-win32_lib_path}
        ${dlfcn-win32_root}
    )

    find_path(dlfcn-win32_implib_dir dl.lib
      HINTS
        ${dlfcn-win32_implib_path}
        ${dlfcn-win32_root}
    )

  if(dlfcn-win32_dir AND dlfcn-win32_include_dir AND dlfcn-win32_library AND dlfcn-win32_implib_dir)
    set(${out_dlfcn-win32_dir} ${dlfcn-win32_dir} PARENT_SCOPE)
    set(${out_dlfcn-win32_include_dirs} ${dlfcn-win32_include_dir} PARENT_SCOPE)
    set(${out_dlfcn-win32_libraries} "${dlfcn-win32_implib_dir}/dl.lib" PARENT_SCOPE)
    set(${out_dlfcn-win32_libraries_dll} "${dlfcn-win32_library_dir}/dl.dll" PARENT_SCOPE)
  endif()

endfunction()


function(find_dlfcn_win32_create_target)
  add_library(dlfcn-win32::dl SHARED IMPORTED GLOBAL)
endfunction()


function(find_dlfcn_win32_set_target dlfcn-win32_library dlfcn-win32_library_dll dlfcn-win32_include_dir)

  if (NOT WIN32)
    message(FATAL_ERROR "dlfcn-win32 is only used on Microsoft Windows.")
  endif ()

  set_target_properties(dlfcn-win32::dl PROPERTIES
    IMPORTED_IMPLIB "${dlfcn-win32_library}"
    IMPORTED_LOCATION "${dlfcn-win32_library_dll}"
    IMPORTED_LINK_INTERFACE_LANGUAGES "C"
    INTERFACE_INCLUDE_DIRECTORIES ${dlfcn-win32_include_dir}
    )

endfunction()


if(NOT MMSOLVER_DOWNLOAD_DEPENDENCIES)

  if(NOT DEFINED dlfcn-win32_ROOT)
    # Search for "dlfcn-win32-config.cmake" given on the command line.
    find_package(dlfcn-win32 ${dlfcn-win32_FIND_VERSION} CONFIG QUIET)
  endif()

  if(dlfcn-win32_FOUND)
    message(FATAL_ERROR "Not Implemented. dlfcn-win32 has been found from the dlfcn-win32-config.cmake file")
  else()
    # Fallback and try to find the package.
    find_dlfcn_win32_find_with_paths(
      ${dlfcn-win32_ROOT}
      ${dlfcn-win32_INCLUDE_PATH}
      ${dlfcn-win32_IMPLIB_PATH}
      ${dlfcn-win32_LIB_PATH}
      dlfcn-win32_INCLUDE_DIRS
      dlfcn-win32_LIBRARIES
      dlfcn-win32_LIBRARIES_DLL
      )
  endif()

  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(dlfcn-win32
    REQUIRED_VARS
      dlfcn-win32_LIBRARIES
      dlfcn-win32_INCLUDE_DIRS
  )

  if(dlfcn-win32_FOUND)
    message(STATUS "dlfcn-win32: Found=${dlfcn-win32_FOUND}")
    message(STATUS "dlfcn-win32: Config=${dlfcn-win32_DIR}")
    message(STATUS "dlfcn-win32: Include=${dlfcn-win32_INCLUDE_DIRS}")
    message(STATUS "dlfcn-win32: Library=${dlfcn-win32_LIBRARIES}")
    message(STATUS "dlfcn-win32: Library DLL=${dlfcn-win32_LIBRARIES_DLL}")
  endif()

endif()


# Ensure a target for dlfcn-win32 is created.
if(NOT TARGET dlfcn-win32::dl)
  find_dlfcn_win32_create_target()
  if(dlfcn-win32_FOUND)
    find_dlfcn_win32_set_target(${dlfcn-win32_LIBRARY} ${dlfcn-win32_LIBRARY_DLL} ${dlfcn-win32_INCLUDE_DIR})
  else()
    set(_dlfcn-win32_TARGET_CREATE TRUE)
  endif()
endif()


# Download, Build and Install.
if(NOT dlfcn-win32_FOUND AND MMSOLVER_DOWNLOAD_DEPENDENCIES)
  include(ExternalProject)
  include(GNUInstallDirs)

  set(_EXTERNAL_INSTALL_DIR "${CMAKE_BINARY_DIR}/ext/install")
  set(_EXTERNAL_BUILD_DIR "${CMAKE_BINARY_DIR}/ext/build")

  # Fill in the expected values/paths that will exist when the build
  # and install of dlfcn-win32 actually happens.
  set(dlfcn-win32_FOUND TRUE)
  set(dlfcn-win32_VERSION ${dlfcn-win32_FIND_VERSION})

  set(dlfcn-win32_INCLUDE_DIR "${_EXTERNAL_INSTALL_DIR}/dlfcn-win32/${CMAKE_INSTALL_INCLUDEDIR}")
  set(dlfcn-win32_IMPL_LIBRARY_DIR "${_EXTERNAL_INSTALL_DIR}/dlfcn-win32/${CMAKE_INSTALL_LIBDIR}")
  set(dlfcn-win32_RUNTIME_DIR "${_EXTERNAL_INSTALL_DIR}/dlfcn-win32/${CMAKE_INSTALL_BINDIR}")
  set(dlfcn-win32_DIR "${_EXTERNAL_INSTALL_DIR}/dlfcn-win32/share/dlfcn-win32")

  set(dlfcn-win32_LIBRARY_DLL_NAME "${CMAKE_SHARED_LIBRARY_PREFIX}dl${CMAKE_SHARED_LIBRARY_SUFFIX}")
  set(dlfcn-win32_LIBRARY_DLL "${dlfcn-win32_RUNTIME_DIR}/${dlfcn-win32_LIBRARY_DLL_NAME}")
  set(dlfcn-win32_LIBRARIES_DLL "${dlfcn-win32_LIBRARY_DLL}")

  set(dlfcn-win32_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}dl${CMAKE_STATIC_LIBRARY_SUFFIX}")
  set(dlfcn-win32_LIBRARY "${dlfcn-win32_IMPL_LIBRARY_DIR}/${dlfcn-win32_LIBRARY_NAME}")
  set(dlfcn-win32_LIBRARIES "${dlfcn-win32_LIBRARY}")

  set(dlfcn-win32_URL "https://github.com/dlfcn-win32/dlfcn-win32.git")

  set(dlfcn-win32_INSTALL_PATH ${_EXTERNAL_INSTALL_DIR}/dlfcn-win32)
  set(dlfcn-win32_PREFIX ${_EXTERNAL_BUILD_DIR}/dlfcn-win32)
  set(dlfcn-win32_SOURCE_DIR ${_EXTERNAL_BUILD_DIR}/dlfcn-win32/src/dlfcn-win32)

  set(dlfcn-win32_CMAKE_ARGS
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
    -DCMAKE_INSTALL_PREFIX=${dlfcn-win32_INSTALL_PATH}
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

    # This package must be shared to work.
    -DBUILD_SHARED_LIBS=1
    -DBUILD_TESTS=0
  )

  # Hack to let imported target be built from ExternalProject_Add
  file(MAKE_DIRECTORY ${dlfcn-win32_INCLUDE_DIR})

  ExternalProject_Add(dlfcn-win32
    PREFIX ${dlfcn-win32_PREFIX}
    GIT_REPOSITORY ${dlfcn-win32_URL}
    GIT_TAG "v${dlfcn-win32_VERSION}"
    INSTALL_DIR ${dlfcn-win32_INSTALL_PATH}
    BUILD_BYPRODUCTS ${dlfcn-win32_LIBRARIES} ${dlfcn-win32_LIBRARIES_DLL}
    CMAKE_ARGS ${dlfcn-win32_CMAKE_ARGS}
    EXCLUDE_FROM_ALL TRUE
    BUILD_COMMAND ""
    INSTALL_COMMAND ${CMAKE_COMMAND} --build . --config ${CMAKE_BUILD_TYPE} --target install --parallel
  )

  add_dependencies(dlfcn-win32::dl dlfcn-win32)
  message(STATUS "Installing dlfcn-win32 (version \"${dlfcn-win32_VERSION}\")")
  message(STATUS "dlfcn-win32: Config=${dlfcn-win32_DIR}")
  message(STATUS "dlfcn-win32: Include=${dlfcn-win32_INCLUDE_DIR}")
  message(STATUS "dlfcn-win32: Library=${dlfcn-win32_LIBRARY}")
  message(STATUS "dlfcn-win32: Library DLL=${dlfcn-win32_LIBRARY_DLL}")

else()

  # Placeholder target that does nothing.
  add_custom_target(dlfcn-win32)

endif()


if(_dlfcn-win32_TARGET_CREATE)
  find_dlfcn_win32_set_target(${dlfcn-win32_LIBRARY} ${dlfcn-win32_LIBRARY_DLL} ${dlfcn-win32_INCLUDE_DIR})
  mark_as_advanced(
    dlfcn-win32_INCLUDE_DIR
    dlfcn-win32_LIBRARY
    dlfcn-win32_LIBRARY_DLL
    dlfcn-win32_VERSION
  )
endif()
