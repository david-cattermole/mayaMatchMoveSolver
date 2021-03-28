# Copyright (C) 2019, 2020 David Cattermole.
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
# Maya MatchMoveSolver build script.
#
cmake_minimum_required(VERSION 2.8.12)


# Project configuration.
project(mayaMatchMoveSolver)
set(PROJECT_VERSION_MAJOR 0)
set(PROJECT_VERSION_MINOR 3)
set(PROJECT_VERSION_PATCH 13)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}")
set(PROJECT_HOMEPAGE_URL "https://github.com/david-cattermole/mayaMatchMoveSolver")
set(PROJECT_DESCRIPTION "Bundle Adjustment solver for MatchMove tasks in Autodesk Maya.")
set(PROJECT_AUTHOR "David Cattermole and others (see AUTHORS.txt file)")
set(PROJECT_COPYRIGHT
  "2018, 2019, 2020, 2021, David Cattermole, Anil Reddy, Kazuma Tonegawa.")


# Add custom modules to the module path
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules)


# Build options; What will we build?  This is used mostly for
# developer debug. If the developer is working on some Python code
# only, we don't need to wait for the Maya Plug-In to compute each
# time.
set(BUILD_PLUGIN 1 CACHE BOOL
        "Do you want to build the plug-in?")
set(BUILD_PYTHON 1 CACHE BOOL
        "Do you want to build and install the Python API and tools?")
set(BUILD_MEL 1 CACHE BOOL
        "Do you want to build and install the MEL scripts and tools?")
set(BUILD_3DEQUALIZER 1 CACHE BOOL
        "Do you want to build and install 3DEqualizer scripts?")
set(BUILD_SYNTHEYES 1 CACHE BOOL
        "Do you want to build and install SynthEyes scripts?")
set(BUILD_QT_UI 1 CACHE BOOL
        "Do you want to build the Qt UI files?")
set(BUILD_DOCS 1 CACHE BOOL
        "Do you want to build and install the documentation?")
set(BUILD_ICONS 1 CACHE BOOL
        "Do you want to build and install the icons?")
set(BUILD_CONFIG 1 CACHE BOOL
        "Do you want to build and install the config files?")
set(BUILD_TESTS 1 CACHE BOOL
        "Do you want to build the test files?")


# Maya SDK
set(MAYA_VERSION "2017" CACHE STRING
        "Maya version number")
set(MAYA_LOCATION "/usr/autodesk/maya${MAYA_VERSION}/" CACHE PATH
        "Maya install directory")
set(DEVKIT_LOCATION "/usr/autodesk/maya${MAYA_VERSION}/" CACHE PATH 
        "Maya development kit (devkit) directory")
set(MAYA_INCLUDE_PATH
        "/usr/autodesk/maya${MAYA_VERSION}/include" CACHE PATH "Maya include directory")
set(MAYA_LIB_PATH "/usr/autodesk/maya${MAYA_VERSION}/lib" CACHE PATH 
        "Maya library directory")


# Lev-Mar
#
# WARNING: 'Lev-Mar' is GPL licensed and must not be
# distributed in binary form to anyone.
set(USE_GPL_LEVMAR 0 CACHE BOOL
        "Compile with the GPL-licensed Lev-Mar library?")
set(LEVMAR_ROOT "/usr/local" CACHE PATH "Levmar directory")
set(LEVMAR_INCLUDE_PATH "/usr/local/include" CACHE PATH
        "Levmar include directory")
set(LEVMAR_LIB_PATH "/usr/local/lib" CACHE PATH "Levmar library directory")


# CMinpack
set(USE_CMINPACK 1 CACHE BOOL "Compile with the cminpack library?")
set(CMINPACK_ROOT "/usr/local" CACHE PATH "CMinpack directory")
set(CMINPACK_INCLUDE_PATH "/usr/local/include" CACHE PATH
        "cminpack include directory")
set(CMINPACK_LIB_PATH "/usr/local/lib" CACHE PATH "cminpack library directory")


# Extra (BLAS) Libraries
set(USE_BLAS OFF CACHE BOOL "Should we use BLAS?")
set(BLAS_INCLUDE_PATH "/usr/include/blas" CACHE PATH "BLAS library directory")
set(BLAS_LIB_PATH "/usr/lib64/blas" CACHE PATH "BLAS library directory")
set(BLAS_LIB_NAMES
        ""
        CACHE STRING
        "BLAS libraries to link")


# Default Solver to use.
set(PREFERRED_SOLVER "cminpack_lmder" CACHE STRING
        "Choices are cminpack_lm, cminpack_lmder or levmar. Which solver is used by default?")

include(MMSolverUtils)

# Build features
add_subdirectory(modules)

# Build external dependancies (including Qt.py).
add_subdirectory(external)

if (BUILD_PLUGIN)
  add_subdirectory(include)
  add_subdirectory(src)
endif ()

if (BUILD_PYTHON)
  add_subdirectory(python)
endif ()

if (BUILD_MEL)
  add_subdirectory(mel)
endif ()

if (BUILD_DOCS)
  add_subdirectory(docs)
endif ()

if (BUILD_3DEQUALIZER)
  add_subdirectory(3dequalizer)
endif ()

if (BUILD_SYNTHEYES)
  add_subdirectory(syntheyes)
endif ()

if (BUILD_ICONS)
  add_subdirectory(icons)
endif ()

if (BUILD_CONFIG)
  add_subdirectory(config)
endif ()

if (BUILD_TESTS)
  enable_testing()
  add_subdirectory(tests)
endif ()


# Install misc files
#
# NOTE: ${MODULE_FULL_NAME} comes from module sub-directory.
install(FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/LICENSE
  ${CMAKE_CURRENT_SOURCE_DIR}/INSTALL.md
  ${CMAKE_CURRENT_SOURCE_DIR}/README.md
  DESTINATION "${MODULE_FULL_NAME}/")


# Package Configuration.
set(CPACK_PACKAGE_NAME "${PROJECT_NAME}")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "${PROJECT_DESCRIPTION}")
set(CPACK_PACKAGE_VENDOR "${PROJECT_AUTHOR}")
set(CPACK_PACKAGE_CONTACT "cattermole91@gmail.com")
set(CPACK_PACKAGE_DESCRIPTION_FILE "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
set(CPACK_PACKAGE_VERSION_MAJOR "${PROJECT_VERSION_MAJOR}")
set(CPACK_PACKAGE_VERSION_MINOR "${PROJECT_VERSION_MINOR}")
set(CPACK_PACKAGE_VERSION_PATCH "${PROJECT_VERSION_PATCH}")
set(CPACK_PACKAGE_FILE_NAME "${MODULE_FULL_NAME}")
set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY 1)
# Put the packages into the source directory, so that when we run
# another build, it's not removed as part of the clean up.
SET(CPACK_OUTPUT_FILE_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/packages")
if (WIN32 AND NOT UNIX)
  # .zip file for Windows.
  set(CPACK_GENERATOR "ZIP")
elseif (UNIX AND NOT WIN32)
  # .tar.gz for Linux and MacOS
  set(CPACK_GENERATOR "TGZ")
endif ()


# TODO: Set up proper 'source' package file inclusion rules.
# # set(CPACK_SOURCE_GENERATOR "TGZ")
# # set(CPACK_SOURCE_PACKAGE_FILE_NAME "${MODULE_NAME}-Source")

# Use CPack (part of CMake) to generate the packages...
# If 'CPack' is not included, the 'packages' target will not be generated.
include(CPack)
