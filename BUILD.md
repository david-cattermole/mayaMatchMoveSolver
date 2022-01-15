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
    - [GCC 6.3.1](https://gcc.gnu.org/) (Maya 2019 and 2020)
  - Windows
    - [Visual Studio 2012 update 5 (MSVC 11.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2016 and 2017)
    - [Visual Studio 2015 update 3 (MSVC 14.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2018 and 2019)
    - [Visual Studio 2017 (MSVC 15.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2020)
  - MacOS
    - [Xcode 7.3.1 with SDK 10.11, clang with libc++](https://developer.apple.com/download) (Maya 2018)
    - [Xcode version 7.3.1 and CMake are required](https://developer.apple.com/download) (Maya 2019)
- [CMake 3.15+](https://cmake.org/)
  - Older versions may work, however the Blender Add-On may fail to
    generate.
- [Autodesk Maya 2016+](https://www.autodesk.com.au/products/maya/overview)
- [Maya Development Kit](https://www.autodesk.com/developer-network/platform-technologies/maya)
- [CMinpack 1.3.6](https://github.com/devernay/cminpack/releases/tag/v1.3.6)
- [Python 2.7.x or 3.x](https://www.python.org/) (for build scripts)
- [Sphinx 1.8.3+](http://www.sphinx-doc.org/en/master/index.html) (for building documentation)

Optional Solver:
- [levmar 2.6](http://users.ics.forth.gr/~lourakis/levmar/)
  - levmar has tested to be slower than the default recommended
    CMinpack by up to 50%.
  - Warning: levmar is GPL licensed, and places restrictions on 
    mmSolver so it may not be distributed in binary form.  
  - Note: The automatic build script for _levmar_ requires 
    [CMake 3.4.3+](https://cmake.org/) with levmar on Windows.

Note: Until mmSolver v0.3.13 [Qt.py 1.1.0](https://github.com/mottosso/Qt.py/releases/tag/1.1.0)
was required for GUI support, but this is now embedded inside mmSolver
directly, so there is no need install it manually.

# Building Overview

An overview of compiling is:

1. Compile CMinpack.
2. Compile mmSolver.
3. Copy 3DEqualizer python scripts into `.3dequalizer` user directory.

Below lists all the commands run in an example session, following the
above sections.

On Linux:
```commandline
# Go to root of project directory.
$ cd <project root>

# Download and Build CMinpack automatically.
$ bash scripts/build_cminpack.bash

# Build mmSolver, compile UI files, compile Maya plug-in, build
# documentation, create module and install to home directory.
$ bash scripts/build_mmSolver_linux_mayaXXXX.bash

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

:: Build mmSolver, compile UI files, compile Maya plug-in, build
:: documentation, create module and install to home directory.
> scripts/build_mmSolver_windows64_mayaXXXX.bat

:: Run tests (optional but encouraged)
> CD build
> nmake test
> CD ..

:: Install 3DE scripts (or install via ScriptDB)
> XCOPY 3dequalizer\scriptdb\* "%AppData%\.3dequalizer\py_scripts" /Y
```

# Building Dependencies

To build dependencies we have pre-configured build scripts for Linux
and Windows.
  
| Build Script Name   | Operating System |
| ------------        | -----------      |
| build_cminpack.bash | Linux            |
| build_cminpack.bat  | Windows          |
| build_qtpy.bash     | Linux            |
| build_qtpy.bat      | Windows          |
| build_levmar.bash   | Linux            |
| build_levmar.bat    | Windows          |

The build scripts are located in `<project root>/scripts/`.
These scripts will automatically install into `<project root>/external/install`.

# Building mmSolver

To build the project we can use the build scripts provided.
  
| Build Script Name                     | Operating System |
| ------------                          | -----------      |
| build_mmSolver_linux_mayaXXXX.bash    | Linux            |
| build_mmSolver_windows64_mayaXXXX.bat | Windows          |

For details of building the project, please see
[BUILD_LINUX.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD_LINUX.md)
or
[BUILD_WINDOWS.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD_WINDOWS.md).

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

NOTE: Other operating systems have not been tested, but may work with
only minor modifications. *Maya 2018* has been tested on CentOS 7.x
Linux.
