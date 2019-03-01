"""
Compiles *.ui files, and saves the generated files alongside them.

The command may use the embedded paths if no path is given, or it may use an
input file to find the directory.

Usage (PyQt4):
$ cd <project root>
$ python compileUI.py
$ python compileUI.py /path/to/file.ui

Usage (PySide - Maya):
$ cd <project root>
$ mayapy compileUI.py
$ mayapy compileUI.py /path/to/file.ui

Note; Different versions of Maya contain different versions of PySide. Maya
2017 and above contain PySide2 (for Qt5), Maya 2016 contains PySide(1).
"""

import sys
import os
try:
    # pyside 1
    from pysideuic import compileUi
except ImportError:
    try:
        # pyside 2
        from pyside2uic import compileUi
    except ImportError:
        try:
            from PyQt4.uic import compileUi
        except ImportError:
            from PyQt5.uic import compileUi


def compile_file(in_path, out_path):
    """
    Compile a .ui file into a .py file.

    :param in_path: Input .ui file path.
    :type in_path: basestring

    :param out_path: Output .py file path.
    :type out_path: basestring

    :returns: Nothing.
    """
    if in_path.endswith('.ui') is False:
        print('Warning: Skipping %r' % in_path)
        return
    if not os.path.isfile(in_path):
        print('Warning: Skipping: %r' % in_path)
        return
    in_dir, in_name = os.path.split(in_path)
    out_dir, out_name = os.path.split(out_path)

    msg = 'Compiling: {0} -> {1}'
    print(msg.format(in_name, out_name))
    try:
        f = open(out_path, 'w')
        compileUi(in_path, f, False, 4, False)
        f.close()
    except Exception:
        print('Warning: File did not compile, %r' % in_path)
        raise
    return


def compile_directory(in_path_dir, out_path_dir):
    """
    Compiles all .ui files in the given directory into .py files.

    :param in_path_dir: Input directory.
    :type in_path_dir: basestring

    :param out_path_dir: Output directory.
    :type out_path_dir: basestring

    :returns: Nothing.
    """
    in_path_dir = os.path.abspath(in_path_dir)
    out_path_dir = os.path.abspath(out_path_dir)
    in_paths = sorted(os.listdir(in_path_dir))
    for in_name in in_paths:
        if in_name.endswith('.ui') is False:
            continue
        in_fullpath = os.path.join(in_path_dir, in_name)
        if not os.path.isfile(in_fullpath):
            continue
        out_name = 'ui_' + in_name.replace('.ui', '.py')
        out_fullpath = os.path.join(out_path_dir, out_name)
        compile_file(in_fullpath, out_fullpath)
    return


if __name__ == '__main__':
    args = sys.argv[1:]
    paths = []
    if len(args) > 0:
        for arg in args:
            if os.path.isfile(arg):
                path = os.path.dirname(arg)
                paths.append(path)
            elif os.path.isdir(arg):
                paths.append(arg)
    else:
        # Compile all the .ui files in the following paths.
        # All compiled .py files are placed in the same directory as the
        # .ui file.
        paths = [
            './python/mmSolver/tools/channelsen/ui',
            './python/mmSolver/tools/loadmarker/ui',
            './python/mmSolver/tools/solver/ui',
            './python/mmSolver/ui',
        ]
    for path in paths:
        assert os.path.isdir(path) is True
        compile_directory(path, path)
    exit()
