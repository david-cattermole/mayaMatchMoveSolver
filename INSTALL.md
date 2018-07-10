# Building and Install

Building mmSolver can be fairly simple or complex, depending if you care about performance. For tests, you may use the "Simple Method"

There are also Linux shell scripts to automate most of the compiling of external dependencies. You may edit these scripts for your system. There are patches required are for different builds in `./external/patches/`. 

## Build Environment

The below processes were tested on a CentOS 6.x Linux distribution.

These are the versions of various software tested:

| Software     | Version |
| ------------ | ----------- |
| OS | CentOS 6.9 |
| Linux Kernel | Linux 2.6.32-696.16.1.el6.x86_64 | 
| GCC | gcc (GCC) 4.4.7 20120313 (Red Hat 4.4.7-18) |
| LDD | ldd (GNU libc) 2.12 |
| CMake | 2.8.12.2 *(see note below)* |
| Autodesk Maya | Autodesk Maya 2016 SP6 |
| Autodesk Maya API | 201614 |

NOTE: If compiling the 'Full Mode', you will require a newer version of CMake. The CMake version 3.6.3 has been confirmed to work. The default CMake in the CentOS 6 repository is not sufficient to build the `metis` sub-component of `SuiteSparse`. However for the 'Simple Method', CMake 2.6 is sufficient.

## Simple Method

An overview of the simple method is:

- Download, unpack, and compile `levmar` with CMake.
- Download, unpack and compile `mmSolver` with CMake and argument paths pointing to `maya`, `levmar`.
- Copy mmSolver plugin into Maya plug-in directory.
- Copy mmSolver python API into Maya scripts directory.

### Build Script

To build without any third-party dependencies other than levmar, run these commmand:
```commandline
$ cd <project root>
$ bash external/download_levmar_archive.sh
$ build_with_levmar.sh
```

###  Dependencies

- C++ compiler ([GCC](https://gcc.gnu.org/), Clang, VC++, etc)
- [CMake 2.8+](https://cmake.org/)
- [Autodesk Maya 2016+](https://www.autodesk.com.au/products/maya/overview)
- [levmar 2.6](http://users.ics.forth.gr/~lourakis/levmar/)

### Install mmSolver Python API

The `mmSolver` project has a convenience Python API for tool writers, which is recommended. The API must be added to the `MAYA_SCRIPT_PATH`. 

To install into our home directory maya `scripts` directory, simply run these commands:

```commandline
$ cd <project root>
$ cp -R python/mmSolver ~/maya/<maya version>/plug-ins
```

### Install mmSolver plugin

Once the `mmSolver` plugin has been build you will need to place it on the `MAYA_PLUG_IN_PATH`. 

To install into our home directory maya `plug-ins` directory (which is automatically on the `MAYA_PLUG_IN_PATH`), simply run these commands:

```commandline
$ cd <project root>
$ mkdir ~/maya/<maya version>/plug-ins
$ cp mmSolver.so ~/maya/<maya version>/plug-ins
```

### Run Test Suite

After all parts of the `mmSolver` are installed and can be found by Maya, try running the test suite to confirm everything is working as expected.

```commandline
$ cd <project root>
$ sh runTests.sh
```


## Full Method with ATLAS

This section is for compiling with the free and open-source library ATLAS.

This method will use both the `levmar`, `sparselm` and `ceres` algorithms, as well as open source libraries for computation; `Automatically Tuned Linear Algebra Software (ATLAS)`.

### Build Script

Note: This will assume the `atlas` is installed via yum on CentOS 6.x. If you wish to build your own custom atlas library it is an undocumented exercise for the user. On CentOS 6.x you may install `atlas` with the following command:
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

###  Dependencies

- C++ compiler ([GCC](https://gcc.gnu.org/), Clang, VC++, etc)
- [CMake 3.6+](https://cmake.org/)
- [Autodesk Maya 2016+](https://www.autodesk.com.au/products/maya/overview)
- [levmar 2.6](http://users.ics.forth.gr/~lourakis/levmar/)
- [ATLAS 3.8.4](http://math-atlas.sourceforge.net/)
- [SuiteSparse 5.0.0](http://faculty.cse.tamu.edu/davis/suitesparse.html)
- [sparseLM 1.3](http://users.ics.forth.gr/~lourakis/sparseLM/)
- [Eigen 3.3.4](http://eigen.tuxfamily.org/)
- [glog 0.3.1](https://github.com/google/glog)
- [gflags 2.2.1](https://github.com/gflags/gflags)
- [ceres-solver 1.13.0](http://ceres-solver.org/)

### Build mmSolver plugin

To compile the Maya plugin, run the commands.

```commandline
$ cd <project root>
$ mkdir build
$ cd build
$ cmake -DCMAKE_BUILD_TYPE=Release \
        -DHAVE_SPLM=1 \
        -DHAVE_CERES=1 \
        -DUSE_SUITE_SPARSE=1 \
        -DUSE_ATLAS=1 \
        -DUSE_MKL=0 \
        -DMAYA_INCLUDE_PATH=/usr/autodesk/maya2016/include \
        -DMAYA_LIB_PATH=/usr/autodesk/maya2016/lib \
        -DLEVMAR_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DLEVMAR_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
        -DATLAS_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DSUITE_SPARSE_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DSPLM_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DSPLM_INCLUDE_PATH=${PROJECT_ROOT}/external/lib \
        -DCERES_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DCERES_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
        ..
$ make -j4
```

Once the plug-in is built successfully, continue on to the section "Install Common Files" below.

## Full Method with Intel MKL

This method will use both the `levmar`, `sparselm` and `ceres` algorithms, as well as highly-optimised libraries for computation; `Intel Math Kernel Libraries`.

### Build Script

Note: This will assume Intel MKL is installed under `/opt/intel/mkl`, you will need to modify the scripts if this location is not correct on your system.

To build with Intel MKL, run these command: 
```commandline
$ cd <project root>
$ bash external/download_all_archives.sh
$ bash build_with_intel_mkl.sh
```

###  Dependencies

- C++ compiler ([GCC](https://gcc.gnu.org/), Clang, VC++, etc)
- [CMake 3.6+](https://cmake.org/)
- [Autodesk Maya 2016+](https://www.autodesk.com.au/products/maya/overview)
- [levmar 2.6](http://users.ics.forth.gr/~lourakis/levmar/)
- [Intel Math Kernel Library (MLK)](https://software.intel.com/en-us/mkl)
- [SuiteSparse 5.0.0](http://faculty.cse.tamu.edu/davis/suitesparse.html)
- [sparseLM 1.3](http://users.ics.forth.gr/~lourakis/sparseLM/)
- [Eigen 3.3.4](http://eigen.tuxfamily.org/)
- [glog 0.3.1](https://github.com/google/glog)
- [gflags 2.2.1](https://github.com/gflags/gflags)
- [ceres-solver 1.13.0](http://ceres-solver.org/)

### Build mmSolver plugin

To compile the Maya plugin, run the commands.

```commandline
$ cd <project root>
$ mkdir build
$ cd build
$ cmake -DCMAKE_BUILD_TYPE=Release \
        -DHAVE_SPLM=1 \
        -DHAVE_CERES=1 \
        -DUSE_ATLAS=0 \
        -DUSE_SUITE_SPARSE=1 \
        -DUSE_MKL=1 \
        -DMAYA_INCLUDE_PATH=/usr/autodesk/maya2016/include \
        -DMAYA_LIB_PATH=/usr/autodesk/maya2016/lib \
        -DLEVMAR_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DLEVMAR_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
        -DMKL_LIB_PATH=/opt/intel/mkl/lib/intel64 \
        -DSUITE_SPARSE_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DSPLM_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DSPLM_INCLUDE_PATH=${PROJECT_ROOT}/external/lib \
        -DCERES_LIB_PATH=${PROJECT_ROOT}/external/lib \
        -DCERES_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
        ..
$ make -j4
```

Once the plug-in is built successfully, continue on to the section "Install Common Files" directly below.

## Install Common Files

### Install mmSolver Python API

The `mmSolver` project has a convenience Python API for tool writers, which is recommended. The API must be added to the `MAYA_SCRIPT_PATH`. 

To install into our home directory maya `scripts` directory, simply run these commands:

```commandline
$ cd <project root>
$ cp -R python/mmSolver ~/maya/<maya version>/plug-ins
```

### Install mmSolver plugin

Once the `mmSolver` plugin has been build you will need to place it on the `MAYA_PLUG_IN_PATH`. 

To install into our home directory maya `plug-ins` directory (which is automatically on the `MAYA_PLUG_IN_PATH`), simply run these commands:

```commandline
$ cd <project root>
$ mkdir ~/maya/<maya version>/plug-ins
$ cp mmSolver.so ~/maya/<maya version>/plug-ins
```

Because we're using a number of third-party libraries, we need to make these libraries available to Maya as the plug-in loads. Below I'll add these into `~/maya/<maya version>/lib`, however you may do so however you wish.

```commandline
$ cd <project root>
$ mkdir ~/maya/<maya version>/lib
$ cp -R external/lib/* ~/maya/<maya version>/lib
```

You will need to add `~/maya/<maya version>/lib` onto your `LD_LIBRARY_PATH` environment variable. For example if you use the 'bash' shell, you add this command into your `~/.bashrc` file.

```bash
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:~/maya/<maya version>/lib
```

### Run Test Suite

After all parts of the `mmSolver` are installed and can be found by Maya, try running the test suite to confirm everything is working as expected.

```commandline
$ cd <project root>
$ sh runTests.sh
```