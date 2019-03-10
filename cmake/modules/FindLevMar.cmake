# - levmar finder module
# This module will look for levmar, using the predefined variable
# LEVMAR_ROOT. On MS Windows, the DLL is expected to be named
# 'levmar.dll'.
#
# Uses Variables:
# - LEVMAR_ROOT_PATH - Directory for the levmar install root.
# - LEVMAR_INCLUDE_PATH - Directory for the header files.
# - LEVMAR_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - LEVMAR_FOUND
# - LEVMAR_LIBRARIES
# - LEVMAR_LIBRARY_DLL
# - LEVMAR_INCLUDE_DIRS
#

find_path(LEVMAR_INCLUDE_DIR levmar.h
    HINTS
        ${LEVMAR_INCLUDE_PATH}
        ${LEVMAR_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
)

find_library(LEVMAR_LIBRARY levmar
    HINTS
        ${LEVMAR_LIB_PATH}
        ${LEVMAR_ROOT}
        /usr/local/lib
        /usr/lib
    PATH_SUFFIXES
        lib/
)

if(WIN32)
    find_path(LEVMAR_LIBRARY_DLL levmar.dll
        HINTS
            ${LEVMAR_LIB_PATH}
            ${LEVMAR_ROOT}
            /usr/local/include
            /usr/include
        PATH_SUFFIXES
            lib/
            bin/
            )
    set(LEVMAR_LIBRARY_DLL "${LEVMAR_LIBRARY_DLL}/levmar.dll")
endif()


if(LEVMAR_INCLUDE_DIR AND LEVMAR_LIBRARY)
    set(LEVMAR_INCLUDE_DIRS ${LEVMAR_INCLUDE_DIR} )
    set(LEVMAR_LIBRARIES ${LEVMAR_LIBRARY} )
endif()

mark_as_advanced(
    LEVMAR_INCLUDE_DIR
)


include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(LevMar
    REQUIRED_VARS
        LEVMAR_INCLUDE_DIRS
        LEVMAR_LIBRARIES
)
