# - Libmv finder module
# This module will look for libmv, using the predefined variable
# LIBMV_ROOT.
#
# Uses Variables:
# - LIBMV_ROOT_PATH - Directory for the libmv install root.
# - LIBMV_INCLUDE_PATH - Directory for the header files.
# - LIBMV_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - LIBMV_FOUND
# - LIBMV_LIBRARIES
# - LIBMV_LIBRARY_DLL
# - LIBMV_INCLUDE_DIRS
#

find_path(LIBMV_INCLUDE_DIR libmv/camera/pinhole_camera.h
    HINTS
        ${LIBMV_INCLUDE_PATH}
        ${LIBMV_ROOT}
        ${LIBMV_ROOT}/include
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        camera/
        include/
        libmv/
        include/libmv/
)


foreach(LIBMV_LIB
    # LibMV primary libraries
    autotrack
    base
    camera
    correspondence
    descriptor
    detector
    image
    multiview
    numeric
    reconstruction
    simple_pipeline
    tools
    tracking

    # LibMV dependancy libraries
    OpenExif
    V3D
    daisy
    fast
    flann
    jpeg
    png
    pthread
    zlib

    # Other libraries
    #
    # TODO: Make seperate Find*.cmake files for each of these libraries.
    ldl
    colamd
    )

    find_library(LIBMV_${LIBMV_LIB}_LIBRARY
            ${LIBMV_LIB}
        HINTS
            ${LIBMV_LIB_PATH}
            ${LIBMV_ROOT}
            /usr/lib
            /usr/local/lib
        PATH_SUFFIXES
            bin/
            lib/
            lib64/
        DOC
            "Libmv's ${LIBMV_LIB} library path"
    )

    if (LIBMV_${LIBMV_LIB}_LIBRARY)
        list(APPEND LIBMV_LIBRARIES ${LIBMV_${LIBMV_LIB}_LIBRARY})
    endif()
endforeach(LIBMV_LIB)


if(LIBMV_INCLUDE_DIR)
    set(LIBMV_INCLUDE_DIRS ${LIBMV_INCLUDE_DIR})
endif()


mark_as_advanced(
    LIBMV_INCLUDE_DIR
)


include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Libmv
    REQUIRED_VARS
        LIBMV_LIBRARIES
        LIBMV_INCLUDE_DIRS
)
