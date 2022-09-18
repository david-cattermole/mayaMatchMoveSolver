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
# - OpenMVG finder module
# This module will look for OpenMVG, using the predefined variable
# OpenMVG_ROOT.
#
# Uses Variables:
# - OpenMVG_ROOT_PATH - Directory for the OpenMVG install root.
# - OpenMVG_INCLUDE_PATH - Directory for the header files.
# - OpenMVG_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - OpenMVG_FOUND
# - OpenMVG_LIBRARIES
# - OpenMVG_INCLUDE_DIRS
#


function(find_OpenMVG_find_with_paths OpenMVG_root OpenMVG_include_path OpenMVG_lib_path)

    find_path(OpenMVG_include_dir openMVG/version.hpp
      HINTS
        ${OpenMVG_include_path}
        ${OpenMVG_root}
        /usr/local/include
        /usr/include
      PATH_SUFFIXES
        include/
    )

    find_library(OpenMVG_library
      NAMES
        libopenMVG_sfm
        openMVG_sfm
      HINTS
        ${OpenMVG_lib_path}
        ${OpenMVG_root}
        /usr/lib
        /usr/local/lib
      PATH_SUFFIXES
        bin/
        lib/
        lib64/
    )

    find_path(OpenMVG_dir
      NAMES
        OpenMVGConfig.cmake
        OpenMVGTargets.cmake
      HINTS
        ${OpenMVG_lib_path}/../share/openMVG/cmake
        ${OpenMVG_root}
        /usr/local/include
        /usr/include
    )

    if(OpenMVG_include_dir AND OpenMVG_library AND OpenMVG_dir)
      get_filename_component(OpenMVG_library_dir ${OpenMVG_library} DIRECTORY)
      set(${out_OpenMVG_include_dirs} ${OpenMVG_include_dir} PARENT_SCOPE)
      set(${out_OpenMVG_library_dirs} ${OpenMVG_library_dir} PARENT_SCOPE)
    endif()

endfunction()


function(find_OpenMVG_create_target)

  add_library(OpenMVG::cereal INTERFACE IMPORTED GLOBAL)
  add_library(OpenMVG::lib_CoinUtils STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::lib_Osi STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::lib_OsiClpSolver STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::lib_clp STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_camera INTERFACE IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_easyexif STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_exif STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_fast STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_features STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_geodesy INTERFACE IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_geometry STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_graph INTERFACE IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_image STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_jpeg STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_kvld STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_lInftyComputerVision STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_lemon INTERFACE IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_linearProgramming STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_matching STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_matching_image_collection STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_multiview STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_numeric STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_png STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_robust_estimation STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_sfm STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_stlplus STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_system STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_tiff STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::openMVG_zlib STATIC IMPORTED GLOBAL)
  add_library(OpenMVG::vlsift STATIC IMPORTED GLOBAL)

endfunction()


function(find_OpenMVG_set_target
    OpenMVG_library_dir
    OpenMVG_include_dir
    Eigen3_include_dir)

  if(WIN32)
    set(_compile_options
      "/DWIN32;/D_WINDOWS;/W3;/GR;/EHsc;-openmp;-D_USE_MATH_DEFINES;-DNOMINMAX;")
  else()
    set(_compile_options
      "-march=skylake;-fopenmp"
    )
  endif()

  set_target_properties(OpenMVG::lib_CoinUtils PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}lib_CoinUtils${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::lib_Osi PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}lib_Osi${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::lib_clp PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}lib_clp${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::lib_OsiClpSolver PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}lib_OsiClpSolver${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::cereal PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir}/openMVG_dependencies/cereal/include"
    )

  set_target_properties(OpenMVG::openMVG_stlplus PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir}/openMVG;${OpenMVG_include_dir}/openMVG/third_party/stlplus3/filesystemSimplified"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_stlplus${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_jpeg PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES "C"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_jpeg${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_zlib PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES "C"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_zlib${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_png PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES "C"
    IMPORTED_LINK_INTERFACE_LIBRARIES_RELEASE "OpenMVG::openMVG_zlib"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_png${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_lemon PROPERTIES
    INTERFACE_COMPILE_DEFINITIONS "LEMON_ONLY_TEMPLATES"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir}/openMVG/third_party/lemon;${OpenMVG_include_dir}/openMVG/third_party"
    )

  set_target_properties(OpenMVG::openMVG_tiff PROPERTIES
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_zlib"
    IMPORTED_LINK_INTERFACE_LANGUAGES "C;CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_tiff${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_easyexif PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_easyexif${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_fast PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_fast${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_camera PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir}"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_numeric;OpenMVG::cereal"
    )

  set_target_properties(OpenMVG::openMVG_exif PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:OpenMVG::openMVG_easyexif>"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_exif${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_features PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_COMPILE_OPTIONS "${_compile_options}"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir};${OpenMVG_include_dir}/openMVG"
    INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:OpenMVG::openMVG_fast>;\$<LINK_ONLY:OpenMVG::openMVG_stlplus>;OpenMVG::cereal"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_features${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_graph PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_lemon"
    )

  set_target_properties(OpenMVG::openMVG_image PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_COMPILE_OPTIONS "${_compile_options}"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir}"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_numeric;\$<LINK_ONLY:OpenMVG::openMVG_jpeg>;\$<LINK_ONLY:OpenMVG::openMVG_png>;\$<LINK_ONLY:OpenMVG::openMVG_zlib>;\$<LINK_ONLY:OpenMVG::openMVG_tiff>"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_image${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_linearProgramming PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir}"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_numeric;\$<LINK_ONLY:OpenMVG::lib_clp>;\$<LINK_ONLY:OpenMVG::lib_OsiClpSolver>;\$<LINK_ONLY:OpenMVG::lib_CoinUtils>;\$<LINK_ONLY:OpenMVG::lib_Osi>"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_linearProgramming${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_lInftyComputerVision PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_linearProgramming;OpenMVG::openMVG_multiview"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_lInftyComputerVision${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_geodesy PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir}"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_numeric"
    )

  set_target_properties(OpenMVG::openMVG_geometry PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir}"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_numeric;OpenMVG::cereal;\$<LINK_ONLY:OpenMVG::openMVG_linearProgramming>"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_geometry${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_matching PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir};${OpenMVG_include_dir}/openMVG"
    INTERFACE_LINK_LIBRARIES "\$<LINK_ONLY:OpenMVG::openMVG_stlplus>;OpenMVG::openMVG_features;Threads::Threads;OpenMVG::cereal"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_matching${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_kvld PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_features;OpenMVG::openMVG_image"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_kvld${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_matching_image_collection PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir};${OpenMVG_include_dir}/openMVG"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_matching;OpenMVG::openMVG_multiview"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_matching_image_collection${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_multiview PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir}"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_numeric;\$<LINK_ONLY:OpenMVG::openMVG_graph>;\$<LINK_ONLY:ceres>"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_multiview${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_numeric PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_COMPILE_OPTIONS "${_compile_options}"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir};${Eigen3_include_dir}"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_numeric${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_robust_estimation PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir};${OpenMVG_include_dir}/openMVG"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_numeric"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_robust_estimation${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_system PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_system${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::openMVG_sfm PROPERTIES
    INTERFACE_COMPILE_FEATURES "cxx_std_11"
    INTERFACE_INCLUDE_DIRECTORIES "${OpenMVG_include_dir};${OpenMVG_include_dir}/openMVG"
    INTERFACE_LINK_LIBRARIES "OpenMVG::openMVG_geometry;OpenMVG::openMVG_features;OpenMVG::openMVG_graph;OpenMVG::openMVG_matching;OpenMVG::openMVG_multiview;OpenMVG::cereal;\$<LINK_ONLY:OpenMVG::openMVG_image>;\$<LINK_ONLY:OpenMVG::openMVG_lInftyComputerVision>;\$<LINK_ONLY:OpenMVG::openMVG_system>;\$<LINK_ONLY:ceres>;\$<LINK_ONLY:OpenMVG::openMVG_stlplus>"
    IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}openMVG_sfm${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

  set_target_properties(OpenMVG::vlsift PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES "C"
    IMPORTED_LOCATION "${OpenMVG_library_dir}/${CMAKE_STATIC_LIBRARY_PREFIX}vlsift${CMAKE_STATIC_LIBRARY_SUFFIX}"
    )

endfunction()


option(OpenMVG_ALLOW_DOWNLOAD
  "Allow automatically downloading and building OpenMVG?" ON)


# OpenMVG requires the 'Threads' package.
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)


if(NOT MMSOLVER_DOWNLOAD_DEPENDENCIES OR NOT OpenMVG_ALLOW_DOWNLOAD)

  if(NOT DEFINED OpenMVG_ROOT)
    # Search for "OpenMVG-config.cmake" given on the command line.
    find_package(OpenMVG ${OpenMVG_FIND_VERSION} CONFIG QUIET)
  endif()

  if(OpenMVG_FOUND)
    message(FATAL_ERROR "Not Implemented. OpenMVG has been found from the OpenMVG-config.cmake file")
  else()
    # Fallback and try to find the package.
    find_OpenMVG_find_with_paths(
      ${OpenMVG_ROOT}
      ${OpenMVG_INCLUDE_PATH}
      ${OpenMVG_LIB_PATH}
      OpenMVG_DIR
      OpenMVG_INCLUDE_DIRS
      OpenMVG_LIBRARIES
      )
  endif()

  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(openmvg
    REQUIRED_VARS
      OpenMVG_LIBRARIES
      OpenMVG_INCLUDE_DIRS
  )

  if(OpenMVG_FOUND)
    message(STATUS "OpenMVG: Found=${OpenMVG_FOUND}")
    message(STATUS "OpenMVG: Config=${OpenMVG_DIR}")
    message(STATUS "OpenMVG: Include=${OpenMVG_INCLUDE_DIRS}")
    message(STATUS "OpenMVG: Library=${OpenMVG_LIBRARIES}")
  endif()

endif()


# Ensure a target for openmvg is created.
if(NOT TARGET OpenMVG::openMVG_sfm)
  find_OpenMVG_create_target()
  if(OpenMVG_FOUND)
    find_OpenMVG_set_target(${OpenMVG_LIBRARY_DIR} ${OpenMVG_INCLUDE_DIR} ${Eigen3_INCLUDE_DIRS})
  else()
    set(_OpenMVG_TARGET_CREATE TRUE)
  endif()
endif()


# Download, Build and Install.
if(NOT OpenMVG_FOUND AND MMSOLVER_DOWNLOAD_DEPENDENCIES AND OpenMVG_ALLOW_DOWNLOAD)
  include(ExternalProject)
  include(GNUInstallDirs)

  set(_EXTERNAL_INSTALL_DIR "${CMAKE_BINARY_DIR}/ext/install")
  set(_EXTERNAL_BUILD_DIR "${CMAKE_BINARY_DIR}/ext/build")

  # Fill in the expected values/paths that will exist when the build
  # and install of openmvg actually happens.
  set(OpenMVG_FOUND TRUE)
  set(OpenMVG_VERSION ${OpenMVG_FIND_VERSION})

  set(OpenMVG_DIR "${_EXTERNAL_INSTALL_DIR}/OpenMVG/share/openMVG/cmake")
  set(OpenMVG_INCLUDE_DIR "${_EXTERNAL_INSTALL_DIR}/OpenMVG/${CMAKE_INSTALL_INCLUDEDIR}")
  # The library path is (unfortunately) hard-coded in the OpenMVG
  # CMakeLists.txt, so we need to match the same behavior.
  set(OpenMVG_LIBRARY_DIR "${_EXTERNAL_INSTALL_DIR}/OpenMVG/lib")

  set(OpenMVG_LIBRARIES "")
  foreach(_lib_name IN ITEMS
      cereal
      lib_CoinUtils
      lib_Osi
      lib_OsiClpSolver
      lib_clp
      openMVG_camera
      openMVG_easyexif
      openMVG_exif
      openMVG_fast
      openMVG_features
      openMVG_geodesy
      openMVG_geometry
      openMVG_graph
      openMVG_image
      openMVG_jpeg
      openMVG_kvld
      openMVG_lInftyComputerVision
      openMVG_lemon
      openMVG_linearProgramming
      openMVG_matching
      openMVG_matching_image_collection
      openMVG_multiview
      openMVG_numeric
      openMVG_png
      openMVG_robust_estimation
      openMVG_sfm
      openMVG_stlplus
      openMVG_system
      openMVG_tiff
      openMVG_zlib
      vlsift)

    set(_OpenMVG_LIBRARY_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}${_lib_name}${CMAKE_STATIC_LIBRARY_SUFFIX}")
    set(OpenMVG_LIBRARY_${_lib_name} "${OpenMVG_LIBRARY_DIR}/${_OpenMVG_LIBRARY_NAME}")
    list(APPEND OpenMVG_LIBRARIES ${OpenMVG_LIBRARY_${_lib_name}})

  endforeach()

  set(OpenMVG_URL
    "https://github.com/openMVG/openMVG.git"
    CACHE STRING
    "The URL for the OpenMVG git repository.")

  set(OpenMVG_GIT_TAG "v${OpenMVG_VERSION}"
    CACHE STRING
    "The Git Tag for the OpenMVG git repository.")

  set(OpenMVG_INSTALL_PATH ${_EXTERNAL_INSTALL_DIR}/OpenMVG)
  set(OpenMVG_PREFIX ${_EXTERNAL_BUILD_DIR}/OpenMVG)
  set(OpenMVG_SOURCE_DIR ${_EXTERNAL_BUILD_DIR}/OpenMVG/src/OpenMVG)

  set(OpenMVG_PATCH_SRC_1 ${CMAKE_SOURCE_DIR}/external/patches/OpenMVG/cmakeFindModules_FindJPEG.cmake)
  set(OpenMVG_PATCH_SRC_2 ${CMAKE_SOURCE_DIR}/external/patches/OpenMVG/cmakeFindModules_FindPNG.cmake)
  set(OpenMVG_PATCH_SRC_3 ${CMAKE_SOURCE_DIR}/external/patches/OpenMVG/cmakeFindModules_FindTIFF.cmake)
  set(OpenMVG_PATCH_SRC_4 ${CMAKE_SOURCE_DIR}/external/patches/OpenMVG/robust_estimator_ACRansac.hpp)

  set(OpenMVG_PATCH_DST_1 ${OpenMVG_SOURCE_DIR}/src/cmakeFindModules/FindJPEG.cmake)
  set(OpenMVG_PATCH_DST_2 ${OpenMVG_SOURCE_DIR}/src/cmakeFindModules/FindPNG.cmake)
  set(OpenMVG_PATCH_DST_3 ${OpenMVG_SOURCE_DIR}/src/cmakeFindModules/FindTIFF.cmake)
  set(OpenMVG_PATCH_DST_4 ${OpenMVG_SOURCE_DIR}/src/openMVG/robust_estimation/robust_estimator_ACRansac.hpp)

  set(OpenMVG_BUILD_SHARED 0)
  set(OpenMVG_BUILD_TESTS 0)
  set(OpenMVG_BUILD_DOC 0)
  set(OpenMVG_BUILD_EXAMPLES 0)
  set(OpenMVG_BUILD_OPENGL_EXAMPLES 0)
  set(OpenMVG_BUILD_SOFTWARES 0)
  set(OpenMVG_BUILD_GUI_SOFTWARES 0)
  set(OpenMVG_BUILD_COVERAGE 0)

  set(OpenMVG_CMAKE_ARGS
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
    -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
    -DCMAKE_INSTALL_PREFIX=${OpenMVG_INSTALL_PATH}
    -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
    -DCMAKE_IGNORE_PATH=${CMAKE_IGNORE_PATH}
    -DCMAKE_POSITION_INDEPENDENT_CODE=${CMAKE_POSITION_INDEPENDENT_CODE}
    -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
    -DCMAKE_CXX_EXTENSIONS=${CXX_EXTENSIONS}
    -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
    -DCMAKE_FIND_PACKAGE_NO_PACKAGE_REGISTRY=1
    -DCMAKE_FIND_PACKAGE_NO_SYSTEM_PACKAGE_REGISTRY=1
    -DCMAKE_FIND_USE_PACKAGE_REGISTRY=0

    -DOpenMVG_BUILD_SHARED=${OpenMVG_BUILD_SHARED}
    -DOpenMVG_BUILD_TESTS=${OpenMVG_BUILD_TESTS}
    -DOpenMVG_BUILD_DOC=${OpenMVG_BUILD_DOC}
    -DOpenMVG_BUILD_EXAMPLES=${OpenMVG_BUILD_EXAMPLES}
    -DOpenMVG_BUILD_OPENGL_EXAMPLES=${OpenMVG_BUILD_OPENGL_EXAMPLES}
    -DOpenMVG_BUILD_SOFTWARES=${OpenMVG_BUILD_SOFTWARES}
    -DOpenMVG_BUILD_GUI_SOFTWARES=${OpenMVG_BUILD_GUI_SOFTWARES}
    -DOpenMVG_BUILD_COVERAGE=${OpenMVG_BUILD_COVERAGE}

    -DOpenMVG_USE_OPENMP=1
    -DOpenMVG_USE_OPENCV=0
    -DOpenMVG_USE_OCVSIFT=0

    # WARNING: Enabling "EIGENSPARSE" results in an LGPL licensed
    # Ceres.
    -DEIGENSPARSE=1

    -DEigen3_DIR=${Eigen3_DIR}
    -DEIGEN_INCLUDE_DIR_HINTS=${Eigen3_INCLUDE_DIR}

    -DCeres_DIR=${ceres_DIR}
    -DCERES_DIR_HINTS=${ceres_DIR}
  )

  # Hack to let imported target be built from ExternalProject_Add
  file(MAKE_DIRECTORY ${OpenMVG_INCLUDE_DIR})
  file(MAKE_DIRECTORY "${OpenMVG_INCLUDE_DIR}/openMVG")
  file(MAKE_DIRECTORY "${OpenMVG_INCLUDE_DIR}/openMVG_dependencies/cereal/include")
  file(MAKE_DIRECTORY "${OpenMVG_INCLUDE_DIR}/openMVG/third_party/lemon")
  file(MAKE_DIRECTORY "${OpenMVG_INCLUDE_DIR}/openMVG/third_party/stlplus3/filesystemSimplified")

  ExternalProject_Add(OpenMVG
    DEPENDS Eigen3 ceres_install
    PREFIX ${OpenMVG_PREFIX}
    GIT_REPOSITORY ${OpenMVG_URL}
    GIT_TAG "${OpenMVG_GIT_TAG}"
    SOURCE_SUBDIR src/  # The CMakeLists.txt is inside the ./src/ directory.
    INSTALL_DIR ${OpenMVG_INSTALL_PATH}
    BUILD_BYPRODUCTS
      ${OpenMVG_LIBRARY_cereal}
      ${OpenMVG_LIBRARY_lib_CoinUtils}
      ${OpenMVG_LIBRARY_lib_Osi}
      ${OpenMVG_LIBRARY_lib_OsiClpSolver}
      ${OpenMVG_LIBRARY_lib_clp}
      ${OpenMVG_LIBRARY_openMVG_camera}
      ${OpenMVG_LIBRARY_openMVG_easyexif}
      ${OpenMVG_LIBRARY_openMVG_exif}
      ${OpenMVG_LIBRARY_openMVG_fast}
      ${OpenMVG_LIBRARY_openMVG_features}
      ${OpenMVG_LIBRARY_openMVG_geodesy}
      ${OpenMVG_LIBRARY_openMVG_geometry}
      ${OpenMVG_LIBRARY_openMVG_graph}
      ${OpenMVG_LIBRARY_openMVG_image}
      ${OpenMVG_LIBRARY_openMVG_jpeg}
      ${OpenMVG_LIBRARY_openMVG_kvld}
      ${OpenMVG_LIBRARY_openMVG_lInftyComputerVision}
      ${OpenMVG_LIBRARY_openMVG_lemon}
      ${OpenMVG_LIBRARY_openMVG_linearProgramming}
      ${OpenMVG_LIBRARY_openMVG_matching}
      ${OpenMVG_LIBRARY_openMVG_matching_image_collection}
      ${OpenMVG_LIBRARY_openMVG_multiview}
      ${OpenMVG_LIBRARY_openMVG_numeric}
      ${OpenMVG_LIBRARY_openMVG_png}
      ${OpenMVG_LIBRARY_openMVG_robust_estimation}
      ${OpenMVG_LIBRARY_openMVG_sfm}
      ${OpenMVG_LIBRARY_openMVG_stlplus}
      ${OpenMVG_LIBRARY_openMVG_system}
      ${OpenMVG_LIBRARY_openMVG_tiff}
      ${OpenMVG_LIBRARY_openMVG_zlib}
      ${OpenMVG_LIBRARY_vlsift}
    PATCH_COMMAND ${CMAKE_COMMAND} -E copy ${OpenMVG_PATCH_SRC_1} ${OpenMVG_PATCH_DST_1}
    COMMAND       ${CMAKE_COMMAND} -E copy ${OpenMVG_PATCH_SRC_2} ${OpenMVG_PATCH_DST_2}
    COMMAND       ${CMAKE_COMMAND} -E copy ${OpenMVG_PATCH_SRC_3} ${OpenMVG_PATCH_DST_3}
    COMMAND       ${CMAKE_COMMAND} -E copy ${OpenMVG_PATCH_SRC_4} ${OpenMVG_PATCH_DST_4}
    CMAKE_ARGS ${OpenMVG_CMAKE_ARGS}
    EXCLUDE_FROM_ALL TRUE
    BUILD_COMMAND ""
    INSTALL_COMMAND ${CMAKE_COMMAND} --build . --config ${CMAKE_BUILD_TYPE} --target install --parallel
  )

  foreach(_target IN ITEMS
      OpenMVG::cereal
      OpenMVG::lib_CoinUtils
      OpenMVG::lib_Osi
      OpenMVG::lib_OsiClpSolver
      OpenMVG::lib_clp
      OpenMVG::openMVG_camera
      OpenMVG::openMVG_easyexif
      OpenMVG::openMVG_exif
      OpenMVG::openMVG_fast
      OpenMVG::openMVG_features
      OpenMVG::openMVG_geodesy
      OpenMVG::openMVG_geometry
      OpenMVG::openMVG_graph
      OpenMVG::openMVG_image
      OpenMVG::openMVG_jpeg
      OpenMVG::openMVG_kvld
      OpenMVG::openMVG_lInftyComputerVision
      OpenMVG::openMVG_lemon
      OpenMVG::openMVG_linearProgramming
      OpenMVG::openMVG_matching
      OpenMVG::openMVG_matching_image_collection
      OpenMVG::openMVG_multiview
      OpenMVG::openMVG_numeric
      OpenMVG::openMVG_png
      OpenMVG::openMVG_robust_estimation
      OpenMVG::openMVG_sfm
      OpenMVG::openMVG_stlplus
      OpenMVG::openMVG_system
      OpenMVG::openMVG_tiff
      OpenMVG::openMVG_zlib
      OpenMVG::vlsift)
    add_dependencies(${_target} OpenMVG)

  endforeach()

  message(STATUS "Installing OpenMVG (version \"${OpenMVG_VERSION}\")")
  message(STATUS "OpenMVG: Config=${OpenMVG_DIR}")
  message(STATUS "OpenMVG: Include=${OpenMVG_INCLUDE_DIR}")
  message(STATUS "OpenMVG: Library=${OpenMVG_LIBRARIES}")

else()

  # Placeholder target that does nothing.
  add_custom_target(OpenMVG)

endif()


if(_OpenMVG_TARGET_CREATE)
  find_OpenMVG_set_target(${OpenMVG_LIBRARY_DIR} ${OpenMVG_INCLUDE_DIR} ${Eigen3_INCLUDE_DIR})
  mark_as_advanced(
    OpenMVG_INCLUDE_DIR
    OpenMVG_LIBRARY
    OpenMVG_VERSION
  )
endif()
