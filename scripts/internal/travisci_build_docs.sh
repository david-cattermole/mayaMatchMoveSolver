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
# Run on TravisCI, builds the documentation for mmSolver, ready to be
# uploaded to GitHub pages.

# The -e flag causes the script to exit as soon as one command returns
# a non-zero exit code.
set -ev

PROJECT_ROOT=`pwd`

cd docs

# Configure the documentation.
cp source/conf.py.in source/conf.py
sed -i 's/@PROJECT_NAME@/mayaMatchMoveSolver/g' source/conf.py
sed -i 's/@PROJECT_COPYRIGHT@/2018-2022, David Cattermole, Anil Reddy, Kazuma Tonegawa, and Patcha Saheb Binginapalli./g' source/conf.py
sed -i 's/@PROJECT_VERSION@/master/g' source/conf.py

make html

# Makes 'jekyll build' run by GitHub Pages ignore the files in this
# directory.
touch build_linux_maya2022/html/.nojekyll

cd ${PROJECT_ROOT}
