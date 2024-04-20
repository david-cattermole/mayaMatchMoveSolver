# Copyright (C) 2020, 2021, 2023 David Cattermole.
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
function(mm_rust_find_rust_library lib_name lib_dir out_linktime_file)
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


# Generate CXX Bridge files.
macro(mm_rust_generate_cxx_bridge_files_with_dirs name source_dir include_dir cpp_api_export_macro_name cxxbridge_exec)
  if(NOT EXISTS "${cxxbridge_exec}")
    message(STATUS "Finding cxxbridge executable...")
    find_program(cxxbridge_exec cxxbridge REQUIRED PATHS $ENV{HOME}/.cargo/bin)
  endif()

  message(STATUS "${name} using cxxbridge executable: ${cxxbridge_exec}")
  set(cxxbridge_in ${source_dir}/cxxbridge.rs)
  set(cxxbridge_source_out ${source_dir}/_cxxbridge.cpp)
  set(cxxbridge_bridge_header_out ${include_dir}/${name}/_cxxbridge.h)
  set(cxxbridge_cxx_header_out ${include_dir}/${name}/_cxx.h)
  set(cxxbridge_args "--cxx-impl-annotations" ${cpp_api_export_macro_name})

  add_custom_command(
    OUTPUT ${cxxbridge_source_out} ${cxxbridge_bridge_header_out}
    COMMAND ${cxxbridge_exec} --header --output ${cxxbridge_cxx_header_out}
    COMMAND ${cxxbridge_exec} ${cxxbridge_in} ${cxxbridge_args} --header --output ${cxxbridge_bridge_header_out}
    COMMAND ${cxxbridge_exec} ${cxxbridge_in} ${cxxbridge_args} --output ${cxxbridge_source_out}
    COMMENT "Generating CXX Bridge: ${cxxbridge_cxx_header_out} ${cxxbridge_bridge_header_out} ${cxxbridge_source_out}"
    DEPENDS ${cxxbridge_in})
endmacro()


function(mm_rust_get_depend_on_libraries depend_on_libraries)
  # NOTE: PARENT_SCOPE is used to set the variable in the "scope"
  # (function) that called this function.
  # https://cmake.org/cmake/help/latest/command/set.html#set-normal-variable
  if (MSVC)
    set(${depend_on_libraries}
      ws2_32 userenv advapi32 shell32 msvcrt Bcrypt Ntdll
      PARENT_SCOPE
    )
  elseif (UNIX)
    set(${depend_on_libraries}
      pthread m dl
      PARENT_SCOPE
    )
  endif ()
endfunction()
