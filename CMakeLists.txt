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

# Project configuration.
project(mayaMatchMoveSolver)
set(PROJECT_VERSION_MAJOR 0)
set(PROJECT_VERSION_MINOR 4)
set(PROJECT_VERSION_PATCH 0)
set(PROJECT_VERSION_TWEAK alpha8)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}.${PROJECT_VERSION_TWEAK}")
set(PROJECT_HOMEPAGE_URL "https://github.com/david-cattermole/mayaMatchMoveSolver")
set(PROJECT_DESCRIPTION "Bundle Adjustment solver for MatchMove tasks in Autodesk Maya.")
set(PROJECT_AUTHOR "David Cattermole and others (see AUTHORS.txt file)")
set(PROJECT_COPYRIGHT
  "2018-2022, David Cattermole, Anil Reddy, Kazuma Tonegawa, Patcha Saheb Binginapalli.")
enable_testing()


# Add custom modules to the module path
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
        ${CMAKE_CURRENT_SOURCE_DIR}/share/cmake/modules)


# Build options; What will we build?  This is used mostly for
# developer debug. If the developer is working on some Python code
# only, we don't need to wait for the Maya Plug-In to compute each
# time, so turn off the plugin.
option(BUILD_PLUGIN "Do you want to build the Maya plug-in?" ON)
option(BUILD_PYTHON "Do you want to build and install the Python API and tools?" ON)
option(BUILD_MEL "Do you want to build and install the MEL scripts and tools?" ON)
option(BUILD_3DEQUALIZER "Do you want to build and install 3DEqualizer scripts?" ON)
option(BUILD_SYNTHEYES "Do you want to build and install SynthEyes scripts?" ON)
option(BUILD_BLENDER "Do you want to build and install Blender add-on?" ON)
option(BUILD_QT_UI "Do you want to build the Qt UI files?" ON)
option(BUILD_MM_RENDERER "Do you want to build and install the MM Renderer?" OFF)
option(BUILD_DOCS "Do you want to build and install the documentation?" ON)
option(BUILD_ICONS "Do you want to build and install the icons?" ON)
option(BUILD_CONFIG "Do you want to build and install the config files?" ON)
option(BUILD_TESTS "Do you want to build the test files?" OFF)


# Maya SDK
set(MAYA_VERSION "2019" CACHE STRING "Maya version number")
set(MAYA_LOCATION "/usr/autodesk/maya${MAYA_VERSION}/" CACHE PATH "Maya install directory")
set(DEVKIT_LOCATION "/usr/autodesk/maya${MAYA_VERSION}/" CACHE PATH "Maya development kit (devkit) directory")
set(MAYA_INCLUDE_PATH "/usr/autodesk/maya${MAYA_VERSION}/include" CACHE PATH "Maya include directory")
set(MAYA_LIB_PATH "/usr/autodesk/maya${MAYA_VERSION}/lib" CACHE PATH "Maya library directory")


# # Google Log
# set(GLOG_ROOT "/usr/local" CACHE PATH "Glog directory")
# set(GLOG_INCLUDE_PATH "/usr/local/include" CACHE PATH "Glog include directory")
# set(GLOG_LIB_PATH "/usr/local/lib" CACHE PATH "Glog library directory")


# CMinpack
set(CMINPACK_ROOT "/usr/local" CACHE PATH "CMinpack directory")
set(CMINPACK_INCLUDE_PATH "/usr/local/include" CACHE PATH "CMinpack include directory")
set(CMINPACK_LIB_PATH "/usr/local/lib" CACHE PATH "CMinpack library directory")


# Ceres
set(CERES_ROOT "/usr/local" CACHE PATH "Ceres directory")
set(CERES_INCLUDE_PATH "/usr/local/include" CACHE PATH "Ceres include directory")
set(CERES_LIB_PATH "/usr/local/lib" CACHE PATH "Ceres library directory")


# OpenMVG
set(OPENMVG_ROOT "/usr/local" CACHE PATH "OpenMVG directory")


# DL-FCN
set(DLFCN_ROOT "/usr/local" CACHE PATH "dl-fcn directory")
set(DLFCN_INCLUDE_PATH "/usr/local/include" CACHE PATH "dl-fcn include directory")
set(DLFCN_LIB_PATH "/usr/local/lib" CACHE PATH "dl-fcn library directory")


# LDPK
set(LDPK_ROOT "/usr/local" CACHE PATH "LDPK directory")
set(LDPK_INCLUDE_PATH "/usr/local/include" CACHE PATH "LDPK include directory")
set(LDPK_LIB_PATH "/usr/local/lib" CACHE PATH "LDPK library directory")


# Default Solver to use.
set(PREFERRED_SOLVER "cminpack_lmder"
  CACHE STRING
  "Choices are cminpack_lm, cminpack_lmder or ceres. Which solver is used by default?")

# Set a default solver
set(DEFAULT_SOLVER ${PREFERRED_SOLVER})


include(MMSolverUtils)

# Build features
add_subdirectory(share)

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

if (BUILD_TESTS)
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
set(CPACK_PACKAGE_VERSION_TWEAK "${PROJECT_VERSION_TWEAK}")
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
