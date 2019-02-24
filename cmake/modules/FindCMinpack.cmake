# message("CMINPACK ROOT = ${CMINPACK_ROOT}")

find_path(CMINPACK_INCLUDE_DIR cminpack.h
    HINTS
        ${CMINPACK_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
        cminpack-1/
        include/cminpack-1/
)
# message("CMINPACK_INCLUDE_DIR = ${CMINPACK_INCLUDE_DIR}")

find_library(CMINPACK_LIBRARY cminpack cminpack_s
    HINTS
        ${CMINPACK_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        lib/
)
# message("CMINPACK_LIBRARY = ${CMINPACK_LIBRARY}")

find_path(CMINPACK_LIBRARY_DLL cminpack.dll
    HINTS
        ${CMINPACK_ROOT}
        /usr/lib
        /usr/local/lib
    PATH_SUFFIXES
        bin/
        )
if(EXISTS ${CMINPACK_LIBRARY_DLL})
    set(CMINPACK_LIBRARY_DLL ${CMINPACK_LIBRARY_DLL}/cminpack.dll)
endif()
# message("CMINPACK_LIBRARY_DLL = ${CMINPACK_LIBRARY_DLL}")

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
