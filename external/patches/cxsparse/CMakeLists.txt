
# Author: TheFrenchLeaf https://github.com/TheFrenchLeaf

cmake_minimum_required(VERSION 3.0)

project(CXSparse C)

file(GLOB CXSparse_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/Source/*.c")
set(CXSparse_INCLUDES "${CMAKE_CURRENT_SOURCE_DIR}/Include/cs.h")
set_source_files_properties(${CXSparse_SRCS} PROPERTIES LANGUAGE C)

add_library(cxsparse ${CXSparse_SRCS})
target_compile_definitions(cxsparse PUBLIC NCOMPLEX)
target_include_directories(cxsparse PRIVATE ./ ./Include)
target_include_directories(cxsparse PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/Include
  )
if(UNIX)
  target_link_libraries(cxsparse m)
  set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif(UNIX)

install(TARGETS cxsparse
  DESTINATION lib
  EXPORT cxsparse-targets)
INSTALL(FILES ${CXSparse_INCLUDES}
  DESTINATION include)
