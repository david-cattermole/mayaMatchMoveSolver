# Building and Install

Building mmSolver is quite easy. The project uses CMake, and provides
pre-made build scripts for Windows (Batch Script) and Linux (Bash -
Shell Script).

You may edit these scripts for your system, or use them as-is if you
have a standard default installation of Maya.

# Dependencies

These tools and libraries are required for building the ``mmSolver``
project. For details, please see the section below for each
dependency.

- [Autodesk Maya](https://www.autodesk.com.au/products/maya/overview)
- [Maya Development Kit](https://www.autodesk.com/developer-network/platform-technologies/maya)
- [CMake](https://cmake.org/)
- C++ Compilier
  - [GCC](https://gcc.gnu.org/) (Linux)
  - [Visual Studio (MSVC)](https://visualstudio.microsoft.com/downloads/) (Windows)
- [Rust](https://www.rust-lang.org/)
  - [cxx-bridge](https://cxx.rs/)
- [CMinpack](https://github.com/devernay/cminpack)
- [Eigen](https://eigen.tuxfamily.org/)
- [Ceres Solver](http://ceres-solver.org/)
  - [Google Log](https://github.com/google/glog)
- [Lens Distortion Plug-in Kit (LDPK)](https://www.3dequalizer.com)
- [Python](https://www.python.org/)
  - [Sphinx](http://www.sphinx-doc.org/en/master/index.html)
  - [Black](https://github.com/psf/black) - development requirement only.
  - [PyLint](https://pylint.org/) - development requirement only.

## Autodesk Maya

[Autodesk Maya 2018+](https://www.autodesk.com.au/products/maya/overview) is
supported and must be installed on the host to build mmSolver. mayapy
is required to run tests and the main Maya executable is required to
test and use mmSolver.

# Maya Development Kit ("devkit")

The [Maya Development Kit](https://www.autodesk.com/developer-network/platform-technologies/maya)
is required for building mmSolver.

Various utilities and libraries and files that are installed with the
Maya devkit are used during the build process.

## CMake

[CMake 3.15+](https://cmake.org/) is required to build all parts of
mmSolver. Older versions if CMake may work, however the Blender Add-On
may fail to generate.

### Ninja

As of mmSolver v0.4.0, the [Ninja build system](https://ninja-build.org/)
is used in the default Windows Batch scripts - Linux build
scripts are not affected. Alternate build systems will likely work
(such as NMake or Visual Studio projects) but are not tested.

## C++ Compiler

Depending on the version of Maya you are targeting, you will need the
C++ compiler recommended by Autodesk for your platform. Below is a
list of the versions currently used and recommended. Please refer to
the Autodesk Maya Developer documentation for details on setting up
your build environment.

Each Maya version also specifies a different C++ standard. As of
mmSolver v0.4.0 a C++ compiler with at least C++11 is required.

- Linux
  - [GCC 4.4.7](https://gcc.gnu.org/) (Maya 2016 and 2017)
  - [GCC 4.8.2](https://gcc.gnu.org/) (Maya 2018)
  - [GCC 6.3.1](https://gcc.gnu.org/) (Maya 2019 and 2020)
    - Red Hat [DST 6.1](https://access.redhat.com/documentation/en-us/red_hat_developer_toolset/6/html/6.1_release_notes/index)
    - `yum install devtoolset-6` on RHEL 7 / CentOS 7
  - [GCC 9.3.1](https://gcc.gnu.org/) (Maya 2022 and 2023)
    - Red Hat [DST 9.1](https://access.redhat.com/documentation/en-us/red_hat_developer_toolset/9/html/9.1_release_notes/index)
    - `yum install devtoolset-9` on RHEL 7 / CentOS 7
  - [GCC 11.2.1](https://gcc.gnu.org/) (Maya 2024 and 2025)
    - Red Hat [DST 11](https://access.redhat.com/documentation/en-us/red_hat_developer_toolset/11/html/11.0_release_notes/dts11.0_release)
    - `dnf install devtoolset-11` on RHEL 8 / Rocky Linux 8
- Windows
  - [Visual Studio 2012 update 5 (MSVC 11.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2016 and 2017)
  - [Visual Studio 2015 update 3 (MSVC 14.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2018 and 2019)
  - [Visual Studio 2017 (MSVC 15.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2020)
  - [Visual Studio 2019 (MSVC 16.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2022 and 2023)
  - [Visual Studio 2022 (MSVC 17.0)](https://visualstudio.microsoft.com/downloads/) (Maya 2024)
  - [Visual Studio 2022 (MSVC 17.8.3+)](https://visualstudio.microsoft.com/downloads/) (Maya 2025)

## Rust

[Rust 1.67+](https://www.rust-lang.org/) is required for various
features inside mmSolver.

Rust is a modern programming language comparable to C or C++ in terms
of speed, is highly performant and provides safety and stability
guarantees for software written in Rust.

Both the Rust compiler (``rustc``) and the Rust package manager
(``cargo``) are required to be installed to build mmSolver. No part of
Rust is required to be installed at run-time.

See the 'Cargo.toml' files for a full list of (automatically)
installed dependencies via the package managers.

### cxx-bridge

[cxx-bridge](https://cxx.rs/) is an executable required for generating
C++ bindings for Rust code. This utility allows C++ code to interact
with Rust code in simple and a safe way.

## Eigen

[Eigen](https://eigen.tuxfamily.org/) is a requirement of mmSolver and
is used to store 3D vectors, matrices, perform linear algebra, and is
also required for `OpenMVG` (see below).

## CMinpack

[CMinpack 1.3.8](https://github.com/devernay/cminpack/releases/tag/v1.3.8)
is required for non-linear least-squares minimization.

This solver is not as sophisticated as Ceres and may be deprecated in a
future release (in favor of [Ceres Solver](http://ceres-solver.org/))

## Ceres Solver

[Ceres Solver](http://ceres-solver.org/) is a state-of-the-art
non-linear least-squares minimization library.

Ceres Solver allows solving large minimization problems efficiently
using sparse matrices. Ceres Solver itself has many dependencies, and
the speed of the library depends on the underlying sparse matrix
libraries and functions. Feel free to compile and use whatever
underlying dependencies provides the best performance for you -
however make sure that sparse matrix solving is available.

Ceres Solver is not optional, and is required for `OpenMVG` features.

In a future version of mmSolver Ceres may replace CMinpack as the
default and recommended solving engine.

## OpenMVG

[OpenMVG 2.0](https://github.com/openMVG/openMVG/releases/tag/v2.0) is
used for traditional Multiple-View Geometry calculations inside
mmSolver, such as Structure from Motion, triangulation and other
features. Only a sub-set of OpenMVG is included with mmSolver.

OpenMVG is not a third-party dependency, because it's included inside
mmSolver. OpenMVG requires Eigen and Ceres Solver internally.

## Lens Distortion Plug-in Kit

[Lens Distortion Plug-in Kit (LDPK)](https://www.3dequalizer.com/?site=tech_docs)
is an open source project provided freely by Science-D-Visions, the
creators of 3DEqualizer.

The LDPK provides a standard set of lens distortion features and the
ability to provide custom lens distortion plug-ins.

## Python

[Python 3.x](https://www.python.org/) is used for development, testing
and formatting Python code.

The mmSolver build will use the provided Maya Python executable
(``mayapy``) for some processes, such as generating Python files from
Qt .ui files. Use of ``mayapy`` will use Python 2.x or 3.x depending
on the Maya version.

See 'requirements-dev.txt' for more details of all dependencies.

### Sphinx

[Sphinx](http://www.sphinx-doc.org/en/master/index.html) is used to
build documentation for mmSolver including the mmSolver
[documentation page](https://david-cattermole.github.io/mayaMatchMoveSolver/index.html),
and the documentation bundled with mmSolver.

### Developer Python Tools - Black and PyLint

[Black](https://github.com/psf/black) is used for for Python code
formatting, and is only used by developers.

[PyLint](https://pylint.org/) for Python code 'linting'. It is not
critical for building mmSolver.

Both Black and PyLint are used for during development and is not
required for building mmSolver.

# Building Overview

An overview of compiling is:

1. Download mayaMatchMoveSolver project from GitHub.
2. Unzip the source code into a directory.
3. Open a command line or terminal and navigate to the unzipped files.
2. Run the provided build script to compile mmSolver.

Below lists all the commands run in an example session, following the
above sections.

On Linux:
```commandline
# Go to root of project directory.
$ cd <project root>

# Build mmSolver, compile UI files, compile Maya plug-in, build
# documentation, create module and install to home directory.
$ make build_XXXX
```

On Windows:
```cmd
:: Go to root of project directory.
> CD <project root>

:: Build mmSolver, compile UI files, compile Maya plug-in, build
:: documentation, create module and install to home directory.
> make build_XXXX
```

# Building mmSolver

To build the project you can use the build scripts provided.

| Build Script Name                     | Operating System |
| ------------                          | -----------      |
| build_mmSolver_linux_mayaXXXX.bash    | Linux            |
| build_mmSolver_windows64_mayaXXXX.bat | Windows          |

## Custom Build Directory

You can override the default build directory location by setting the
`BUILD_DIR_BASE` environment variable before running any build script. This
allows you to build in a custom location instead of the default parent
directory.

For details of building the project, please see
[BUILD_LINUX.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD_LINUX.md)
or
[BUILD_WINDOWS.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD_WINDOWS.md).

# Testing mmSolver

After building mmSolver, you can run the test suite to verify everything is
working correctly.

## Test Scripts

Convenience test scripts are provided for easy testing:

| Test Script Name                      | Operating System |
| ------------                          | -----------      |
| test_mmSolver_linux_mayaXXXX.bash     | Linux            |
| test_mmSolver_windows64_mayaXXXX.bat  | Windows          |

## Running Tests

On Linux:
```commandline
# Go to root of project directory.
$ cd <project root>

# Run full test suite for Maya 2024
$ make test_2024

# Run specific test file
$ make test_2024 tests/test/test_api/test_solve_robotArm.py

# Run all API tests
$ make test_2024 tests/test/test_api/
```

On Windows:
```cmd
:: Go to root of project directory.
> CD <project root>

:: Run full test suite for Maya 2024
> make test_2024

:: Run specific test file
> make test_2024 tests\test\test_api\test_solve_robotArm.py

:: Run all API tests
> make test_2024 tests\test\test_api\
```

For more information about testing, see the Testing section in
[tests/README.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/tests/README.md).

# Cleaning Build Files

After building mmSolver, you may want to clean the build directories to free up
disk space or prepare for a clean build. The easiest way is to use the combined
clean targets that remove both mmSolver and OpenColorIO build artifacts.

## Using Make Targets

The recommended way to clean build files is using the combined clean targets:

On Linux:
```commandline
# Go to root of project directory.
$ cd <project root>

# Clean all build files for Maya 2024 (both mmSolver and OpenColorIO)
$ make clean_2024
```

On Windows:
```cmd
:: Go to root of project directory.
> CD <project root>

:: Clean all build files for Maya 2024 (both mmSolver and OpenColorIO).
> make clean_2024
```

**Note:** For a complete list of available targets including individual component
clean targets, run `make help` (Linux) or `make.bat help` (Windows).
