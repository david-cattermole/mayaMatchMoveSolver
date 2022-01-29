# - Dlfcn finder module
# This module will look for dlfcn, using the predefined variable
# DLFCN_ROOT. On MS Windows, the DLL is expected to be named
# 'dlfcn.dll'.
#
# Uses Variables:
# - DLFCN_ROOT_PATH - Directory for the dlfcn install root.
# - DLFCN_INCLUDE_PATH - Directory for the header files.
# - DLFCN_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - DLFCN_FOUND
# - DLFCN_LIBRARIES
# - DLFCN_LIBRARY_DLL
# - DLFCN_INCLUDE_DIRS
#

find_path(DLFCN_INCLUDE_DIR dlfcn.h
    HINTS
        ${DLFCN_INCLUDE_PATH}
        ${DLFCN_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
        dlfcn-1/
        include/dlfcn-1/
)

find_library(DLFCN_LIBRARY
  NAMES
        dl
    HINTS
        ${DLFCN_LIB_PATH}
        ${DLFCN_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        lib/
        lib64/
)

find_path(DLFCN_LIBRARY_DLL dl.dll
    HINTS
        ${DLFCN_LIB_PATH}
        ${DLFCN_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        )
if(EXISTS ${DLFCN_LIBRARY_DLL})
    set(DLFCN_LIBRARY_DLL ${DLFCN_LIBRARY_DLL}/dl.dll)
endif()

if(DLFCN_INCLUDE_DIR AND DLFCN_LIBRARY)
    set(DLFCN_INCLUDE_DIRS ${DLFCN_INCLUDE_DIR} )
    set(DLFCN_LIBRARIES ${DLFCN_LIBRARY} )
endif()

mark_as_advanced(
    DLFCN_INCLUDE_DIR
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Dlfcn
    REQUIRED_VARS
        DLFCN_LIBRARIES
        DLFCN_INCLUDE_DIRS
)
