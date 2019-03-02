"""
Get the CMinpack source code.
"""

import sys
import os
import shutil
import download_unpack


def main(archives_dir, working_dir, patches_dir):
    url = 'http://devernay.free.fr/hacks/cminpack/cminpack-1.3.6.tar.gz'
    archive_name = 'cminpack-1.3.6.tar.gz'
    name = 'cminpack-1.3.6'
    download_unpack.add_package(
        name,
        archive_name,
        url,
        archives_dir,
        working_dir)

    # Patch the CMake script, to ours, so we can build a shared library.
    src = os.path.join(patches_dir, 'cminpack', 'CMakeLists.txt')
    dst = os.path.join(working_dir, name, 'CMakeLists.txt')
    shutil.copy(src, dst)
    return


if __name__ == '__main__':
    archives_dir = os.path.abspath(sys.argv[1])
    working_dir = os.path.abspath(sys.argv[2])
    patches_dir = os.path.abspath(sys.argv[3])
    main(archives_dir, working_dir, patches_dir)
