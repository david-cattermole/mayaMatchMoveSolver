# Copyright (C) 2022, 2023 David Cattermole.
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

# Expected inputs.
set(MM_LIBRARY_LIB_DIR "/path/to/rust/build/directory/" CACHE PATH
  "The path to the directory containing the compiled library.")
set(MM_LIBRARY_INCLUDE_DIR "/path/to/rust/include/directory/" CACHE PATH
  "The path to the generated include headers.")
set(MM_LIBRARY_CXXBRIDGE_EXE "/path/to/cxxbridge/executable/cxxbridge" CACHE PATH
  "The path to the cxxbridge executable file.")

# C++ Source Code
set(lib_source_files
  ${CMAKE_CURRENT_SOURCE_DIR}/_cxxbridge.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/attrdatablock.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/flatscene.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/line.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/scenebake.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/scenegraph.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/evaluationobjects.cpp
  )

include(MMRustUtils)

set(rust_linktime_file "NOT-FOUND")
mm_rust_find_rust_library("mmscenegraph" ${MM_LIBRARY_LIB_DIR} rust_linktime_file)
message(STATUS "Rust Linktime Library: ${rust_linktime_file}")
if(NOT EXISTS "${rust_linktime_file}")
    message(FATAL_ERROR "mmscenegraph rust linktime library was not found.")
endif()

mm_rust_generate_cxx_bridge_files("mmscenegraph" "MMSCENEGRAPH_API_EXPORT" ${MM_LIBRARY_CXXBRIDGE_EXE})

mm_rust_get_depend_on_libraries(depend_on_libraries)

# Add 'mmscenegraph' library as a C++ wrapper around the Rust library.
mm_rust_add_target_library(${target_release_lib_name}
  "${lib_source_files}" "${depend_on_libraries}" ${rust_linktime_file})
mm_rust_install_target_library("mmscenegraph" ${target_release_lib_name})
