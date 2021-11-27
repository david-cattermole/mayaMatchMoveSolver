# - Eigen3 finder module
# This module will look for eigen3, using the predefined variable
# EIGEN3_ROOT.
#
# Uses Variables:
# - EIGEN3_ROOT_PATH - Directory for the eigen3 install root.
# - EIGEN3_INCLUDE_PATH - Directory for the header files.
# - EIGEN3_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - EIGEN3_FOUND
# - EIGEN3_INCLUDE_DIRS
#

find_path(EIGEN3_INCLUDE_DIR Eigen/Core
    HINTS
        ${EIGEN3_INCLUDE_PATH}
        ${EIGEN3_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
        eigen3/
        include/eigen3/
)

if(EIGEN3_INCLUDE_DIR)
    set(EIGEN3_INCLUDE_DIRS ${EIGEN3_INCLUDE_DIR} )
endif()

mark_as_advanced(
    EIGEN3_INCLUDE_DIR
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Eigen3
    REQUIRED_VARS
        EIGEN3_INCLUDE_DIRS
)
