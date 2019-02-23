# Building and Install

Building mmSolver can be fairly simple or complex, depending if you
want to use ATLAS or Intel MKL to speed up computation and increase
robustness in solving, for most practical cases, ATLAS or
Intel MKL are not required. For testing the tool, you may use
the "Simple Method".

There are Linux shell or Windows Batch scripts to automate most of
the compiling of external dependencies. You may edit these scripts
for your system.

There are patches required for different builds and are stored
in `./external/patches/`.

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


NOTE: Other operating systems have not been tested, but may work
with only minor modifications.

# Dependencies

These projects are needed for building the ``mmSolver`` project.

Required:
- C++ compiler
  - Linux (depending on Maya version)
    - [GCC 4.4.7](https://gcc.gnu.org/) (Maya 2016 and 2017)
    - [GCC 4.8.3](https://gcc.gnu.org/) (Maya 2018)
    - [GCC 6.3.1](https://gcc.gnu.org/) (Maya 2019)
  - Windows
    - [Visual Studio 2012 update 5 (MSVC 11.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2016 and 2017)
    - [Visual Studio 2015 update 3 (MSVC 14.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2018 and 2019)
- [CMake 2.8+](https://cmake.org/)
- [Autodesk Maya 2016+](https://www.autodesk.com.au/products/maya/overview)
- [levmar 2.6](http://users.ics.forth.gr/~lourakis/levmar/)

Optional (**required for GUI support**):
- [Qt.py 0.6.9](https://github.com/mottosso/Qt.py/releases/tag/0.6.9)

Optional (**required for building documentation**):
- [Python 2.7.x](https://www.python.org/)
- [Sphinx 1.8.3+](http://www.sphinx-doc.org/en/master/index.html)

Optional:
- [ATLAS 3.8.4](http://math-atlas.sourceforge.net/)
- [Intel Math Kernel Library (MLK)](https://software.intel.com/en-us/mkl)

# Building Overview

An overview of the simple method is:

1. Compile Qt .ui files.
2. Build Documentation
3. Edit `build_with_*` script.
4. Install optional dependancies
   1. Install ATLAS with Package Manager (optional)
   2. Install Intel MKL (optional)
5. Run `build_with_...` script.
6. Copy 3DEqualizer python scripts into .3dequalizer home directory.

*Note:* Only ATLAS **or** Intel MKL is optional. Both libraries are not needed
together.

Below lists all the commands run in an example session, following the
above sections. The text editors `vi` and `notepad` are used as
example only, any text editor may be used.

On Linux:
```commandline
$ cd <project root>

# Build Qt .ui files
$ /usr/autodesk/mayaVERSION/bin/mayapy compileUI.py

# Build Documentation (with Python and Sphinx)
$ cd docs
$ make html
$ cd ..

# Download levmar to "<project root>/external/archives/"
$ bash external/download_all_archives.sh

# Edit variables as needed (in your prefered text editor).
$ vi build_with_levmar.sh

# Build Maya plug-in, create module and install to home directory.
# Note: Edit build_with_levmar.bat and remove 'make install' to stop automatic installation.
$ build_with_levmar.sh

# Run tests (with 'mayapy')
$ /usr/autodesk/mayaVERSION/bin/mayapy tests/runTests.py

# Install 3DE scripts (or install via ScriptDB)
$ cp ./3dequalizer/scriptdb/* ~/.3dequalizer/py_scripts
```

On Windows:
```cmd
> CD <project root>

:: Compile Qt .ui files
> "C:\Program Files\Autodesk\MayaVERSION\bin\mayapy.exe" compileUI.py

:: Build Documentation (with Python and Sphinx)
> CD docs
> CMD /C make.bat html
> CD ..

:: User must download levmar *manually* to "<project root>/external/archives/"

:: Edit variables as needed (in your prefered text editor).
> notepad build_with_levmar.bat

:: Build Maya plug-in, create module and install to home directory.
::
:: Note: Edit build_with_levmar.bat and remove 'nmake /F Makefile install'
:: to stop automatic installation.
> CMD /C build_with_levmar.bat

:: Run tests (with 'mayapy')
::
:: Note 'cmd.exe' is very slow printing text to the console, therefore
:: redirecting to a log file ('> file.log' below) will improve performance
:: of the test suite greatly.
> "C:\Program Files\Autodesk\MayaVERSION\bin\mayapy" tests\runTests.py > tests.log

:: Install 3DE scripts (or install via ScriptDB)
> XCOPY 3dequalizer\scriptdb\* "%AppData%\.3dequalizer\py_scripts" /Y
```

# Compile Qt UI files

We must compile the `*.ui` files for your version of Maya (either
PySide or PySide2) in order to use the mmSolver tool GUIs. To compile
the `*.ui` files, run these commands.

On Linux:
```commandline
$ cd <project root>
$ mayapy compileUI.py
```

On Windows:
```cmd
> CD <project root>
> mayapy compileUI.py
```

These commands use `mayapy`, the Maya Python interpreter. Make sure the use the
executable with the version of Maya you plan to use mmSolver with.

NOTE: Replace ``<project root>`` and ``<maya version>`` as required.

# Build Documentation

mmSolver comes with a set of documentation, and Sphinx building
scripts to automate HTML page generation. It is recommended to build
the HTML documentation, however it is optional.

To build the documentation, you will need to install both
[Python](https://www.python.org/) and
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
> CMD /C make.bat html
```

If this documentation build is successful, it will be installed
automatically into the Maya Module (in the next section).

*Note:* Sphinx will likely list a number of 'errors' while building
the documentation, this means the automatic tools failed to find
documentation. This is normal. A majority of the documentation will be
present.

# Build Plug-In (and Maya Module)

To build the Plug-In

There are three different scripts to build ``mmSolver`` depending on
the dependencies you want to use:

| Build Script Name       | Operating System | Dependencies      |
| ------------            | -----------      | -----------       |
| build_with_levmar.sh    | Linux            | levmar            |
| build_with_levmar.bat   | Windows          | levmar            |
| build_with_atlas.sh     | Linux            | levmar, ATLAS     |
| build_with_intel_mkl.sh | Linux            | levmar, Intel MKL |

For details of using these build scripts and building the plug-in,
please see
[BUILD_LINUX.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD_LINUX.md)
or
[BUILD_WINDOWS.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD_WINDOWS.md).

# Run Test Suite

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

On Windows, 'cmd.exe' is very slow printing text to the console,
therefore redirecting to a log file ('> file.log' below) will improve
performance of the test suite greatly.

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

# Install 3DEqualizer Files

To install the 3DEqualizer (3DE) tools for `mmSolver`, follow the steps below.
The 3DEqualizer tools are for integration into workflows using 3DEqualizer.
These tools have been tested with `3DEqualizer4 Release 5`.

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

Alternatively, you may install scripts manually by copying the 3DEqualizer python
scripts in `<project root>/3dequalizer/scriptdb` into the `~/.3dequalizer/py_scripts` directory.

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
