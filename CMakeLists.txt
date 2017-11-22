cmake_minimum_required(VERSION 2.8)
project(mayaMatchMoveSolver)
set(CMD_NAME mmSolver)
set(CMAKE_CXX_STANDARD 11)

# Maya SDK
set(MAYA_INCLUDE_PATH "/usr/autodesk/maya2016/include" CACHE PATH "Maya include directory")
set(MAYA_LIB_PATH "/usr/autodesk/maya2016/lib" CACHE PATH "Maya library directory")

# Lev-Mar
SET(LEVMAR_INCLUDE_PATH "/usr/local/include" CACHE PATH "Levmar include directory")
set(LEVMAR_LIB_PATH "/usr/local/lib" CACHE PATH "Levmar library directory")

# ATLAS
set(USE_ATLAS ON CACHE BOOLEAN "Should we use ATLAS with Lev-Mar?")
set(ATLAS_LIB_PATH "/usr/lib64/atlas" CACHE PATH "ATLAS library directory")

# GL Math
SET(GLM_INCLUDE_PATH "/usr/local/include" CACHE PATH "GL Math include directory")

# Source
set(SOURCE_FILES
        include/utilities/debugUtils.h
        include/utilities/cgCameraUtils.h
        include/mayaUtils.h
        include/Camera.h
        include/Marker.h
        include/Bundle.h
        include/Attr.h
        include/mmSolverCmd.h
        include/mmSolverUtils.h
        src/Camera.cpp
        src/Marker.cpp
        src/Bundle.cpp
        src/Attr.cpp
        src/mmSolverCmd.cpp
        src/pluginMain.cpp
)

include_directories(
        include
        ${GLM_INCLUDE_PATH}
        ${LEVMAR_INCLUDE_PATH}
        ${MAYA_INCLUDE_PATH}
)

link_directories(
        ${LIBRARY_OUTPUT_PATH}
        ${ATLAS_LIB_PATH}
        ${LEVMAR_LIB_PATH}
        ${MAYA_LIB_PATH}
)

# 'mmSolver' maya plugin library
add_library(${CMD_NAME} SHARED ${SOURCE_FILES})
if (USE_ATLAS)
    target_link_libraries(${CMD_NAME}
            OpenMaya
            OpenMayaAnim
            Foundation
            levmar
            lapack
            f77blas
            atlas
            m)
else()
    target_link_libraries(${CMD_NAME}
            OpenMaya
            OpenMayaAnim
            Foundation
            levmar
            m)
endif()
set_target_properties(${CMD_NAME} PROPERTIES
        PREFIX "" # no 'lib' prefix to .so files
        )