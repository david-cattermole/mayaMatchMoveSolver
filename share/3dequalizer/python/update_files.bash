#!/usr/bin/env bash
#
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
# Updates the Python files in the 3DEqualizer files.
#
# The files below are used in 3dequalizer scripts, bundled into single
# files and are distributed via the 3DEqualizer ScriptDB site.

PROJECT_ROOT=`pwd`

SRC="${PROJECT_ROOT}/python/"
DST="${PROJECT_ROOT}/share/3dequalizer/python"

declare -a FILES=(
    "mmSolver/__init__.py"
    "mmSolver/utils/__init__.py"
    "mmSolver/utils/python_compat.py"
    "mmSolver/utils/loadfile/excep.py"
    "mmSolver/utils/loadfile/floatutils.py"
    "mmSolver/utils/loadfile/formatmanager.py"
    "mmSolver/utils/loadfile/__init__.py"
    "mmSolver/utils/loadfile/keyframedata.py"
    "mmSolver/utils/loadfile/loader.py"
    "mmSolver/utils/loadmarker/fileinfo.py"
    "mmSolver/utils/loadmarker/fileutils.py"
    "mmSolver/utils/loadmarker/formatmanager.py"
    "mmSolver/utils/loadmarker/__init__.py"
    "mmSolver/utils/loadmarker/markerdata.py"
    "mmSolver/utils/loadmarker/formats/__init__.py"
    "mmSolver/utils/loadmarker/formats/pftrack2dt.py"
    "mmSolver/utils/loadmarker/formats/rz2.py"
    "mmSolver/utils/loadmarker/formats/tdetxt.py"
    "mmSolver/utils/loadmarker/formats/uvtrack.py"
)


for i in "${FILES[@]}"
do
    echo "Copying: ${SRC}/$i -> ${DST}/$i"
    cp "${SRC}/$i" "${DST}/$i"
done

cd ${PROJECT_ROOT}
