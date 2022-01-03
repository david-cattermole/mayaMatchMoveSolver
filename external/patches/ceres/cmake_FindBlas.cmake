# - Blas finder module
# This module will look for blas, using the predefined variable
# BLAS_ROOT. On MS Windows, the DLL is expected to be named
# 'blas.dll'.
#
# Uses Variables:
# - BLAS_ROOT - Directory for the blas install root.
# - BLAS_INCLUDE_PATH - Directory for the header files.
# - BLAS_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - BLAS_FOUND
# - BLAS_LIBRARIES
# - BLAS_LIBRARY_DLL
# - BLAS_INCLUDE_DIRS
#

find_path(BLAS_INCLUDE_DIR blas.h
    HINTS
        ${BLAS_INCLUDE_PATH}
        ${BLAS_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
        blas-1/
        include/blas-1/
)

find_library(BLAS_LIBRARY
  NAMES
        libblas.1
        libblas.so.1
        libblas.1.dylib
        libblas
        blas
        libblas_s
        blas_s
    HINTS
        ${BLAS_LIB_PATH}
        ${BLAS_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        lib/
        lib64/
)

find_path(BLAS_LIBRARY_DLL blas.dll
    HINTS
        ${BLAS_LIB_PATH}
        ${BLAS_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        )
if(EXISTS ${BLAS_LIBRARY_DLL})
    set(BLAS_LIBRARY_DLL ${BLAS_LIBRARY_DLL}/blas.dll)
endif()

if(BLAS_INCLUDE_DIR AND BLAS_LIBRARY)
    set(BLAS_INCLUDE_DIRS ${BLAS_INCLUDE_DIR} )
    set(BLAS_LIBRARIES ${BLAS_LIBRARY} )
endif()

mark_as_advanced(
    BLAS_INCLUDE_DIR
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Blas
    REQUIRED_VARS
        BLAS_LIBRARIES
        BLAS_INCLUDE_DIRS
)
