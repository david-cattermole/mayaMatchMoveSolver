try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

maya.cmds.file(new=True, force=True)
maya.cmds.unloadPlugin('mmSolver')
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
    startFrame=1,
    endFrame=1,
    verbose=True,
)

# maya.cmds.lookThru(cam_tfm)

maya.cmds.quit(force=True)