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
# - glog finder module
# This module will look for glog, using the predefined variable
# glog_ROOT.
#
# Uses Variables:
# - glog_ROOT_PATH - Directory for the glog install root.
# - glog_INCLUDE_PATH - Directory for the header files.
# - glog_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - glog_FOUND
# - glog_LIBRARIES
# - glog_INCLUDE_DIRS
#

function(find_glog_find_with_paths glog_root glog_include_path glog_lib_path out_glog_include_dirs out_glog_libraries)

    find_path(glog_include_dir glog.h
      HINTS
        ${glog_include_path}
        ${glog_root}
        /usr/local/include
        /usr/include
      PATH_SUFFIXES
        include/
        glog-1/
        include/glog-1/
    )

    find_library(glog_library
      NAMES
        libglog.1
        libglog.so.1
        libglog.1.dylib
        libglog
        libglogd
        glog
        glogd
        libglog_s
        glog_s
      HINTS
        ${glog_lib_path}
        ${glog_root}
        /usr/lib
        /usr/local/lib
      PATH_SUFFIXES
        bin/
        lib/
        lib64/
    )

    if(glog_include_dir AND glog_library)
      set(${out_glog_include_dirs} ${glog_include_dir} PARENT_SCOPE)
      set(${out_glog_libraries} ${glog_library} PARENT_SCOPE)
    endif()

endfunction()


function(find_glog_create_target)
  add_library(glog::glog UNKNOWN IMPORTED GLOBAL)
endfunction()


function(find_glog_set_target glog_library glog_include_dir)

  set_target_properties(glog::glog PROPERTIES
    IMPORTED_LOCATION ${glog_library}
    INTERFACE_INCLUDE_DIRECTORIES ${glog_include_dir}
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    INTERFACE_COMPILE_DEFINITIONS "GLOG_NO_ABBREVIATED_SEVERITIES"
    )

  if (WIN32)
    set_target_properties(glog::glog PROPERTIES
      INTERFACE_LINK_LIBRARIES "dbghelp"
      )
  endif()

endfunction()


option(glog_ALLOW_DOWNLOAD
  "Allow automatically downloading and building Google Log?" ON)


if(NOT MMSOLVER_DOWNLOAD_DEPENDENCIES OR NOT glog_ALLOW_DOWNLOAD)

  if(NOT DEFINED glog_ROOT)
    # Search for "glog-config.cmake" given on the command line.
    find_package(glog ${glog_FIND_VERSION} CONFIG QUIET)
  endif()

  if(glog_FOUND)
    message(STATUS "glog: Found=${glog_FOUND}")
    message(STATUS "glog: Root=${glog_ROOT}")
    message(STATUS "glog: Include=${glog_INCLUDE_DIRS}")
    message(STATUS "glog: Library=${glog_LIBRARIES}")
  else()
    # Fallback to manual search when glog-config.cmake is not found
    find_glog_find_with_paths(
      ${glog_ROOT}
      ${glog_INCLUDE_PATH}
      ${glog_LIB_PATH}
      glog_INCLUDE_DIRS
      glog_LIBRARIES
      )

    if(glog_INCLUDE_DIRS AND glog_LIBRARIES)
      set(glog_FOUND TRUE)
      # Convert to singular form expected by find_glog_set_target
      set(glog_INCLUDE_DIR ${glog_INCLUDE_DIRS})
      set(glog_LIBRARY ${glog_LIBRARIES})
      message(STATUS "glog: Found=${glog_FOUND} (manual search)")
      message(STATUS "glog: Include=${glog_INCLUDE_DIR}")
      message(STATUS "glog: Library=${glog_LIBRARY}")
    endif()
  endif()

endif()


# Ensure a target for glog is created.
if(NOT TARGET glog::glog)
  find_glog_create_target()
  if(glog_FOUND)
    find_glog_set_target(${glog_LIBRARY} ${glog_INCLUDE_DIR})
  else()
    set(_glog_TARGET_CREATE TRUE)
  endif()
endif()


# Download, Build and Install.
if(NOT glog_FOUND AND MMSOLVER_DOWNLOAD_DEPENDENCIES AND glog_ALLOW_DOWNLOAD)
  include(ExternalProject)
  include(GNUInstallDirs)

  set(_EXTERNAL_INSTALL_DIR "${CMAKE_BINARY_DIR}/ext/install")
  set(_EXTERNAL_BUILD_DIR "${CMAKE_BINARY_DIR}/ext/build")

  # Fill in the expected values/paths that will exist when the build
  # and install of glog actually happens.
  set(glog_FOUND TRUE)
  set(glog_VERSION ${glog_FIND_VERSION})

  set(glog_INCLUDE_DIR "${_EXTERNAL_INSTALL_DIR}/glog/${CMAKE_INSTALL_INCLUDEDIR}")
  set(glog_LIBRARY_DIR "${_EXTERNAL_INSTALL_DIR}/glog/${CMAKE_INSTALL_LIBDIR}")

  set(glog_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}glog${CMAKE_STATIC_LIBRARY_SUFFIX}")
  if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(glog_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}glogd${CMAKE_STATIC_LIBRARY_SUFFIX}")
  endif()
  set(glog_LIBRARY "${glog_LIBRARY_DIR}/${glog_LIBRARY_NAME}")

  set(glog_URL
    "https://github.com/google/glog.git"
    CACHE STRING
    "The URL for the glog git repository.")

  set(glog_GIT_TAG "v${glog_VERSION}"
    CACHE STRING
    "The Git Tag for the glog git repository.")

  set(glog_INSTALL_PATH ${_EXTERNAL_INSTALL_DIR}/glog)
  set(glog_PREFIX ${_EXTERNAL_BUILD_DIR}/glog)
  set(glog_SOURCE_DIR ${_EXTERNAL_BUILD_DIR}/glog/src/glog)

  # Find Threads in parent context to get the variables we need
  find_package(Threads REQUIRED)

  set(glog_CMAKE_ARGS
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
    -DCMAKE_INSTALL_PREFIX=${glog_INSTALL_PATH}
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

  # Hack to let imported target be built from ExternalProject_Add
  file(MAKE_DIRECTORY ${glog_INCLUDE_DIR})

  ExternalProject_Add(glog
    PREFIX ${glog_PREFIX}
    GIT_REPOSITORY ${glog_URL}
    GIT_TAG "${glog_GIT_TAG}"
    INSTALL_DIR ${glog_INSTALL_PATH}
    BUILD_BYPRODUCTS ${glog_LIBRARY}
    CMAKE_ARGS ${glog_CMAKE_ARGS}
    EXCLUDE_FROM_ALL TRUE
    BUILD_COMMAND ""
    INSTALL_COMMAND ${CMAKE_COMMAND} --build . --config ${CMAKE_BUILD_TYPE} --target install --parallel
  )

  add_dependencies(glog::glog glog)
  message(STATUS "Installing glog (version \"${glog_VERSION}\")")
  message(STATUS "glog: Include=${glog_INCLUDE_DIR}")
  message(STATUS "glog: Library=${glog_LIBRARY}")

else()

  # Placeholder target that does nothing.
  add_custom_target(glog)

endif()


if(_glog_TARGET_CREATE)
  find_glog_set_target(${glog_LIBRARY} ${glog_INCLUDE_DIR})
  mark_as_advanced(
    glog_INCLUDE_DIR
    glog_LIBRARY
    glog_VERSION
  )
endif()
