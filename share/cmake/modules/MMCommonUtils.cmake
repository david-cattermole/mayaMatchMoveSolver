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
# CMake utilities for mmSolver.
#

macro(mm_common_set_relative_library_rpath target relative_path)
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


macro(mm_common_set_rpath_to_cwd target)
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


function(mm_common_add_target_link_library_names target names)
  string(STRIP ${names} names_strip)
  string(REPLACE " " ";" names_list ${names_strip})
  foreach (name IN LISTS names_list)
    target_link_libraries(${target} ${name})
  endforeach ()
endfunction()


macro(mm_common_install_target_library target_name target_release_lib_name)
  include(GNUInstallDirs)
  install(TARGETS ${target_release_lib_name}
    EXPORT ${target_name}Targets
  )
endmacro()


function(mm_common_add_install_target target_name cmake_config_template_file)
  include(GNUInstallDirs)

  # Generate CMake Targets file.
  install(EXPORT ${target_name}Targets
    FILE ${target_name}Targets.cmake
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${target_name}"
    NAMESPACE ${target_name}::
  )

  # Generate and install a CMake target config files.
  include(CMakePackageConfigHelpers)
  configure_package_config_file(${cmake_config_template_file}
    "${CMAKE_CURRENT_BINARY_DIR}/${target_name}Config.cmake"
    INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${target_name}"
  )
  write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/${target_name}ConfigVersion.cmake"
    VERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    COMPATIBILITY AnyNewerVersion
  )
  install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/${target_name}Config.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/${target_name}ConfigVersion.cmake"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${target_name}")
  export(EXPORT ${target_name}Targets
    FILE "${CMAKE_INSTALL_LIBDIR}/${target_name}Targets.cmake"
  )
endfunction()
