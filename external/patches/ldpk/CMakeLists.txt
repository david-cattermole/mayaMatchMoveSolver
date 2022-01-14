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
# CMake Build script for Science-D-Vision's Lens Distortion Plugin
# Kit.
#
cmake_minimum_required(VERSION 3.0)


# Project configuration.
project(ldpk)
set(PROJECT_VERSION_MAJOR 2)
set(PROJECT_VERSION_MINOR 4)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")
set(PROJECT_HOMEPAGE_URL "https://www.3dequalizer.com/?site=tech_docs")
set(PROJECT_COPYRIGHT "Science-D-Visions, (c) 2011,2012,2013,2014,2015,2016,2017,2018,2019,2020.")

# if (WIN32)
#   set(PYTHON_INCLUDE_DIR "C:/Python27/include")
#   set(PYTHON_LIB_DIR "C:/Python27/libs")
# else ()
#   set(PYTHON_INCLUDE_DIR "/usr/include/python2.7")
#   set(PYTHON_LIB_DIR "/usr/lib/python2.7")  # TODO: Test on Linux.
# endif ()

# Ensure we can find the installed dlfcn CMake module, so we can load
# the package.
set(CMAKE_PREFIX_PATH ${CMAKE_MODULE_PATH} ${DLFCN_LOCATION}/share)

# Base LDPK Plug-in Loader
set(LDPK_BASE_SOURCE_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/ldpk_model_parser.C
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/ldpk_plugin_loader.C
  ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/ldpk_table_generator.C
  )

# # Python Module
# set(LDPK_PYTHON_BINDINGS_SOURCE_FILES
#   ${CMAKE_CURRENT_SOURCE_DIR}/source/ldpk/tde4_lens_distortion_plugins.module.C
# )

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
    # Under Windows we need to include the 'algorithm' header, because
    # we need std::min and std::max.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /FI \"algorithm\"")

    # The file "ldpk_plugin_loader.h" does not include "dlfcn.h" on
    # Windows (for some strange reason) even when it requires it for
    # building. We therefore force the include without wanting to
    # patch the file itself.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /FI \"dlfcn.h\"")
endif ()

# Load 'dlfcn' library on Windows only.
if (WIN32)
  find_package(dlfcn-win32 REQUIRED)
endif ()

# Base LPDK Static library
add_library(ldpk STATIC ${LDPK_BASE_SOURCE_FILES})
target_include_directories(ldpk
  PRIVATE
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include>"
  # PUBLIC ${dlfcn-win32_INCLUDE_DIRS}
  )
target_link_libraries(ldpk dlfcn-win32::dl)
install(TARGETS ldpk
  EXPORT ldpk-targets
  RUNTIME DESTINATION "${CMAKE_INSTALL_PREFIX}/bin"
  LIBRARY DESTINATION "${CMAKE_INSTALL_PREFIX}/lib"
  ARCHIVE DESTINATION "${CMAKE_INSTALL_PREFIX}/lib"
  INCLUDES DESTINATION "${CMAKE_INSTALL_PREFIX}/include"
  )
install(EXPORT ldpk-targets
  FILE ldpk-targets.cmake
  NAMESPACE ldpk::
  DESTINATION lib/cmake/ldpk
  )

# # Model "3DE Classic LD Model"
# add_library(tde4_ldp_classic_3de_mixed SHARED
#   ${TDE4_LDP_CLASSIC_3DE_MIXED_SOURCE_FILES})
# target_compile_definitions(tde4_ldp_classic_3de_mixed
#   PRIVATE -DLDPK_COMPILE_AS_PLUGIN_SDV)
# # no 'lib' prefix for .so files.
# set_target_properties(tde4_ldp_classic_3de_mixed PROPERTIES PREFIX "")
# target_include_directories(tde4_ldp_classic_3de_mixed
#   PRIVATE include
#   # PUBLIC ${dlfcn-win32_INCLUDE_DIRS}
#   )
# target_link_libraries(tde4_ldp_classic_3de_mixed dlfcn-win32::dl)
# install(TARGETS tde4_ldp_classic_3de_mixed
#   RUNTIME DESTINATION "${CMAKE_INSTALL_PREFIX}/bin"
#   LIBRARY DESTINATION "${CMAKE_INSTALL_PREFIX}/lib"
#   ARCHIVE DESTINATION "${CMAKE_INSTALL_PREFIX}/lib"
#   INCLUDES DESTINATION "${CMAKE_INSTALL_PREFIX}/include"
#   )


# Install headers
install(DIRECTORY
  ${CMAKE_CURRENT_SOURCE_DIR}/include/
  DESTINATION "${CMAKE_INSTALL_PREFIX}/include"
  FILES_MATCHING PATTERN "*.h")


# # Make sure we can find the Python libraries to link to.
# link_directories(${PYTHON_LIB_DIR})

# # Python Bindings
# add_library(lens_distortion_plugins SHARED ${LDPK_PYTHON_BINDINGS_SOURCE_FILES})
# # no 'lib' prefix for .so files.
# set_target_properties(lens_distortion_plugins PROPERTIES PREFIX "")
# target_include_directories(lens_distortion_plugins
#   PRIVATE include
#   PUBLIC ${PYTHON_INCLUDE_DIR}
#   # PUBLIC ${dlfcn-win32_INCLUDE_DIRS}
#   )
# target_link_libraries(lens_distortion_plugins dlfcn-win32::dl)
# target_link_libraries(lens_distortion_plugins python27.lib)
# install(TARGETS lens_distortion_plugins
#   RUNTIME DESTINATION "${CMAKE_INSTALL_PREFIX}/python"
#   LIBRARY DESTINATION "${CMAKE_INSTALL_PREFIX}/python"
#   ARCHIVE DESTINATION "${CMAKE_INSTALL_PREFIX}/python"
#   )

# Correctly export the location of installed includes in the target
target_include_directories(ldpk INTERFACE $<INSTALL_INTERFACE:include>)

# Export the targets  (build tree)
export(EXPORT ldpk-targets
  NAMESPACE ldpk::
  FILE "${CMAKE_CURRENT_BINARY_DIR}/cmake/ldpk-targets.cmake")

# Write the CMake config file
set(CMAKE_CONF_INSTALL_DIR share/ldpk)
set(INCLUDE_INSTALL_DIR include)
include(CMakePackageConfigHelpers)
configure_package_config_file(
  ldpk-config.cmake.in ${CMAKE_BINARY_DIR}/ldpk-config.cmake
  INSTALL_DESTINATION ${CMAKE_CONF_INSTALL_DIR}
  PATH_VARS INCLUDE_INSTALL_DIR
  NO_CHECK_REQUIRED_COMPONENTS_MACRO)

# Install the targets (install)
install(EXPORT ldpk-targets
        FILE ldpk-targets.cmake
        NAMESPACE ldpk::
        DESTINATION ${CMAKE_CONF_INSTALL_DIR})

# Install the CMake config file
install(FILES ${CMAKE_BINARY_DIR}/ldpk-config.cmake
        DESTINATION ${CMAKE_CONF_INSTALL_DIR})
