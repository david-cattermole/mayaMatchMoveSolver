# MM image

The 'mmimage' library can read and write EXR images, as well as read
EXR headers and custom attributes. This library can be used to query
EXRs of useful metadata for matchmove purposes (such as focal length,
or focus distance information).

This library is primarily written in Rust, with bindings for C++ to be
used in Maya.

# Structure

mmimage is split into 2 different directories; 'rust/mmimage' and 'cppbind/mmimage'.

'rust/mmimage' is the core library written in Rust without the
requirements of C++. The rust code uses the 'exrs' crate
(https://github.com/johannesvollmer/exrs) to read and write OpenEXR
files

'cppbind/mmimage' is a Rust crate to define C++ bindings with the help
of the CXX crate.

# Build Process

'cppbind/mmimage' and 'rust/mmimage' are built as part of
'mmsolverlibs'.
