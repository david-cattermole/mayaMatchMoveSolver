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

## Usage

Here is a simple example of how to use the mmSolver command.

```python
import maya.cmds

# Load Plugin
maya.cmds.loadPlugin('mmSolver')

cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

bundle_tfm = maya.cmds.createNode('transform', name='bundle_tfm')
bundle_shp = maya.cmds.createNode('locator', name='bundle_shp', parent=bundle_tfm)
maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)

marker_tfm = maya.cmds.createNode('transform', name='marker_tfm', parent=cam_tfm)
marker_shp = maya.cmds.createNode('locator', name='marker_shp', parent=marker_tfm)
maya.cmds.setAttr(marker_tfm + '.tx', -2.5)
maya.cmds.setAttr(marker_tfm + '.ty', 1.3)
maya.cmds.setAttr(marker_tfm + '.tz', -10)

cameras = (
    (cam_tfm, cam_shp),
)
weight = 1.0
markers = (
    (marker_tfm, cam_shp, bundle_tfm, weight),
)
node_attrs = [
    (bundle_tfm + '.tx', 1),
    (bundle_tfm + '.ty', 1),
]

# Run solver!
maya.cmds.mmSolver(
    camera=cameras,
    marker=markers,
    attr=node_attrs,
    iterations=1000,
    verbose=True,
)

# Take a look of our results.
maya.cmds.lookThru(cam_tfm)
```

_See 'tests/test*.py' files for more examples_

## Command Flags

The command syntax is:
```text
mmSolver [flags]
```

The command can be run in both MEL and Python. 

MEL Example:
```text
mmSolver  
    -camera "camera1" "cameraShape1" 
    -marker "camera1" "marker1" "bundle1" 1.0
    -marker "camera1" "marker2" "bundle2" 1.0
    -attr "node.attr" 1
    -attr "bundle1.tx" 1
    -attr "bundle1.ty" 1
    -attr "bundle1.tz" 1
    -iterations 1000;
```

Python Example:
```python
maya.cmds.mmSolver(
    camera=('camera1', 'cameraShape1'),
    marker=(
        ('camera1', 'marker1', 'bundle1', 1.0),
        ('camera1', 'marker2', 'bundle2', 1.0),
    ),
    attr=(
        ('bundle1.tx', 1), 
        ('bundle1.ty', 1), 
        ('bundle1.tz', 1)
    ),
    iterations=1000
)
```

Here is a table of command flags, as currently specified in the command. 

| Flag              | Type                   | Description | Default Value |
| ----------------- | ---------------------- | ----------- | ------------- |
| -camera (-c)      | string, string         | Camera transform and shape nodes | None |
| -marker (-m)      | string, string, string, double | Marker, Camera, Bundle and error weighting | None |
| -attr (-a)        | string, bool           | Node attribute and dynamic | None |
| -iterations (-it) | int                    | Number of iterations to perform. | 1000 |
| -verbose (-v)     | bool                   | Prints more information | False |

## Build and Install

For building and installation follow the instructions in [INSTALL.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL.md).

## Known Bugs 

_To be written_
