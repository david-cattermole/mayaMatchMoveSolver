# MM lens

The 'mmlens' library allows us to apply lens distortion operations;
undistort and redistort.

'mmlens' wraps the Science-D-Visions Lens Distortion Plug-in Kit
(LDPK) maths into mmSolver classes, trying to gain performance over
the LDPK "plug-ins" by avoiding virtual calls on each calculation
trying to improve code inlining. C++ template functions are used to
improve performance with multiple 2D coordinates being processed at
once.

This library is primarily written in C++.

# Structure

mmlens is only defined in the 'cppbind/mmlens' directory.

'cppbind/mmlens' is a Rust crate to define C++ bindings with the help
of the CXX crate.

'cppbind/mmlens' can mix both C++ and Rust.

# Build Process

'cppbind/mmlens' and 'rust/mmlens' are built as part of
'mmsolverlibs'.
