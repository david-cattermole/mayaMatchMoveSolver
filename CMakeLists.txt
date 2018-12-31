cmake_minimum_required(VERSION 2.8)
project(mayaMatchMoveSolver)
set(CMD_NAME mmSolver)
set(CMAKE_CXX_STANDARD 11)

# Compile Flags, Release flags come from the Autodesk Maya build
# scripts (and Visual Studio project files).
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
set(MAYA_INCLUDE_PATH "/usr/autodesk/maya2017/include" CACHE PATH "Maya include directory")
set(MAYA_LIB_PATH "/usr/autodesk/maya2017/lib" CACHE PATH "Maya library directory")

# Lev-Mar
set(LEVMAR_INCLUDE_PATH "/usr/local/include" CACHE PATH "Levmar include directory")
set(LEVMAR_LIB_PATH "/usr/local/lib" CACHE PATH "Levmar library directory")

# ATLAS
set(USE_ATLAS OFF CACHE BOOLEAN "Should we use ATLAS with Lev-Mar?")
set(ATLAS_LIB_PATH "/usr/lib64/atlas" CACHE PATH "ATLAS library directory")

# Intel Math Kernel Library
set(USE_MKL OFF CACHE BOOLEAN "Should we use MKL?")
set(MKL_LIB_PATH "/opt/intel/mkl/lib/intel64" CACHE PATH "Intel MKL library directory")

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
add_library(${CMD_NAME} SHARED ${SOURCE_FILES})
target_link_libraries(${CMD_NAME}
        OpenMaya
        OpenMayaAnim
        Foundation
        levmar)

# On Linux the 'm' library is required.
if (UNIX)
    target_link_libraries(${CMD_NAME} m)
endif()

# Atlas
if (USE_ATLAS)
    if(USE_MKL)
        message(FATAL_ERROR "Cannot use both Atlas and Intel MKL, please change USE_MKL or USE_ATLAS to OFF.")
    endif()
    link_directories(
        ${ATLAS_LIB_PATH}
        )
    target_link_libraries(${CMD_NAME}
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
    target_link_libraries(${CMD_NAME}
            mkl_core
            mkl_def
            mkl_gf_lp64
            mkl_gnu_thread
            mkl_intel_lp64
            mkl_intel_thread
            mkl_mc
            mkl_sequential)
endif()

set_target_properties(${CMD_NAME} PROPERTIES
        PREFIX "" # no 'lib' prefix to .so files
        )

# On Windows, the Maya Plug-In file extension is '.mll', not '.dll'.
if (WIN32)
    set_target_properties(${CMD_NAME} PROPERTIES
        SUFFIX ".mll"
        )
endif()
