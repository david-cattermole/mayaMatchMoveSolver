# - CMinpack finder module
# This module will look for cminpack, using the predefined variable
# CMINPACK_ROOT. On MS Windows, the DLL is expected to be named
# 'cminpack.dll'.
#
# Uses Variables:
# - CMINPACK_ROOT_PATH - Directory for the cminpack install root.
# - CMINPACK_INCLUDE_PATH - Directory for the header files.
# - CMINPACK_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - CMINPACK_FOUND
# - CMINPACK_LIBRARIES
# - CMINPACK_LIBRARY_DLL
# - CMINPACK_INCLUDE_DIRS
#

find_path(CMINPACK_INCLUDE_DIR cminpack.h
    HINTS
        ${CMINPACK_INCLUDE_PATH}
        ${CMINPACK_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
        cminpack-1/
        include/cminpack-1/
)

find_library(CMINPACK_LIBRARY libcminpack.so.1 libcminpack_s cminpack cminpack_s
    HINTS
        ${CMINPACK_LIB_PATH}
        ${CMINPACK_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        lib/
        lib64/
)

find_path(CMINPACK_LIBRARY_DLL cminpack.dll
    HINTS
        ${CMINPACK_LIB_PATH}
        ${CMINPACK_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        )
if(EXISTS ${CMINPACK_LIBRARY_DLL})
    set(CMINPACK_LIBRARY_DLL ${CMINPACK_LIBRARY_DLL}/cminpack.dll)
endif()

if(CMINPACK_INCLUDE_DIR AND CMINPACK_LIBRARY)
    set(CMINPACK_INCLUDE_DIRS ${CMINPACK_INCLUDE_DIR} )
    set(CMINPACK_LIBRARIES ${CMINPACK_LIBRARY} )
endif()

mark_as_advanced(
    CMINPACK_INCLUDE_DIR
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(CMinpack
    REQUIRED_VARS
        CMINPACK_LIBRARIES
        CMINPACK_INCLUDE_DIRS
)
