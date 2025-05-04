# Building on MacOS

*NOTE:* Building for MacOS is no longer supported after v0.3.15 on
Maya 2019 with MacOS El Capitan 10.11. These build instructions are
provided for historical reasons only and are not up to date (as of
Maya 2020).

We can build `mmSolver` on MacOS. We have provided a Bash build script
and CMake script which are configurable and readable for developers.

To use the pre-made build scripts, you can use the following commands
to build the entire project (assuming you have already installed the
build dependancies):

On MacOS:
```commandline
$ cd /path/to/project/root/
$ bash scripts/build_thirdparty_mac_mayaXXXX.bash
$ bash scripts/build_mmSolver_mac_mayaXXXX.bash
```

Note: Replace XXXX, with the Maya version to build for.

The sections below explain the process in more detail.

# Installing Build Dependencies

mmSolver has a few dependencies, and are listed in
[BUILD.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD.md#dependencies).
Install the dependencies using the guide listed below.

- Maya 2018 and 2019
  - MacOS El Capitan 10.11 - https://www.apple.com/
  - Xcode 7.3.1 - https://developer.apple.com/download/
  - Developer Command line tools 7.3.1 - https://developer.apple.com/download/
  - Maya Development Kit (devkit) 2018 or 2019 - https://www.autodesk.com/developer-network/platform-technologies/maya
  - Maya 2018 or 2019 - https://www.autodesk.com.au/products/maya/overview
- CMake 3.x - from cmake website https://cmake.org/download/
- Python (version 2.x or 3.x) - https://www.python.org/downloads/mac-osx/
- Sphinx 1.8.5+ (using Python 'pip' command - see below)

- Maya 2020
  - MacOS El Capitan 10.14 - https://www.apple.com/
  - Xcode 10.2.1 - https://developer.apple.com/download/
  - Maya Development Kit (devkit) 2020 - https://www.autodesk.com/developer-network/platform-technologies/maya
  - Maya 2020 - https://www.autodesk.com.au/products/maya/overview

NOTE: Some of these dependancies are requirements of the Maya version and
should be obtained from the Maya developer documentation.

## Installing Maya Development Kit

The Maya development environment must be installed and set up
correctly. The Autodesk Maya documentation contains details on how
this can be done.

- [Maya 2018](https://help.autodesk.com/view/MAYAUL/2018/ENU/?guid=__files_Setting_up_your_build_environment_Mac_OS_X_environment_htm)
- [Maya 2019](https://help.autodesk.com/view/MAYAUL/2019/ENU/?guid=__developer_Maya_SDK_MERGED_Setting_up_your_build_Mac_OS_X_environment_html)

When you download the devkit, make sure to extract it. mmSolver will
use the devkit files for building. It is assumed the devkit is
installed to `~/maya####_devkitBase/devkit/bin/` (with `####` replaced
with the Maya version number), otherwise you should modify the
`<project root>/scripts/build_mmSolver_mac_maya####.bash` script with
the correct path.

## Installing Sphinx

To install Sphinx, you can use the Pythin package manager:
```commandline
$ pip install sphinx
```

## Checking Build Dependencies

Running the below commands should give you a similar output and will
mean you have all the needed dependancies.
```commandline
$ cmake --version
cmake version 3.0.2

CMake suite maintained and supported by Kitware (kitware.com/cmake).

$ clang --version
Apple LLVM version 7.3.0 (clang-703.0.31)
Target: x86_64-apple-darwin15.0.0
Thread model: posix
InstalledDir: /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin

$ make --version
GNU Make 3.81
Copyright (C) 2006  Free Software Foundation, Inc.
This is free software; see the source for copying conditions.
There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.

This program built for i386-apple-darwin11.3.0

$ python --version
Python 2.7.18

$ pip show sphinx
Name: Sphinx
Version: 1.8.5
Summary: Python documentation generator
Home-page: http://sphinx-doc.org/
Author: Georg Brandl
Author-email: georg@python.org
License: BSD
Location: /Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages
Requires: sphinxcontrib-websupport, imagesize, setuptools, babel, typing, Pygments, requests, six, docutils, packaging, snowballstemmer, alabaster, Jinja2
Required-by:

```

If everything looks good you can proceed to building, otherwise you
will need to find and install the required dependancy.

# Building Dependencies

The dependencies can be easily downloaded and built for mmSolver using
build scripts provided in the `<project root>/scripts` directory.

On MacOS:
```commandline
$ cd /path/to/project/root
$ bash scripts/build_thirdparty_mac_mayaXXXX.bash
```

Note: Replace XXXX, with the Maya version to build for.

If the commands above have worked, you should see the following
directories under `<project root>/external/install`.

- cminpack
- eigen
- libmv
- openMVG

These dependencies will automatically be found by the mmSolver build
script and installed.

# Build mmSolver

After building Thirdparty, you can now build mmSolver.

Run these commands, on MacOS:
```commandline
$ cd <project root>
$ bash scripts/build_mmSolver_mac_mayaXXXX.bash

# Run tests (optional but encouraged)
$ cd build
$ make test
$ cd ..
```

Note: Replace XXXX, with the Maya version to build for.

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

The build scripts contain default values for your version of Maya, and
will work for default installations. If you have a custom install
path, then you may need to edit the build scripts.

Below lists the variables in the build scripts:

| Variable           | Description                                  |                                 Example Value |
| ------------       | -----------                                  |                                   ----------- |
| MAYA_VERSION       | Maya version to build for.                   |                                        `2018` |
| MAYA_LOCATION      | Location for Maya header (.h) files.         |             `/Applications/Autodesk/maya2018` |
| INSTALL_MODULE_DIR | Directory to install the Maya module.        | `~/Library/Preferences/Autodesk/2018/modules` |
| FRESH_BUILD        | Delete all build files before re-compiling.  |                                             1 |
| RUN_TESTS          | After build, run the test suite inside Maya. |                                             0 |
| WITH_CMINPACK      | Use the CMinpack library for solving.        |                                             1 |
| BUILD_PACKAGE      | Create an archive file ready to distribute.  |                                             0 |

# CMake Build Script

For those needing or wanting to compile the ``mmSolver`` Maya plug-in
manually you can do it easily using the following commands.

Example CMake usage on MacOS:
```commandline
$ cd <project root>
$ mkdir build
$ cd build

# Configure make files
$ cmake -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=~/Library/Preferences/Autodesk/2018/modules \
        -DUSE_CMINPACK=1 \
        -DMAYA_VERSION=2018 \
        -DMAYA_LOCATION=/Applications/Autodesk/maya2018 \
        -DCMINPACK_ROOT=/project_root/external/install/cminpack \
        ..

# Compile the project (including documentation, and Qt .ui files)
$ make -j4

# Install to Maya module directory.
$ make install

# Create .tar.gz archive.
$ make package
```

Common options:

| CMake Option         | Description                                  |
| -------------------- | -------------------------------------------- |
| CMAKE_INSTALL_PREFIX | Location to install the Maya module.         |
| MAYA_VERSION         | Maya version to build for.                   |
| MAYA_LOCATION        | Path to Maya install directory               |
| USE_CMINPACK         | Build with CMinpack? (default = 1)           |
| CMINPACK_ROOT        | Directory to CMinpack install base directory |

Advanced options:

| CMake Option          | Description                                             |
| --------------------  | ------------------------------------------------------- |
| CMAKE_BUILD_TYPE      | The type of build (`Release`, `Debug`, etc)             |
| MAYA_INCLUDE_PATH     | Directory to the Maya header include files              |
| MAYA_LIB_PATH         | Directory to the Maya library files                     |
| USE_CMINPACK          | Build with CMinpack? (default = 1)                      |
| CMINPACK_INCLUDE_PATH | Directory to CMinpack header includes                   |
| CMINPACK_LIB_PATH     | Directory to CMinpack library                           |
| PREFERRED_SOLVER      | Preferred solver; 'cminpack_lmdif' or 'cminpack_lmder'. |

You can read any of the build scripts to find out how they work. The
build scripts can be found in `<project root>/scripts/build_*.bash`.

If you are new to building Maya plug-ins using CMake, we recommend
watching these videos by Chad Vernon:

- [Compiling Maya Plug-ins with CMake (Part 1)](https://www.youtube.com/watch?v=2mUOt_F2ywo)
- [Compiling Maya Plug-ins with CMake (Part 2)](https://www.youtube.com/watch?v=C56N5KgDaTg)

# Building Packages

For developers wanting to produce a pre-compiled archive "package",
simply turn on the variable `BUILD_PACKAGE` in the build script, by
setting it to `1`, then re-run the build script.

```commandline
$ cd <project root>
$ bash scripts/build_mmSolver_mac_mayaXXXX.bash
```

This will re-compile mmSolver, then copy all scripts and plug-ins into
a `.tar.gz` file, ready for distribution to users.

# Compile Qt UI files

The CMake build script will automatically compile the Qt .ui files,
however these scripts can also be run manually if needed.

The Qt Designer `.ui` files must be compiled using the intended version
of Maya (either PySide or PySide2) in order to use the mmSolver tool
GUIs.

To compile the `*.ui` files, run these commands.

On MacOS:
```commandline
$ cd <project root>
$ /Applications/Autodesk/maya<VERSION>/Maya.app/Contents/bin/mayapy scripts/compileUI.py

# Or to compile a specific directory:
$ /Applications/Autodesk/maya<VERSION>/Maya.app/Contents/bin/mayapy scripts/compileUI.py /path/to/directory
```

These commands use `mayapy`, the Maya Python interpreter. Make sure
the use the executable with the version of Maya you are installing to.
Using incorrect versions may cause unforeseen errors.

NOTE: Replace ``<project root>`` and ``<VERSION>`` as required.

# Build Documentation

The CMake build script will automatically build the documentation, but
the steps are documented manually below.

*mmSolver* comes with a set of documentation, and Sphinx building
scripts to automate HTML page generation. It is recommended to build
the HTML documentation, however it is optional for an installation.

To build the documentation, you will need to install both
[Python 2.7.x](https://www.python.org/) and
[Sphinx](http://www.sphinx-doc.org/en/master/usage/installation.html).

After Sphinx is installed (and Python is on your PATH environment
variable), you can build the documentation with the following command line.

On MacOS:
```commandline
$ cd <project root>/docs
$ make html
```

If this documentation build is successful, it will be installed
automatically into the Maya Module (when the build script is run).

*Note:* Sphinx will likely list a number of 'errors' while building
the documentation, this means the automatic tools failed to find
documentation. This is (unfortunately) normal. A majority of the
documentation will be present.

# Run Test Suite

If you use the build script, you can automatically run the test suite
after compiling and installing. Make sure to turn on the variable
`RUN_TESTS` in the `.bash` or `.bat` scripts.

After all parts of the `mmSolver` are installed and can be found by
Maya, try running the test suite to confirm everything is working as
expected.

On MacOS:
```commandline
$ cd <project root>
$ /Applications/Autodesk/maya<VERSION>/Maya.app/Contents/bin/mayapy tests/runTests.py
```

Make sure you use the same Maya version 'mayapy' for testing as you
have build for.

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

# Build Release Packages from Scratch

If you wish to build a (.tar.gz) package for users to download, there
are a number of steps to ensure are run correctly in specific
environments. The commands below are one-liner commands to set up
everything from scratch and build, then package.

The directories below are hard-coded for the author's computer, you
may need to change the paths for your environment.

Run in the MacOS Bash terminal:
```commandline
# Maya 2018
$ mkdir -p ~/dev ; cd ~/dev ; git clone https://github.com/david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2018Deploy_mac
$ cd ~/dev/mayaMatchMoveSolver_maya2018Deploy_mac ; git fetch --all; git checkout -f issue146; git pull; rm -R -f build_* ; rm -R -f external/install/* ; rm -R -f external/working/*/ ; bash scripts/build_thirdparty_mac_maya2018.bash ; bash scripts/build_mmSolver_mac_maya2018.bash

# Maya 2019
$ mkdir -p ~/dev ; cd ~/dev ; git clone https://github.com/david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2019Deploy_mac
$ cd ~/dev/mayaMatchMoveSolver_maya2019Deploy_mac ; git fetch --all; git checkout -f issue146; git pull; rm -R -f build_* ; rm -R -f external/install/* ; rm -R -f external/working/*/ ; bash scripts/build_thirdparty_mac_maya2019.bash ; bash scripts/build_mmSolver_mac_maya2019.bash

# Maya 2020
$ mkdir -p ~/dev ; cd ~/dev ; git clone https://github.com/david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2020Deploy_mac
$ cd ~/dev/mayaMatchMoveSolver_maya2020Deploy_mac ; git fetch --all; git checkout -f issue146; git pull; rm -R -f build_* ; rm -R -f external/install/* ; rm -R -f external/working/*/ ; bash scripts/build_thirdparty_mac_maya2020.bash ; bash scripts/build_mmSolver_mac_maya2020.bash
```

Package files can then be uploaded from the
"~/dev/mayaMatchMoveSolver_maya*Deploy_mac/packages" folder.
