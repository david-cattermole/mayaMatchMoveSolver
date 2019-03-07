# Building and Install

Building mmSolver is quite easy. The project uses CMake, and provides 
pre-made build scripts for Windows (Batch Script) and Linux (Bash - 
Shell Script).

You may edit these scripts for your system, or use them as-is if you 
have a standard default installation of Maya.

# Dependencies

These projects are needed for building the ``mmSolver`` project.

Required:
- C++ compiler (depending on Maya version)
  - Linux
    - [GCC 4.4.7](https://gcc.gnu.org/) (Maya 2016 and 2017)
    - [GCC 4.8.3](https://gcc.gnu.org/) (Maya 2018)
    - [GCC 6.3.1](https://gcc.gnu.org/) (Maya 2019)
  - Windows
    - [Visual Studio 2012 update 5 (MSVC 11.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2016 and 2017)
    - [Visual Studio 2015 update 3 (MSVC 14.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2018 and 2019)
- [CMake 2.8+](https://cmake.org/)
- [Autodesk Maya 2016+](https://www.autodesk.com.au/products/maya/overview)
- [CMinpack 1.3.6](https://github.com/devernay/cminpack/releases/tag/v1.3.6)
- [Python 2.7.x](https://www.python.org/) (for build scripts)

**Required for GUI support**:
- [Qt.py 0.6.9](https://github.com/mottosso/Qt.py/releases/tag/0.6.9)

**Required for building documentation**:
- [Sphinx 1.8.3+](http://www.sphinx-doc.org/en/master/index.html)

Optional Solver:
- [levmar 2.6](http://users.ics.forth.gr/~lourakis/levmar/)
  - levmar has tested to be slower than the default recommended
    CMinpack by up to 50%.
  - Warning: levmar is GPL licensed, and places restrictions on 
    mmSolver so it may not be distributed in binary form.  
  - Note: The automatic build script for _levmar_ requires 
    CMake 3.4.3+ with levmar on Windows.

# Building Overview

An overview of compiling is:

1. Compile CMinpack (using `build_cminpack.bash` or 
   `build_cminpack.bat`).
2. Edit build script (`build_mmSolver_linux.bash` or 
   `build_mmSolver_windows64.bat`).
3. Compile mmSolver (using `build_mmSolver_linux.bash` or 
   `build_mmSolver_windows64.bat` script).
6. Copy 3DEqualizer python scripts into `.3dequalizer` user directory.

Below lists all the commands run in an example session, following the
above sections. The text editors `vi` and `notepad` are used as
example only, any text editor may be used.

On Linux:
```commandline
# Go to root of project directory.
$ cd <project root>

# Download and Build CMinpack automatically.
$ bash scripts/build_cminpack.bash

# Edit variables as needed (in your prefered text editor).
$ nano build_with_levmar.sh

# Build mmSolver, compile UI files, compile Maya plug-in, build
# documentation, create module and install to home directory.
$ bash scripts/build_mmSolver_linux.bash

# Run tests (optional but encouraged)
$ cd build
$ make test
$ cd ..

# Install 3DE scripts (or install via ScriptDB)
$ cp ./3dequalizer/scriptdb/* ~/.3dequalizer/py_scripts
```

On Windows:
```cmd
:: Go to root of project directory.
> CD <project root>

# Download and Build CMinpack automatically.
> scripts/build_cminpack.bat

:: Edit variables as needed (in your prefered text editor).
> notepad build_with_levmar.bat

:: Build mmSolver, compile UI files, compile Maya plug-in, build
:: documentation, create module and install to home directory.
> scripts/build_with_levmar.bat

:: Run tests (optional but encouraged)
> CD build
> nmake test
> CD ..

:: Install 3DE scripts (or install via ScriptDB)
> XCOPY 3dequalizer\scriptdb\* "%AppData%\.3dequalizer\py_scripts" /Y
```

# Building Dependencies

To build the `cminpack` (or `levmar`), we have pre-configured build 
scripts for Linux and Windows. 
  
| Build Script Name     | Operating System |
| ------------          | -----------      |
| build_cminpack.bash   | Linux            |
| build_cminpack.bat    | Windows          |
| build_levmar.bash     | Linux            |
| build_levmar.bat      | Windows          |

The build scripts are located in `<project root>/scripts/`.
These scripts will automatically install into `<project root>/external/install`.

# Building mmSolver

To build the project we can use the build scripts provided
  
| Build Script Name            | Operating System |
| ------------                 | -----------      |
| build_mmSolver_linux.bash    | Linux            |
| build_mmSolver_windows64.bat | Windows          |

For details of using these build scripts and building the plug-in,
please see
[BUILD_LINUX.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD_LINUX.md)
or
[BUILD_WINDOWS.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD_WINDOWS.md).

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

On Windows:
```cmd
> CD <project root>/docs
> make html
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

On Linux run:
```commandline
$ cd <project root>
$ /usr/autodesk/mayaVERSION/bin/mayapy tests/runTests.py
```

On Windows run:
```cmd
> CD <project root>
> "C:\Program Files\Autodesk\MayaVERSION\bin\mayapy" tests\runTests.py > tests.log
```

Make sure you use the same Maya version 'mayapy' for testing as you
have build for.

**Note:** On Windows, 'cmd.exe' is very slow printing text to the console,
therefore redirecting to a log file ('> file.log' below) will improve
performance of the test suite greatly.

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

# Install 3DEqualizer Files

To install the 3DEqualizer (3DE) tools for `mmSolver`, follow the 
steps below. The 3DEqualizer tools are for integration into workflows 
using 3DEqualizer. These tools have been tested with 
`3DEqualizer4 Release 5`, but earlier versions.

There are currently two 3DEqualizer tools available:

| File Name                | Tool Name                                      |
| ------------------------ | ---------------------------------------------- |
| copy_track_mmsolver.py   | Copy 2D Tracks (MM Solver)                     |
| export_track_mmsolver.py | Export 2D Tracks (MM Solver)...                |

## Script Database

For 3DEqualizer versions supporting the online
[Script Database](https://www.3dequalizer.com/?site=scriptdb), you may
install the latest tools via the menu '3DE4 > Python > ScriptDB Installer'.

See this [video tutorial](https://www.youtube.com/watch?v=gVr_Fo1xh0E) for
an example of installing scripts with ScriptDB.

## Home Directory

Alternatively, you may install scripts manually by copying the 
3DEqualizer python scripts in `<project root>/3dequalizer/scriptdb`
into the `~/.3dequalizer/py_scripts` directory.

On Linux:
```commandline
$ cd <project root>
$ cp ./3dequalizer/scriptdb/* ~/.3dequalizer/py_scripts
```

On Windows:
```cmd
> CD <project root>
> XCOPY 3dequalizer/scriptdb/* "%AppData%/.3dequalizer/py_scripts" /Y
```

# Build Environment

These are the versions of various software tested together.

Maya 2017 on Linux:

| Software          | Version                                     |
| ------------      | -----------                                 |
| OS                | CentOS 7.x                                  |
| Linux Kernel      | 3.10.0-862.3.3.el7.x86_64                   |
| GCC               | gcc (GCC) 4.8.5 20150623 (Red Hat 4.8.5-28) |
| LDD               | ldd (GNU libc) 2.17                         |
| CMake             | 2.8.12.2                                    |
| Autodesk Maya     | **Autodesk Maya 2017 Update 5**             |
| Autodesk Maya API | **201780**                                  |

Maya 2016 on Linux:

| Software          | Version                                     |
| ------------      | -----------                                 |
| OS                | CentOS 7.x                                  |
| Linux Kernel      | 3.10.0-862.3.3.el7.x86_64                   |
| GCC               | gcc (GCC) 4.8.5 20150623 (Red Hat 4.8.5-28) |
| LDD               | ldd (GNU libc) 2.17                         |
| CMake             | 2.8.12.2                                    |
| Autodesk Maya     | **Autodesk Maya 2016 Service Pack 6**       |
| Autodesk Maya API | **201614**                                  |

Maya 2017 on Windows:

| Software          | Version                                     |
| ------------      | -----------                                 |
| OS Name           | Microsoft Windows 10 Pro                    |
| OS Version        | 10.0.17134 Build 17134                      |
| MSVC              | 17.0.61030.0                                |
| Visual Studio     | 11.0.61030.00 Update 4 (Visual Studio 2012) |
| CMake             | 3.12.0                                      |
| Autodesk Maya     | **Autodesk Maya 2017**                      |
| Autodesk Maya API | **201700**                                  |

Maya 2018 on Windows:

| Software          | Version                                               |
| ------------      | -----------                                           |
| OS Name           | Microsoft Windows 10 Pro                              |
| OS Version        | 10.0.17134 N/A Build 17134                            |
| MSVC              | 19.00.24215.1                                         |
| Visual Studio     | 14.0.25431.01 Update 3 (Visual Studio Community 2015) |
| CMake             | 3.12.0                                                |
| Autodesk Maya     | **Autodesk Maya 2018**                                |
| Autodesk Maya API | **201800**                                            |

NOTE: Other operating systems have not been tested, but may work
with only minor modifications. *Maya 2018* has been tested on CentOS 7.x
Linux and *Maya 2019* have been known to work on Windows 10.
