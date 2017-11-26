# Maya MatchMove Solver (mmSolver)

A generic solver for matchmove related tasks using a Non-Linear Least Squares algorithm.

This tool is currently in development and is considered ALPHA software, do not use this in production.

The aim of this project is to provide a optimising/minimising solver to aid in complex matchmoving tasks inside Autodesk Maya. This tool is not intended as a one-click-solution; this tool is for advanced users.

## Use Cases

- Solving camera or object position / rotation based on 2D to 3D positions.
- Using DAG hierarchies to solve objects in specific spaces (for example object space).
- Generation of approximate 3D positions from 2D screen-space positions.
- Reconstruction of multi-camera shooting environments (photogrammetry).

## Current Features

- Solver Plug-in
  - Minimising residual error between 2D and 3D positions.
  - Single-frame and multi-frame solving is supported.
  - Full Undo/redo support.
  - Spinning ("busy") cursor is shown when solving.
  - Ability to cancel out of solve before it's completed (partially solved parameters will be lost).
  - Small number of build dependencies.
- User Tools
  - None

## Planned Features

- Solver Plug-in
  - Multi-camera solving (photogrammetry) - only a single camera is currently supported.
  - 2D-to-3D error weighting.
  - Evaluation of complex character rigs for soft-deformation. 
  - Optimised multi-frame solving - research into faster (smarter) multi-frame solving.
  - Marker 'validity' support - frames where markers are occluded.
  - Smoothness / Jerkiness error metric to enable the solver reduce bumpy solves.
  - Sparse curve solving - solving attributes at only specific frames, rather than per-frame.

- User Tools
  - GUI to select camera and object channels to solve.
    - GUI to associate/disassociate 2D tracks and 3D locators.
  - 2D tracks can either be locators or special objects that look like 2D tracks with pattern/search boxes.
    - Dynamic NURBS curves to connect the display of the 2D and 3D points.
  - Tool to project 2D tracks onto polygons, creating associated static or animated locators.
  - Tool to import 2D tracks to Maya, reading 3DE or pfTrack, etc. 2D tracking files.

## Documentation

The documentation has been split into [Tool Usage](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/USAGE.md) and [Script API](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/API.md).

Additionally some of the low-level design is documented in [DESIGN.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DESIGN.md).

If you're interested in contributing to the Maya MatchMove Solver project, please see the conventions and information in [DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

The documentation is lacking at this time.

## Building and Installation

For building and installation follow the instructions in [INSTALL.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL.md).

## Known Bugs 

All issues are listed in the [issues page](https://github.com/david-cattermole/mayaMatchMoveSolver/issues) on GitHub. If you have found a bug, please submit an issue and we will try to address it.
