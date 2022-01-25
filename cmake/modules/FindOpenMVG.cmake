# - OpenMVG finder module
# This module will look for openMVG, using the predefined variable
# OPENMVG_ROOT.
#
# Uses Variables:
# - OPENMVG_ROOT_PATH - Directory for the openMVG install root.
# - OPENMVG_INCLUDE_PATH - Directory for the header files.
# - OPENMVG_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - OPENMVG_FOUND
# - OPENMVG_LIBRARIES
# - OPENMVG_LIBRARY_DLL
# - OPENMVG_INCLUDE_DIRS
#

find_path(OPENMVG_INCLUDE_DIR openMVG/multiview/solver_translation_knownRotation_kernel.hpp
    HINTS
        ${OPENMVG_INCLUDE_PATH}
        ${OPENMVG_ROOT}
        ${OPENMVG_ROOT}/include
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        camera/
        include/
        openMVG/
        include/openMVG/
)

find_path(OPENMVG_THIRDPARTY_INCLUDE_DIR third_party/stlplus3/filesystemSimplified/file_system.hpp
    HINTS
        ${OPENMVG_INCLUDE_PATH}
        ${OPENMVG_ROOT}
        ${OPENMVG_ROOT}/include
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        camera/
        include/
        openMVG/
        include/openMVG/
)


foreach(OPENMVG_LIB
    # OpenMVG primary libraries
    openMVG_ceres
    openMVG_cxsparse
    openMVG_easyexif
    openMVG_exif
    openMVG_fast
    openMVG_jpeg
    openMVG_kvld
    openMVG_features
    openMVG_geometry
    openMVG_image
    openMVG_linearProgramming
    openMVG_lInftyComputerVision
    openMVG_matching_image_collection
    openMVG_matching
    openMVG_multiview
    openMVG_numeric
    openMVG_png
    openMVG_robust_estimation
    openMVG_sfm
    openMVG_stlplus
    openMVG_system
    openMVG_tiff
    openMVG_zlib

    # OpenMVG dependancy libraries
    lib_clp
    lib_CoinUtils
    lib_OsiClipSolver
    lib_Osi

    # Other
    vlsift)

    find_library(OPENMVG_${OPENMVG_LIB}_LIBRARY
            ${OPENMVG_LIB}
        HINTS
            ${OPENMVG_LIB_PATH}
            ${OPENMVG_LIB_PATH}/../lib64  # required for finding Ceres in OpenMVG v2.0.
            ${OPENMVG_ROOT}
            /usr/lib
            /usr/local/lib
        PATH_SUFFIXES
            bin/
            lib/
            lib64/
        DOC
            "OpenMVG's ${OPENMVG_LIB} library path"
            )

    if (OPENMVG_${OPENMVG_LIB}_LIBRARY)
        list(APPEND OPENMVG_LIBRARIES ${OPENMVG_${OPENMVG_LIB}_LIBRARY})
    endif()
endforeach(OPENMVG_LIB)


if(OPENMVG_INCLUDE_DIR)
    set(OPENMVG_INCLUDE_DIRS ${OPENMVG_INCLUDE_DIRS} ${OPENMVG_INCLUDE_DIR})
endif()
if(OPENMVG_THIRDPARTY_INCLUDE_DIR)
    set(OPENMVG_INCLUDE_DIRS ${OPENMVG_INCLUDE_DIRS} ${OPENMVG_THIRDPARTY_INCLUDE_DIR})
endif()


mark_as_advanced(
    OPENMVG_INCLUDE_DIR
)


include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(OpenMVG
    REQUIRED_VARS
        OPENMVG_LIBRARIES
        OPENMVG_INCLUDE_DIRS
)
