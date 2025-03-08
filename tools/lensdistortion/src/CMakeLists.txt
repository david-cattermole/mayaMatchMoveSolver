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

include(MMSolverUtils)

set(lensdistortion_exe_name "mmsolver-lensdistortion")

set(source_files
  ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
)

# Add test executable using the C++ bindings.
add_executable(${lensdistortion_exe_name} ${source_files})

# MM Solver standalone libraries.
find_package(mmsolverlibs_cpp REQUIRED)
find_package(mmsolverlibs_rust REQUIRED)

target_link_libraries(${lensdistortion_exe_name}
  # The order of these libraries matters. See similar
  # 'target_link_libraries()' in '${PROJECT_ROOT}/src/CMakeLists.txt'.
  PUBLIC mmsolverlibs_rust::mmsolverlibs_rust
  PUBLIC mmsolverlibs_cpp::mmsolverlibs_cpp

  PRIVATE ${rust_depend_on_libraries}
)

# MM Color IO dependencies
include(MMColorIOUtils)
mmcolorio_find_packages()
mmcolorio_target_link_packages(${lensdistortion_exe_name})

target_include_directories(${lensdistortion_exe_name}
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
)

install_target_executable_to_module(${lensdistortion_exe_name} "${MODULE_FULL_NAME}")
