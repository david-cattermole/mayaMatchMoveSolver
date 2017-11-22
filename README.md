# Maya MatchMove Solver (mmSolver)

A generic solver for matchmove related tasks using a Non-Linear Least Squares algorithm.

This tool is currently in development and is considered ALPHA software, do not use this in production.

Use Cases:
- Solving camera or object position / rotation based on 2D to 3D positions.
- Using DAG hierarchies to solve objects in specific spaces (for example object space).
- Generation of approximate 3D positions from 2D screen-space positions.

## Current Features

- Solver Plug-in
  - Minimising residual error between 2D and 3D positions.
  - Small number of build dependencies.
  - Single frame solving - multi-frame solving is not supported.
  - No undo/redo support.
- User Tools
  - None

## Planned Features

- Solver Plug-in
  - 2D-to-3D error weighting.
  - Evaluation of complex character rigs for soft-deformation. 
  - Full Undo/Redo support.
  - Single frame or frame range solve.

- User Tools
  - GUI to select camera and object channels to solve.
    - GUI to associate/disassociate 2D tracks and 3D locators.
  - 2D tracks can either be locators or special objects that look like 2D tracks with pattern/search boxes.
    - Dynamic NURBS curves to connect the display of the 2D and 3D points.
  - Tool to project 2D tracks onto polygons, creating associated static or animated locators.
  - Tool to import 2D tracks to Maya, reading 3DE or pfTrack, etc. 2D tracking files.

## Usage

Here is a simple example of how to use the mmSolver command.

```python
import maya.cmds

# Load Plugin
maya.cmds.loadPlugin('mmSolver')

cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

bundle_tfm = maya.cmds.createNode('transform', name='bundle_tfm')
bundle_shp = maya.cmds.createNode('locator', name='bundle_shp', parent=bundle_tfm)
maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)

marker_tfm = maya.cmds.createNode('transform', name='marker_tfm', parent=cam_tfm)
marker_shp = maya.cmds.createNode('locator', name='marker_shp', parent=marker_tfm)
maya.cmds.setAttr(marker_tfm + '.tx', -2.5)
maya.cmds.setAttr(marker_tfm + '.ty', 1.3)
maya.cmds.setAttr(marker_tfm + '.tz', -10)

cameras = (
    (cam_tfm, cam_shp),
)
weight = 1.0
markers = (
    (marker_tfm, cam_shp, bundle_tfm, weight),
)
node_attrs = [
    (bundle_tfm + '.tx', 1),
    (bundle_tfm + '.ty', 1),
]

# Run solver!
maya.cmds.mmSolver(
    camera=cameras,
    marker=markers,
    attr=node_attrs,
    iterations=1000,
    verbose=True,
)

# Take a look of our results.
maya.cmds.lookThru(cam_tfm)
```

_See 'test1.py' and 'test2.py' for more details_

## Command Flags

The command syntax is:
```text
mmSolver [flags]
```

The command can be run in both MEL and Python. 

MEL Example:
```text
mmSolver  
    -camera "camera1" "cameraShape1" 
    -marker "camera1" "marker1" "bundle1" 1.0
    -marker "camera1" "marker2" "bundle2" 1.0
    -attr "node.attr" 1
    -attr "bundle1.tx" 1
    -attr "bundle1.ty" 1
    -attr "bundle1.tz" 1
    -iterations 1000;
```

Python Example:
```python
maya.cmds.mmSolver(
    camera=('camera1', 'cameraShape1'),
    marker=(
        ('camera1', 'marker1', 'bundle1', 1.0),
        ('camera1', 'marker2', 'bundle2', 1.0),
    ),
    attr=(
        ('bundle1.tx', 1), 
        ('bundle1.ty', 1), 
        ('bundle1.tz', 1)
    ),
    iterations=1000
)
```

Here is a table of command flags, as currently specified in the command. 

| Flag              | Type                   | Description | Default Value |
| ----------------- | ---------------------- | ----------- | ------------- |
| -camera (-c)      | string, string         | Camera transform and shape nodes | None |
| -marker (-m)      | string, string, string, double | Marker, Camera, Bundle and error weighting | None |
| -attr (-a)        | string                 | Node attributes to solve | None |
| -iterations (-it) | int                    | Number of iterations to perform. | 1000 |
| -verbose (-v)     | bool                   | Prints more information | False |

## Building and Install

### Dependencies

- C++ compiler ([GCC](https://gcc.gnu.org/), Clang, VC++, etc)
- [CMake 2.6+](https://cmake.org/)
- [glm (GL Math)](https://glm.g-truc.net/)
- [levmar 2.6+](http://users.ics.forth.gr/~lourakis/levmar/)
- [Autodesk Maya 2016+](https://www.autodesk.com.au/products/maya/overview)
- [ATLAS (optional)](http://www.netlib.org/atlas/)
- [LAPACK (optional)](http://www.netlib.org/lapack/)
- [BLAS (optional)](http://www.netlib.org/blas/)

### Build and Install
  
Run the following in a Bash-like shell:

#### Build LevMar

Lev-Mar is the core library at the heart of this plug-in solver; the plug-in will not function without it.

There are two approaches to building Lev-Mar, one simple, the other is more complex.

In the simple build method we do not use the LAPACK library. LAPACK is a 'Linear Algebra' package, and has been implemented multiple times for heavy performance and robustness optimisations over many years. If you would like to compile with LAPACK, follow the 'complex method' below.

##### Build LevMar (simple method)

Levmar does not use 'make install', and it will only compile a static library, which we will link against in the next step.

```commandline
$ tar -xf levmar-2.6.tgz
$ cd levmar-2.6
$ mkdir build
$ cd build
$ cmake -DNEED_F2C=0 -DHAVE_LAPACK=0 -DBUILD_DEMO=1 ..
-- The C compiler identification is GNU 4.4.7
-- The CXX compiler identification is GNU 4.4.7
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Configuring done
-- Generating done
-- Build files have been written to: /path/to/example/directory/levmar-2.6/build
$ make
Scanning dependencies of target levmar
[ 14%] Building C object CMakeFiles/levmar.dir/lm.c.o
[ 28%] Building C object CMakeFiles/levmar.dir/Axb.c.o
[ 42%] Building C object CMakeFiles/levmar.dir/misc.c.o
In file included from /home/davidc/bin/levmar/test/levmar-2.6/misc.c:47:
/path/to/example/directory/levmar-2.6/misc_core.c:577:2: warning: #warning LAPACK not available, LU will be used for matrix inversion when computing the covariance; this might be unstable at times
In file included from /path/to/example/directory/levmar-2.6/misc.c:64:
/path/to/example/directory/levmar-2.6/misc_core.c:577:2: warning: #warning LAPACK not available, LU will be used for matrix inversion when computing the covariance; this might be unstable at times
[ 57%] Building C object CMakeFiles/levmar.dir/lmlec.c.o
/path/to/example/directory/levmar-2.6/lmlec.c:39:2: warning: #warning Linearly constrained optimization requires LAPACK and was not compiled!
[ 71%] Building C object CMakeFiles/levmar.dir/lmbc.c.o
[ 85%] Building C object CMakeFiles/levmar.dir/lmblec.c.o
/path/to/example/directory/levmar-2.6/lmblec.c:39:2: warning: #warning Combined box and linearly constrained optimization requires LAPACK and was not compiled!
[100%] Building C object CMakeFiles/levmar.dir/lmbleic.c.o
/path/to/example/directory/levmar-2.6/lmbleic.c:40:2: warning: #warning Linear inequalities constrained optimization requires LAPACK and was not compiled!
Linking C static library liblevmar.a
[100%] Built target levmar
$ ./lmdemo  # run the demo (optional)
 Covariance of the fit:
 0.00483514 -0.00162445 -0.000548114
 -0.00162445 0.000546079 0.000184356
 -0.000548114 0.000184356 6.22705e-05
 
 Results for Meyer's (reformulated) problem:
 Levenberg-Marquardt returned 208 in 208 iter, reason 2
 Solution: 2.481779 6.181346 3.502236
 
 Minimization info:
 1308.25 8.79459e-05 1.12674e-07 1.13856e-29 636.638 208 2 272 21 209
$ ls -l -h liblevmar.a  # ensure the library exists 
-rw-rw-r--. 1 user user 97K Aug 22 13:19 liblevmar.a
```

##### Build LevMar (complex method)

This complex method will use LAPACK. For this method to work you need to install the library 'ATLAS', which contains 'LAPACK', 'BLAS' and others. It is advised to do this using your operating system's software repository if you can.
 
Unfortunately I cannot provide detailed instructions for building [ATLAS](http://www.netlib.org/atlas/), [LAPACK](http://www.netlib.org/lapack/) or [BLAS](http://www.netlib.org/blas/). Please refer to the respective websites for information of building.

On CentOS 6 install the needed packages from the base repository with:
```commandline
$ yum install atlas atlas-devel
```

Unpack the Lev-Mar source code, and start editing the Makefile.
```commandline
$ tar -xf levmar-2.6.tgz
$ cd levmar-2.6
$ emacs Makefile  # open Makefile in your favourite text editor.
```

After you've opened the Makefile, by default you'll see something similar to this:
```text
#
# Unix/Linux GCC Makefile for Levenberg - Marquardt minimization
# Under windows, use Makefile.vc for MSVC
#

CC=gcc
CONFIGFLAGS=#-ULINSOLVERS_RETAIN_MEMORY
#ARCHFLAGS=-march=pentium4 # YOU MIGHT WANT TO UNCOMMENT THIS FOR P4
CFLAGS=$(CONFIGFLAGS) $(ARCHFLAGS) -O3 -funroll-loops -Wall #-g #-ffast-math #-pg
LAPACKLIBS_PATH=/usr/local/lib # WHEN USING LAPACK, CHANGE THIS TO WHERE YOUR COMPILED LIBS ARE!
LDFLAGS=-L$(LAPACKLIBS_PATH) -L.
LIBOBJS=lm.o Axb.o misc.o lmlec.o lmbc.o lmblec.o lmbleic.o
LIBSRCS=lm.c Axb.c misc.c lmlec.c lmbc.c lmblec.c lmbleic.c
DEMOBJS=lmdemo.o
DEMOSRCS=lmdemo.c
AR=ar
RANLIB=ranlib
LAPACKLIBS=-llapack -lblas -lf2c # comment this line if you are not using LAPACK.
                                 # On systems with a FORTRAN (not f2c'ed) version of LAPACK, -lf2c is
                                 # not necessary; on others, -lf2c is equivalent to -lF77 -lI77
```

Edit 'CFLAGS' and add '-fPIC', so we can compile and link the shared library with other libraries (in the Maya plug-in):
```text
CFLAGS=$(CONFIGFLAGS) $(ARCHFLAGS) -O3 -funroll-loops -Wall -fPIC
```

Change the 'LAPACKLIBS' section to:
```text
LAPACKLIBS=-L/usr/lib64/atlas -llapack -lf77blas -latlas
```
Note '/usr/lib64/atlas' is a specific location in CentOS 6 which ATLAS is installed, it may be different on other Linux distributions.

Now, lets go back to the command line and 'make' our project. 
```commandline
$ make -j4
gcc   -O3 -funroll-loops -Wall -fPIC   -c -o lm.o lm.c
gcc   -O3 -funroll-loops -Wall -fPIC   -c -o Axb.o Axb.c
gcc   -O3 -funroll-loops -Wall -fPIC   -c -o misc.o misc.c
gcc   -O3 -funroll-loops -Wall -fPIC   -c -o lmlec.o lmlec.c
gcc   -O3 -funroll-loops -Wall -fPIC   -c -o lmbc.o lmbc.c
gcc   -O3 -funroll-loops -Wall -fPIC   -c -o lmblec.o lmblec.c
gcc   -O3 -funroll-loops -Wall -fPIC   -c -o lmbleic.o lmbleic.c
gcc   -O3 -funroll-loops -Wall -fPIC   -c -o lmdemo.o lmdemo.c
ar crv liblevmar.a lm.o Axb.o misc.o lmlec.o lmbc.o lmblec.o lmbleic.o
r - lm.o
r - Axb.o
r - misc.o
r - lmlec.o
r - lmbc.o
r - lmblec.o
r - lmbleic.o
ranlib liblevmar.a
gcc -L/usr/lib  -L. lmdemo.o -o lmdemo -llevmar -L/usr/lib64/atlas -llapack -lf77blas -latlas  -lm
/usr/bin/ld: skipping incompatible /usr/lib/libm.so when searching for -lm
/usr/bin/ld: skipping incompatible /usr/lib/libc.so when searching for -lc
$ ./lmdemo  # run the demo (optional)
Covariance of the fit:
0.00483514 -0.00162445 -0.000548114
-0.00162445 0.000546079 0.000184356
-0.000548114 0.000184356 6.22705e-05

Results for Meyer's (reformulated) problem:
Levenberg-Marquardt returned 208 in 208 iter, reason 2
Solution: 2.481779 6.181346 3.502236

Minimization info:
1308.25 8.79459e-05 1.12674e-07 1.13856e-29 636.638 208 2 272 21 209
$ ls -l -h liblevmar.a  # ensure the library exists 
-rw-rw-r--. 1 user user 461K Aug 22 13:19 liblevmar.a
```
#### Build mmSolver plugin

To compile the Maya plugin, run the commands.

```commandline
$ cd <project root>
$ mkdir build
$ cd build
$ cmake \
  -DMAYA_INCLUDE_PATH=/path/to/maya/include \
  -DMAYA_LIB_PATH=/path/to/maya/lib \
  -DLEVMAR_LIB_PATH=/path/to/levmar/lib \
  -DLEVMAR_INCLUDE_PATH=/path/to/levmar/include \
  -DATLAS_LIBRARY_PATH=/path/to/atlas/libraries \
  -DGLM_INCLUDE_PATH=/path/to/glm \
  ..
$ make -j4
```

#### Install mmSolver plugin

Now lets install into our home directory maya 'plug-ins' directory.

```commandline
$ mkdir ~/maya/<maya version>/plug-ins
$ cp mmSolver.so ~/maya/<maya version>/plug-ins
```

## Limitations and Known Bugs 

_To be written_
