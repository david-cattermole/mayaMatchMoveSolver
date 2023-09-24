# Copyright (C) 2023 David Cattermole.
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
# - mmsolverlibs_rust finder module
# This module will look for mmsolverlibs_rust, using the predefined variable
# mmsolverlibs_rust_ROOT.
#
# Uses Variables:
# - mmsolverlibs_rust_ROOT_PATH - Directory for the mmsolverlibs_rust install root.
# - mmsolverlibs_rust_LIBRARY_PATH - Directory for the library files.
#
# Defines Variables:
# - mmsolverlibs_rust_FOUND
# - mmsolverlibs_rust_LIBRARIES
#

include(MMRustUtils)

function(find_mmsolverlibs_rust_find_with_paths
    mmsolverlibs_rust_staticlib_path
    out_mmsolverlibs_rust_libraries)

    set(mmsolverlibs_rust_staticlib_file "NOT-FOUND")
    mm_rust_find_rust_library(
      mmsolverlibs_rust
      ${mmsolverlibs_rust_staticlib_path}
      mmsolverlibs_rust_staticlib_file
    )

    if(mmsolverlibs_rust_staticlib_file)
      set(${out_mmsolverlibs_rust_libraries} ${mmsolverlibs_rust_staticlib_file} PARENT_SCOPE)
    endif()
endfunction()


function(find_mmsolverlibs_rust_create_target)
  add_library(mmsolverlibs_rust::mmsolverlibs_rust STATIC IMPORTED GLOBAL)
endfunction()


function(find_mmsolverlibs_rust_set_target mmsolverlibs_rust_libraries)
  set_target_properties(mmsolverlibs_rust::mmsolverlibs_rust PROPERTIES
    IMPORTED_LOCATION ${mmsolverlibs_rust_libraries}
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    )
endfunction()


find_mmsolverlibs_rust_find_with_paths(
  ${mmsolverlibs_rust_ROOT}
  ${mmsolverlibs_rust_LIBRARY_PATH}
  mmsolverlibs_rust_DIR
  mmsolverlibs_rust_LIBRARIES
  )


include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(mmsolverlibs_rust
  REQUIRED_VARS
  mmsolverlibs_rust_LIBRARIES
  )
message(STATUS "mmsolverlibs_rust: Found=${mmsolverlibs_rust_FOUND}")
message(STATUS "mmsolverlibs_rust: Libraries=${mmsolverlibs_rust_LIBRARIES}")


# Ensure a target for mmsolverlibs_rust is created.
if(NOT TARGET mmsolverlibs_rust::mmsolverlibs_rust)
  find_mmsolverlibs_rust_create_target()
  if(mmsolverlibs_rust_FOUND)
    find_mmsolverlibs_rust_set_target(${mmsolverlibs_rust_LIBRARIES})
  else()
    set(_mmsolverlibs_rust_TARGET_CREATE TRUE)
  endif()
endif()


if(_mmsolverlibs_rust_TARGET_CREATE)
  find_mmsolverlibs_rust_set_target(${mmsolverlibs_rust_LIBRARIES})
  mark_as_advanced(
    mmsolverlibs_rust_LIBRARIES
    mmsolverlibs_rust_VERSION
  )
endif()
