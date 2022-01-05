# - Glog finder module
# This module will look for glog, using the predefined variable
# GLOG_ROOT. On MS Windows, the DLL is expected to be named
# 'glog.dll'.
#
# Uses Variables:
# - GLOG_ROOT_PATH - Directory for the glog install root.
# - GLOG_INCLUDE_PATH - Directory for the header files.
# - GLOG_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - GLOG_FOUND
# - GLOG_LIBRARIES
# - GLOG_LIBRARY_DLL
# - GLOG_INCLUDE_DIRS
#

find_path(GLOG_INCLUDE_DIR glog/logging.h
    HINTS
        ${GLOG_INCLUDE_PATH}
        ${GLOG_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
        glog-1/
        include/glog-1/
)

find_library(GLOG_LIBRARY
  NAMES
        libglog
        libglog_s
        glog_s
        glog
    HINTS
        ${GLOG_LIB_PATH}
        ${GLOG_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        lib/
        lib64/
)

find_path(GLOG_LIBRARY_DLL glog.dll
    HINTS
        ${GLOG_LIB_PATH}
        ${GLOG_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        )
if(EXISTS ${GLOG_LIBRARY_DLL})
    set(GLOG_LIBRARY_DLL ${GLOG_LIBRARY_DLL}/glog.dll)
endif()

if(GLOG_INCLUDE_DIR AND GLOG_LIBRARY)
    set(GLOG_INCLUDE_DIRS ${GLOG_INCLUDE_DIR} )
    set(GLOG_LIBRARIES ${GLOG_LIBRARY} )
endif()

mark_as_advanced(
    GLOG_INCLUDE_DIR
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Glog
    REQUIRED_VARS
        GLOG_LIBRARIES
        GLOG_INCLUDE_DIRS
)
