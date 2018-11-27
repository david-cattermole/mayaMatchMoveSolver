# Maya MatchMove Solver (MM Solver)

A Solver for matchmove (MM) related tasks.

This tool is currently in development, and is not considered stable
yet. Do not use this in production.

## What Is It?

The aim of this project is to provide an optimising / minimising
non-linear least squares solver to aid in complex matchmoving tasks
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

## Current Features

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
  -

- User Tools
  - Solver GUI
    - Supports creation of mmSolver arguments using a GUI.
  - Load Marker GUI
    - Supports 3DEqualizer *.txt, MatchMover *.rz2 and custom *.uv
      file formats.

## Planned Features

- Solver Plug-in
  - Evaluation of complex character rigs for soft-deformation.
  - Smoothness / Jerkiness error metric to enable the solver reduce
    bumpy solves, especially for multi-frame solves.
  - Sparse curve solving - solving attributes at only specific frames,
    rather than per-frame.
  - Error weighting based on un-realistic Center-Of-Mass trajectory
    velocities.
  
- Python API
  - Returning, storing and parsing output data from a mmSolve
    execution.

- User Tools
  - GUI to select camera and object channels to solve.
    - GUI to link/unlink 2D markers and 3D bundles.
  - 2D markers can either be locators or special objects that look
    like 2D tracks with pattern/search boxes.
    - Dynamic lines to visually connect the display of the 2D and 3D
      points.
  - Tool to project 2D markers onto polygons, creating associated
    static or animated locators.
  - Graphing Solve information including errors per-frame, solve
    time taken, etc.

Note: Due to the complexity of integrating Lens Distortion into Maya
and the MM Solver, Lens Distortion is not handled by this solver. It
is possible to be added later, but for now such a feature is out of
the scope of this project.

## Documentation

The documentation has been split into [Tool
Usage](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/USAGE.md)
and [Script
API](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/API.md).

Additionally some of the low-level design is documented in
[DESIGN.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DESIGN.md).

If you're interested in contributing to the Maya MatchMove Solver
project, please see the conventions and information in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

The documentation is lacking at this time.

## Building and Installation

For building and installation follow the instructions in
[INSTALL.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL.md).

## Known Bugs 

All issues are listed in the [issues
page](https://github.com/david-cattermole/mayaMatchMoveSolver/issues)
on GitHub. If you have found a bug, please submit an issue and we will
try to address it.
