# Building on Linux

We can build `mmSolver` on Linux quite easily. We have provided a
Bash build script and CMake script which are configurable and readable.

To use the pre-made build scripts, you can use the following commands
to build the entire project and dependencies:

On Linux:
```commandline
$ cd <project root>
$ bash scripts/build_cminpack.bash
$ bash scripts/build_mmSolver_linux_mayaXXXX.bash
```

Note: Replace XXXX, with the Maya version use build for.

The sections below explain the process in more detail.

# Installing Dependencies

mmSolver has a few dependencies, and are listed in
[BUILD.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD.md#dependencies).
Install the dependencies using your Linux distribution's package manager.

For example on CentOS 7 we use the `yum` command to install some dependencies:
```commandline
$ yum install gcc make cmake python python-sphinx 
```

To be sure you have the above dependencies installed, run the following in a terminal and you should expect similar output:
```commandline
$ cmake --version
cmake version 2.8.12.2

$ gcc --version
gcc (GCC) 4.8.5 20150623 (Red Hat 4.8.5-36)
Copyright (C) 2015 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 
$ make --version
GNU Make 3.82
Built for x86_64-redhat-linux-gnu
Copyright (C) 2010  Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

$ python --version
Python 2.7.5

```

# Building Dependencies

`cminpack`, `levmar` and `Qt.py` can be easily downloaded and built
for mmSolver using build scripts provided in the `<project
root>/scripts` directory.

On Linux:
```commandline
$ cd <project root>
$ bash scripts/build_cminpack.bash
$ bash scripts/build_qtpy.bash
$ bash scripts/build_levmar.bash
```

If the commands above have worked, you should see the following
directories under `<project root>/external/install`.

- cminpack
- levmar
- qtpy

These dependencies will automatically be found by the mmSolver build
script and installed.

If you do not want to install `Qt.py` into mmSolver, simply do not use
the build script and delete the directory `<project
root>/external/install/qtpy`.

# Build mmSolver

After installing CMinpack, you can now build mmSolver. 

Run these commands, on Linux:
```commandline
$ cd <project root>
$ bash scripts/build_mmSolver_linux_mayaXXXX.bash

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

The build scripts contain default values for your version of Maya, and
will work for default installations. If you have a custom install
path, then you may need to edit the build scripts.

Below lists the variables in the build scripts:

| Variable           | Description                                  |            Example Value |
| ------------       | -----------                                  |              ----------- |
| MAYA_VERSION       | Maya version to build for.                   |                   `2017` |
| MAYA_LOCATION      | Location for Maya header (.h) files.         | `/usr/autodesk/maya2017` |
| INSTALL_MODULE_DIR | Directory to install the Maya module.        |    `~/maya/2017/modules` |
| FRESH_BUILD        | Delete all build files before re-compiling.  |                        1 |
| RUN_TESTS          | After build, run the test suite inside Maya. |                        0 |
| WITH_CMINPACK      | Use the CMinpack library for solving.        |                        1 |
| WITH_GPL_CODE      | Use the levmar library for solving.          |                        0 |
| BUILD_PACKAGE      | Create an archive file ready to distribute.  |                        0 |

# CMake Build Script

For those needing or wanting to compile the ``mmSolver`` Maya plug-in
manually you can do it easily using the following commands.

Example CMake usage on Linux:
```commandline
$ cd <project root>
$ mkdir build
$ cd build

# Configure make files
$ cmake -DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_PREFIX=~/maya/2017/modules \
	-DUSE_CMINPACK=1 \
	-DMAYA_VERSION=2017 \
	-DMAYA_LOCATION=/usr/autodesk/maya2017 \
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

| CMake Option          | Description                                  |
| --------------------  | -------------------------------------------  |
| CMAKE_INSTALL_PREFIX  | Location to install the Maya module.         |
| MAYA_VERSION          | Maya version to build for.                   |
| MAYA_LOCATION         | Path to Maya install directory               |
| USE_CMINPACK          | Build with CMinpack? (default = 1)           |
| CMINPACK_ROOT         | Directory to CMinpack install base directory ||
| PREFERRED_SOLVER      | Preferred solver; levmar or cminpack_lm.     |

Advanced options:

| CMake Option          | Description                                 |
| --------------------  | ------------------------------------------- |
| CMAKE_BUILD_TYPE      | The type of build (`Release`, `Debug`, etc) |
| MAYA_INCLUDE_PATH     | Directory to the Maya header include files  |
| MAYA_LIB_PATH         | Directory to the Maya library files         |
| USE_CMINPACK          | Build with CMinpack? (default = 1)          |
| CMINPACK_INCLUDE_PATH | Directory to CMinpack header includes       |
| CMINPACK_LIB_PATH     | Directory to CMinpack library               |
| USE_GPL_CODE          | Build with levmar? (default = 0)            |
| LEVMAR_INCLUDE_PATH   | Directory to levmar header includes         |
| LEVMAR_LIB_PATH       | Directory to levmar library                 |
| PREFERRED_SOLVER      | Preferred solver; levmar or cminpack_lm.    |

*WARNING: 'levmar' is GPL licensed. If used with mmSolver, mmSolver
must not be distributed in binary form to anyone.*

You can read any of the build scripts to find out how they work. The
build scripts can be found in `<project root>/scripts/build_*.bash`.

If you are new to building Maya plug-ins using CMake, we recommend
watching these videos by Chad Vernon:

* [Compiling Maya Plug-ins with CMake (Part 1)](https://www.youtube.com/watch?v=2mUOt_F2ywo)
* [Compiling Maya Plug-ins with CMake (Part 2)](https://www.youtube.com/watch?v=C56N5KgDaTg)

# Building Packages

For developers wanting to produce a pre-compiled archive "package",
simply turn on the variable `BUILD_PACKAGE` in the build script, by
setting it to `1`, then re-run the build script.

```commandline
$ cd <project root>
$ bash scripts/build_mmSolver_linux_mayaXXXX.bash
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

On Linux:
```commandline
$ cd <project root>
$ /usr/autodesk/maya<VERSION>/bin/mayapy scripts/compileUI.py

# Or to compile a specific directory:
$ /usr/autodesk/maya<VERSION>/bin/mayapy scripts/compileUI.py /path/to/directory
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

On Linux, Python is likely already installed, however you can install
it on CentOS Linux with this command line:
```commandline
$ yum install python python-sphinx
```

After Sphinx is installed (and Python is on your PATH environment
variable), you can build the documentation with the following command line:

On Linux:
```commandline
$ cd <project root>/docs
$ make html
```

If this documentation build is successful, it will be installed
automatically into the Maya Module (when the build script is run).

*Note:* Sphinx will likely list a number of 'errors' while building
the documentation, this means the automatic tools failed to find
documentation. This is normal. A majority of the documentation will be
present.

# Run Test Suite

If you use the build script, you can automatically run the test suite 
after compiling and installing. Make sure to turn on the variable 
`RUN_TESTS` in the `.bash` or `.bat` scripts.

After all parts of the `mmSolver` are installed and can be found by
Maya, try running the test suite to confirm everything is working as
expected.

On Linux:
```commandline
$ cd <project root>
$ /usr/autodesk/mayaVERSION/bin/mayapy tests/runTests.py
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

Run in the Linux Bash terminal:
```commandline
# Maya 2016
$ load_maya2016.sh  # Example script to set up Maya environment
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2016Deploy_linux ; cd /media/dev/mayaMatchMoveSolver_maya2016Deploy_linux ; git fetch --all; git checkout master; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_cminpack.bash ; bash scripts/build_qtpy.bash ; bash scripts/build_mmSolver_linux_maya2016.bash

# Maya 2017
$ load_maya2017.sh  # Example script to set up Maya environment
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2016Deploy_linux ; cd /media/dev/mayaMatchMoveSolver_maya2017Deploy_linux ; git fetch --all; git checkout master; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_cminpack.bash ; bash scripts/build_qtpy.bash ; bash scripts/build_mmSolver_linux_maya2017.bash

# Maya 2018
$ load_maya2018.sh  # Example script to set up Maya environment
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2016Deploy_linux ; cd /media/dev/mayaMatchMoveSolver_maya2018Deploy_linux ; git fetch --all; git checkout master; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_cminpack.bash ; bash scripts/build_qtpy.bash ; bash scripts/build_mmSolver_linux_maya2018.bash

# Maya 2019
$ load_maya2019.sh  # Example script to set up Maya environment
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2016Deploy_linux ; cd /media/dev/mayaMatchMoveSolver_maya2019Deploy_linux ; git fetch --all; git checkout master; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_cminpack.bash ; bash scripts/build_qtpy.bash ; bash scripts/build_mmSolver_linux_maya2019.bash
```

Package files can then be uploaded from the
"~/dev/mayaMatchMoveSolver_maya*Deploy_linux/packages" folder.
