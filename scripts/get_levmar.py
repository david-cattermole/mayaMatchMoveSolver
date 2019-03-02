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
