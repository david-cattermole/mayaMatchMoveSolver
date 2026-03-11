#!/bin/bash
#
# Copyright (C) 2024 David Cattermole.
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
# Runs 'inkscape' to export PNG files from .svg files.
#
# This file exports multiple resolutions using a naming convention.

# Any subsequent commands which fail will cause the shell script to
# exit immediately.
set -e

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

INKSCAPE_EXE="inkscape"

OUTPUT_DIR="${THIS_DIR}"

cd ${THIS_DIR}

# Export node PNG icons at 20 x 20 resolution, for use in the Outliner.
#
# 20 x 20 is the resolution expected by Maya's Outliner.
OUT_RESOLUTION=20
for i in edit/node/*.svg; do
    name=$(basename "${i}" .svg)
    echo "-------------------------------------------------------------"
    echo "Input file: ${i}"
    echo "Output file: ${OUTPUT_DIR}/out_${name}.png"

    ${INKSCAPE_EXE} \
        --without-gui \
        --export-area-page \
        --export-width=${OUT_RESOLUTION} \
        --export-height=${OUT_RESOLUTION} \
        --file="${i}" \
        --export-png="${OUTPUT_DIR}/out_${name}.png"
done

# Export node plain SVG icons.
OUT_RESOLUTION=20
for i in edit/node/*.svg; do
    name=$(basename "${i}" .svg)
    echo "-------------------------------------------------------------"
    echo "Input file: ${i}"
    echo "Output file: ${OUTPUT_DIR}/${name}.svg"

    ${INKSCAPE_EXE} \
        --without-gui \
        --export-area-page \
        --file="${i}" \
        --export-plain-svg="${OUTPUT_DIR}/${name}.svg"
done

# Export shelf PNG icons at 32 x 32 resolution.
OUT_RESOLUTION=32
for i in edit/shelf/*.svg; do
    name=$(basename "${i}" .svg)
    echo "-------------------------------------------------------------"
    echo "Input file: ${i}"
    echo "Output file: ${OUTPUT_DIR}/${name}_${OUT_RESOLUTION}x${OUT_RESOLUTION}.png"

    ${INKSCAPE_EXE} \
        --without-gui \
        --export-area-page \
        --export-width=${OUT_RESOLUTION} \
        --export-height=${OUT_RESOLUTION} \
        --file="${i}" \
        --export-png="${OUTPUT_DIR}/${name}.png"
done

# Export shelf PNG icons at 48 x 48 resolution (150% scale).
OUT_RESOLUTION=48
for i in edit/shelf/*.svg; do
    name=$(basename "${i}" .svg)
    echo "-------------------------------------------------------------"
    echo "Input file: ${i}"
    echo "Output file: ${OUTPUT_DIR}/${name}_150.png"

    ${INKSCAPE_EXE} \
        --without-gui \
        --export-area-page \
        --export-width=${OUT_RESOLUTION} \
        --export-height=${OUT_RESOLUTION} \
        --file="${i}" \
        --export-png="${OUTPUT_DIR}/${name}_150.png"
done

# Export shelf PNG icons at 64 x 64 resolution (200% scale).
OUT_RESOLUTION=64
for i in edit/shelf/*.svg; do
    name=$(basename "${i}" .svg)
    echo "-------------------------------------------------------------"
    echo "Input file: ${i}"
    echo "Output file: ${OUTPUT_DIR}/${name}_200.png"

    ${INKSCAPE_EXE} \
        --without-gui \
        --export-area-page \
        --export-width=${OUT_RESOLUTION} \
        --export-height=${OUT_RESOLUTION} \
        --file="${i}" \
        --export-png="${OUTPUT_DIR}/${name}_200.png"
done
