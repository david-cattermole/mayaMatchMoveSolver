# - Suitesparse finder module
# This module will look for suitesparse, using the predefined variable
# SUITESPARSE_ROOT.
#
# Uses Variables:
# - SUITESPARSE_ROOT_PATH - Directory for the suitesparse install root.
# - SUITESPARSE_INCLUDE_PATH - Directory for the header files.
# - SUITESPARSE_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - SUITESPARSE_FOUND
# - SUITESPARSE_LIBRARIES
# - SUITESPARSE_LIBRARY_DLL
# - SUITESPARSE_INCLUDE_DIRS
#

find_path(SUITESPARSE_INCLUDE_DIR suitesparse/SuiteSparse_config.h
    HINTS
        ${SUITESPARSE_INCLUDE_PATH}
        ${SUITESPARSE_ROOT}
        ${SUITESPARSE_ROOT}/include
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        suitesparse/
)


foreach(SUITESPARSE_LIB
    amd
    btf
    camd
    ccolamd
    cholmod
    cxsparse
    klu
    ldl
    spqr
    umfpack
    metis
    suitesparseconfig
    )

    find_library(SUITESPARSE_${SUITESPARSE_LIB}_LIBRARY
        NAMES
            ${SUITESPARSE_LIB}
            "lib${SUITESPARSE_LIB}"
        HINTS
            ${SUITESPARSE_LIB_PATH}
            ${SUITESPARSE_ROOT}
            /usr/lib
            /usr/local/lib
        PATH_SUFFIXES
            bin/
            lib/
            lib64/
        DOC
            "Suitesparse's ${SUITESPARSE_LIB} library path"
    )

    if (SUITESPARSE_${SUITESPARSE_LIB}_LIBRARY)
        list(APPEND SUITESPARSE_LIBRARIES ${SUITESPARSE_${SUITESPARSE_LIB}_LIBRARY})
    endif()
endforeach(SUITESPARSE_LIB)


if(SUITESPARSE_INCLUDE_DIR)
    set(SUITESPARSE_INCLUDE_DIRS ${SUITESPARSE_INCLUDE_DIR})
endif()


mark_as_advanced(
    SUITESPARSE_INCLUDE_DIR
)


include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Suitesparse
    REQUIRED_VARS
        SUITESPARSE_LIBRARIES
        SUITESPARSE_INCLUDE_DIRS
)
