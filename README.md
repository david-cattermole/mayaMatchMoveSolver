# Maya MatchMove Solver (MM Solver)

An error minimisation solver for MatchMove (MM) related tasks
utilising Maya's DG and DAG architecture, allowing solving of
complex constraints driven by 2D-to-3D re-projection deviation.

This tool currently lacks user-friendly tools, but the API and
Plug-in command is nearing stability.

Please do not use this in production, yet.

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
reduce 2D-to-3D reprojection error. Use Maya's DG and DAG nodes to
setup complex constraints and find the best solution to any
MatchMove solve you need.

## Use Cases

- Solving camera or object position / rotation based on 2D to 3D
  positions.
- Using DAG hierarchies to solve objects in specific spaces (for
  example object space).
- Generation of 3D positions from 2D screen-space positions.
- Reconstruction of multi-camera shooting environments
  (photogrammetry).

## Features

- Solver Plug-in
  - Minimising residual error between 2D and 3D positions.
  - Single-frame and multi-frame solving is supported.
  - Dense or Sparse Levenberg-Marquardt solving types for different
    types of solves.
  - Full Undo/redo support.
  - Spinning ("busy") cursor is shown when solving.
  - Ability to cancel out of solve before it's completed (partially
    solved parameters will be lost).
  - Multi-camera solving (photogrammetry).
  - 2D-to-3D error weighting.
  - Marker 'validity' support - frames where markers are occluded.
  
- Python API
  - Object-Oriented Helper classes to create node networks and store
    the data structure inside a Maya scene.
  - Allows storage of multiple 'collections' of solver arguments in
    one Maya scene file.
  - Creates Maya nodes to represent Markers and Bundles.

- User Tools
  - Solver GUI
    - Supports creation of mmSolver arguments using a GUI.
  - Load Marker GUI
    - Supports 3DEqualizer *.txt, MatchMover *.rz2 and custom *.uv
      file formats.

For a list of future features please see
[TODO.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/TODO.md).

## Documentation

- [Tool Documentation](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/TOOLS.md)
- [Python API](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/API.md)
- [Solver Design Concepts](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DESIGN.md)

## Building and Installation

For building and installation follow the instructions in
[INSTALL.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL.md).

## Contributing

If you're interested in contributing to the Maya MatchMove Solver
project, please see the conventions and information in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

## Known Bugs 

All issues are listed in the [issues
page](https://github.com/david-cattermole/mayaMatchMoveSolver/issues)
on GitHub. If you have found a bug, please submit an issue and we will
try to address it.
