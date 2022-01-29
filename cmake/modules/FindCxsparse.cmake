# - Cxsparse finder module
# This module will look for cxsparse, using the predefined variable
# CXSPARSE_ROOT. On MS Windows, the DLL is expected to be named
# 'cxsparse.dll'.
#
# Uses Variables:
# - CXSPARSE_ROOT_PATH - Directory for the cxsparse install root.
# - CXSPARSE_INCLUDE_PATH - Directory for the header files.
# - CXSPARSE_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - CXSPARSE_FOUND
# - CXSPARSE_LIBRARIES
# - CXSPARSE_LIBRARY_DLL
# - CXSPARSE_INCLUDE_DIRS
#

find_path(CXSPARSE_INCLUDE_DIR cs.h
    HINTS
        ${CXSPARSE_INCLUDE_PATH}
        ${CXSPARSE_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
)

find_library(CXSPARSE_LIBRARY
    NAMES
        cxsparse
    HINTS
        ${CXSPARSE_LIB_PATH}
        ${CXSPARSE_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        lib/
)

# find_path(CXSPARSE_LIBRARY_DLL
#     NAMES
#         cxsparse.dll
#     HINTS
#         ${CXSPARSE_LIB_PATH}
#         ${CXSPARSE_ROOT}
#         /usr/lib
#         /usr/local/lib
#     PATH_SUFFIXES
#         bin/
#         lib/
#         )
# if(EXISTS ${CXSPARSE_LIBRARY_DLL})
#     set(CXSPARSE_LIBRARY_DLL ${CXSPARSE_LIBRARY_DLL}/cxsparse.dll)
# endif()

if(CXSPARSE_INCLUDE_DIR AND CXSPARSE_LIBRARY)
    set(CXSPARSE_INCLUDE_DIRS ${CXSPARSE_INCLUDE_DIR} )
    set(CXSPARSE_LIBRARIES ${CXSPARSE_LIBRARY} )
endif()

mark_as_advanced(
    CXSPARSE_INCLUDE_DIR
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Cxsparse
    REQUIRED_VARS
        CXSPARSE_LIBRARIES
        CXSPARSE_INCLUDE_DIRS
)
