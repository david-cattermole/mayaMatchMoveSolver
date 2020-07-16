# Building on MacOS

We can build `mmSolver` on MacOS. We have provided a Bash build script
and CMake script which are configurable and readable.

To use the pre-made build scripts, you can use the following commands
to build the entire project (assuming you have already installed the
build dependancies):

On MacOS:
```commandline
$ cd /path/to/project/root/
$ bash scripts/build_qtpy.bash
$ bash scripts/build_cminpack.bash
$ bash scripts/build_mmSolver_mac_mayaXXXX.bash
```

Note: Replace XXXX, with the Maya version use build for.

The sections below explain the process in more detail.

# Installing Build Dependencies

mmSolver has a few dependencies, and are listed in
[BUILD.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD.md#dependencies).
Install the dependencies using the guide listed below.

- MacOS El Capitan 10.11 - https://www.apple.com/
- Xcode 7.3.1 - https://developer.apple.com/download/
- Developer Command line tools 7.3.1 - https://developer.apple.com/download/
- Maya Development Kit (devkit) 2018+ - https://www.autodesk.com/developer-network/platform-technologies/maya
- Maya 2018+ - https://www.autodesk.com.au/products/maya/overview
- CMake 3.x - from cmake website https://cmake.org/download/
- Python (version 2.x or 3.x) - https://www.python.org/downloads/mac-osx/
- Sphinx (using Python 'pip' command)

# Building Dependencies

`cminpack` and `Qt.py` can be easily downloaded and built
for mmSolver using build scripts provided in the `<project
root>/scripts` directory.

On MacOS:
```commandline
$ cd /path/to/project/root
$ bash scripts/build_cminpack.bash
$ bash scripts/build_qtpy.bash
```

If the commands above have worked, you should see the following
directories under `<project root>/external/install`.

- cminpack
- qtpy

These dependencies will automatically be found by the mmSolver build
script and installed.

If you do not want to install `Qt.py` with mmSolver, simply do not use
the build script and delete the directory `<project
root>/external/install/qtpy`.

# Build mmSolver

After building CMinpack, you can now build mmSolver. 

Run these commands, on MacOS:
```commandline
$ cd /path/to/project/root
$ bash scripts/build_mmSolver_mac_mayaXXXX.bash

# Run tests (optional but encouraged)
$ cd build
$ make test
$ cd ..
```

Note: Replace XXXX, with the Maya version use build for.

The build script (using CMake) will perform the following tasks:
- Build documentation using Sphinx.
- Compile Qt Designer .ui files into a format for Maya's version of
  Qt (PySide or PySide2).
- Create a module (.mod) with configuration options.
- Copy all needed files (including dependencies) into a module.

Following the steps above you will have the Maya plug-in compiled, and
installed into your `~/maya/MAYA_VERSION/modules` directory.

The below sections in this file list more details and how to run
different stages of the build manually.

# Customize Build Scripts

To be written.

# CMake Build Script

To be written.

# Building Packages

To be written.

# Compile Qt UI files

To be written.

# Build Documentation

To be written.

# Run Test Suite

To be written.

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).
