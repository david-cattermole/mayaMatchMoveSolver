# Building on Linux

We can build `mmSolver` on Linux quite easily. We have provided a
CMake build script which is easily usable, configurable and readable.

On Linux we have tested three different library dependency combinations:
1. With `levmar` only.
2. With `levmar` and `ATLAS` for improved speed and robustness.
3. Or, With `levmar` and `Intel MKL` for improved speed and robustness.

# Build with levmar

To build without any third-party dependencies other than `levmar`, run
these commands:
```commandline
$ cd <project root>
$ bash external/download_all_archives.sh
$ vi build_with_levmar.sh  # Edit path to Maya include / library
$ build_with_levmar.sh
```

NOTE: Replace ``<project root>`` as required.

Using the `build_with_levmar.sh` script will combine `levmar`
into the shared library `mmSolver.so`. This means you only need one
plug-in file, and do not need to worry about setting
`LD_LIBRARY_PATH` paths.

# Build with levmar and ATLAS

This section is for compiling with the free and open-source library
`ATLAS`.

This method will use the `levmar` algorithm, and `Automatically Tuned
Linear Algebra Software (ATLAS)` for performance computation and
stability. `ATLAS` is Free Open Source Software, Using a third-party
maths library is recommended by the `levmar` project.

This will assume `atlas` is installed via yum on CentOS 7.x. If you
wish to build your own custom `atlas` library it is an undocumented
exercise for the user. On CentOS 7.x you may install `atlas` with the
following command (as `root` user):

```commandline
$ yum install atlas.x86_64 atlas-devel.x86_64
$ yum install lapack64.x86_64 lapack64-devel.x86_64
```

After ATLAS has been installed, you may build `mmSolver`
with ATLAS using these commands:
```commandline
$ cd <project root>
$ bash external/download_all_archives.sh  # Download archives (only required once)
$ vi build_with_atlas.sh  # Edit path to Maya include / library
$ bash build_with_atlas.sh
```

NOTE: Replace ``<project root>`` as required.

# Build with levmar and Intel MKL

This method will use both the `levmar` algorithm, as well as
highly-optimised libraries for computation; `Intel Math Kernel
Libraries (Intel MKL)`. `Intel MKL` is proprietary closed-source
software. Using a third-party maths library is recommended by the
`levmar` project.

Intel MKL must be installed manually, this build script will not
install it for you. You will need to sign up, download and install
from the [Intel MKL website](https://software.intel.com/en-us/mkl).

The instructions below assume Intel MKL is installed under
`/opt/intel/mkl`, you will need to modify the scripts if this location
is not correct on your system.

To build with `Intel MKL`, run these command:
```commandline
$ cd <project root>
$ bash external/download_all_archives.sh  # Download archives (only required once)
$ vi build_with_intel_mkl.sh  # Edit path to Maya include / library
$ bash build_with_intel_mkl.sh
```

NOTE: Replace ``<project root>`` as required.

# CMake Build Script

For those needing or wanting to compile the ``mmSolver`` Maya plug-in
manually you can do it easily using the following commands.

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

| CMake Option         | Description                                 |
| -------------------- | ------------------------------------------- |
| CMAKE_BUILD_TYPE     | The type of build (`Release`, `Debug`, etc) |
| MAYA_INCLUDE_PATH    | Directory to the Maya header include files  |
| MAYA_LIB_PATH        | Directory to the Maya library files         |
| LEVMAR_LIB_PATH      | Directory to levmar library                 |
| LEVMAR_INCLUDE_PATH  | Directory to levmar header includes         |
| USE_ATLAS            | Use ATLAS libraries?                        |
| ATLAS_LIB_PATH       | Directory to ATLAS libraries                |
| USE_MKL              | Use Intel MKL libraries?                    |
| MKL_LIB_PATH         | Directory to Intel MKL libraries            |

Setting ``USE_ATLAS`` and ``USE_MKL`` to ``1`` is an error, both
libraries provide the same functionality and both are not needed,
only one. If `ATLAS` and `Intel MKL` are not required you may set both
``USE_ATLAS`` and ``USE_MKL`` to ``0``.

You can read any of the build scripts to find out how they work.
The build scripts can be found in `<project root>/build_with_*.sh`
and `<project root>/external/*.sh`.

Following the steps above you should have a compiled Maya plug-in.

Next we must install the plug-in and corresponding files.
[INSTALL.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL.md)
