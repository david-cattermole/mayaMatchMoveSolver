# Maya MatchMove Solver (MM Solver)

An error minimisation solver for MatchMove (MM) related tasks
utilising Maya's DG and DAG architecture, allowing solving of
complex constraints driven by 2D-to-3D re-projection deviation.

## What Is It?

The aim of this project is to provide an minimising non-linear
least squares solver to aid in complex matchmoving tasks
inside Autodesk Maya. This tool is not intended as a
one-click-solution; this tool is for advanced users.

The solver performs [Bundle Adjustment
(BA)](https://en.wikipedia.org/wiki/Bundle_adjustment), solving for 3D
positions (Bundles) of 2D features (Markers) with arbitrary solving
attributes.

Using arbitrary solving attributes makes the solver extremely
flexible; any floating-point attribute in Maya can be adjusted to
reduce 2D-to-3D re-projection error. Use Maya's DG and DAG nodes to
setup complex constraints and find the best solution to any
MatchMove solve you need.

## Use Cases

- Solving camera or object transforms based on 2D to 3D
  positions.
- Using DAG hierarchies to solve objects in specific spaces (for
  example object or camera space).
- Generation of 3D positions from 2D screen-space positions.
- Reconstruction of multi-camera shooting environments
  (photogrammetry).

## Features

- Solver User Interface
  - Uses Plug-In to set up and run solver.
  - Displays relationships of Cameras, (2D) Markers and (3D) Bundles
    nodes.
  - Lists Maya Attributes used for solving.
  - Lists individual Solver 'steps' depicting how the Solver will
    execute.
  - Supports creation of mmSolver arguments using a GUI.
  - Single-Frame solve override

- User Tools
  - Load 2D Tracks (Markers) from Third-Party software
    - Supports 3DEqualizer *.txt, MatchMover *.rz2 and custom *.uv
      file formats.
  - Convert from 3D Transform Nodes to 2D Markers.
  - Center Viewport on 3D Transform Node
  - Maya Shelf for quick access to tools
  - Selection tools
    - Toggle Selection between 2D and 3D nodes
    - Select connected 2D and 3D nodes
  - Control 2D and 3D node relationships; linking and unlinking nodes.
  - And more...

- Solver Plug-in
  - Maya DG and DAG evaluation support.
  - Options to tune the required solver iterations and error
    thresholds.
  - Minimising residual error between 2D and 3D positions.
  - Solving translate, rotate, scale and any custom floating point
    values, including camera focal length.
  - Static and animated attribute solving.
  - Per-frame, single-frame and multi-frame solving is supported.
  - Multi-camera solving (photogrammetry).
  - Marker weights support (force a point to solve with higher weight
    than others).
  - Marker 'validity' support - frames where markers are occluded.
  - Full undo/redo support.

- Python API
  - Object-Oriented helper classes to create node networks and store
    the data structure inside a Maya scene.
  - Allows storage of multiple 'collections' of solver arguments in
    one Maya scene file - all data is stored in the Maya scene file.
  - Creates Maya nodes to represent Markers and Bundles.

For a list of future features please see
[TODO.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/TODO.md).

## Documentation

For all written tutorials, documentation of Tools, Python API
and Maya Plug-In features, take a look at the
[Documentation Home Page](https://david-cattermole.github.io/mayaMatchMoveSolver/).

A copy of the documentation is also installed with *Maya MatchMove
Solver*, you can find it by pressing the *help* button in the Solver
UI, or in the module install directory, for example this path:

(On Windows)
```
C:/Users/<user name>/My Documents/maya/2017/modules/mayaMatchMoveSolver-0.1.0-maya2017-win64/docs/html/index.html
```

## Community

There is a Google Group mailing list, named
 [maya-matchmove-solver](https://groups.google.com/forum/#!forum/maya-matchmove-solver).

The mailing list is a place for user questions and discussions, and
will have release announcements of new versions.

If you find a bug, please report it on the GitHub project
[issues page](https://github.com/david-cattermole/mayaMatchMoveSolver/issues).

## Installation

If you have a 'mayaMatchMoveSolver' archive package and need to
install it, follow the instructions in
[INSTALL.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL.md).

## Building

To build (compile) the plug-in follow the steps in
[BUILD.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD.md).

## License

*Maya MatchMove Solver* (mmSolver) is licensed under the
[Lesser GNU Public License v3.0](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/LICENSE)
or *LGPL-3.0* for short.
This means the project is Free Open Source Software, and will always
stay Free Open Source Software:
[TL;DR](https://www.tldrlegal.com/l/lgpl-3.0).

Please read the *LICENSE* (text) file for details.

## Contributing

If you're interested in contributing to the Maya MatchMove Solver
project, please see the conventions and information in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

## Bugs or Issues?

All issues are listed in the
[issues page](https://github.com/david-cattermole/mayaMatchMoveSolver/issues)
on the project page. If you have found a bug, please submit an issue and we will
try to address it as soon as possible.
