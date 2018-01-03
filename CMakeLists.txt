cmake_minimum_required(VERSION 2.8)
project(mayaMatchMoveSolver)
set(CMD_NAME mmSolver)
set(CMAKE_CXX_STANDARD 11)

# Compile Flags, Release flags come from the Autodesk Maya build scripts.
set(CMAKE_CXX_FLAGS_DEBUG "-std=c++0x -O0 -g -Wall")
set(CMAKE_C_FLAGS_RELEASE "-std=c++0x -DBits64_ -m64 -DUNIX -D_BOOL -DLINUX -DFUNCPROTO -D_GNU_SOURCE -DLINUX_64 -fPIC -fno-strict-aliasing -DREQUIRE_IOSTREAM -O3 -Wall -Wno-multichar -Wno-comment -Wno-sign-compare -funsigned-char -pthread -fopenmp")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -Wno-deprecated -Wno-reorder -ftemplate-depth-25 -fno-gnu-keywords")

# Maya SDK
set(MAYA_INCLUDE_PATH "/usr/autodesk/maya2016/include" CACHE PATH "Maya include directory")
set(MAYA_LIB_PATH "/usr/autodesk/maya2016/lib" CACHE PATH "Maya library directory")

# Lev-Mar
set(LEVMAR_INCLUDE_PATH "/usr/local/include" CACHE PATH "Levmar include directory")
set(LEVMAR_LIB_PATH "/usr/local/lib" CACHE PATH "Levmar library directory")

# SuiteSparse library path
set(USE_SUITE_SPARSE ON CACHE BOOLEAN "Can we use SuiteSparse?")
set(SUITE_SPARSE_LIB_PATH "/usr/lib64/atlas" CACHE PATH "SuiteSparse library directory")

# ATLAS
set(USE_ATLAS ON CACHE BOOLEAN "Should we use ATLAS with Lev-Mar?")
set(ATLAS_LIB_PATH "/usr/lib64/atlas" CACHE PATH "ATLAS library directory")

# Intel Math Kernel Library
set(USE_MKL ON CACHE BOOLEAN "Should we use MKL?")
set(MKL_LIB_PATH "/opt/intel/mkl/lib/intel64" CACHE PATH "Intel MKL library directory")

# Sparse Lev-Mar (SPLM)
set(HAVE_SPLM OFF CACHE BOOLEAN "Use Sparse Lev-Mar?")
set(SPLM_INCLUDE_PATH "/usr/local/include" CACHE PATH "Levmar include directory")
set(SPLM_LIB_PATH "/usr/local/lib" CACHE PATH "Levmar library directory")

# Ceres Solver
set(HAVE_CERES ON CACHE BOOLEAN "Can we use Ceres Solver?")
set(CERES_INCLUDE_PATH "/usr/local/include" CACHE PATH "Ceres include directory")
set(CERES_LIB_PATH "/usr/local/lib" CACHE PATH "Ceres library directory")


# Source
set(SOURCE_FILES
        include/utilities/debugUtils.h
        include/nodeTypeIds.h
        include/mayaUtils.h
        include/mmSolver.h
        include/mmSolverCeres.h
        include/mmSolverLevMar.h
        include/Camera.h
        include/Marker.h
        include/Bundle.h
        include/Attr.h
        include/MMMarkerScaleNode.h
        include/MMTestCameraMatrixCmd.h
        include/MMSolverCmd.h
        src/mmSolver.cpp
        src/mmSolverCeres.cpp
        src/mmSolverLevMar.cpp
        src/Camera.cpp
        src/Marker.cpp
        src/Bundle.cpp
        src/Attr.cpp
        src/MMMarkerScaleNode.cpp
        src/MMTestCameraMatrixCmd.cpp
        src/MMSolverCmd.cpp
        src/pluginMain.cpp
)

include_directories(
        include
        ${LEVMAR_INCLUDE_PATH}
        ${SPLM_INCLUDE_PATH}
        ${CERES_INCLUDE_PATH}
        ${MAYA_INCLUDE_PATH}
)

link_directories(
        ${LIBRARY_OUTPUT_PATH}
        ${LEVMAR_LIB_PATH}
        ${SPLM_LIB_PATH}
        ${MAYA_LIB_PATH}
        ${MKL_LIB_PATH}
        ${ATLAS_LIB_PATH}
        ${SUITE_SPARSE_LIB_PATH}
)

# 'mmSolver' maya plugin library
add_library(${CMD_NAME} SHARED ${SOURCE_FILES})
target_link_libraries(${CMD_NAME}
        OpenMaya
        OpenMayaAnim
        Foundation
        levmar
        m)

# Atlas
if (USE_ATLAS)
    if(USE_MKL)
        message(FATAL_ERROR "Cannot use both Atlas and Intel MKL, please change USE_MKL or USE_ATLAS to OFF.")
    endif()
    target_link_libraries(${CMD_NAME}
            lapack
            f77blas
            atlas
            )
endif()

# Intel MKL
if (USE_MKL)
    if(USE_ATLAS)
        message(FATAL_ERROR "Cannot use both Atlas and Intel MKL, please change USE_MKL or USE_ATLAS to OFF.")
    endif()
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

# SuiteSparse
if (USE_SUITE_SPARSE)
    if(NOT USE_ATLAS AND NOT USE_MKL)
        message(FATAL_ERROR "SuiteSparse needs either Atlas or Intel MKL for BLAS and LAPACK functions.")
    endif()
    target_link_libraries(${CMD_NAME}
            suitesparseconfig
            amd
            ldl
            cholmod
            umfpack)
endif()

# Sparse LevMar
if(HAVE_SPLM)
    if(NOT USE_SUITE_SPARSE)
        message(FATAL_ERROR "Must have SuiteSparse in order to use SparseLM!")
    endif()
    if(NOT USE_ATLAS AND NOT USE_MKL)
        message(FATAL_ERROR "SuiteSparse needs either Atlas or Intel MKL for BLAS and LAPACK functions.")
    endif()
    add_definitions( -DHAVE_SPLM=1 )
    target_link_libraries(${CMD_NAME}
            splm
            )
else()
    add_definitions( -DHAVE_SPLM=0 )
endif()

# Ceres
if(HAVE_CERES)
    if(NOT USE_SUITE_SPARSE)
        message(FATAL_ERROR "Must have SuiteSparse in order to use Ceres!")
    endif()
    if(NOT USE_ATLAS AND NOT USE_MKL)
        message(FATAL_ERROR "SuiteSparse needs either Atlas or Intel MKL for BLAS and LAPACK functions.")
    endif()
    add_definitions( -DHAVE_CERES=1 )
    target_link_libraries(${CMD_NAME}
            ceres
            )
else()
    add_definitions( -DHAVE_CERES=0 )
endif()

set_target_properties(${CMD_NAME} PROPERTIES
        PREFIX "" # no 'lib' prefix to .so files
        )