# - Gtest finder module
# This module will look for gtest, using the predefined variable
# GTEST_ROOT. On MS Windows, the DLL is expected to be named
# 'gtest.dll'.
#
# Uses Variables:
# - GTEST_ROOT_PATH - Directory for the gtest install root.
# - GTEST_INCLUDE_PATH - Directory for the header files.
# - GTEST_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - GTEST_FOUND
# - GTEST_LIBRARIES
# - GTEST_LIBRARY_DLL
# - GTEST_INCLUDE_DIRS
#

find_path(GTEST_INCLUDE_DIR gtest/gtest.h
    HINTS
        ${GTEST_INCLUDE_PATH}
        ${GTEST_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
        gtest-1/
        include/gtest-1/
)

find_library(GTEST_LIBRARY
  NAMES
        libgtest
        libgtest_s
        gtest_s
        gtest
    HINTS
        ${GTEST_LIB_PATH}
        ${GTEST_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        lib/
        lib64/
)

find_path(GTEST_LIBRARY_DLL gtest.dll
    HINTS
        ${GTEST_LIB_PATH}
        ${GTEST_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        )
if(EXISTS ${GTEST_LIBRARY_DLL})
    set(GTEST_LIBRARY_DLL ${GTEST_LIBRARY_DLL}/gtest.dll)
endif()

if(GTEST_INCLUDE_DIR AND GTEST_LIBRARY)
    set(GTEST_INCLUDE_DIRS ${GTEST_INCLUDE_DIR} )
    set(GTEST_LIBRARIES ${GTEST_LIBRARY} )
endif()

mark_as_advanced(
    GTEST_INCLUDE_DIR
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Gtest
    REQUIRED_VARS
        GTEST_LIBRARIES
        GTEST_INCLUDE_DIRS
)
