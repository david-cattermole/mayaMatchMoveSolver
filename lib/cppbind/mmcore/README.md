# MM Core

The 'mmcore' library contains core data structures and functions that
are independent of external dependencies.

* mmcamera - Camera maths.
* mmcoord - Coordinate systems.
* mmdata - Data structures (for Matrices, points and vectors mostly)
* mmhash - Hashing related functions.
* mmmath - Matrix and Vector Maths.

This library is primarily written in Rust, with bindings for C++ to be
used in Maya.

# Structure

Unlike the other similar sub-libraries 'mmcore' is only defined in
'cppbind/mmcore', the Rust component is not yet needed and has not
been added.

'cppbind/mmcore' is a Rust crate to define C++ bindings with the help
of the CXX crate.

# Build Process

'cppbind/mmcore' are built as part of
'mmsolverlibs'.
