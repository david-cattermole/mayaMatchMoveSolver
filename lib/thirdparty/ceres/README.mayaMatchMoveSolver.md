# Ceres Solver 1.14.0 - Non-Linear Least Squares Minimizer

Ceres Solver is a portable C++ library that allows for modeling and solving
large, complicated optimization problems. It is a feature-rich tool that is used
for solving non-linear least squares problems with bounds constraints and
general unconstrained optimization problems.

This directory contains a vendored copy of Ceres Solver 1.14.0 that has been
integrated into the mmSolver project to eliminate external dependency management
and ensure consistent behavior across all build environments.

Ceres is used internally by OpenMVG for various least-squares minimization
solving, with both dense and sparse matrices. In the future, mmSolver may use
Ceres Solver directly for advanced optimization tasks.

## Source Repository

This project was copied from the following location:

**Page:** http://ceres-solver.org/
**Documentation:** http://ceres-solver.org/nnls_tutorial.html
**Git URL:** https://github.com/ceres-solver/ceres-solver.git
**Git Tag:** 1.14.0
**Release Date:** April 2018

## What's Included

The complete Ceres Solver 1.14.0 source tree has been vendored, including:

```
include/            # Public headers
internal/           # Internal Ceres implementation
cmake/              # CMake configuration files
examples/           # Example applications (not built)
data/               # Test data files
docs/               # Documentation source
LICENSE             # BSD 3-Clause license
README.md           # Original Ceres README
CMakeLists.txt      # Main CMake build file (replaced with mmSolver version)
```

## What's NOT Included

Various Bazel build files and some test-related files were removed as they are
not needed in mmSolver.

## Integration Details

### CMake Integration

The vendored Ceres is integrated through:

- `lib/thirdparty/ceres/CMakeLists.txt` - Creates the `ceres::ceres` interface target.
- `lib/thirdparty/CMakeLists.txt` - Includes ceres sub-directory.
- `share/cmake/modules/FindCeres.cmake` - Modified to prefer vendored version.

### Build Configuration

Ceres is configured to build as a static library with the following settings:

- Static library (`BUILD_SHARED_LIBS=OFF`).
- No testing, examples, or benchmarks (`BUILD_TESTING=OFF`).
- Uses vendored glog for logging.
- Uses vendored Eigen for linear algebra.
- EIGENSPARSE enabled for Eigen sparse matrix support.
- No LAPACK or SuiteSparse dependencies.
- OpenMP enabled for parallelization.
- C++11 support enabled.

## Dependencies

Ceres depends on the following vendored libraries in mmSolverLibs:

- **Eigen 3.4.0** - Linear algebra library (vendored)
- **glog 0.7.1** - Logging library (vendored)
- **OpenMP** - Parallel processing support (system)

## License

Ceres Solver is licensed under the BSD 3-Clause License. The complete license
text is available in the `LICENSE` file.

The vendored copy maintains all original license files and copyright notices.

## Maintenance

When updating Ceres:

1. Download the new version from the official GitHub repository.
2. Replace the contents of this directory with the new version.
3. Update this README with new version information.
4. Update the custom CMakeLists.txt with any new source files.
5. Test build compatibility with glog, Eigen, and OpenMVG components.
6. Update version references in build scripts.
7. Verify no API changes affect existing OpenMVG usage.

## Build Notes

The original CMakeLists.txt has been replaced with a simplified version that
integrates with the mmSolverLibs build system. The original build system
supported many features and configurations that are not needed for mmSolver's
specific use case.

Key build customizations and improvements:
- **Manual source listing**: Explicitly lists all required source files for reliable builds.
- **Static configuration**: Uses pre-configured `config.h` instead of dynamic feature detection.
- **Consolidated definitions**: All compile definitions in a single, clear call.
- **Removed unused modules**: Eliminated CMake modules for disabled features (SuiteSparse, CXSparse, TBB, etc.).
- **Enhanced documentation**: Clear comments explaining each configuration section.
- **Direct integration**: Links directly with vendored glog and Eigen.
- **Static library output**: Suitable for embedding in Maya plugins.
- **Maya compatibility**: Optimized compiler settings and disabled threading.

### Maintenance Benefits

The simplified build system provides several maintenance advantages:
- **Explicit source control**: Manual file listing ensures only intended files are compiled.
- **Consistent configuration**: Fixed settings prevent build variations across environments.
- **Reduced complexity**: Fewer files and simpler logic make the build easier to understand.
- **Better documentation**: Comments explain the purpose of each configuration section.
