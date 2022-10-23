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

# Expected inputs.
set(MMSCENEGRAPH_LIB_DIR "/path/to/rust/build/directory/" CACHE PATH
  "The path to the directory containing the compiled library.")
set(MMSCENEGRAPH_INCLUDE_DIR "/path/to/rust/include/directory/" CACHE PATH
  "The path to the generated include headers.")
set(MMSCENEGRAPH_CXXBRIDGE_EXE "/path/to/cxxbridge/executable/cxxbridge" CACHE PATH
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

# Find the Rust Library
include(MMSceneGraphUtils)
set(rust_linktime_file "NOT-FOUND")
find_rust_library("mmscenegraph" ${MMSCENEGRAPH_LIB_DIR} rust_linktime_file)
message(STATUS "Rust Linktime Library: ${rust_linktime_file}")
if(NOT EXISTS "${rust_linktime_file}")
    message(FATAL_ERROR "mmscenegraph rust linktime library was not found.")
endif()

# Generate CXX Bridge files.
set(cxxbridge_exec ${MMSCENEGRAPH_CXXBRIDGE_EXE})
if(NOT EXISTS "${MMSCENEGRAPH_CXXBRIDGE_EXE}")
  message(STATUS "Finding cxxbridge executable...")
  find_program(cxxbridge_exec cxxbridge REQUIRED PATHS $ENV{HOME}/.cargo/bin)
endif()
message(STATUS "Using cxxbridge executable: ${cxxbridge_exec}")
set(cxxbridge_in ${CMAKE_CURRENT_SOURCE_DIR}/cxxbridge.rs)
set(cxxbridge_source_out ${CMAKE_CURRENT_SOURCE_DIR}/_cxxbridge.cpp)
set(cxxbridge_header_out ${CMAKE_CURRENT_SOURCE_DIR}/../include/mmscenegraph/_cxxbridge.h)
set(cxxbridge_args "--cxx-impl-annotations" "MMSCENEGRAPH_API_EXPORT")
add_custom_command(
  OUTPUT ${cxxbridge_source_out} ${cxxbridge_header_out}
  COMMAND ${cxxbridge_exec} ${cxxbridge_in} ${cxxbridge_args} --header --output ${cxxbridge_header_out}
  COMMAND ${cxxbridge_exec} ${cxxbridge_in} ${cxxbridge_args} --output ${cxxbridge_source_out}
  COMMENT "Generating CXX Bridge: ${cxxbridge_header_out} ${cxxbridge_source_out}"
  DEPENDS ${cxxbridge_in})

if (MSVC)
  set(depend_on_libraries
    ws2_32 userenv advapi32 shell32 msvcrt Bcrypt
    )
elseif (UNIX)
  set(depend_on_libraries
    pthread m dl
    )
endif ()

# Add 'mmscenegraph' library as a C++ wrapper around the Rust library.
add_library(${target_release_lib_name}
  ${lib_source_files})
target_link_libraries(${target_release_lib_name}
  ${depend_on_libraries}
  ${rust_linktime_file}
  )
target_include_directories(${target_release_lib_name}
  INTERFACE
  PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../include>
  PRIVATE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
  PUBLIC $<INSTALL_INTERFACE:include/>
  )

include(GNUInstallDirs)
install(TARGETS ${target_release_lib_name}
  EXPORT mmscenegraphTargets
  )
