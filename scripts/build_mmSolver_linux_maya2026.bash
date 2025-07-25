#!/usr/bin/env bash
#
# Copyright (C) 2019, 2022, 2023, 2024 David Cattermole.
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
# Builds the Maya MatchMove Solver project.

# Build location - where to build the project.
#
# Defaults to ${PROJECT_ROOT}/.. if not set.
if [ -z "$BUILD_DIR_BASE" ]; then
    BUILD_DIR_BASE="$(pwd)/.."
fi

# Maya
MAYA_VERSION=2026
MAYA_LOCATION=/usr/autodesk/maya2026/

# Executable names/paths used for build process.
PYTHON_EXE=python3.9
CMAKE_EXE=cmake3
RUST_CARGO_EXE=cargo

# OpenColorIO specific options.
OPENCOLORIO_TARBALL_NAME="OpenColorIO-2.3.2.tar.gz"
OPENCOLORIO_TARBALL_EXTRACTED_DIR_NAME="OpenColorIO-2.3.2"
EXPAT_RELATIVE_CMAKE_DIR=lib64/cmake/expat-2.4.1/
EXPAT_RELATIVE_LIB_PATH=lib64/libexpat.a
# yaml-cpp 0.7.0
YAML_RELATIVE_CMAKE_DIR=share/cmake/yaml-cpp
YAML_RELATIVE_LIB_PATH=lib64/libyaml-cpp.a
PYSTRING_RELATIVE_LIB_PATH=lib64/libpystring.a
ZLIB_RELATIVE_LIB_PATH=lib/libz.a

# Manually override OpenGL include headers, because CMake doesn't seem
# to automatically find OpenGL headers on RockyLinux8 (which is used
# in the Docker containers).
OPENGL_INCLUDE_DIR=/usr/include/

# Which version of the VFX platform are we "using"? (Maya doesn't
# currently conform to the VFX Platform.)
VFX_PLATFORM=2024

# C++ Standard to use.
CXX_STANDARD=14

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

CWD=`pwd`

# These scripts assume 'RUST_CARGO_EXE' has been set to the Rust
# 'cargo' executable.
source "${CWD}/scripts/internal/build_openColorIO_linux.bash"
source "${CWD}/scripts/internal/build_mmSolverLibs_linux.bash"
source "${CWD}/scripts/internal/build_mmSolver_linux.bash"

cd ${CWD}
