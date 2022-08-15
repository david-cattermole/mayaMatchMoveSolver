# - Ldpk finder module
# This module will look for ldpk, using the predefined variable
# LDPK_ROOT.
#
# Uses Variables:
# - LDPK_ROOT_PATH - Directory for the ldpk install root.
# - LDPK_INCLUDE_PATH - Directory for the header files.
# - LDPK_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - LDPK_FOUND
# - LDPK_LIBRARIES
# - LDPK_INCLUDE_DIRS
#

find_path(LDPK_INCLUDE_DIR ldpk.h
    HINTS
        ${LDPK_INCLUDE_PATH}
        ${LDPK_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
        ldpk-1/
        include/ldpk-1/
)

find_library(LDPK_LIBRARY
  NAMES
        libldpk
        libldpk.so
        libldpk.dylib
        libldpk
        ldpk
    HINTS
        ${LDPK_LIB_PATH}
        ${LDPK_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        lib/
        lib64/
)

if(LDPK_INCLUDE_DIR AND LDPK_LIBRARY)
    set(LDPK_INCLUDE_DIRS ${LDPK_INCLUDE_DIR} )
    set(LDPK_LIBRARIES ${LDPK_LIBRARY} )
endif()

mark_as_advanced(
    LDPK_INCLUDE_DIR
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(LDPK
    REQUIRED_VARS
        LDPK_LIBRARIES
        LDPK_INCLUDE_DIRS
)
