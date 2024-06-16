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

# Expected inputs.
set(MMSOLVERLIBS_CXXBRIDGE_EXE "/path/to/cxxbridge/executable/cxxbridge" CACHE PATH
  "The path to the cxxbridge executable file.")

set(main_include_dir ${CMAKE_CURRENT_SOURCE_DIR}/../include)
set(mmcolorio_include_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../cppbind/mmcolorio/include)
set(mmcolorio_source_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../cppbind/mmcolorio/src)
set(mmcore_include_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../cppbind/mmcore/include)
set(mmcore_source_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../cppbind/mmcore/src)
set(mmimage_include_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../cppbind/mmimage/include)
set(mmimage_source_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../cppbind/mmimage/src)
set(mmlens_include_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../cppbind/mmlens/include)
set(mmlens_source_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../cppbind/mmlens/src)
set(mmscenegraph_include_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../cppbind/mmscenegraph/include)
set(mmscenegraph_source_dir ${CMAKE_CURRENT_SOURCE_DIR}/../../cppbind/mmscenegraph/src)

# C++ Source Code
set(lib_source_files
  ${mmcolorio_source_dir}/lib.cpp

  ${mmcore_source_dir}/_cxxbridge.cpp
  ${mmcore_source_dir}/lib.cpp
  ${mmcore_source_dir}/mmcamera.cpp
  ${mmcore_source_dir}/mmcoord.cpp
  ${mmcore_source_dir}/mmdata.cpp
  ${mmcore_source_dir}/mmhash.cpp
  ${mmcore_source_dir}/mmmath.cpp

  ${mmlens_source_dir}/_cxxbridge.cpp
  ${mmlens_source_dir}/distortion_layers.cpp
  ${mmlens_source_dir}/distortion_process.cpp
  ${mmlens_source_dir}/lens_model_3de_anamorphic_deg_4_rotate_squeeze_xy.cpp
  ${mmlens_source_dir}/lens_model_3de_anamorphic_deg_4_rotate_squeeze_xy_rescaled.cpp
  ${mmlens_source_dir}/lens_model_3de_classic.cpp
  ${mmlens_source_dir}/lens_model_3de_radial_decentered_deg_4_cylindric.cpp
  ${mmlens_source_dir}/lens_model_passthrough.cpp
  ${mmlens_source_dir}/lib.cpp

  ${mmimage_source_dir}/_cxxbridge.cpp
  ${mmimage_source_dir}/imagemetadata.cpp
  ${mmimage_source_dir}/imagepixelbuffer.cpp
  ${mmimage_source_dir}/lib.cpp

  ${mmscenegraph_source_dir}/_cxxbridge.cpp
  ${mmscenegraph_source_dir}/attrdatablock.cpp
  ${mmscenegraph_source_dir}/evaluationobjects.cpp
  ${mmscenegraph_source_dir}/flatscene.cpp
  ${mmscenegraph_source_dir}/line.cpp
  ${mmscenegraph_source_dir}/scenebake.cpp
  ${mmscenegraph_source_dir}/scenegraph.cpp
)

include(MMCommonUtils)
include(MMSolverUtils)
include(MMRustUtils)

message(STATUS "MMSOLVERLIBS_CXXBRIDGE_EXE: ${MMSOLVERLIBS_CXXBRIDGE_EXE}")
mm_rust_generate_cxx_bridge_files_with_dirs(mmcore
  ${mmcore_source_dir} ${mmcore_include_dir} "MMCORE_API_EXPORT"
  ${MMSOLVERLIBS_CXXBRIDGE_EXE}
)
mm_rust_generate_cxx_bridge_files_with_dirs(mmlens
  ${mmlens_source_dir} ${mmlens_include_dir} "MMLENS_API_EXPORT"
  ${MMSOLVERLIBS_CXXBRIDGE_EXE}
)
mm_rust_generate_cxx_bridge_files_with_dirs(mmimage
  ${mmimage_source_dir} ${mmimage_include_dir} "MMIMAGE_API_EXPORT"
  ${MMSOLVERLIBS_CXXBRIDGE_EXE}
)
mm_rust_generate_cxx_bridge_files_with_dirs(mmscenegraph
  ${mmscenegraph_source_dir} ${mmscenegraph_include_dir} "MMSCENEGRAPH_API_EXPORT"
  ${MMSOLVERLIBS_CXXBRIDGE_EXE}
)

# Add 'mmsolverlibs_cpp' library as a C++ wrapper around the Rust library.
add_library(${cpp_lib_name} ${lib_source_files})
target_link_libraries(${cpp_lib_name}
  PUBLIC "${rust_depend_on_libraries}"
  PUBLIC "${rust_linktime_file}"
)

# We must force this target ('cpp_lib_name') to wait for
# ldpk to be installed so we have the 'ldpk_INCLUDE_DIR' variable.
add_dependencies(${cpp_lib_name} ldpk::ldpk)

# MM Color IO dependencies
include(MMColorIOUtils)
mmcolorio_find_packages()
mmcolorio_target_link_packages(${cpp_lib_name})
mmcolorio_target_include_packages(${cpp_lib_name})

target_include_directories(${cpp_lib_name}
  PUBLIC $<BUILD_INTERFACE:${main_include_dir}>
  PUBLIC $<BUILD_INTERFACE:${mmcolorio_include_dir}>
  PUBLIC $<BUILD_INTERFACE:${mmcore_include_dir}>
  PUBLIC $<BUILD_INTERFACE:${mmlens_include_dir}>
  PUBLIC $<BUILD_INTERFACE:${mmimage_include_dir}>
  PUBLIC $<BUILD_INTERFACE:${mmscenegraph_include_dir}>
  PRIVATE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
  PRIVATE $<BUILD_INTERFACE:${ldpk_INCLUDE_DIR}>
  PUBLIC $<INSTALL_INTERFACE:include/>
  )

mm_common_install_target_library("mmsolverlibs_cpp" ${cpp_lib_name})

# Install public headers
include(GNUInstallDirs)
install(DIRECTORY
  "${mmcolorio_include_dir}/"
  "${mmcore_include_dir}/"
  "${mmimage_include_dir}/"
  "${mmlens_include_dir}/"
  "${mmscenegraph_include_dir}/"
  "${main_include_dir}/"
  DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
  FILES_MATCHING PATTERN "*.h")
