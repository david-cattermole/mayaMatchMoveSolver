#!/usr/bin/env bash
#
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
# Centralised build directory configuration for Linux builds.
#
# This file defines all build directory names, paths, and patterns used
# across the mmSolver build system. By centralising these definitions,
# we ensure consistency and make it easier to maintain the build system.
#
# NOTE: This file should be sourced by build scripts after MAYA_VERSION
# has been set, as many paths depend on the Maya version.

# Validate that MAYA_VERSION is set.
if [ -z "$MAYA_VERSION" ]; then
    echo "WARNING: MAYA_VERSION not set when sourcing build_config_linux.bash"
    echo "Some build directory paths may be incomplete."
fi

# Base build directory configuration.
#
# Can be overridden by setting BUILD_DIR_BASE environment variable.
if [ -z "$BUILD_DIR_BASE" ]; then
    BUILD_DIR_BASE="$(pwd)/.."
fi

# Build directory names.
BUILD_MMSOLVER_DIR_NAME="build_mmsolver"
BUILD_OCIO_DIR_NAME="build_opencolorio"
BUILD_MMSOLVERLIBS_DIR_NAME="build_mmsolverlibs"  # Legacy

# Build directory base paths.
BUILD_MMSOLVER_DIR_BASE="${BUILD_DIR_BASE}/${BUILD_MMSOLVER_DIR_NAME}"
BUILD_OCIO_DIR_BASE="${BUILD_DIR_BASE}/${BUILD_OCIO_DIR_NAME}"
BUILD_MMSOLVERLIBS_DIR_BASE="${BUILD_DIR_BASE}/${BUILD_MMSOLVERLIBS_DIR_NAME}"  # Legacy

# Set default BUILD_TYPE if not already set.
if [ -z "$BUILD_TYPE" ]; then
    BUILD_TYPE=Release
fi

# Build directory patterns.
BUILD_CMAKE_DIR_PATTERN="cmake_linux_maya${MAYA_VERSION}_${BUILD_TYPE}"
BUILD_RUST_DIR_PATTERN="rust_linux_maya${MAYA_VERSION}"
BUILD_PYTHON_VENV_DIR_PATTERN="python_venv_linux_maya${MAYA_VERSION}"
BUILD_DOCS_DIR_PATTERN="docs_linux_maya${MAYA_VERSION}"

# OCIO-specific patterns.
OCIO_INSTALL_DIR_PATTERN="install/maya${MAYA_VERSION}_linux"
OCIO_SOURCE_DIR_PATTERN="source/maya${MAYA_VERSION}_linux"

# Derived paths.
BUILD_MMSOLVER_CMAKE_DIR="${BUILD_MMSOLVER_DIR_BASE}/${BUILD_CMAKE_DIR_PATTERN}"
BUILD_MMSOLVER_RUST_DIR="${BUILD_MMSOLVER_DIR_BASE}/${BUILD_RUST_DIR_PATTERN}"
BUILD_MMSOLVER_PYTHON_VENV_DIR="${BUILD_MMSOLVER_DIR_BASE}/${BUILD_PYTHON_VENV_DIR_PATTERN}"
BUILD_DOCS_DIR_BASE="${BUILD_MMSOLVER_DIR_BASE}/${BUILD_DOCS_DIR_PATTERN}/"

BUILD_OCIO_CMAKE_DIR="${BUILD_OCIO_DIR_BASE}/${BUILD_CMAKE_DIR_PATTERN}"
BUILD_OCIO_INSTALL_DIR="${BUILD_OCIO_DIR_BASE}/${OCIO_INSTALL_DIR_PATTERN}/"
BUILD_OCIO_SOURCE_DIR="${BUILD_OCIO_DIR_BASE}/${OCIO_SOURCE_DIR_PATTERN}"

# For backwards compatibility with existing scripts.
MMSOLVERLIBS_CPP_TARGET_DIR="${BUILD_MMSOLVER_RUST_DIR}"
PYTHON_VIRTUAL_ENV_DIR_NAME="${BUILD_PYTHON_VENV_DIR_PATTERN}"

# Export all variables for use by child scripts.
export BUILD_DIR_BASE
export BUILD_MMSOLVER_DIR_NAME BUILD_OCIO_DIR_NAME BUILD_MMSOLVERLIBS_DIR_NAME
export BUILD_MMSOLVER_DIR_BASE BUILD_OCIO_DIR_BASE BUILD_MMSOLVERLIBS_DIR_BASE
export BUILD_CMAKE_DIR_PATTERN BUILD_RUST_DIR_PATTERN BUILD_PYTHON_VENV_DIR_PATTERN BUILD_DOCS_DIR_PATTERN
export OCIO_INSTALL_DIR_PATTERN OCIO_SOURCE_DIR_PATTERN
export BUILD_MMSOLVER_CMAKE_DIR BUILD_MMSOLVER_RUST_DIR BUILD_MMSOLVER_PYTHON_VENV_DIR BUILD_DOCS_DIR_BASE
export BUILD_OCIO_CMAKE_DIR BUILD_OCIO_INSTALL_DIR BUILD_OCIO_SOURCE_DIR
export MMSOLVERLIBS_CPP_TARGET_DIR PYTHON_VIRTUAL_ENV_DIR_NAME

# Debug output when VERBOSE is set.
if [ "$VERBOSE" = "1" ]; then
    echo "Build Config Linux:"
    echo "  BUILD_DIR_BASE: ${BUILD_DIR_BASE}"
    echo "  BUILD_MMSOLVER_DIR_BASE: ${BUILD_MMSOLVER_DIR_BASE}"
    echo "  BUILD_OCIO_DIR_BASE: ${BUILD_OCIO_DIR_BASE}"
    echo "  BUILD_MMSOLVER_CMAKE_DIR: ${BUILD_MMSOLVER_CMAKE_DIR}"
    echo "  BUILD_MMSOLVER_RUST_DIR: ${BUILD_MMSOLVER_RUST_DIR}"
    echo "  BUILD_MMSOLVER_PYTHON_VENV_DIR: ${BUILD_MMSOLVER_PYTHON_VENV_DIR}"
    echo "  BUILD_DOCS_DIR_BASE: ${BUILD_DOCS_DIR_BASE}"
fi
