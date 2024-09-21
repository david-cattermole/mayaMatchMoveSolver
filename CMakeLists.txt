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
cmake_minimum_required(VERSION 3.15)


# find_package() will use <PackageName>_ROOT variables.
#
# https://cmake.org/cmake/help/latest/policy/CMP0074.html
cmake_policy(SET CMP0074 NEW)

# The "project" command will overwrite the "VERSION" variables. We set
# the VERSION variables after the "project" command, so it should not
# affect us.
#
# https://cmake.org/cmake/help/latest/policy/CMP0048.html
cmake_policy(SET CMP0048 NEW)

# Honor visibility properties for all target types.
#
# https://cmake.org/cmake/help/latest/policy/CMP0063.html
cmake_policy(SET CMP0063 NEW)

if(CMAKE_VERSION VERSION_GREATER_EQUAL "3.24.0")
  # Changes how timestamps of downloaded files with
  # ExternalProject_Add() are set.
  #
  # https://cmake.org/cmake/help/latest/policy/CMP0135.html
  cmake_policy(SET CMP0135 NEW)
endif()

# Do not allow using GNU extensions (such as '-std=g++11'), because
# it's not compatible with Maya.
set(CXX_EXTENSIONS OFF)

# For Windows, allow paths of more than 250 to avoid build issues
# arrising on Windows with very long file paths.
if(NOT DEFINED CMAKE_OBJECT_PATH_MAX)
    set(CMAKE_OBJECT_PATH_MAX 300)
endif()

# Project configuration.
project(mayaMatchMoveSolver)
set(PROJECT_VERSION_MAJOR 0)
set(PROJECT_VERSION_MINOR 5)
set(PROJECT_VERSION_PATCH 0)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}")
set(PROJECT_HOMEPAGE_URL "https://github.com/david-cattermole/mayaMatchMoveSolver")
set(PROJECT_DESCRIPTION "Bundle Adjustment solver for MatchMove tasks in Autodesk Maya.")
set(PROJECT_AUTHOR "David Cattermole, Patcha Saheb Binginapalli, and others (see AUTHORS.txt file)")
set(PROJECT_COPYRIGHT
  "2018-2024, David Cattermole, Anil Reddy, Kazuma Tonegawa, Patcha Saheb Binginapalli.")
enable_testing()


# Add custom modules to the module path
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
        ${CMAKE_CURRENT_SOURCE_DIR}/share/cmake/modules)

# Build options; What will we build?  This is used mostly for
# developer debug. If the developer is working on some Python code
# only, we don't need to wait for the Maya Plug-In to compute each
# time, so turn off the plugin.
option(MMSOLVER_BUILD_PLUGIN "Build the Maya plug-in?" ON)
option(MMSOLVER_BUILD_TOOLS "Build C++ tools?" ON)
option(MMSOLVER_BUILD_PYTHON "Build and install the Python API and tools?" ON)
option(MMSOLVER_BUILD_MEL "Build and install the MEL scripts and tools?" ON)
option(MMSOLVER_BUILD_3DEQUALIZER "Build and install 3DEqualizer scripts?" ON)
option(MMSOLVER_BUILD_SYNTHEYES "Build and install SynthEyes scripts?" ON)
option(MMSOLVER_BUILD_BLENDER "Build and install Blender add-on?" ON)
option(MMSOLVER_BUILD_QT_UI "Build the Qt UI files?" ON)
option(MMSOLVER_BUILD_RENDERER "Build and install the MM Renderer?" OFF)
option(MMSOLVER_BUILD_DOCS "Build and install the documentation?" ON)
option(MMSOLVER_BUILD_ICONS "Build and install the icons?" ON)
option(MMSOLVER_BUILD_CONFIG "Build and install the config files?" ON)
option(MMSOLVER_BUILD_TESTS "Build the test files?" OFF)
option(MMSOLVER_DOWNLOAD_DEPENDENCIES "Automatically download and build missing dependencies?" ON)


# Maya SDK
set(MAYA_VERSION "2019" CACHE STRING "Maya version number")
set(MAYA_LOCATION "/usr/autodesk/maya${MAYA_VERSION}/" CACHE PATH "Maya install directory")
set(DEVKIT_LOCATION "/usr/autodesk/maya${MAYA_VERSION}/" CACHE PATH "Maya development kit (devkit) directory")
set(MAYA_INCLUDE_PATH "/usr/autodesk/maya${MAYA_VERSION}/include" CACHE PATH "Maya include directory")
set(MAYA_LIB_PATH "/usr/autodesk/maya${MAYA_VERSION}/lib" CACHE PATH "Maya library directory")


# Set a default minimizing solver.
#
# Choices are "cminpack_lm" or "cminpack_lmder".
#
# "cminpack_lmder" is the best performing (for now). "ceres" is
# planned for a future release.
set(DEFAULT_SOLVER "cminpack_lmder")


include(MMSolverUtils)

# Build features
add_subdirectory(share)

# C++ include files
if (MMSOLVER_BUILD_PLUGIN OR MMSOLVER_BUILD_TOOLS)
  add_subdirectory(include)
endif ()

if (MMSOLVER_BUILD_PLUGIN)
  # Finds and builds external (third-party) dependencies.
  include(FindAndBuildExternalPackages)
  add_subdirectory(external)

  add_subdirectory(src)
endif ()

if (MMSOLVER_BUILD_TOOLS)
  add_subdirectory(tools)
endif ()

if (MMSOLVER_BUILD_PYTHON)
  add_subdirectory(python)
endif ()

if (MMSOLVER_BUILD_MEL)
  add_subdirectory(mel)
endif ()

if (MMSOLVER_BUILD_DOCS)
  add_subdirectory(docs)
endif ()

if (MMSOLVER_BUILD_TESTS)
  add_subdirectory(tests)
endif ()


# Install misc files
#
# NOTE: ${MODULE_FULL_NAME} comes from share/module sub-directory.
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


# Use CPack (part of CMake) to generate the packages...
# If 'CPack' is not included, the 'packages' target will not be generated.
include(CPack)
