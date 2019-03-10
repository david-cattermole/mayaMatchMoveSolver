# message("LEMVAR ROOT = ${LEVMAR_ROOT}")

find_path(LEVMAR_INCLUDE_DIR levmar.h
    HINTS
        ${LEVMAR_INCLUDE_PATH}
        ${LEVMAR_ROOT}
        /usr/local/include
        /usr/include
    PATH_SUFFIXES
        include/
)
# message("LEVMAR_INCLUDE_DIR = ${LEVMAR_INCLUDE_DIR}")

find_library(LEVMAR_LIBRARY levmar
    HINTS
        ${LEVMAR_LIB_PATH}
        ${LEVMAR_ROOT}
        /usr/local/lib
        /usr/lib
    PATH_SUFFIXES
        lib/
)
# message("LEVMAR_LIBRARY = ${LEVMAR_LIBRARY}")

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
    # message("LEVMAR_LIBRARY_DLL = ${LEVMAR_LIBRARY_DLL}")
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
