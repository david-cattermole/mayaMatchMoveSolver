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


# Use vendored cminpack from lib/thirdparty/cminpack. The vendored
# cminpack is built as part of the main build process.
set(cminpack_FOUND TRUE)
set(cminpack_VERSION ${cminpack_FIND_VERSION})
message(STATUS "Using vendored cminpack (version \"${cminpack_VERSION}\")")

# Placeholder target that does nothing since vendored cminpack is
# built as part of the main build process.
if(NOT TARGET cminpack)
  add_custom_target(cminpack)
endif()

# Note: The target cminpack::cminpack is created automatically by the
# vendored CMakeLists.txt in lib/thirdparty/cminpack, so no additional
# target creation is needed here.
