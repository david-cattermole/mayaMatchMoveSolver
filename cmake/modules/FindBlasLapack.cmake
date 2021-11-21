# - BlasLapack finder module
# This module will look for blasLapack, using the predefined variable
# BLASLAPACK_ROOT.
#
# Uses Variables:
# - BLASLAPACK_ROOT_PATH - Directory for the blasLapack install root.
# - BLASLAPACK_LIB_PATH - Directory for shared libraries (.so and .dll).
#
# Defines Variables:
# - BLASLAPACK_FOUND
# - BLASLAPACK_LIBRARIES
# - BLASLAPACK_LIBRARIES_DLL
#

message(STATUS "BLASLAPACK_ROOT: ${BLASLAPACK_ROOT}")
foreach(BLASLAPACK_LIB_NAME
    libblas
    libgcc_s_sjlj-1
    libgfortran-3
    libquadmath-0
    liblapack
    )

  find_path(BLASLAPACK_LIBRARY_DLL "${BLASLAPACK_LIB_NAME}.dll"
    HINTS
        ${BLASLAPACK_ROOT}
        ${BLASLAPACK_LIB_PATH}
        /usr/lib
        /usr/local/lib
    )
  message(STATUS "BLASLAPACK_LIBRARY_DLL: ${BLASLAPACK_LIBRARY_DLL}")

  if(EXISTS ${BLASLAPACK_LIBRARY_DLL})
    list(APPEND BLASLAPACK_LIBRARIES "library_name_here")
    list(APPEND BLASLAPACK_LIBRARIES_DLL "${BLASLAPACK_LIBRARY_DLL}/${BLASLAPACK_LIB_NAME}.dll")
  endif()
endforeach()
message(STATUS "BLASLAPACK_LIBRARIES: ${BLASLAPACK_LIBRARIES}")
message(STATUS "BLASLAPACK_LIBRARIES_DLL: ${BLASLAPACK_LIBRARIES_DLL}")

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(BlasLapack
    REQUIRED_VARS
        BLASLAPACK_LIBRARIES
        BLASLAPACK_LIBRARIES_DLL
)
