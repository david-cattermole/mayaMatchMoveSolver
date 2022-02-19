# Copyright (C) 2020, 2021 David Cattermole.
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
# CMake utilities for mmSolver using Rust.
#


# Find the Rust compiled library
function(find_rust_library lib_name lib_dir out_linktime_file)
  if (MSVC)
    set(staticlib_name "${lib_name}.lib")

    # Get the Rust Library .lib (for Windows).
    message(STATUS "Finding: ${staticlib_name} in ${lib_dir}")
    find_path(linktime_dir ${staticlib_name}
      HINTS ${lib_dir}
      PATHS ${lib_dir}
      )
    if(EXISTS ${linktime_dir})
      set(${out_linktime_file} ${linktime_dir}/${staticlib_name} PARENT_SCOPE)
    endif()

  elseif (UNIX)
    set(archive_name "lib${lib_name}.a")

    # Get the Rust Library .a (for Linux).
    message(STATUS "Finding: ${archive_name} in ${lib_dir}")
    find_path(linktime_dir ${archive_name}
      HINTS ${lib_dir}
      PATHS ${lib_dir}
      )
    if(EXISTS ${linktime_dir})
      set(${out_linktime_file} ${linktime_dir}/${archive_name} PARENT_SCOPE)
    endif()

  else ()
    message(FATAL_ERROR "Only Linux and Windows are supported.")
  endif ()
endfunction()


macro(set_relative_library_rpath target relative_path)
  # HACK: We must change the RPATH variable for the library so that a
  # binary can find the shared object, even if it's not in the
  # $LD_LIBRARY_PATH.
  if (UNIX)
    # We must escape the '$' symbol to make sure it is passed to the
    # compiler.
    set_target_properties(${target} PROPERTIES
      BUILD_WITH_INSTALL_RPATH ON
      INSTALL_RPATH "\$ORIGIN/${relative_path}"
      )
  endif ()
endmacro()


macro(set_rpath_to_cwd target)
# HACK: We must change the RPATH variable for the library so that a
# binary can find the shared object, even if it's not in the
# $LD_LIBRARY_PATH.
if (UNIX)
 # We must escape the '$' symbol to make sure it is passed to the
 # compiler.
 set_target_properties(${target} PROPERTIES
   BUILD_WITH_INSTALL_RPATH ON
   INSTALL_RPATH "\$ORIGIN/."
   )
endif ()
endmacro()


function(add_target_link_library_names target names)
    string(STRIP ${names} names_strip)
    string(REPLACE " " ";" names_list ${names_strip})
    foreach (name IN LISTS names_list)
        target_link_libraries(${target} ${name})
    endforeach ()
endfunction()
