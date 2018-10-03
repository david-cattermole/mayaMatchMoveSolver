# Building and Install

Building mmSolver can be fairly simple or complex, depending if you
want to use ATLAS or Intel MKL to speed up computation. 
For testing the tool, you may use the "Simple Method".

There are Linux shell scripts to automate most of the compiling
of external dependencies. You may edit these scripts for your
system. There are patches required for different builds and 
are stored in `./external/patches/`.

## Build Environment

The below processes were tested on a CentOS 7.x Linux distribution.

These are the versions of various software tested:

| Software          | Version                                     |
| ------------      | -----------                                 |
| OS                | CentOS 7.x                                  |
| Linux Kernel      | 3.10.0-862.3.3.el7.x86_64                   |
| GCC               | gcc (GCC) 4.8.5 20150623 (Red Hat 4.8.5-28) |
| LDD               | ldd (GNU libc) 2.17                         |
| CMake             | 2.8.12.2                                    |
| Autodesk Maya     | Autodesk Maya 2017 Update5                  |
| Autodesk Maya API | 201780                                      |

NOTE: Other operating systems have not been tested, but may work
without modification or with only minor modifications.

##  Dependencies

These projects are needed for building the ``mmSolver`` project. 

Required:
- C++ compiler ([GCC](https://gcc.gnu.org/), Clang, VC++, etc)
- [CMake 2.8+](https://cmake.org/)
- [Autodesk Maya 2017+](https://www.autodesk.com.au/products/maya/overview)
- [levmar 2.6](http://users.ics.forth.gr/~lourakis/levmar/)

Optional:
- [ATLAS 3.8.4](http://math-atlas.sourceforge.net/)
- [Intel Math Kernel Library (MLK)](https://software.intel.com/en-us/mkl)
- [Qt.py](https://github.com/mottosso/Qt.py)

## Building Overview

An overview of the simple method is:

1. Download, unpack, and compile `levmar` with CMake.
2. Install ATLAS with Package Manager (optional)
3. Install Intel MKL (optional)
4. Download, unpack and compile `mmSolver` with CMake.
5. Copy mmSolver plugin into Maya plug-in directory.
6. Copy mmSolver python API into Maya scripts directory.

Only ATLAS **or** Intel MKL is optional. Both libraries are not needed
together.

### Build Script

There are three different scripts to build ``mmSolver`` depending on
the dependencies you want to use:

| Build Script Name       | Dependencies      |
| ------------            | -----------       |
| build_with_levmar.sh    | levmar            |
| build_with_atlas.sh     | levmar, ATLAS     |
| build_with_intel_mkl.sh | levmar, Intel MKL |
|                         |                   |

#### Build Script (with levmar)

To build without any third-party dependencies other than levmar, run
these commmand:
```commandline
$ cd <project root>
$ bash external/download_all_archives.sh
$ build_with_levmar.sh 
```

#### Build Script (with levmar and ATLAS)

This section is for compiling with the free and open-source library
ATLAS.

This method will use the `levmar` algorithm, and `Automatically Tuned
Linear Algebra Software (ATLAS)` for performance computation and
stability. `ATLAS` is Free Open Source Software, Using a third-party
maths library is recommended by the `levmar` project.

This will assume the `atlas` is installed via yum on CentOS 7.x. If
you wish to build your own custom atlas library it is an undocumented
exercise for the user. On CentOS 7.x you may install `atlas` with the
following command (as `root` user):

```commandline
$ yum install atlas.x86_64 atlas-devel.x86_64
$ yum install lapack64.x86_64 lapack64-devel.x86_64
```

To build with ATLAS, run these command: 
```commandline
$ cd <project root>
$ bash external/download_all_archives.sh
$ bash build_with_atlas.sh
```

#### Build Script (with levmar and Intel MKL)

This method will use both the `levmar` algorithm, as well as
highly-optimised libraries for computation; `Intel Math Kernel
Libraries (Intel MKL)`. `Intel MKL` is proprietary closed-source
software, Using a third-party maths library is recommended by the
`levmar` project.

Intel MKL must be installed manually, this build script will not
install it for you. You will need to sign up, download and install
from the [Intel MKL website](https://software.intel.com/en-us/mkl).
 
The instructions below assume Intel MKL is installed under
`/opt/intel/mkl`, you will need to modify the scripts if this location
is not correct on your system.

To build with Intel MKL, run these command: 
```commandline
$ cd <project root>
$ bash external/download_all_archives.sh
$ bash build_with_intel_mkl.sh
```

#### Manually building mmSolver plugin

For those needing or wanting to compile the ``mmSolver`` Maya plug-in
manually you can do it easily using the following commands.

| CMake Option         | Description                                |
| -------------------- | ----------------------------               |
| USE_ATLAS            | Use ATLAS libraries?                       |
| USE_MKL              | Use Intel MKL libraries?                   |
| MAYA_INCLUDE_PATH    | Directory to the Maya header include files |
| MAYA_LIB_PATH        | Directory to the Maya library files        |
| LEVMAR_LIB_PATH      | Directory to levmar library                |
| LEVMAR_INCLUDE_PATH  | Directory to levmar header includes        |
| ATLAS_LIB_PATH       | Directory to ATLAS libraries               |
| MKL_LIB_PATH         | Directory to Intel MKL libraries           |

Setting ``USE_ATLAS`` and ``USE_MKL`` is an error, both libraries
provide the same functionallity and both are not needed, only one.

Example command line:
```commandline
$ cd <project root>
$ mkdir build
$ cd build
$ cmake -DCMAKE_BUILD_TYPE=Release \
        -DUSE_ATLAS=0 \
        -DUSE_MKL=0 \
        -DMAYA_INCLUDE_PATH=/usr/autodesk/maya2017/include \
        -DMAYA_LIB_PATH=/usr/autodesk/maya2017/lib \
        -DLEVMAR_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DLEVMAR_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
        -DATLAS_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DMKL_LIB_PATH=/opt/intel/mkl/lib/intel64 \
        ..
$ make -j4
```

You can read any of the build scripts to find out how they work. 
The build scripts can be found in `<project root>/build_with_*.sh` and `<project root>/external/*.sh`.

Once the plug-in is built successfully, continue on to the section
"Install Common Files" below.

### Install mmSolver Python API

The `mmSolver` project has a convenience Python API for tool writers,
which is recommended to be used.  The API must be added to the
`MAYA_SCRIPT_PATH`.

To install into the home directory maya `scripts` directory, simply
run these commands:

```commandline
$ cd <project root>
$ cp -R python/mmSolver ~/maya/<maya version>/scripts
```

### Install mmSolver plugin

Once the `mmSolver` plugin has been built you will need to place it on
the `MAYA_PLUG_IN_PATH` environment variable.

To install into our home directory maya `plug-ins` directory (which is
automatically on the `MAYA_PLUG_IN_PATH`), simply run these commands:

```commandline
$ cd <project root>
$ mkdir ~/maya/<maya version>/plug-ins
$ cp mmSolver.so ~/maya/<maya version>/plug-ins
```
Replace ``<project root>`` and ``<maya version>`` as required.

### Run Test Suite

After all parts of the `mmSolver` are installed and can be found by
Maya, try running the test suite to confirm everything is working as
expected.

```commandline
$ cd <project root>
$ sh runTests.sh
```

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

## Install Common Files

### Install mmSolver Python API

The `mmSolver` project has a convenience Python API for tool writers,
which is recommended. The API must be added to the `MAYA_SCRIPT_PATH`.

To install into our home directory maya `scripts` directory, simply
run these commands:

```commandline
$ cd <project root>
$ cp -R python/mmSolver ~/maya/<maya version>/plug-ins
```

### Install mmSolver plugin

Once the `mmSolver` plugin has been built you will need to place it on
the `MAYA_PLUG_IN_PATH`.

To install into our home directory maya `plug-ins` directory (which is
automatically on the `MAYA_PLUG_IN_PATH`), simply run these commands:

```commandline
$ cd <project root>
$ mkdir ~/maya/<maya version>/plug-ins
$ cp mmSolver.so ~/maya/<maya version>/plug-ins
```

Because we're using a number of third-party libraries, we need to make
these libraries available to Maya as the plug-in loads. Below I'll add
these into `~/maya/<maya version>/lib`, however you may do so however
you wish.

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

### Run Test Suite

After all parts of the `mmSolver` are installed and can be found by
Maya, try running the test suite to confirm everything is working as
expected.

```commandline
$ cd <project root>
$ sh runTests.sh
```

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).
