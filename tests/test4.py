"""
Testing a single point nodal camera solve across time.
"""

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds
import time

start = 1
end = 100

maya.cmds.file(new=True, force=True)
maya.cmds.unloadPlugin('mmSolver')
maya.cmds.loadPlugin('mmSolver')

cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
# maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=start, value=0.0)
# maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=0.0)
maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=start, value=-2.0)
maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=end, value=2.0)
maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=-2.5)
maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=2.5)

bundle_tfm = maya.cmds.createNode('transform', name='bundle_tfm')
bundle_shp = maya.cmds.createNode('locator', name='bundle_shp', parent=bundle_tfm)
maya.cmds.setAttr(bundle_tfm + '.tx', -2.5)
maya.cmds.setAttr(bundle_tfm + '.ty', 2.4)
maya.cmds.setAttr(bundle_tfm + '.tz', -15.0)

marker_tfm = maya.cmds.createNode('transform', name='marker_tfm', parent=cam_tfm)
marker_shp = maya.cmds.createNode('locator', name='marker_shp', parent=marker_tfm)
maya.cmds.setAttr(marker_tfm + '.tz', -10)
maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=start, value=-2.5)
maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=end, value=3.0)
maya.cmds.setKeyframe(marker_tfm, attribute='translateY', time=start, value=1.5)
maya.cmds.setKeyframe(marker_tfm, attribute='translateY', time=end, value=1.3)

cameras = (
    (cam_tfm, cam_shp),
)
weight = 1.0
markers = (
    (marker_tfm, cam_shp, bundle_tfm, weight),
)
# NOTE: All dynamic attributes must have a keyframe before starting to solve.
node_attrs = [
    (cam_tfm + '.rx', 1),
    (cam_tfm + '.ry', 1),
]

# Turn off the viewport.
panels = []
if not maya.cmds.about(batch=True):
    panels = maya.cmds.getPanel(type='modelPanel')
    for panel in panels:
        maya.cmds.control(panel, edit=True, manage=False)

# Run solver!
s = time.time()
err = maya.cmds.mmSolver(
    camera=cameras,
    marker=markers,
    attr=node_attrs,
    iterations=10000,
    startFrame=start,
    endFrame=end,
    verbose=True,
)

# Turn viewports back on.
if not maya.cmds.about(batch=True):
    for panel in panels:
        maya.cmds.control(panel, edit=True, manage=True)

e = time.time()
print 'total time:', e - s

# Ensure the values are correct
assert err < 0.001

if maya.cmds.about(batch=True):
    maya.cmds.quit(force=True)
else:
    maya.cmds.lookThru(cam_tfm)
