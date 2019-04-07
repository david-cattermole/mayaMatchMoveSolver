"""
Get the LevMar source code.
"""

import sys
import os
import download_unpack


def main(archives_dir, working_dir, patches_dir):
    url = 'https://github.com/mottosso/Qt.py/archive/1.1.0.tar.gz'
    user_agent = None
    archive_name = 'Qt.py-1.1.0.tar.gz'
    name = 'Qt.py-1.1.0'
    download_unpack.add_package(
        name,
        archive_name,
        url,
        archives_dir,
        working_dir,
        user_agent=user_agent)
    return


if __name__ == '__main__':
    archives_dir = os.path.abspath(sys.argv[1])
    working_dir = os.path.abspath(sys.argv[2])
    patches_dir = os.path.abspath(sys.argv[3])
    main(archives_dir, working_dir, patches_dir)
