
# Author: TheFrenchLeaf https://github.com/TheFrenchLeaf

cmake_minimum_required(VERSION 3.0)

project(CXSparse C)

include(GNUInstallDirs)

file(GLOB CXSparse_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/Source/*.c")
set(CXSparse_INCLUDES
  "${CMAKE_CURRENT_SOURCE_DIR}/Include/cs.h"
  "${CMAKE_CURRENT_SOURCE_DIR}/Include/SuiteSparse_config.h"
)
set_source_files_properties(${CXSparse_SRCS} PROPERTIES LANGUAGE C)

add_library(cxsparse ${CXSparse_SRCS})
target_compile_definitions(cxsparse PUBLIC NCOMPLEX)
target_include_directories(cxsparse PRIVATE ./ ./Include)
target_include_directories(cxsparse PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/Include
  )
if(UNIX)
  target_link_libraries(cxsparse m)
endif(UNIX)

# Install the libraries and includes.
install(TARGETS cxsparse
  EXPORT cxsparse-targets
  RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
  LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  INCLUDES DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
  )
install(FILES ${CXSparse_INCLUDES}
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

# Correctly export the location of installed includes in the target
target_include_directories(cxsparse INTERFACE $<INSTALL_INTERFACE:include>)

# Export the targets to the build tree.
export(EXPORT cxsparse-targets
  NAMESPACE cxsparse::
  FILE "${CMAKE_CURRENT_BINARY_DIR}/cmake/cxsparse-targets.cmake")

# Generate the CMake config file.
set(CMAKE_CONF_INSTALL_DIR "${CMAKE_INSTALL_DATAROOTDIR}/cxsparse")
set(INCLUDE_INSTALL_DIR ${CMAKE_INSTALL_INCLUDEDIR})
include(CMakePackageConfigHelpers)
configure_package_config_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/cxsparse-config.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/cxsparse-config.cmake
  INSTALL_DESTINATION ${CMAKE_CONF_INSTALL_DIR}
  PATH_VARS INCLUDE_INSTALL_DIR
  NO_CHECK_REQUIRED_COMPONENTS_MACRO
)

# Install generatated targets file.
install(EXPORT cxsparse-targets
  FILE cxsparse-targets.cmake
  NAMESPACE cxsparse::
  DESTINATION "${CMAKE_CONF_INSTALL_DIR}"
)

# Install the CMake config file.
install(FILES
  ${CMAKE_CURRENT_BINARY_DIR}/cxsparse-config.cmake
  DESTINATION ${CMAKE_CONF_INSTALL_DIR}
)
