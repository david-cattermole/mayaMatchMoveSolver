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
set(PROJECT_VERSION_PATCH 6)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}")
set(PROJECT_HOMEPAGE_URL "https://github.com/david-cattermole/mayaMatchMoveSolver")
set(PROJECT_DESCRIPTION "Bundle Adjustment solver for MatchMove tasks in Autodesk Maya.")
set(PROJECT_AUTHOR "David Cattermole and others (see AUTHORS.txt file)")
set(PROJECT_COPYRIGHT "2018, 2019, 2020, David Cattermole, Anil Reddy.")


# Add custom modules to the module path
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules)


# Build options; What will we build?  This is used mostly for
# developer debug. If the developer is working on some Python code
# only, we don't need to wait for the Maya Plug-In to compute each
# time.
set(BUILD_PLUGIN 1 CACHE BOOLEAN "Do you want to build the plug-in?")
set(BUILD_PYTHON 1 CACHE BOOLEAN "Do you want to build and install the Python API and tools?")
set(BUILD_MEL 1 CACHE BOOLEAN "Do you want to build and install the MEL scripts and tools?")
set(BUILD_3DEQUALIZER 1 CACHE BOOLEAN "Do you want to build and install 3DEqualizer scripts?")
set(BUILD_SYNTHEYES 1 CACHE BOOLEAN "Do you want to build and install SynthEyes scripts?")
set(BUILD_QT_UI 1 CACHE BOOLEAN "Do you want to build the Qt UI files?")
set(BUILD_DOCS 1 CACHE BOOLEAN "Do you want to build and install the documentation?")
set(BUILD_ICONS 1 CACHE BOOLEAN "Do you want to build and install the icons?")
set(BUILD_CONFIG 1 CACHE BOOLEAN "Do you want to build and install the config files?")
set(BUILD_TESTS 1 CACHE BOOLEAN "Do you want to build the test files?")


# Maya SDK
set(MAYA_VERSION "2017" CACHE STRING "Maya version number")
set(MAYA_LOCATION "/usr/autodesk/maya${MAYA_VERSION}/" CACHE PATH "Maya install directory")
set(DEVKIT_LOCATION "/usr/autodesk/maya${MAYA_VERSION}/" CACHE PATH "Maya development kit (devkit) directory")
set(MAYA_INCLUDE_PATH "/usr/autodesk/maya${MAYA_VERSION}/include" CACHE PATH "Maya include directory")
set(MAYA_LIB_PATH "/usr/autodesk/maya${MAYA_VERSION}/lib" CACHE PATH "Maya library directory")


# Lev-Mar
#
# WARNING: 'Lev-Mar' is GPL licensed and must not be
# distributed in binary form to anyone.
set(USE_GPL_LEVMAR 0 CACHE BOOLEAN "Compile with the GPL-licensed Lev-Mar library?")
set(LEVMAR_ROOT "/usr/local" CACHE PATH "Levmar directory")
set(LEVMAR_INCLUDE_PATH "/usr/local/include" CACHE PATH "Levmar include directory")
set(LEVMAR_LIB_PATH "/usr/local/lib" CACHE PATH "Levmar library directory")


# CMinpack
set(USE_CMINPACK 1 CACHE BOOLEAN "Compile with the cminpack library?")
set(CMINPACK_ROOT "/usr/local" CACHE PATH "CMinpack directory")
set(CMINPACK_INCLUDE_PATH "/usr/local/include" CACHE PATH "cminpack include directory")
set(CMINPACK_LIB_PATH "/usr/local/lib" CACHE PATH "cminpack library directory")


# Extra (BLAS) Libraries
set(USE_BLAS OFF CACHE BOOLEAN "Should we use BLAS?")
set(BLAS_INCLUDE_PATH "/usr/include/blas" CACHE PATH "BLAS library directory")
set(BLAS_LIB_PATH "/usr/lib64/blas" CACHE PATH "BLAS library directory")
set(BLAS_LIB_NAMES "" CACHE STRING "BLAS libraries to link")

# Default Solver to use.
set(PREFERRED_SOLVER "cminpack_lmder" CACHE STRING "Choices are cminpack_lm, cminpack_lmder or levmar. Which solver is used by default?")

include(MMSolverUtils)

if(MSVC)
  add_compile_options(/W4 /WX)
else()
  add_compile_options(-W -Wall -Werror -Wpedantic)
endif()

# Build features
add_subdirectory(modules)

# add_subdirectory(external)

if (BUILD_PLUGIN)
  add_subdirectory(python)
endif ()

if (BUILD_PYTHON)
  add_subdirectory(python)
endif ()

<<<<<<< Updated upstream

# Source
set(SOURCE_FILES
        include/utilities/debugUtils.h
        include/nodeTypeIds.h
        src/core/reprojection.h
        src/core/reprojection.cpp
        src/core/bundleAdjust_defines.h
        src/core/bundleAdjust_base.h
        src/core/bundleAdjust_base.cpp
        src/core/bundleAdjust_relationships.h
        src/core/bundleAdjust_relationships.cpp
        src/core/bundleAdjust_solveFunc.h
        src/core/bundleAdjust_solveFunc.cpp
        src/core/bundleAdjust_levmar_bc_dif.h
        src/core/bundleAdjust_levmar_bc_dif.cpp
        src/core/bundleAdjust_cminpack_base.h
        src/core/bundleAdjust_cminpack_base.cpp
        src/core/bundleAdjust_cminpack_lmdif.h
        src/core/bundleAdjust_cminpack_lmdif.cpp
        src/core/bundleAdjust_cminpack_lmder.h
        src/core/bundleAdjust_cminpack_lmder.cpp
        src/mayaUtils.h
        src/Camera.h
        src/Camera.cpp
        src/Marker.h
        src/Marker.cpp
        src/Bundle.h
        src/Bundle.cpp
        src/Attr.h
        src/Attr.cpp
        src/commonArgFlags.h
        src/commonArgFlags.cpp
        src/MMSolverAffectsCmd.h
        src/MMSolverAffectsCmd.cpp
        src/MMMarkerScaleNode.h
        src/MMMarkerScaleNode.cpp
        src/MMReprojectionNode.h
        src/MMReprojectionNode.cpp
        src/MMMarkerGroupTransformNode.h
        src/MMMarkerGroupTransformNode.cpp
        src/MMTestCameraMatrixCmd.h
        src/MMTestCameraMatrixCmd.cpp
        src/MMSolverCmd.h
        src/MMSolverCmd.cpp
        src/MMSolverTypeCmd.h
        src/MMSolverTypeCmd.cpp
        src/MMReprojectionCmd.h
        src/MMReprojectionCmd.cpp
        src/pluginMain.cpp
        )


# Find external packages
find_package(Maya REQUIRED)
find_package(LevMar)
find_package(CMinpack)


# Compile Flags.
#
# Release flags come from the Autodesk Maya build scripts (and
# Visual Studio project files).
if (MSVC)
    # For Visual Studio 11 2012
    set(CMAKE_CXX_FLAGS "")  # Zero out the C++ flags, we have complete control.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GS /W4 /Zc:wchar_t /Zi /fp:precise /WX- /Zc:forScope /GR /Gd /EHsc")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"OSWin_\" /D \"WIN32\" /D \"_WINDOWS\" /D \"_USRDLL\" /D \"NT_PLUGIN\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"_HAS_ITERATOR_DEBUGGING=0\" /D \"_SECURE_SCL=0\" /D \"_SECURE_SCL_THROWS=0\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"_SECURE_SCL_DEPRECATE=0\" /D \"_CRT_SECURE_NO_DEPRECATE\" /D \"TBB_USE_DEBUG=0\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"__TBB_LIB_NAME=tbb.lib\" /D \"Bits64_\" /D \"_WINDLL\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"NT_PLUGIN\" /D \"REQUIRE_IOSTREAM\"")

    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS} /D \"_DEBUG\"")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /MDd /Gm /Od /RTC1")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Ob0 /GR /GL /Oi /Gy /Zi /EHsc")

    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} /D \"NDEBUG\"")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Gy /Gm- /O2 /Ob1 /GF")

    # Must add the plug-in entry/exit points otherwise
    # the plug-in won't load.
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} /export:initializePlugin /export:uninitializePlugin")
else (APPLE)
    # For MacOS with Clang (which is the supported compiler for Maya
    # 2018+)
    set(CMAKE_CXX_FLAGS "")  # Zero out the C++ flags, we have complete control.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -arch x86_64")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x  -stdlib=libc++")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-multichar -Wno-comment -Wno-sign-compare")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated -Wno-reorder")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -ftemplate-depth-35 -fno-gnu-keywords")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -funsigned-char -fpascal-strings")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DCC_GNU_ -DOSMac_ -DOSMacOSX_ -DOSMac_MachO_ -D_LANGUAGE_C_PLUS_PLUS -mmacosx-version-min=10.8")

    # Special MacOS linking stuff
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -headerpad_max_install_names")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework System")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework SystemConfiguration")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework CoreServices")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework Carbon")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework Cocoa")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework ApplicationServices")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -framework IOKit")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -bundle")

    set(CMAKE_CXX_FLAGS_DEBUG "-O0 -g")
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -fPIC -fno-strict-aliasing -m64")
else ()
    # For Linux with GCC
    set(CMAKE_CXX_FLAGS "")  # Zero out the C++ flags, we have complete control.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-multichar -Wno-comment -Wno-sign-compare")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -funsigned-char -pthread -fopenmp")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DBits64_ -DUNIX -D_BOOL -DLINUX -DFUNCPROTO -D_GNU_SOURCE -DLINUX_64 -DREQUIRE_IOSTREAM")
    # '-ftemplate-depth-27', rather than '25' is required to compile under GCC 4.8.5.
    # '-ftemplate-depth-35', rather than '25' is required to compile under GCC 5.5.x.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated -Wno-reorder -ftemplate-depth-35 -fno-gnu-keywords")
    set(CMAKE_CXX_FLAGS_DEBUG "-O0 -g")
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -fPIC -fno-strict-aliasing -m64")
endif ()


function(add_target_link_library_names target names)
    string(STRIP ${names} names_strip)
    string(REPLACE " " ";" names_list ${names_strip})
    foreach (name IN LISTS names_list)
        target_link_libraries(${target} ${name})
    endforeach ()
endfunction()


if (BUILD_PLUGIN)
    # 'mmSolver' maya plugin library
    if (APPLE)
      add_library(mmSolver MODULE ${SOURCE_FILES})
    else ()
      add_library(mmSolver SHARED ${SOURCE_FILES})
    endif ()
    target_include_directories(mmSolver
            PRIVATE include
            PRIVATE src
            PUBLIC ${MAYA_INCLUDE_DIRS}
            )
    target_link_libraries(mmSolver
            ${MAYA_OpenMaya_LIBRARY}
            ${MAYA_OpenMayaAnim_LIBRARY}
            ${MAYA_Foundation_LIBRARY}
            )

    if (USE_GPL_LEVMAR)
        message(WARNING
                "'levmar' library is licensed under GNU GPL and therefore this library "
                "must not be distributed in binary form.")
        target_include_directories(mmSolver PUBLIC ${LEVMAR_INCLUDE_DIRS})
        target_link_libraries(mmSolver ${LEVMAR_LIBRARIES})
        add_definitions(-DUSE_SOLVER_LEVMAR)


        if(CMAKE_SYSTEM_NAME STREQUAL Darwin)
            # To locate Levmar from the mmSolver dynamic library we
            # must change the "install name" to a path relative to the
            # loaded bundle.
            #
            # Run:
            # $ install_name_tool -change liblevmar.dylib @loader_path/../lib/liblevmar.dylib mmSolver.bundle
            #
            # NOTE: If ${LEVMAR_LIBRARIES} has more than one library,
            #  this command will fail.
            #
            get_filename_component(LEVMAR_LIBRARY_NAME ${LEVMAR_LIBRARIES} NAME)
            add_custom_command(TARGET mmSolver
                POST_BUILD COMMAND
                ${CMAKE_INSTALL_NAME_TOOL} -change ${LEVMAR_LIBRARIES} @loader_path/../lib/${LEVMAR_LIBRARIES}
                $<TARGET_FILE:mmSolver>
            )
        endif()
    endif ()


    if (USE_CMINPACK)
        target_include_directories(mmSolver PUBLIC ${CMINPACK_INCLUDE_DIRS})
        target_link_libraries(mmSolver ${CMINPACK_LIBRARIES})
        add_definitions(-DUSE_SOLVER_CMINPACK)

        if(CMAKE_SYSTEM_NAME STREQUAL Darwin)
            # To locate CMinpack from the mmSolver dynamic library we
            # must change the "install name" to a path relative to the
            # loaded bundle.
            #
            # Run:
            # $ install_name_tool -change libcminpack.1.dylib @loader_path/../lib/libcminpack.1.dylib mmSolver.bundle
            #
            # NOTE: If ${CMINPACK_LIBRARIES} has more than one library,
            #  this command will fail.
            #
            get_filename_component(CMINPACK_LIBRARY_NAME ${CMINPACK_LIBRARIES} NAME)
            add_custom_command(TARGET mmSolver
                POST_BUILD COMMAND
                ${CMAKE_INSTALL_NAME_TOOL} -change ${CMINPACK_LIBRARY_NAME} @loader_path/../lib/${CMINPACK_LIBRARY_NAME}
                $<TARGET_FILE:mmSolver>
            )
        endif()
    endif ()

    # On Linux the 'm' library is required.
    if(CMAKE_SYSTEM_NAME STREQUAL Linux)
        target_link_libraries(mmSolver m)
    endif ()

    # no 'lib' prefix to Maya plugin .so files
    set_target_properties(mmSolver PROPERTIES PREFIX "")

    # On Linux, the Maya Plug-In file extension is '.so'.
    # On MacOS, the Maya Plug-In file extension is '.bundle'.
    # On Windows, the Maya Plug-In file extension is '.mll', not '.dll'.
    set(MAYA_PLUGIN_SUFFIX ".so")
    if (APPLE)
        set(MAYA_PLUGIN_SUFFIX ".bundle")
    elseif (WIN32)
        set(MAYA_PLUGIN_SUFFIX ".mll")
    else()
        message(FATAL_ERROR "Only Linux, MacOS and Windows are supported.")
    endif ()
    set_target_properties(mmSolver PROPERTIES SUFFIX ${MAYA_PLUGIN_SUFFIX})

    if(CMAKE_SYSTEM_NAME STREQUAL Linux)
        # HACK: On Linux, LD_LIBRARY_PATH cannot be modified at runtime (on
        # Windows it can), therefore the .mod files *can* change
        # LD_LIBRARY_PATH, but the changes are not used by 'ld.so', which
        # resolves the library path. Therefore, to make sure the the libraries
        # in <module root>/lib are searched for libraries, we add a relative
        # directory 'RPATH' to the library which tells the library resolution
        # to search in the 'lib' directory inside the module root. Note: Linux
        # does not allow run-time changes for security reasons.

        # We must escape the '$' symbol to make sure it is passed to the
        # compiler.
        set_target_properties(mmSolver PROPERTIES
                BUILD_WITH_INSTALL_RPATH ON
                INSTALL_RPATH "\$ORIGIN/../lib"
                )
    endif ()

    # Output to the Module plug-ins directory.
    #
    # On Windows, the Plug-In is treated as a 'RUNTIME' type,
    # on Linux, it's a 'LIBRARY' type.
    set_target_properties(mmSolver PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}"
            LIBRARY_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}"
            ARCHIVE_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}")
=======
if (BUILD_MEL)
  add_subdirectory(mel)
>>>>>>> Stashed changes
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
SET(CPACK_OUTPUT_FILE_PREFIX "../packages")
if (WIN32 AND NOT UNIX)
  # .zip file for Windows.
  set(CPACK_GENERATOR "ZIP")
elseif (UNIX AND NOT WIN32)
  # .tar.gz for Linux.
  set(CPACK_GENERATOR "TGZ")
endif ()


# TODO: Set up proper 'source' package file inclusion rules.
# # set(CPACK_SOURCE_GENERATOR "TGZ")
# # set(CPACK_SOURCE_PACKAGE_FILE_NAME "${MODULE_NAME}-Source")

# Use CPack (part of CMake) to generate the packages...
# If 'CPack' is not included, the 'packages' target will not be generated.
include(CPack)
