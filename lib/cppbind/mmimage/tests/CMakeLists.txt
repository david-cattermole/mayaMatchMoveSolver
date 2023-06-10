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

# Static build information.
set(target_test_exe_name "mmimage_tests")

set(test_source_files
  ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_a.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_b.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/test_c.cpp
)

# Add test executable using the C++ bindings.
message(STATUS "target_test_exe_name: ${target_test_exe_name}")
message(STATUS "test_source_files: ${test_source_files}")
message(STATUS "target_release_lib_name: ${target_release_lib_name}")
add_executable(${target_test_exe_name} ${test_source_files})
target_link_libraries(${target_test_exe_name} ${target_release_lib_name})
target_include_directories(${target_test_exe_name}
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/../include
  PUBLIC ${RUST_INCLUDE_DIR}
)

install(TARGETS ${target_test_exe_name})
