#!/bin/bash
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
# Runs 'clang-format' for the project.

# Any subsequent commands which fail will cause the shell script to
# exit immediately.
set -e

PROJECT_ROOT=`pwd`

find \
    ${PROJECT_ROOT}/src \
    ${PROJECT_ROOT}/include \
    ${PROJECT_ROOT}/mmscenegraph/cppbind/src \
    ${PROJECT_ROOT}/mmscenegraph/cppbind/include \
    ${PROJECT_ROOT}/mmscenegraph/cppbind/tests \
    -not -iname *cxx* -iname *.h -or -not -iname *cxx* -iname *.cpp \
    | xargs clang-format --dry-run --style=file --Werror

cd ${PROJECT_ROOT}
