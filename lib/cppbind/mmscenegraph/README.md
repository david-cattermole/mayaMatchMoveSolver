# MM Scene Graph

MatchMove Scene Graph (MM Scene Graph or 'mmscenegraph') is for
representing a 3D Scene Graph for MatchMove solving.

Solving MatchMove cameras and objects for Visual Effects (VFX) may
require the use of a 3D transform a hierarchy, known as a DAG
(Directed Acyclic Graph). The MM Scene Graph is designed to model the
Scene Graph for MatchMove tasks and provide efficent functions for
evaluation.

This library is primarily written in Rust, with bindings for C++ to be
used in Maya.

# Structure

mmscenegraph is split into 2 different directories;
'rust/mmscenegraph' and 'cppbind/mmscenegraph'.

'rust/mmscenegraph' is the core library written in Rust without the
requirements of C++.

'cppbind/mmscenegraph' is a Rust project to create C++ bindings with
the help of the CXX crate.

# Build Process

Rust does not (natively) use CMake; Rust uses the 'Cargo' package
manager tool that comes with Rust.

However mmSolver uses CMake as it's main build system, therefore we
must ensure Cargo is run for the Rust code, and CMake for the C++.

This is handled by the build scripts for Windows (\*.bat), Linux or
MacOS (\*.bash).
