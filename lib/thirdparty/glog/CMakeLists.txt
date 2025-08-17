# Copyright (C) 2025 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------
#
# CMake build for vendored glog (version 0.7.1)
#
# This is a simplified build of glog, configured for compatibility with Ceres 1.14.0.
# It builds glog as a static library without tests, gflags, or other optional features.
#

set(GLOG_VERSION "0.7.1")
set(GLOG_VERSION_MAJOR 0)
set(GLOG_VERSION_MINOR 7)
set(GLOG_VERSION_PATCH 1)

# Required CMake modules..
include(CheckIncludeFile)
include(CheckFunctionExists)
include(CheckSymbolExists)
include(CheckCXXSymbolExists)
include(CheckTypeSize)
include(CheckCXXCompilerFlag)
include(GenerateExportHeader)

# Compiler feature detection.
check_include_file(dlfcn.h HAVE_DLFCN_H)
check_include_file(execinfo.h HAVE_EXECINFO_H)
check_include_file(memory.h HAVE_MEMORY_H)
check_include_file(pwd.h HAVE_PWD_H)
check_include_file(sys/stat.h HAVE_SYS_STAT_H)
check_include_file(sys/syscall.h HAVE_SYS_SYSCALL_H)
check_include_file(sys/time.h HAVE_SYS_TIME_H)
check_include_file(sys/types.h HAVE_SYS_TYPES_H)
check_include_file(sys/utsname.h HAVE_SYS_UTSNAME_H)
check_include_file(syscall.h HAVE_SYSCALL_H)
check_include_file(syslog.h HAVE_SYSLOG_H)
check_include_file(unistd.h HAVE_UNISTD_H)
check_include_file(ucontext.h HAVE_UCONTEXT_H)

check_function_exists(fcntl HAVE_FCNTL)
check_function_exists(sigaltstack HAVE_SIGALTSTACK)
check_cxx_symbol_exists(snprintf cstdio HAVE_SNPRINTF)
check_symbol_exists(__argv sys/stdlib.h HAVE___ARGV)
check_symbol_exists(__progname stdlib.h HAVE___PROGNAME)

# Check for system types that might conflict.
check_type_size("mode_t" HAVE_MODE_T)
check_type_size("ssize_t" HAVE_SSIZE_T)
check_function_exists(pread HAVE_PREAD)
check_function_exists(pwrite HAVE_PWRITE)

# Configure the config.h file from template.
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/src/config.h.cmake.in
               ${CMAKE_CURRENT_BINARY_DIR}/config.h)

# Copy all glog header files to build directory.
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/src/glog/
     DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/glog/
     FILES_MATCHING PATTERN "*.h")


# Source files.
set(GLOG_SRCS
    src/demangle.cc
    src/flags.cc
    src/logging.cc
    src/raw_logging.cc
    src/signalhandler.cc
    src/stacktrace.cc
    src/symbolize.cc
    src/utilities.cc
    src/vlog_is_on.cc
)

# Windows-specific source files
if(WIN32)
    list(APPEND GLOG_SRCS src/windows/port.cc)
endif()

# Create the glog library as the standard glog::glog target.
add_library(glog STATIC ${GLOG_SRCS})
target_compile_features(glog PUBLIC cxx_std_14)

# Generate export header using CMake standard approach.
generate_export_header(glog
  BASE_NAME glog
  EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/glog/export.h
  STATIC_DEFINE GLOG_STATIC_DEFINE
)

# Configure compile definitions for static library.
#
# Also see glog compile flags in:
# - "<PROJECT_ROOT>/src/CMakeLists.txt"
# - "<PROJECT_ROOT>/share/cmake/modules/FindCeres.cmake"
target_compile_definitions(glog PUBLIC
  GLOG_STATIC_DEFINE
  GLOG_USE_GLOG_EXPORT
  GOOGLE_GLOG_DLL_DECL=
  GOOGLE_GLOG_DLL_DECL_FOR_UNITTESTS=
)

target_compile_definitions(glog PRIVATE
  $<$<CONFIG:Debug>:_DEBUG>
  HAVE_CONFIG_H
  $<$<PLATFORM_ID:Windows>:GLOG_USE_WINDOWS_PORT>
  $<$<PLATFORM_ID:Windows>:NOMINMAX>
)

# Include directories
target_include_directories(glog PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
  $<INSTALL_INTERFACE:include>
)

target_include_directories(glog PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_BINARY_DIR}
  $<$<PLATFORM_ID:Windows>:${CMAKE_CURRENT_SOURCE_DIR}/src/windows>
)

# Link libraries
if (WIN32)
  target_link_libraries(glog PUBLIC dbghelp)
endif()

# Find required threading library
find_package(Threads REQUIRED)
target_link_libraries(glog PUBLIC Threads::Threads)

# Create the glog::glog alias for compatibility
add_library(glog::glog ALIAS glog)

# Set library properties
set_target_properties(glog PROPERTIES
  VERSION ${GLOG_VERSION}
  SOVERSION ${GLOG_VERSION_MAJOR}
  POSITION_INDEPENDENT_CODE ON
  OUTPUT_NAME glog
)

message(STATUS "glog: Version ${GLOG_VERSION} (vendored)")
