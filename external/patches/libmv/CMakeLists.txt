# Wrapper CMakeLists.txt file for 'libmv'.

cmake_minimum_required(VERSION 2.8.12)

project(libmv)

if(WIN32)
  # Fix compilier error with MSVC
  #
  # "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\include\ratio(111): error C2065: 'INTMAX_MAX': undeclared identifier"
  #
  add_definitions(-D__STDC_LIMIT_MACROS)
endif()

add_subdirectory(src)
