cmake_minimum_required(VERSION 2.8)

# Project configuration.
project(mayaMatchMoveSolver)
set(PROJECT_VERSION_MAJOR 0)
set(PROJECT_VERSION_MINOR 1)
set(PROJECT_VERSION_PATCH 0)
set(PROJECT_VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}")
set(PROJECT_HOMEPAGE_URL "https://github.com/david-cattermole/mayaMatchMoveSolver")
set(PROJECT_DESCRIPTION "Bundle Adjustment solver for MatchMove tasks in Autodesk Maya.")
set(PROJECT_AUTHOR "David Cattermole")

set(PLUGIN_NAME mmSolver)

# Compile Flags, Release flags come from the Autodesk Maya build
# scripts (and Visual Studio project files).
set(CMAKE_CXX_STANDARD 11)
if (MSVC)
    # For Visual Studio 11 2012
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /GS /W3 /Zc:wchar_t /Zi /fp:precise /WX- /Zc:forScope /GR /Gd /EHsc")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"OSWin_\" /D \"WIN32\" /D \"_WINDOWS\" /D \"_USRDLL\" /D \"NT_PLUGIN\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"_HAS_ITERATOR_DEBUGGING=0\" /D \"_SECURE_SCL=0\" /D \"_SECURE_SCL_THROWS=0\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"_SECURE_SCL_DEPRECATE=0\" /D \"_CRT_SECURE_NO_DEPRECATE\" /D \"TBB_USE_DEBUG=0\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"__TBB_LIB_NAME=tbb.lib\" /D \"Bits64_\" /D \"_WINDLL\"")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /D \"NT_PLUGIN\" /D \"REQUIRE_IOSTREAM\"")

    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS} /D \"_DEBUG\"")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Gm /Od /RTC1")

    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} /D \"NDEBUG\"")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Gy /Gm- /O2 /Ob1 /GF")

    # Must add the plug-in entry/exit points otherwise
    # the plug-in won't load.
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} /export:initializePlugin /export:uninitializePlugin")
else()
    # For Linux with GCC
    set(CMAKE_CXX_FLAGS_DEBUG "-std=c++0x -O0 -g -Wall")
    set(CMAKE_CXX_FLAGS_RELEASE "-std=c++0x -O3 -fPIC -fno-strict-aliasing -m64")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -DBits64_ -DUNIX -D_BOOL -DLINUX -DFUNCPROTO -D_GNU_SOURCE -DLINUX_64 -DREQUIRE_IOSTREAM")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -Wall -Wno-multichar -Wno-comment -Wno-sign-compare -funsigned-char -pthread -fopenmp")
    # '-ftemplate-depth-27', rather than '25' is required to compile under GCC 4.8.5.
    # '-ftemplate-depth-35', rather than '25' is required to compile under GCC 5.5.x.
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -Wno-deprecated -Wno-reorder -ftemplate-depth-35 -fno-gnu-keywords")
endif()

# Maya SDK
set(MAYA_VERSION "2017" CACHE STRING "Maya version number")
set(MAYA_INCLUDE_PATH "/usr/autodesk/maya${MAYA_VERSION}/include" CACHE PATH "Maya include directory")
set(MAYA_LIB_PATH "/usr/autodesk/maya${MAYA_VERSION}/lib" CACHE PATH "Maya library directory")

# Lev-Mar
set(LEVMAR_INCLUDE_PATH "/usr/local/include" CACHE PATH "Levmar include directory")
set(LEVMAR_LIB_PATH "/usr/local/lib" CACHE PATH "Levmar library directory")

# ATLAS
set(USE_ATLAS OFF CACHE BOOLEAN "Should we use ATLAS with Lev-Mar?")
set(ATLAS_LIB_PATH "/usr/lib64/atlas" CACHE PATH "ATLAS library directory")

# Intel Math Kernel Library
set(USE_MKL OFF CACHE BOOLEAN "Should we use MKL?")
set(MKL_LIB_PATH "/opt/intel/mkl/lib/intel64" CACHE PATH "Intel MKL library directory")

# Module paths
if (UNIX)
    set(MODULE_OS_NAME linux)
elseif(MSVC)
    set(MODULE_OS_NAME win64)
else()
    message(FATAL_ERROR "Only Linux and Windows are supported.")
endif()

set(MODULE_NAME "${PROJECT_NAME}-${PROJECT_VERSION}")
set(MODULE_FULL_NAME "${MODULE_NAME}-maya${MAYA_VERSION}-${MODULE_OS_NAME}")
set(MODULE_BUILD_DIR "${CMAKE_BINARY_DIR}/${MODULE_FULL_NAME}")

# Create Module Description file.
configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/modules/mayaMatchMoveSolver.mod
        ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_FULL_NAME}.mod
        @ONLY)

# Source
set(SOURCE_FILES
        include/utilities/debugUtils.h
        include/nodeTypeIds.h
        include/mayaUtils.h
        include/mmSolver.h
        include/mmSolverLevMar.h
        include/Camera.h
        include/Marker.h
        include/Bundle.h
        include/Attr.h
        include/MMMarkerScaleNode.h
        include/MMReprojectionNode.h
        include/MMMarkerGroupTransformNode.h
        include/MMTestCameraMatrixCmd.h
        include/MMSolverCmd.h
        src/mmSolver.cpp
        src/mmSolverLevMar.cpp
        src/Camera.cpp
        src/Marker.cpp
        src/Bundle.cpp
        src/Attr.cpp
        src/MMMarkerScaleNode.cpp
        src/MMReprojectionNode.cpp
        src/MMMarkerGroupTransformNode.cpp
        src/MMTestCameraMatrixCmd.cpp
        src/MMSolverCmd.cpp
        src/pluginMain.cpp
)

include_directories(
        include
        ${LEVMAR_INCLUDE_PATH}
        ${MAYA_INCLUDE_PATH}
)

link_directories(
        ${LIBRARY_OUTPUT_PATH}
        ${LEVMAR_LIB_PATH}
        ${MAYA_LIB_PATH}
)

# 'mmSolver' maya plugin library
add_library(${PLUGIN_NAME} SHARED ${SOURCE_FILES})
target_link_libraries(${PLUGIN_NAME}
        OpenMaya
        OpenMayaAnim
        Foundation
        levmar)

# On Linux the 'm' library is required.
if (UNIX)
    target_link_libraries(${PLUGIN_NAME} m)
endif()

# Atlas
if (USE_ATLAS)
    if(USE_MKL)
        message(FATAL_ERROR "Cannot use both Atlas and Intel MKL, please change USE_MKL or USE_ATLAS to OFF.")
    endif()
    link_directories(
        ${ATLAS_LIB_PATH}
        )
    target_link_libraries(${PLUGIN_NAME}
            lapack
            satlas  # serial compiled library, not threaded
            )
endif()

# Intel MKL
if (USE_MKL)
    if(USE_ATLAS)
        message(FATAL_ERROR "Cannot use both Atlas and Intel MKL, please change USE_MKL or USE_ATLAS to OFF.")
    endif()
    link_directories(
        ${MKL_LIB_PATH}
        )
    target_link_libraries(${PLUGIN_NAME}
            mkl_core
            mkl_def
            mkl_gf_lp64
            mkl_gnu_thread
            mkl_intel_lp64
            mkl_intel_thread
            mkl_mc
            mkl_sequential)
endif()

# no 'lib' prefix to .so files
set_target_properties(${PLUGIN_NAME} PROPERTIES
        PREFIX ""
        )

# On Windows, the Maya Plug-In file extension is '.mll', not '.dll'.
if (WIN32)
    set_target_properties(${PLUGIN_NAME} PROPERTIES
        SUFFIX ".mll"
        )
endif()

# Output to the Module plug-ins directory.
#
# On Windows, the Plug-In is treated as a 'RUNTIME' type,
# on Linux, it's a 'LIBRARY' type.
set_target_properties(${PLUGIN_NAME} PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}"
        LIBRARY_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}"
        ARCHIVE_OUTPUT_DIRECTORY "${MODULE_FULL_NAME}"
        )

# Install the Module Description file.
install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_FULL_NAME}.mod
        DESTINATION "./")

# Install the Plug-In.
install(TARGETS ${PLUGIN_NAME}
        RUNTIME DESTINATION "${MODULE_FULL_NAME}/plug-ins"
        LIBRARY DESTINATION "${MODULE_FULL_NAME}/plug-ins")

# Install Python API and tools
install(DIRECTORY "python/"
        DESTINATION "${MODULE_FULL_NAME}/python"
        FILES_MATCHING PATTERN "*.py")

# Install Maya MEL and Python scripts.
install(DIRECTORY "mel/"
        DESTINATION "${MODULE_FULL_NAME}/scripts"
        FILES_MATCHING PATTERN "*.mel")
install(DIRECTORY "mel/"
        DESTINATION "${MODULE_FULL_NAME}/scripts"
        FILES_MATCHING PATTERN "*.py")
install(DIRECTORY "mel/AETemplates/"
        DESTINATION "${MODULE_FULL_NAME}/scripts/AETemplates"
        FILES_MATCHING PATTERN "*.mel")

# Install 3DEqualizer scripts.
install(DIRECTORY "3dequalizer/scriptdb/"
        DESTINATION "${MODULE_FULL_NAME}/3dequalizer"
        FILES_MATCHING PATTERN "*.py")

# Install Icons.
install(DIRECTORY "icons/"
        DESTINATION "${MODULE_FULL_NAME}/icons"
        FILES_MATCHING PATTERN "*.png"
        PATTERN "icons/edit" EXCLUDE
        PATTERN "icons/library" EXCLUDE)
install(DIRECTORY "icons/"
        DESTINATION "${MODULE_FULL_NAME}/icons"
        FILES_MATCHING PATTERN "*.svg"
        PATTERN "icons/edit" EXCLUDE
        PATTERN "icons/library" EXCLUDE)

# Install Documentation
install(DIRECTORY "docs/build/html/"
        DESTINATION "${MODULE_FULL_NAME}/docs/html")

# Install misc files
install(FILES
        ${CMAKE_CURRENT_SOURCE_DIR}/LICENSE
        ${CMAKE_CURRENT_SOURCE_DIR}/README.md
        DESTINATION "${MODULE_FULL_NAME}/")

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
endif()

# TODO: Set up proper 'source' package file inclusion rules.
# # set(CPACK_SOURCE_GENERATOR "TGZ")
# # set(CPACK_SOURCE_PACKAGE_FILE_NAME "${MODULE_NAME}-Source")

# Use CPack (part of CMake) to generate the packages...
# If 'CPack' is not included, the 'packages' target will not be generated.
include(CPack)
