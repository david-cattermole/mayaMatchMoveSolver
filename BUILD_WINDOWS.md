# Building on Microsoft Windows

Maya MatchMove Solver can be built on Microsoft Windows. We have provided a
Windows Batch build script and CMake script which are configurable and readable.

To use the pre-made build scripts, you can use the following commands
to build the entire project and dependencies:

On Windows:
```cmd
> CD <project root>
> scripts\build_thirdparty_windows64_mayaXXXX.bat
> scripts\build_mmSolver_windows64_mayaXXXX.bat
```

Note: Replace XXXX, with the Maya version to build for.

The sections below explain the process in more detail.

# Windows Command Prompt

All commands in this install guide are assumed to be run
inside a Windows Command Prompt, with Visual Studio environment
variables set.

For example, from the Start Menu on Microsoft Windows 10, go to
`Programs (list) > Microsoft Visual Studio 2012 > VS2012 x64 Cross Tools Command Prompt`.
This will open a Command Prompt for you to type commands below.

It is *important* you use the `x64` Command Prompt, *not*
`Developer`, `x86` or `ARM`.

# Building Dependencies

mmSolver has a few dependencies, and are listed in
[BUILD.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD.md#dependencies).

The dependencies can be easily downloaded and built for mmSolver using
build scripts provided in the `<project root>/scripts` directory.

On Windows:
```cmd
> CD <project root>
> scripts\build_thirdparty_windows64_mayaXXXX.bat
```

Note: Replace XXXX, with the Maya version to build for.

If the commands above have worked, you should see the following
directories under `<project root>\external\install`.

- cminpack
- eigen
- libmv
- openMVG

These dependencies will automatically be found by the mmSolver build
script and installed.

# Build mmSolver

After installing Third-party dependencies, you can now build mmSolver.

Run these commands, on Windows:
```cmd
> CD <project root>
> scripts\build_mmSolver_windows64_mayaXXXX.bat

# Run tests (optional but encouraged)
> CD build
> NMAKE test
< CD ..
```
 
Note: Replace XXXX, with the Maya version to build for.
 
The build script (using CMake) will perform the following tasks:
 - Build documentation using Sphinx.
 - Compile Qt Designer .ui files into a format for Maya's version of
   Qt (PySide or PySide2).
 - Create a module (.mod) with configuration options.
 - Copy all needed files (including dependencies) into a module.
 
Following the steps above you will have the Maya plug-in compiled, and
installed into your `%USERPROFILE%\maya\MAYA_VERSION\modules` directory.
 
The below sections in this file list more details and how to run
different stages of the build manually.

# Customize Build Scripts

The build scripts contain default values for your version of Maya, and
will work for default installations. If you have a custom install
path, then you may need to edit the build scripts.

Below lists the variables in the build scripts:

| Variable           | Description                                  | Example Value                                 |
| ------------       | -----------                                  | -----------                                   |
| MAYA_VERSION       | Maya version to build for.                   | `2017`                                        |
| MAYA_LOCATION      | Location for Maya header (.h) files.         | `C:\Program Files\Autodesk\Maya2017`          |
| INSTALL_MODULE_DIR | Directory to install the Maya module.        | `C:\Users\MyUser\Documents\maya\2017\modules` |
| FRESH_BUILD        | Delete all build files before re-compiling.  | 1                                             |
| RUN_TESTS          | After build, run the test suite inside Maya. | 0                                             |
| WITH_CMINPACK      | Use the CMinpack library for solving.        | 1                                             |
| BUILD_PACKAGE      | Create an archive file ready to distribute.  | 0                                             |

For developers on Windows, you may change the variable 
`GENERATE_SOLUTION` to "1". This will build a Visual Studio solution 
file, ready to make changes and compile interactively inside 
Visual Studio.

# CMake Build Script

For those needing or wanting to compile the ``mmSolver`` Maya plug-in
manually you can do it easily using the following commands.

Example CMake usage on Windows:
```cmd
> CD <project root>
> MKDIR build
> CD build

:: Configure make files
> cmake -G "NMake Makefiles" ^
        -DCMAKE_BUILD_TYPE=Release ^
        -DCMAKE_INSTALL_PREFIX="C:\Users\MyUser\Documents\maya\2017\modules" ^
        -DUSE_CMINPACK=1 ^
        -DMAYA_VERSION="2017" ^
        -DMAYA_LOCATION="C:\Program Files\Autodesk\Maya2017" ^
        -DCMINPACK_ROOT="project_root\external\install\cminpack" ^
        ..

:: Compile the project (including documentation, and Qt.ui files). 
> NMAKE all

:: Install to Maya module directory.
> NMAKE install

:: Create .zip archive.
> NMAKE package
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
build scripts can be found in `<project root>\scripts\build_*.bat`.

If you are new to building Maya plug-ins using CMake, we recommend 
watching these videos by Chad Vernon:

- [Compiling Maya Plug-ins with CMake (Part 1)](https://www.youtube.com/watch?v=2mUOt_F2ywo)
- [Compiling Maya Plug-ins with CMake (Part 2)](https://www.youtube.com/watch?v=C56N5KgDaTg)

# Building Packages

For developers wanting to produce a pre-compiled archive "package",
simply turn on the variable `BUILD_PACKAGE` in the build script, by
setting it to `1`, then re-run the build script.

```cmd
> CD <project root> 
> scripts\build_mmSolver_windows64_mayaXXXX.bat
```

This will re-compile mmSolver, then copy all scripts and plug-ins into
a `.zip` file, ready for distribution to users.

# Compile Qt UI files

The CMake build script will automatically compile the Qt .ui files, 
however these scripts can also be run manually if needed. 

The Qt Designer `.ui` files must be compiled using the intended version
of Maya (either PySide or PySide2) in order to use the mmSolver tool 
GUIs. 

To compile the `*.ui` files, run these commands. 

On Windows:
```cmd
> CD <project root>
> "C:\Program Files\Autodesk\Maya<VERSION>\bin\mayapy.exe" scripts\compileUI.py

:: Or to compile a specific directory:
> "C:\Program Files\Autodesk\Maya<VERSION>\bin\mayapy.exe" scripts\compileUI.py C:\path\to\dir
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
variable), you can build the documentation with the following command line:

On Windows:
```cmd
> CD <project root>\docs
> make html
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

On Windows:
```cmd
> CD <project root>
> "C:\Program Files\Autodesk\MayaVERSION\bin\mayapy.exe" tests\runTests.py > tests.log
```

Make sure you use the same Maya version 'mayapy' for testing as you
have build for.

**Note:** On Windows, 'cmd.exe' is very slow printing text to the console,
therefore redirecting to a log file ('> file.log' below) will improve
performance of the test suite greatly.

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

# Build Release Packages from Scratch

If you wish to build a (.zip) package for users to download, there
are a number of steps to ensure are run correctly in specific
environments. The commands below are one-liner commands to set up
everything from scratch and build, then package.

The directories below are hard-coded for the author's computer, you
may need to change the paths for your environment.

Run in the Git Bash terminal for Windows:
```commandline
# Maya 2016
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2016Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2016Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2016Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2017
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2017Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2017Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2017Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2018
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2018Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2018Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2018Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2019
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2019Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2019Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2019Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2020
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2020Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2020Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2020Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2022
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2022Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2022Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2022Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;

# Maya 2023
$ mkdir -p ~/dev/mayaMatchMoveSolver_maya2023Deploy_windows64 ; cd ~/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2023Deploy_windows64
$ cd ~/dev/mayaMatchMoveSolver_maya2023Deploy_windows64/; git fetch --all; git checkout -f develop; git reset --hard HEAD ; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ;
```

Run in the Windows Command Prompt with the needed MSVC compiler environment paths set up:
(For example run "VS2012 x64 Cross Tools Command Prompt" or "VS2015 x86 x64 Cross Tools Command Prompt")

Visual Studio 2012:
```cmd
REM Maya 2016
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2016Deploy_windows64 && scripts\build_thirdparty_windows64_maya2016.bat && scripts\build_mmSolver_windows64_maya2016.bat

REM Maya 2017
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2017Deploy_windows64 && scripts\build_thirdparty_windows64_maya2017.bat && scripts\build_mmSolver_windows64_maya2017.bat
```

Visual Studio 2015:
```cmd
REM Maya 2018
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2018Deploy_windows64 && scripts\build_thirdparty_windows64_maya2018.bat && scripts\build_mmSolver_windows64_maya2018.bat

REM Maya 2019
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2019Deploy_windows64 && scripts\build_thirdparty_windows64_maya2019.bat && scripts\build_mmSolver_windows64_maya2019.bat
```

Visual Studio 2017:
```cmd
REM Maya 2020
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2020Deploy_windows64 && scripts\build_thirdparty_windows64_maya2020.bat && scripts\build_mmSolver_windows64_maya2020.bat
```

Visual Studio 2019:
```cmd
REM Maya 2022
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2022Deploy_windows64 && scripts\build_thirdparty_windows64_maya2022.bat && scripts\build_mmSolver_windows64_maya2022.bat

REM Maya 2023
> cd %userprofile%\dev\mayaMatchMoveSolver_maya2023Deploy_windows64 && scripts\build_thirdparty_windows64_maya2023.bat && scripts\build_mmSolver_windows64_maya2023.bat
```

Package files can then be uploaded from the
"%userprofile%\dev\mayaMatchMoveSolver_maya*Deploy_windows64\packages"
folder.
