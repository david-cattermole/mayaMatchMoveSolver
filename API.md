# API Usage

Here is a simple example of how to use the mmSolver command. There is no functional API, yet.

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
    (bundle_tfm + '.tx', 0),
    (bundle_tfm + '.ty', 0),
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

# Command Flags

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
    -attr "node.attr" 0
    -attr "bundle1.tx" 0
    -attr "bundle1.ty" 0
    -attr "bundle1.tz" 0
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
        ('bundle1.tx', 0), 
        ('bundle1.ty', 0), 
        ('bundle1.tz', 0)
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

