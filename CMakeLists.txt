# Copyright (C) 2019 David Cattermole.
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
cmake_minimum_required(VERSION 2.8)


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
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
        ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules)


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
set(MAYA_INCLUDE_PATH "/usr/autodesk/maya${MAYA_VERSION}/include" CACHE PATH
        "Maya include directory")
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


# Module paths
if (UNIX)
    set(MODULE_OS_NAME linux)
elseif (MSVC)
    set(MODULE_OS_NAME win64)
else ()
    message(FATAL_ERROR "Only Linux and Windows are supported.")
endif ()


# Module names
set(MODULE_NAME "${PROJECT_NAME}-${PROJECT_VERSION}")
set(MODULE_FULL_NAME "${MODULE_NAME}-maya${MAYA_VERSION}-${MODULE_OS_NAME}")
set(MODULE_BUILD_DIR "${CMAKE_BINARY_DIR}/${MODULE_FULL_NAME}")


# Set a default solver
set(DEFAULT_SOLVER ${PREFERRED_SOLVER})
if ((USE_GPL_LEVMAR EQUAL 1) AND (USE_CMINPACK EQUAL 1))
    # Support both levmar and cminpack.
elseif ((USE_CMINPACK EQUAL 1) AND (USE_GPL_LEVMAR EQUAL 0))
    if (NOT (DEFAULT_SOLVER MATCHES "cminpack_lm[a-zA-Z]+"))
        message(WARNING
                "Preferred solver cannot be used because it's not enabled. "
                "preferred=${PREFERRED_SOLVER} "
                "default=${DEFAULT_SOLVER} "
                "use_cminpack=${USE_CMINPACK} "
                "use_gpl_levmar=${USE_GPL_LEVMAR}"
                )
        set(DEFAULT_SOLVER "cminpack_lm")
    endif ()
elseif ((USE_GPL_LEVMAR EQUAL 1) AND (USE_CMINPACK EQUAL 0))
    if (NOT (DEFAULT_SOLVER STREQUAL "levmar"))
        message(WARNING
                "Preferred solver cannot be used because it's not enabled. "
                "preferred=${PREFERRED_SOLVER} "
                "default=${DEFAULT_SOLVER} "
                "use_cminpack=${USE_CMINPACK} "
                "use_gpl_levmar=${USE_GPL_LEVMAR}"
                )
        set(DEFAULT_SOLVER "levmar")
    endif ()
else ()
    message(FATAL_ERROR
            " Solver is not available! "
            "preferred=${PREFERRED_SOLVER} "
            "default=${DEFAULT_SOLVER} "
            "use_cminpack=${USE_CMINPACK} "
            "use_gpl_levmar=${USE_GPL_LEVMAR}"
            )
endif ()


# Create Module Description file.
if (UNIX)
    configure_file(
            ${CMAKE_CURRENT_SOURCE_DIR}/modules/mayaMatchMoveSolver_linux.mod
            ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_FULL_NAME}.mod
            @ONLY)
elseif (MSVC)
    configure_file(
            ${CMAKE_CURRENT_SOURCE_DIR}/modules/mayaMatchMoveSolver_windows.mod
            ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_FULL_NAME}.mod
            @ONLY)
else ()
    message(FATAL_ERROR "Only Linux and Windows are supported.")
endif ()


# Create Python file with some build options baked in.
if (BUILD_PYTHON)
    configure_file(
            ${CMAKE_CURRENT_SOURCE_DIR}/python/mmSolver/constant.py.in
            ${CMAKE_CURRENT_SOURCE_DIR}/python/mmSolver/constant.py
            @ONLY)
endif ()


# Create C Header file with some build options baked in.
if (BUILD_PLUGIN)
    configure_file(
            ${CMAKE_CURRENT_SOURCE_DIR}/include/buildConstant.h.in
            ${CMAKE_CURRENT_SOURCE_DIR}/include/buildConstant.h
            @ONLY)
endif ()


# Create Python file for documentation sphinx build with some build
# options baked in.
if (BUILD_PYTHON)
    configure_file(
            ${CMAKE_CURRENT_SOURCE_DIR}/docs/source/conf.py.in
            ${CMAKE_CURRENT_SOURCE_DIR}/docs/source/conf.py
            @ONLY)
endif ()


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
        src/renderer/MMRendererCmd.cpp
        src/renderer/QuadRenderBase.cpp
        src/renderer/QuadRenderEdgeDetect.cpp
        src/renderer/QuadRenderBlend.cpp
        src/renderer/QuadRenderInvert.cpp
        src/renderer/HudRender.cpp
        src/renderer/PresentTarget.cpp
        src/renderer/SceneRender.cpp
        src/renderer/MMRendererMainOverride.cpp
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
    add_library(mmSolver SHARED ${SOURCE_FILES})
    target_include_directories(mmSolver
            PRIVATE include
            PRIVATE src
            PUBLIC ${MAYA_INCLUDE_DIRS}
            )
    target_link_libraries(mmSolver
            ${MAYA_OpenMaya_LIBRARY}
            ${MAYA_OpenMayaAnim_LIBRARY}
            ${MAYA_OpenMayaRender_LIBRARY}
            ${MAYA_OpenMayaUI_LIBRARY}
            ${MAYA_Foundation_LIBRARY}
            )

    if (USE_GPL_LEVMAR)
        message(WARNING
                "'levmar' library is licensed under GNU GPL and therefore this library "
                "must not be distributed in binary form.")
        target_include_directories(mmSolver PUBLIC ${LEVMAR_INCLUDE_DIRS})
        target_link_libraries(mmSolver ${LEVMAR_LIBRARIES})
        add_definitions(-DUSE_SOLVER_LEVMAR)
    endif ()

    if (USE_CMINPACK)
        target_include_directories(mmSolver PUBLIC ${CMINPACK_INCLUDE_DIRS})
        target_link_libraries(mmSolver ${CMINPACK_LIBRARIES})
        add_definitions(-DUSE_SOLVER_CMINPACK)
    endif ()

    # On Linux the 'm' library is required.
    if (UNIX)
        target_link_libraries(mmSolver m)
    endif ()

    # no 'lib' prefix to Maya plugin .so files
    set_target_properties(mmSolver PROPERTIES PREFIX "")

    # On MacOS, the Maya Plug-In file extension is '.bundle'.
    # On Windows, the Maya Plug-In file extension is '.mll', not '.dll'.
    if (APPLE)
        set(MAYA_PLUGIN_SUFFIX ".bundle")
    elseif (WIN32)
        set_target_properties(mmSolver PROPERTIES SUFFIX ".mll")
    endif ()

    # HACK: On Linux, LD_LIBRARY_PATH cannot be modified at runtime (on
    # Windows it can), therefore the .mod files *can* change
    # LD_LIBRARY_PATH, but the changes are not used by 'ld.so', which
    # resolves the library path. Therefore, to make sure the the libraries
    # in <module root>/lib are searched for libraries, we add a relative
    # directory 'RPATH' to the library which tells the library resolution
    # to search in the 'lib' directory inside the module root. Note: Linux
    # does not allow run-time changes for security reasons.
    if (UNIX)
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
endif ()


# Install the Module Description file.
install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_FULL_NAME}.mod
        DESTINATION "./")


if (BUILD_PLUGIN)
    # Install the Plug-In.
    install(TARGETS mmSolver
            RUNTIME DESTINATION "${MODULE_FULL_NAME}/plug-ins"
            LIBRARY DESTINATION "${MODULE_FULL_NAME}/plug-ins")


    # Install dynamic libraries; cminpack
    if (USE_CMINPACK AND CMINPACK_FOUND)
        if (WIN32)
            if (EXISTS ${CMINPACK_LIBRARY_DLL})
                install(FILES ${CMINPACK_LIBRARY_DLL}
                        DESTINATION "${MODULE_FULL_NAME}/lib/")
            else ()
                install(FILES ${CMINPACK_LIBRARY}
                        DESTINATION "${MODULE_FULL_NAME}/lib/")
            endif ()
        elseif (UNIX)
            # Install both symlink and real library
            get_filename_component(ABS_CMINPACK_LIBRARY ${CMINPACK_LIBRARY} REALPATH)
            install(FILES ${CMINPACK_LIBRARY}
                    DESTINATION "${MODULE_FULL_NAME}/lib/")
            install(FILES ${ABS_CMINPACK_LIBRARY}
                    DESTINATION "${MODULE_FULL_NAME}/lib/")
        endif ()
    endif ()

    # Install dynamic libraries; levmar
    if (USE_GPL_LEVMAR AND LEVMAR_FOUND)
        if (WIN32)
            if (EXISTS ${LEVMAR_LIBRARY_DLL})
                install(FILES ${LEVMAR_LIBRARY_DLL}
                        DESTINATION "${MODULE_FULL_NAME}/lib/")
            else ()
                install(FILES ${LEVMAR_LIBRARY}
                        DESTINATION "${MODULE_FULL_NAME}/lib/")
            endif ()
        elseif (UNIX)
            # Install both symlink and real library
            get_filename_component(ABS_LEVMAR_LIBRARY ${LEVMAR_LIBRARY} REALPATH)
            install(FILES ${LEVMAR_LIBRARY}
                    DESTINATION "${MODULE_FULL_NAME}/lib/")
            install(FILES ${ABS_LEVMAR_LIBRARY}
                    DESTINATION "${MODULE_FULL_NAME}/lib/")
        endif ()
    endif ()
endif ()


# Install Qt.py, if exists.
set(QTPY_FILE "${CMAKE_SOURCE_DIR}/external/install/qtpy/Qt.py")
if (EXISTS ${QTPY_FILE})
    install(FILES ${QTPY_FILE}
            DESTINATION "${MODULE_FULL_NAME}/python_qtpy/")
endif ()


# Install Python API and tools
if (BUILD_PYTHON)
    install(DIRECTORY "python/"
            DESTINATION "${MODULE_FULL_NAME}/python"
            FILES_MATCHING PATTERN "*.py")
endif ()


# Install Maya MEL and Python scripts.
if (BUILD_MEL)
    install(DIRECTORY "mel/"
            DESTINATION "${MODULE_FULL_NAME}/scripts"
            FILES_MATCHING PATTERN "*.mel")
    install(DIRECTORY "mel/"
            DESTINATION "${MODULE_FULL_NAME}/scripts"
            FILES_MATCHING PATTERN "*.py")
    install(DIRECTORY "mel/AETemplates/"
            DESTINATION "${MODULE_FULL_NAME}/scripts/AETemplates"
            FILES_MATCHING PATTERN "*.mel")
endif ()


# Install 3DEqualizer scripts.
install(DIRECTORY "3dequalizer/scriptdb/"
        DESTINATION "${MODULE_FULL_NAME}/3dequalizer"
        FILES_MATCHING PATTERN "*.py")


# Install SynthEyes scripts.
install(DIRECTORY "syntheyes/"
        DESTINATION "${MODULE_FULL_NAME}/syntheyes"
        FILES_MATCHING PATTERN "*.szl")


# Install Config.
if (BUILD_CONFIG)
    install(DIRECTORY "config/"
            DESTINATION "${MODULE_FULL_NAME}/config"
            FILES_MATCHING PATTERN "*.json")
endif ()


# Install Icons.
if (BUILD_ICONS)
    install(DIRECTORY "icons/"
            DESTINATION "${MODULE_FULL_NAME}/resources"
            FILES_MATCHING PATTERN "*.rcc"
            PATTERN "icons/edit" EXCLUDE
            PATTERN "icons/library" EXCLUDE
            PATTERN "icons/ui" EXCLUDE)
    install(DIRECTORY "icons/"
            DESTINATION "${MODULE_FULL_NAME}/icons"
            FILES_MATCHING PATTERN "*.png"
            PATTERN "icons/edit" EXCLUDE
            PATTERN "icons/library" EXCLUDE
            PATTERN "icons/ui" EXCLUDE)
    install(DIRECTORY "icons/"
            DESTINATION "${MODULE_FULL_NAME}/icons"
            FILES_MATCHING PATTERN "*.svg"
            PATTERN "icons/edit" EXCLUDE
            PATTERN "icons/library" EXCLUDE
            PATTERN "icons/ui" EXCLUDE)
endif ()


# Install Documentation
if (BUILD_DOCS)
    install(DIRECTORY "docs/build/html/"
            DESTINATION "${MODULE_FULL_NAME}/docs/html")
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

add_subdirectory(shader)

if (BUILD_PYTHON)
    add_subdirectory(python)
endif ()

if (BUILD_DOCS)
    add_subdirectory(docs)
endif ()

if (BUILD_ICONS)
    add_subdirectory(icons)
endif ()

if (BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif ()
