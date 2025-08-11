# Google Logging Library (glog) 0.7.1 - C++ Logging Framework

Google glog is a C++14 library that implements application-level logging.
The library provides logging APIs based on C++-style streams and various
helper macros to simplify common logging tasks.

This directory contains a vendored copy of glog 0.7.1 that has been integrated
into the mmSolver project to eliminate external dependency management and ensure
consistent behavior across all build environments.

glog is used internally by Ceres Solver for logging optimization progress and
debug information during mathematical solving operations.

## Source Repository

This project was copied from the following location:

**Page:** https://github.com/google/glog
**Documentation:** https://google.github.io/glog/0.7.1/
**Git URL:** https://github.com/google/glog.git
**Git Tag:** v0.7.1
**Release Date:** October 2024

## What's Included

The complete glog 0.7.1 source tree has been vendored, including:

```
src/                # Core glog source files
cmake/              # CMake configuration files
AUTHORS             # Project contributors
COPYING             # Apache 2.0 license
ChangeLog           # Version history
README.rst          # Original glog README
CMakeLists.txt      # Main CMake build file
```

## What's NOT Included

Various Bazel related build files were removed as they are not needed in
mmSolver.

## Integration Details

### CMake Integration

The vendored glog is integrated through:

- `lib/thirdparty/glog/CMakeLists.txt` - Creates the `glog::glog` interface target
- `lib/thirdparty/CMakeLists.txt` - Includes glog subdirectory
- `share/cmake/modules/Findglog.cmake` - Modified to prefer vendored version

### Build Configuration

glog is configured to build as a static library with the following settings:

- Static library (`BUILD_SHARED_LIBS=OFF`)
- No testing (`BUILD_TESTING=OFF`)
- No Google Test integration (`WITH_GTEST=OFF`)
- No gflags dependency (`WITH_GFLAGS=OFF`)
- Thread-safe logging enabled.
- Custom namespace to avoid conflicts.

## License

glog is licensed under the Apache License 2.0. The complete license text
is available in the `COPYING` file.

The vendored copy maintains all original license files and copyright notices.

## Maintenance

When updating glog:

1. Download the new version from the official GitHub repository.
2. Replace the contents of this directory with the new version.
3. Update this README with new version information.
4. Test build compatibility with Ceres and mmSolver components.
5. Update version references in build scripts.
6. Verify no API changes affect existing usage.

## Dependencies

glog has minimal external dependencies:

- **C++14 Standard Library** - Required for core functionality.
- **pthreads** - For thread-safe operations on Unix systems.
- **dbghelp** - For stack traces on Windows (optional).

No additional external libraries are required when built with default settings.
