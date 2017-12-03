# Python API

## API Usage

Here is a complete example of how to use the `mmSolver` Python API.

```python
import maya.cmds

import mmSolver.api as mmapi

# Load Plugin
maya.cmds.loadPlugin('mmSolver')

# Camera
cam_tfm = maya.cmds.createNode('transform',
                               name='cam_tfm')
cam_shp = maya.cmds.createNode('camera',
                               name='cam_shp',
                               parent=cam_tfm)
maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

# Bundle
bundle_tfm = maya.cmds.createNode('transform',
                                  name='bundle_tfm')
bundle_shp = maya.cmds.createNode('locator',
                                  name='bundle_shp',
                                  parent=bundle_tfm)
maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
bnd = mmapi.Bundle(bundle_tfm)

# Marker
marker_tfm = maya.cmds.createNode('transform',
                                  name='marker_tfm',
                                  parent=cam_tfm)
marker_shp = maya.cmds.createNode('locator',
                                  name='marker_shp',
                                  parent=marker_tfm)
maya.cmds.setAttr(marker_tfm + '.tx', -2.5)
maya.cmds.setAttr(marker_tfm + '.ty', 1.3)
maya.cmds.setAttr(marker_tfm + '.tz', -10)
mkr = mmapi.Marker(marker_tfm)
mkr.link_to_bundle(bnd)

# Attributes
attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
attr_ty = mmapi.Attribute(bundle_tfm + '.ty')

# Solver
slvr = mmapi.Solver()
slvr.set_max_iterations(1000)
slvr.set_solver_type(mmapi.SOLVER_TYPE_LEVMAR)
slvr.set_verbose(True)
slvr.add_frame(1)
slvr.set_frame_list([1])

# Collection
col = mmapi.Collection()
col.create('mySolveCollection')
col.set_solver(slvr)
col.add_marker(marker_tfm)
col.add_attribute(attr_tx)
col.add_attribute(attr_ty)

# Run solver!
result = col.execute()

# Ensure the values are correct
print 'Solve Error:', result.get_error()

# Take a look at our results.
maya.cmds.lookThru(cam_tfm)
```

## API Classes

![API Classes](https://raw.githubusercontent.com/david-cattermole/mayaMatchMoveSolver/master/design/api/api_classes.png)

| Class        | Description |
| ------------ | ----------- |
| Marker       | 2D point to determine screen-space features |
| Bundle       | 3D point to determine real-location of 2D feature |
| Attribute    | Attribute that will be solved |
| Camera       | Camera to view the world |
| Frame        | Point in time |
| Solver       | Options that describe how the solving algorithm will run |
| Collection   | A set of Markers and Attributes to use during solving |
| SolveResult  | Output of the solver; Details of what happened in a solve |

# Commands

The command named 'mmSolver' is the primary command used to perform a solve. 

## Command Flags

The command can be run in both MEL and Python. 

Python Example:
```python
maya.cmds.mmSolver(
    camera=('camera1', 'cameraShape1'),
    marker=(
        ('camera1', 'marker1', 'bundle1', 1.0),
        ('camera1', 'marker2', 'bundle2', 1.0),
    ),
    attr=(
        ('node.attr', 0),
        ('bundle1.tx', 0), 
        ('bundle1.ty', 0), 
        ('bundle1.tz', 0)
    ),
    iterations=1000
)
```

MEL Example:
```text
mmSolver  
    -camera "camera1" "cameraShape1" 
    -marker "camera1" "marker1" "bundle1" 1.0
    -marker "camera1" "marker2" "bundle2" 1.0
    -attr "node.attr" 0
    -attr "bundle1.tx" 0
    -attr "bundle1.ty" 0
    -attr "bundle1.tz" 0
    -iterations 1000;
```

Here is a table of command flags, as currently specified in the command. 

| Flag              | Type                   | Description | Default Value |
| ----------------- | ---------------------- | ----------- | ------------- |
| -camera (-c)      | string, string         | Camera transform and shape nodes | None |
| -marker (-m)      | string, string, string | Marker, Camera, Bundle | None |
| -attr (-a)        | string, bool           | Node attribute and dynamic | None |
| -solverType (-st)  | int                   | Type of solver to use; 0=levmar 1=splm | 1000 |
| -iterations (-it) | int                    | Maximum number of iterations to perform. | 1000 |
| -verbose (-v)     | bool                   | Prints more information | False |

## Command Return

The `mmSolver` command will return a list of strings.

The list of strings has a specific structure and stores all the data from the core solver engines, so the user can do whatever they wish to. 