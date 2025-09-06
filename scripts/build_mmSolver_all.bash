#!/usr/bin/env bash
#
# Copyright (C) 2019, 2022 David Cattermole.
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
# Builds the Maya MatchMove Solver project for all supported operating
# systems, with Linux as a host operating system.

# Exit immediately if a command exits with a non-zero status.
set -e

# Get the absolute path of the project's root directory.
# realpath resolves the full path, and dirname gets the script's directory.
PROJECT_ROOT=$(realpath "$(dirname "$0")/..")
echo "Project Root: ${PROJECT_ROOT}"

# Ensure scripts are called from the correct location.
cd "${PROJECT_ROOT}"

# Docker common variables.
DOCKERFILE_DIR="${PROJECT_ROOT}/share/docker"
VOLUME="${PROJECT_ROOT}:/mmSolver"

# Run the Docker container to build the given Maya version.
docker_build_project() {
    local MAYA_VERSION=$1
    local NAME="mmsolver-linux-maya${MAYA_VERSION}-build"
    local DOCKERFILE="${DOCKERFILE_DIR}/Dockerfile_maya${MAYA_VERSION}"
    local SCRIPT_PATH="./scripts/build_mmSolver_linux_maya${MAYA_VERSION}.bash"

    echo "Building for Maya ${MAYA_VERSION}..."
    docker buildx build --file "${DOCKERFILE}" -t "${NAME}" "${PROJECT_ROOT}"
    docker container run --volume "${VOLUME}" "${NAME}" "bash -c '${SCRIPT_PATH}'"
}

# Linux - Maya 2022 Build.
docker_build_project 2022

# Linux - Maya 2023 Build.
docker_build_project 2023

# Linux - Maya 2024 Build.
docker_build_project 2024

# Linux - Maya 2025 Build.
docker_build_project 2025

# Linux - Maya 2026 Build.
docker_build_project 2026
