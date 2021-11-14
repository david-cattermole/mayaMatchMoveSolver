# - Ceres finder module
# This module will look for ceres, using the predefined variable
# CERES_ROOT. On MS Windows, the DLL is expected to be named
# 'ceres.dll'.
#
# Uses Variables:
# - CERES_ROOT_PATH - Directory for the ceres install root.
# - CERES_INCLUDE_PATH - Directory for the header files.
# - CERES_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - CERES_FOUND
# - CERES_LIBRARIES
# - CERES_LIBRARY_DLL
# - CERES_INCLUDE_DIRS
#

find_path(CERES_INCLUDE_DIR ceres.h
    HINTS
        ${CERES_INCLUDE_PATH}
        ${CERES_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
        ceres/
        include/ceres/
)
# message(STATUS "CERES_INCLUDE_DIR = ${CERES_INCLUDE_DIR}")

find_library(CERES_LIBRARY
  NAMES
        libceres
        libceres.so
        libceres.dylib
        libceres_s
        ceres_s
        libceres
        ceres
    HINTS
        ${CERES_LIB_PATH}
        ${CERES_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        lib/
        lib64/
)
# message(STATUS "CERES_LIBRARY = ${CERES_LIBRARY}")

find_path(CERES_LIBRARY_DLL ceres.dll
    HINTS
        ${CERES_LIB_PATH}
        ${CERES_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        )
# message(STATUS "CERES_LIBRARY_DLL = ${CERES_LIBRARY_DLL}")
if(EXISTS ${CERES_LIBRARY_DLL})
    set(CERES_LIBRARY_DLL ${CERES_LIBRARY_DLL}/ceres.dll)
endif()

if(CERES_INCLUDE_DIR AND CERES_LIBRARY)
    set(CERES_INCLUDE_DIRS ${CERES_INCLUDE_DIR} )
    set(CERES_LIBRARIES ${CERES_LIBRARY} )
endif()

mark_as_advanced(
    CERES_INCLUDE_DIR
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Ceres
    REQUIRED_VARS
        CERES_LIBRARIES
        CERES_INCLUDE_DIRS
)
