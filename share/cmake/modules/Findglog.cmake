# Copyright (C) 2022 David Cattermole.
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
# - glog finder module
# This module sets up the vendored glog library.
#
# Defines Variables:
# - glog_FOUND
# - glog_LIBRARIES
# - glog_INCLUDE_DIRS
#

# Always use vendored glog.
message(STATUS "glog: Using vendored glog library")
set(glog_FOUND TRUE)

# Include both source and build directories for headers.
set(glog_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/lib/thirdparty/glog/src;${CMAKE_BINARY_DIR}/lib/thirdparty/glog")
set(glog_LIBRARY "glog::glog")
set(glog_LIBRARIES "glog::glog")

# Display configuration.
if(glog_FOUND)
  message(STATUS "glog: Found=${glog_FOUND} (vendored)")
  message(STATUS "glog: Include=${glog_INCLUDE_DIR}")
  message(STATUS "glog: Library=${glog_LIBRARY}")
endif()

# Mark variables as advanced for GUI CMake tools.
mark_as_advanced(
  glog_INCLUDE_DIR
  glog_LIBRARY
)
