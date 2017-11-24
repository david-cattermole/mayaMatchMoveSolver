# Building and Install

Building mmSolver can be fairly simple or complex, depending if you care about performance.

The simple steps are:

- Download and unpack `glm`.
- Download, unpack, and compile `levmar` with CMake.
- Download, unpack and compile `mmSolver` with CMake and argument paths pointing to `maya`, `levmar` and `glm`.
- Copy mmSolver plugin into Maya plug-in directory.

## Dependencies

- C++ compiler ([GCC](https://gcc.gnu.org/), Clang, VC++, etc)
- [CMake 2.6+](https://cmake.org/)
- [glm (GL Math)](https://glm.g-truc.net/)
- [levmar 2.6+](http://users.ics.forth.gr/~lourakis/levmar/)
- [Autodesk Maya 2016+](https://www.autodesk.com.au/products/maya/overview)
- [ATLAS](http://www.netlib.org/atlas/) (optional)
- [LAPACK](http://www.netlib.org/lapack/)  (optional)
- [BLAS](http://www.netlib.org/blas/)  (optional)

## Build and Install

### Build GL Math (glm)

GL Math (glm) is a header-only library implementing common OpenGL-like classes and functions for mathematics, like vectors and matrices.

Download glm from the [github project](https://github.com/g-truc/glm/releases/tag/0.9.8.5) and uncompress the ZIP file into a directory. Get the location of the glm headers, we will use when building the Maya plug-in.

```commandline
$ tar -xf glm-0.9.8.5.tar.gz
$ cd glm-0.9.8.5
$ pwd
/path/to/glm-0.9.8.5
```

### Build LevMar

Lev-Mar is the core library at the heart of this plug-in solver; the plug-in will not function without it.

There are two approaches to building Lev-Mar, one simple, the other is more complex.

In the simple build method we do not use the LAPACK library. LAPACK is a 'Linear Algebra' package, and has been implemented multiple times for heavy performance and robustness optimisations over many years. If you would like to compile with LAPACK, follow the 'complex method' below.

#### Build LevMar (simple method)

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

#### Build LevMar (complex method)

This complex method will use LAPACK. For this method to work you need to install the library 'ATLAS', which contains 'LAPACK', 'BLAS' and others. It is advised to do this using your operating system's software repository if you can.
 
Unfortunately I cannot provide detailed instructions for building [ATLAS](http://www.netlib.org/atlas/), [LAPACK](http://www.netlib.org/lapack/) or [BLAS](http://www.netlib.org/blas/). Please refer to the respective websites for information of building.

On CentOS 6 install the needed packages from the base repository with:
```commandline
$ yum install atlas atlas-devel
```
Note: You will need `root` access to install packages.

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
### Build mmSolver plugin

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

### Install mmSolver plugin

Now lets install into our home directory maya 'plug-ins' directory.

```commandline
$ mkdir ~/maya/<maya version>/plug-ins
$ cp mmSolver.so ~/maya/<maya version>/plug-ins
```
