# Copyright (C) 2020 David Cattermole.
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
# CMake utilities for mmSolver.
#

function(add_target_link_library_names target names)
    string(STRIP ${names} names_strip)
    string(REPLACE " " ";" names_list ${names_strip})
    foreach (name IN LISTS names_list)
        target_link_libraries(${target} ${name})
    endforeach ()
endfunction()


# Install shared (dynamic) library.
function(install_library lib_file lib_file_dll install_dir)
  # message(STATUS "INSTALL FILE: ${lib_file}")
  # message(STATUS "INSTALL DLL: ${lib_file_dll}")
  # message(STATUS "INSTALL DIR: ${install_dir}")
  if (WIN32)
    if (EXISTS ${lib_file_dll})
      install(FILES ${lib_file_dll}
        DESTINATION ${install_dir})
    else ()
      message(FATAL_ERROR "Cannot find .dll file to install: ${lib_file_dll}")
    endif ()
  elseif (UNIX)
    # Install both symlink and real library
    get_filename_component(absolute_lib_file ${lib_file} REALPATH)
    install(FILES ${lib_file} DESTINATION ${install_dir})
    install(FILES ${absolute_lib_file} DESTINATION ${install_dir})
  endif ()
endfunction()


# Install many shared (dynamic) libraries.
function(install_libraries lib_files lib_files_dll install_dir)
  # message(STATUS "INSTALL FILES: ${lib_files}")
  # message(STATUS "INSTALL DLLS: ${lib_files_dll}")
  # message(STATUS "INSTALL DIR: ${install_dir}")

  string(STRIP "${lib_files}" lib_files_strip)
  string(STRIP "${lib_files_dll}" lib_files_dll_strip)

  string(REPLACE " " ";" lib_files_list "${lib_files_strip}")
  string(REPLACE " " ";" lib_files_dll_list "${lib_files_dll_strip}")

  list(LENGTH lib_files_list len1)
  math(EXPR len2 "${len1} - 1")

  foreach(val RANGE ${len2})
    list(GET lib_files_list ${val} lib_file)
    list(GET lib_files_dll_list ${val} lib_file_dll)

    install_library(
      ${lib_file}
      ${lib_file_dll}
      ${install_dir})
  endforeach ()
endfunction()
