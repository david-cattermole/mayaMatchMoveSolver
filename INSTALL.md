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

The below processes were tested on a CentOS 7.x Linux distribution.
The below processes were tested on Microsoft Windows 10 Pro, with Visual Studio 11 2012.

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

#  Dependencies

These projects are needed for building the ``mmSolver`` project.

Required:
- C++ compiler ([GCC](https://gcc.gnu.org/), MSVC, etc)
- [CMake 2.8+](https://cmake.org/)
- [Autodesk Maya 2016+](https://www.autodesk.com.au/products/maya/overview)
- [levmar 2.6](http://users.ics.forth.gr/~lourakis/levmar/)

Required for GUI:
- [Qt.py](https://github.com/mottosso/Qt.py)

Optional:
- [ATLAS 3.8.4](http://math-atlas.sourceforge.net/)
- [Intel Math Kernel Library (MLK)](https://software.intel.com/en-us/mkl)

# Building Overview

An overview of the simple method is:

1. Install ATLAS with Package Manager (optional)
2. Install Intel MKL (optional)
3. Download, unpack, and compile `levmar` with Makefile.
4. Download, unpack, and compile `mmSolver` with CMake.
5. Copy mmSolver python API into Maya scripts directory.
6. Copy mmSolver plugin into Maya plug-in directory.
7. Copy 3DEqualizer python scripts into .3dequalizer home directory.

Only ATLAS **or** Intel MKL is optional. Both libraries are not needed
together.

# Build mmSolver Scripts

There are three different scripts to build ``mmSolver`` depending on
the dependencies you want to use:

| Build Script Name       | Operating System  | Dependencies      |
| ------------            | -----------       | -----------       |
| build_with_levmar.sh    | Linux             | levmar            |
| build_with_levmar.bat   | Windows           | levmar            |
| build_with_atlas.sh     | Linux             | levmar, ATLAS     |
| build_with_intel_mkl.sh | Linux             | levmar, Intel MKL |

The scripts will assume a default Maya install directory
You will need to edit the build script with your custom Maya include
and library directories.

For details of using these build scripts and building, please see
[INSTALL_LINUX.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL_LINUX.md) or
[INSTALL_WINDOWS.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL_WINDOWS.md).

# Install mmSolver Python Scripts

The `mmSolver` project has a convenience Python API for tool writers,
which is recommended to be used. The API must be added to the `MAYA_SCRIPT_PATH`
environment variable.

We must also compile the `*.ui` files for your version of Maya (either PySide or
PySide2) in order to use the mmSolver tool GUIs. To compile the `*.ui` files,
run these commands.

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

Now, to install the Python scripts into the home directory's Maya `scripts`
directory, simply run these commands:

On Linux:
```commandline
$ cd <project root>
$ cp -R python/mmSolver ~/maya/<maya version>/scripts
```

On Windows:
```cmd
> CD <project root>
> XCOPY python\mmSolver %USERPROFILE%\Documents\maya\<maya version>\scripts /E /Y
```

NOTE: Replace ``<project root>`` and ``<maya version>`` as required.

# Install mmSolver plugin

Once the `mmSolver` plugin has been built you will need to place it on
the `MAYA_PLUG_IN_PATH` environment variable path.

To install into our home directory maya `plug-ins` directory (which is
automatically on the `MAYA_PLUG_IN_PATH`), simply run these commands...

On Linux:
```commandline
$ mkdir ~/maya/<maya version>/plug-ins
$ cd <project root>
$ cp build/mmSolver.so ~/maya/<maya version>/plug-ins
```

On Windows:
```cmd
> MKDIR %USERPROFILE%\Documents\maya\<maya version>\plug-ins
> CD <project root>
> COPY build/mmSolver.mll %USERPROFILE%\Documents\maya\<maya version>\plug-ins\mmSolver.mll
```
Replace ``<project root>`` and ``<maya version>`` as required.

# Install ATLAS / Intel MKL libraries

If you have chosen to compile `mmSolver` with ATLAS or Intel MKL support,
you must make sure Maya can access those third-party libraries, if you
have not, you can skip this section. Below I'll add these into
`~/maya/<maya version>/lib`, however you may do so however you wish.

NOTE: Currently using ATLAS or Intel MKL is untested under Microsoft Windows, and
instructions are therefore not given.

On Linux:
```commandline
$ cd <project root>
$ mkdir ~/maya/<maya version>/lib
$ cp -R external/lib/* ~/maya/<maya version>/lib
```

You will need to add `~/maya/<maya version>/lib` onto your
`LD_LIBRARY_PATH` environment variable. For example if you use the
'bash' shell, you add this command into your `~/.bashrc` file.

```bash
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:~/maya/<maya version>/lib
```
Be careful editing ``LD_LIBRARY_PATH``! This environment variable is
important and affects how all software in the shell will find
libraries. Setting this incorrectly can cause problems of Maya not
loading correctly or random crashes if libraries conflict with
internal Maya libraries.

# Run Test Suite

After all parts of the `mmSolver` are installed and can be found by
Maya, try running the test suite to confirm everything is working as
expected.

On Linux run:
```commandline
$ cd <project root>
$ sh runTests.sh
```

On Windows run:
```cmd
> CD <project root>
> CMD /C runTests.bat
```

This will find and use the currently available 'mayapy' executable,
please make sure 'mayapy' is on your PATH environment variable.

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

# Install 3DEqualizer Files

To install the 3DEqualizer (3DE) tools for `mmSolver`, follow the steps below.
The 3DEqualizer tools are for integration into workflows using 3DEqualizer.
These tools have been tested with `3DEqualizer4 Release 5`.

Copy the python scripts into the `~/.3dequalizer/py_scripts` directory.

On Linux:
```commandline
$ cd <project root>
$ cp ./3dequalizer/python/* ~/.3dequalizer/py_scripts
```

On Windows:
```cmd
> CD <project root>
> XCOPY 3dequalizer/python/* "%AppData%/.3dequalizer/py_scripts" /Y
```

Alternatively, you can modify the `PYTHONPATH` environment variable
before 3DEqualizer starts and add `<project root>/3dequalizer/python/`
to the list of search paths.

There are currently two 3DEqualizer tools available:
| File Name                | Tool Name                                      |
| --------------------     | ------------------------------------------     |
| copy_track_mmsolver.py   | Copy 2D Tracks (Maya MM Solver)                |
| export_track_mmsolver.py | Export 2D Tracks (Maya MM Solver)...           |
