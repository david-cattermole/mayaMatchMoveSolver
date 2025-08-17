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
# CMake build for vendored CMinpack (version 1.3.8)
#
# This is a simplified build of CMinpack, configured for use with mmSolver.
# It only builds the double precision version needed by mmSolver.
#

set(CMINPACK_VERSION "1.3.8")
set(CMINPACK_SOVERSION "1")

# Define the source files for CMinpack
set(CMINPACK_SOURCE_FILES
  # Headers
  cminpack.h
  cminpackP.h
  minpack.h

  # Double precision C source files
  chkder.c
  covar.c
  covar1.c
  dogleg.c
  dpmpar.c
  enorm.c
  fdjac1.c
  fdjac2.c
  hybrd.c
  hybrd1.c
  hybrj.c
  hybrj1.c
  lmder.c
  lmder1.c
  lmdif.c
  lmdif1.c
  lmpar.c
  lmstr.c
  lmstr1.c
  qform.c
  qrfac.c
  qrsolv.c
  r1mpyq.c
  r1updt.c
  rwupdt.c
)

# Create the cminpack static library
add_library(cminpack_s STATIC ${CMINPACK_SOURCE_FILES})

# Set library properties
set_target_properties(cminpack_s PROPERTIES
  VERSION ${CMINPACK_VERSION}
  SOVERSION ${CMINPACK_SOVERSION}
)

# Configure include directories
target_include_directories(cminpack_s PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
  $<INSTALL_INTERFACE:include/cminpack-1>
)

# Configure compile definitions
target_compile_definitions(cminpack_s PUBLIC
  CMINPACK_PRECISION=d  # Double precision
)

# Windows-specific configuration
if(WIN32)
  target_compile_definitions(cminpack_s PUBLIC
    CMINPACK_NO_DLL
  )
endif()

# Set position independent code if needed
if(CMAKE_POSITION_INDEPENDENT_CODE)
  set_target_properties(cminpack_s PROPERTIES
    POSITION_INDEPENDENT_CODE ON
  )
endif()

# Create an alias to match the expected target name
add_library(cminpack::cminpack ALIAS cminpack_s)
