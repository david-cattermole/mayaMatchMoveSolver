# Copyright (C) 2020, 2021, 2022 David Cattermole.
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
# CMake Build script for Science-D-Vision's Lens Distortion Plugin
# Kit.
#
cmake_minimum_required(VERSION 3.0)


# Project configuration.
project(ldpk)
set(PROJECT_VERSION_MAJOR 2)
set(PROJECT_VERSION_MINOR 7)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")
set(PROJECT_HOMEPAGE_URL "https://www.3dequalizer.com/?site=tech_docs")
set(PROJECT_COPYRIGHT "Science-D-Visions, (c) 2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022.")

include(GNUInstallDirs)

# Ensure we can find the installed dlfcn-win32 CMake module, so we can load
# the package.
set(CMAKE_PREFIX_PATH ${CMAKE_MODULE_PATH} ${dlfcn-win32_DIR})

# Base LDPK Plug-in Loader
set(LDPK_BASE_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/ldpk_model_parser.C
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/ldpk_plugin_loader.C
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/ldpk_table_generator.C
  )

# Lens Distortion Plug-ins.
set(TDE4_LDP_ALL_PAR_TYPES_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_all_par_types.C
)

set(TDE4_LDP_ANAMORPHIC_DEG_4_ROTATE_SQUEEZE_XY_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_anamorphic_deg_4_rotate_squeeze_xy.C
)

set(TDE4_LDP_ANAMORPHIC_DEG_4_ROTATE_SQUEEZE_XY_RESCALED_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_anamorphic_deg_4_rotate_squeeze_xy_rescaled.C
)

set(TDE4_LDP_ANAMORPHIC_DEG_6_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_anamorphic_deg_6.C
)

set(TDE4_LDP_CLASSIC_3DE_MIXED_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_classic_3de_mixed.C
)

set(TDE4_LDP_EXAMPLE_RADIAL_DEG_8_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_example_radial_deg_8.C
)

set(TDE4_LDP_NOOP_DEBUGGING_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_noop_debugging.C
)

set(TDE4_LDP_RADIAL_DECENTERED_DEG_4_CYLINDRIC_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_radial_decentered_deg_4_cylindric.C
)

set(TDE4_LDP_RADIAL_DEG_8_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_radial_deg_8.C
)

set(TDE4_LDP_RADIAL_DEG_8_RELEASE_1_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_radial_deg_8_release_1.C
)

# Lens Distortion Plug-ins (EXPERIMENTAL).
set(TDE4_LDP_RADIAL_FISHEYE_EQUIDISTANT_DEG_8_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_radial_fisheye_equidistant_deg_8.experimental.C
)

set(TDE4_LDP_RADIAL_FISHEYE_EQUISOLID_DEG_8_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_radial_fisheye_equisolid_deg_8.experimental.C
)

set(TDE4_LDP_RADIAL_FISHEYE_ORTHOGRAPHIC_DEG_8_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_radial_fisheye_orthographic_deg_8.experimental.C
)

set(TDE4_LDP_RADIAL_FISHEYE_STEREOGRAPHIC_DEG_8_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_radial_fisheye_stereographic_deg_8.experimental.C
)

set(TDE4_LDP_RADIAL_HOMOMORPHIC_DECENTERED_DEG_2_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_ldp_radial_homomorphic_decentered_deg_2.experimental.C
  )

if (MSVC)
    # Ensure the compilier knows we are on MS Windows, so that LDPK
    # does not use pthreads and use native Windows threads instead.
    add_compile_definitions(_WINDOWS)

    # Under Windows we need to include the 'algorithm' header, because
    # we need std::min and std::max.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /FI \"algorithm\"")

    # The file "ldpk_plugin_loader.h" does not include "dlfcn.h" on
    # Windows (for some strange reason) even when it requires it for
    # building. We therefore force the include without wanting to
    # patch the file itself.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /FI \"dlfcn.h\"")
endif ()

# Load 'dlfcn-win32' library on Windows only.
if (WIN32)
  find_package(dlfcn-win32 REQUIRED)
endif ()

# Base LPDK Static library
add_library(ldpk STATIC ${LDPK_BASE_SOURCE_FILES})
target_include_directories(ldpk
  PRIVATE
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include>"
  )
if (WIN32)
  target_link_libraries(ldpk dlfcn-win32::dl)
endif()
install(TARGETS ldpk
  EXPORT ldpk-targets
  RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
  LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  INCLUDES DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
install(EXPORT ldpk-targets
  FILE ldpk-targets.cmake
  NAMESPACE ldpk::
  DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/ldpk"
)

# Install headers
install(DIRECTORY
  ${CMAKE_CURRENT_SOURCE_DIR}/include/
  DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
  FILES_MATCHING PATTERN "*.h"
)

# Correctly export the location of installed includes in the target
target_include_directories(ldpk INTERFACE $<INSTALL_INTERFACE:include>)

# Export the targets to the build tree.
export(EXPORT ldpk-targets
  NAMESPACE ldpk::
  FILE "${CMAKE_CURRENT_BINARY_DIR}/cmake/ldpk-targets.cmake"
)

# Write the CMake config file
set(CMAKE_CONF_INSTALL_DIR "${CMAKE_INSTALL_DATAROOTDIR}/ldpk")
set(INCLUDE_INSTALL_DIR ${CMAKE_INSTALL_INCLUDEDIR})
include(CMakePackageConfigHelpers)
configure_package_config_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/ldpk-config.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/ldpk-config.cmake
  INSTALL_DESTINATION ${CMAKE_CONF_INSTALL_DIR}
  PATH_VARS INCLUDE_INSTALL_DIR
  NO_CHECK_REQUIRED_COMPONENTS_MACRO
)

# Install the targets (install)
install(EXPORT ldpk-targets
        FILE ldpk-targets.cmake
        NAMESPACE ldpk::
        DESTINATION ${CMAKE_CONF_INSTALL_DIR}
)

# Install the CMake config file
install(FILES
  ${CMAKE_CURRENT_BINARY_DIR}/ldpk-config.cmake
  DESTINATION ${CMAKE_CONF_INSTALL_DIR}
)
