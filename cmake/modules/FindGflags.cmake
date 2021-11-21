# - Gflags finder module
# This module will look for gflags, using the predefined variable
# GFLAGS_ROOT. On MS Windows, the DLL is expected to be named
# 'gflags.dll'.
#
# Uses Variables:
# - GFLAGS_ROOT_PATH - Directory for the gflags install root.
# - GFLAGS_INCLUDE_PATH - Directory for the header files.
# - GFLAGS_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - GFLAGS_FOUND
# - GFLAGS_LIBRARIES
# - GFLAGS_LIBRARY_DLL
# - GFLAGS_INCLUDE_DIRS
#

find_path(GFLAGS_INCLUDE_DIR gflags/gflags.h
    HINTS
        ${GFLAGS_INCLUDE_PATH}
        ${GFLAGS_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
        gflags/
        include/gflags/
)

find_library(GFLAGS_LIBRARY
    NAMES
        libgflags
        libgflags_static
        gflags_static
        gflags
    HINTS
        ${GFLAGS_LIB_PATH}
        ${GFLAGS_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        lib/
        lib64/
)

find_path(GFLAGS_LIBRARY_DLL gflags.dll
    HINTS
        ${GFLAGS_LIB_PATH}
        ${GFLAGS_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        )
if(EXISTS ${GFLAGS_LIBRARY_DLL})
    set(GFLAGS_LIBRARY_DLL ${GFLAGS_LIBRARY_DLL}/gflags.dll)
endif()

if(GFLAGS_INCLUDE_DIR AND GFLAGS_LIBRARY)
    set(GFLAGS_INCLUDE_DIRS ${GFLAGS_INCLUDE_DIR} )
    set(GFLAGS_LIBRARIES ${GFLAGS_LIBRARY} )
endif()

mark_as_advanced(
    GFLAGS_INCLUDE_DIR
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Gflags
    REQUIRED_VARS
        GFLAGS_LIBRARIES
        GFLAGS_INCLUDE_DIRS
)
