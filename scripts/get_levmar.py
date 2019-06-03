# Copyright (C) 2019 David Cattermole.
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
#
"""
Get the LevMar source code.
"""

import sys
import os
import shutil
import download_unpack


def main(archives_dir, working_dir, patches_dir):
    url = 'http://users.ics.forth.gr/~lourakis/levmar/levmar-2.6.tgz'
    user_agent = 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    archive_name = 'levmar-2.6.tgz'
    name = 'levmar-2.6'
    download_unpack.add_package(
        name,
        archive_name,
        url,
        archives_dir,
        working_dir,
        user_agent=user_agent)

    # Patch the CMake script, to ours, so we can build a shared library.
    src = os.path.join(patches_dir, 'levmar', 'CMakeLists.txt')
    dst = os.path.join(working_dir, name, 'CMakeLists.txt')
    shutil.copy(src, dst)
    return


if __name__ == '__main__':
    archives_dir = os.path.abspath(sys.argv[1])
    working_dir = os.path.abspath(sys.argv[2])
    patches_dir = os.path.abspath(sys.argv[3])
    main(archives_dir, working_dir, patches_dir)
