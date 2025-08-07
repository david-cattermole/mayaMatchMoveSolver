# CMinpack - C/C++ Minpack

CMinpack provides nonlinear equation solving and nonlinear least squares
optimization algorithms and is required for building mmSolver. CMinpack
is used as a fallback solver when Ceres Solver is not available or for
specific legacy solver algorithms.

This directory contains a copy of the complete CMinpack source code
plus CMake build scripts that have been written for mmSolver.

The goal of this vendoring was to eliminate the need to download and
build external dependencies during the mmSolver build process, ensuring
a consistent and reproducible build environment.

Another goal was to reduce build complexity and ensure that mmSolver
can be built offline without internet connectivity.

## Source Repository

This project was copied from the following location:

**Page:** https://github.com/devernay/cminpack
**Documentation:** http://devernay.github.io/cminpack
**Git URL:** https://github.com/devernay/cminpack.git
**Git Tag:** v1.3.8
**Git Commit:** cb7c3f6 (prepare for 1.3.8 release)

## Copied Files

The following files have been copied without modification:

```
cminpack/CopyrightMINPACK.txt
cminpack/README.md
cminpack/cminpack.h
cminpack/cminpackP.h
cminpack/minpack.h
cminpack/chkder.c
cminpack/covar.c
cminpack/covar1.c
cminpack/dogleg.c
cminpack/dpmpar.c
cminpack/enorm.c
cminpack/fdjac1.c
cminpack/fdjac2.c
cminpack/hybrd.c
cminpack/hybrd1.c
cminpack/hybrj.c
cminpack/hybrj1.c
cminpack/lmder.c
cminpack/lmder1.c
cminpack/lmdif.c
cminpack/lmdif1.c
cminpack/lmpar.c
cminpack/lmstr.c
cminpack/lmstr1.c
cminpack/qform.c
cminpack/qrfac.c
cminpack/qrsolv.c
cminpack/r1mpyq.c
cminpack/r1updt.c
cminpack/rwupdt.c
```

## Build Configuration

This vendored version is configured to:

- Build only the double precision version (CMINPACK_PRECISION=d)
- Create a static library (cminpack_s)
- Disable BLAS/LAPACK dependencies for simplicity
- Use position-independent code when required
- Support Windows and Linux builds
- Provide the expected cminpack::cminpack target alias

## Notes

- The original CMinpack supports single, double, and extended precision variants
- This vendored version only builds the double precision variant needed by mmSolver
- The underscore variants (e.g., chkder_.c) are not included as they are FORTRAN-style interfaces
- Examples, tests, and documentation from the original repository are not included
- The vendored version is designed to integrate seamlessly with mmSolver's build system

## License

CMinpack is distributed under a BSD-like license. See `CopyrightMINPACK.txt` for full license text.

## Authors

- Original FORTRAN MINPACK: Jorge Moré, Burt Garbow, Ken Hillstrom (Argonne National Laboratory)
- C/C++ port: Manolis Lourakis (2002)
- Maintenance and improvements: Frédéric Devernay
- mmSolver integration: David Cattermole
