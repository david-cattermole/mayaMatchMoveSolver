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

# Allow creating DLLs in Windows without touching the source code:
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

message(STATUS "GFLAGS_ROOT: ${GFLAGS_ROOT}")
message(STATUS "GLOG_ROOT: ${GLOG_ROOT}")
message(STATUS "LDL_ROOT: ${LDL_ROOT}")
message(STATUS "COLAMD_ROOT: ${COLAMD_ROOT}")
message(STATUS "EIGEN_INCLUDE_DIR: ${EIGEN_INCLUDE_DIR}")

set(GFLAGS_ROOT /usr/local/gflags CACHE PATH "Root path for Google Flags installation.")
set(GFLAGS_INCLUDE_DIR /usr/include/gflags CACHE PATH "Google Flags headers directory.")
set(GFLAGS_LIBRARY_DIR /usr/lib CACHE PATH "Google Flags library directory.")

set(GLOG_ROOT /usr/local/glog CACHE PATH "Root path for Google Log installation.")
set(GLOG_INCLUDE_DIR /usr/include/glog CACHE PATH "Google Log headers directory.")
set(GLOG_LIBRARY_DIR /usr/lib CACHE PATH "Google Log library directory.")

set(LDL_ROOT /usr/local/ldl CACHE PATH "Root path for LDL installation.")
set(LDL_INCLUDE_DIR /usr/include/ldl CACHE PATH "LDL headers directory.")
set(LDL_LIBRARY_DIR /usr/lib CACHE PATH "LDL library directory.")

set(COLAMD_ROOT /usr/local/colamd CACHE PATH "Root path for COLAMD installation.")
set(COLAMD_INCLUDE_DIR /usr/include/colamd CACHE PATH "COLAMD headers directory.")
set(COLAMD_LIBRARY_DIR /usr/lib CACHE PATH "COLAMD library directory.")

set(SUITE_SPARSE_CONFIG_ROOT /usr/local/suite_sparse_config CACHE PATH
  "Root path for SUITE_SPARSE_CONFIG installation.")
set(SUITE_SPARSE_CONFIG_INCLUDE_DIR /usr/include/suite_sparse_config CACHE PATH
  "SUITE_SPARSE_CONFIG headers directory.")
set(SUITE_SPARSE_CONFIG_LIBRARY_DIR /usr/lib CACHE PATH
  "SUITE_SPARSE_CONFIG library directory.")


set(EIGEN_INCLUDE_DIR /usr/include/eigen CACHE PATH "Root path for Eigen headers.")


# Google Flags
find_path(GFLAGS_INCLUDE_DIR gflags/gflags.h
  HINTS
      ${GFLAGS_ROOT}
      ${GFLAGS_INCLUDE_DIR}
      /usr/local/include
      /usr/include
  PATH_SUFFIXES
      include/
  )
find_library(GFLAGS_LIBRARY
  NAMES
      libgflags
      libgflags_static
      gflags_static
      gflags
  HINTS
      ${GFLAGS_ROOT}
      ${GFLAGS_LIBRARY_DIR}
      /usr/local/lib
      /usr/lib
  PATH_SUFFIXES
      lib/
  )
message(STATUS "GFLAGS_INCLUDE_DIR: ${GFLAGS_INCLUDE_DIR}")
message(STATUS "GFLAGS_LIBRARY: ${GFLAGS_LIBRARY}")

set(GFLAGS_FOUND False)
if(GFLAGS_INCLUDE_DIR AND GFLAGS_LIBRARY)
  set(GFLAGS_INCLUDE_DIRS ${GFLAGS_INCLUDE_DIR} )
  set(GFLAGS_LIBRARIES ${GFLAGS_LIBRARY} )
  set(GFLAGS_FOUND True)
endif()


# Google Log
find_path(GLOG_INCLUDE_DIR glog.h
  HINTS
      ${GLOG_INCLUDE_DIR}
      ${GLOG_ROOT}
      /usr/local/include
      /usr/include
  PATH_SUFFIXES
      include/
  )
find_library(GLOG_LIBRARY glog
  HINTS
      ${GLOG_LIBRARY_DIR}
      ${GLOG_ROOT}
      /usr/local/lib
      /usr/lib
  PATH_SUFFIXES
      lib/
  )
message(STATUS "GLOG_INCLUDE_DIR: ${GLOG_INCLUDE_DIR}")
message(STATUS "GLOG_LIBRARY: ${GLOG_LIBRARY}")

set(GLOG_FOUND False)
if(GLOG_INCLUDE_DIR AND GLOG_LIBRARY)
  set(GLOG_INCLUDE_DIRS ${GLOG_INCLUDE_DIR} )
  set(GLOG_LIBRARIES ${GLOG_LIBRARY} )
  set(GLOG_FOUND True)
endif()


# LDL
find_path(LDL_INCLUDE_DIR ldl.h
  HINTS
      ${LDL_INCLUDE_DIR}
      ${LDL_ROOT}
      /usr/local/include
      /usr/include
  )
find_library(LDL_LIBRARY ldl
  NAMES
      ldl
      libldl
  HINTS
      ${LDL_LIBRARY_DIR}
      ${LDL_ROOT}
      /usr/local/lib
      /usr/lib
  PATH_SUFFIXES
      lib/
      )
message(STATUS "LDL_INCLUDE_DIR: ${LDL_INCLUDE_DIR}")
message(STATUS "LDL_LIBRARY: ${LDL_LIBRARY}")

# set(LDL_LIBRARIES LDL_LIBRARY_NOT_FOUND)
# set(LDL_INCLUDE_DIRS LDL_INCLUDE_NOT_FOUND)
set(LDL_FOUND False)
if(LDL_INCLUDE_DIR AND LDL_LIBRARY)
  set(LDL_INCLUDE_DIRS ${LDL_INCLUDE_DIR} )
  set(LDL_LIBRARIES ${LDL_LIBRARY} )
  set(LDL_FOUND True)
endif()

message(STATUS "LDL_FOUND: ${LDL_FOUND}")
message(STATUS "LDL_INCLUDE_DIRS: ${LDL_INCLUDE_DIRS}")
message(STATUS "LDL_LIBRARIES: ${LDL_LIBRARIES}")


# COLAMD
find_path(COLAMD_INCLUDE_DIR colamd.h
  HINTS
      ${COLAMD_INCLUDE_DIR}
      ${COLAMD_ROOT}
      /usr/local/include
      /usr/include
  )
find_library(COLAMD_LIBRARY colamd
  NAMES
      colamd
      libcolamd
  HINTS
      ${COLAMD_LIBRARY_DIR}
      ${COLAMD_ROOT}
      /usr/local/lib
      /usr/lib
  PATH_SUFFIXES
      lib/
  )
message(STATUS "COLAMD_INCLUDE_DIR: ${COLAMD_INCLUDE_DIR}")
message(STATUS "COLAMD_LIBRARY: ${COLAMD_LIBRARY}")

set(COLAMD_LIBRARIES COLAMD_LIBRARY_NOT_FOUND)
set(COLAMD_INCLUDE_DIRS COLAMD_INCLUDE_NOT_FOUND)
set(COLAMD_FOUND False)
if(COLAMD_INCLUDE_DIR AND COLAMD_LIBRARY)
  set(COLAMD_INCLUDE_DIRS ${COLAMD_INCLUDE_DIR} )
  set(COLAMD_LIBRARIES ${COLAMD_LIBRARY} )
  set(COLAMD_FOUND True)
endif()

message(STATUS "COLAMD_FOUND: ${COLAMD_FOUND}")
message(STATUS "COLAMD_INCLUDE_DIRS: ${COLAMD_INCLUDE_DIRS}")
message(STATUS "COLAMD_LIBRARIES: ${COLAMD_LIBRARIES}")


# SuiteSparse Config
find_path(SUITE_SPARSE_CONFIG_INCLUDE_DIR SuiteSparse_config.h
  HINTS
      ${SUITE_SPARSE_CONFIG_INCLUDE_DIR}
      ${SUITE_SPARSE_CONFIG_ROOT}
      /usr/local/include
      /usr/include
  )
find_library(SUITE_SPARSE_CONFIG_LIBRARY suitesparseconfig
  NAMES
      suitesparseconfig
      libsuitesparseconfig
  HINTS
      ${SUITE_SPARSE_CONFIG_LIBRARY_DIR}
      ${SUITE_SPARSE_CONFIG_ROOT}
      /usr/local/lib
      /usr/lib
  PATH_SUFFIXES
      lib/
  )
message(STATUS "SUITE_SPARSE_CONFIG_INCLUDE_DIR: ${SUITE_SPARSE_CONFIG_INCLUDE_DIR}")
message(STATUS "SUITE_SPARSE_CONFIG_LIBRARY: ${SUITE_SPARSE_CONFIG_LIBRARY}")

set(SUITE_SPARSE_CONFIG_LIBRARIES SUITE_SPARSE_CONFIG_LIBRARY_NOT_FOUND)
set(SUITE_SPARSE_CONFIG_INCLUDE_DIRS SUITE_SPARSE_CONFIG_INCLUDE_NOT_FOUND)
set(SUITE_SPARSE_CONFIG_FOUND False)
if(SUITE_SPARSE_CONFIG_INCLUDE_DIR AND SUITE_SPARSE_CONFIG_LIBRARY)
  set(SUITE_SPARSE_CONFIG_INCLUDE_DIRS ${SUITE_SPARSE_CONFIG_INCLUDE_DIR} )
  set(SUITE_SPARSE_CONFIG_LIBRARIES ${SUITE_SPARSE_CONFIG_LIBRARY} )
  set(SUITE_SPARSE_CONFIG_FOUND True)
endif()

message(STATUS "SUITE_SPARSE_CONFIG_FOUND: ${SUITE_SPARSE_CONFIG_FOUND}")
message(STATUS "SUITE_SPARSE_CONFIG_INCLUDE_DIRS: ${SUITE_SPARSE_CONFIG_INCLUDE_DIRS}")
message(STATUS "SUITE_SPARSE_CONFIG_LIBRARIES: ${SUITE_SPARSE_CONFIG_LIBRARIES}")


# Eigen headers.
set(EIGEN_INCLUDE_DIRS ${EIGEN_INCLUDE_DIR})


add_subdirectory(src)
