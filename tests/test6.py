"""
Testing a single point nodal camera solve across time.
This script calls the solver multiple times in different ways, the aim is to reduce the slowness while maintaining static value solving.
"""

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds
import os
import time

def approxEqual(x, y, eps=0.0001):
    return x == y or (x < (y+eps) and x > (y-eps))

start = 1
end = 100
mid = start + ((end - start) / 2)

maya.cmds.file(new=True, force=True)
maya.cmds.unloadPlugin('mmSolver')
maya.cmds.loadPlugin('mmSolver')

# Start the Profiler
profilerOutPath = None
if '__file__' in dir():
    profilerOutPath = os.path.join(os.path.dirname(__file__), 'test6.txt')
maya.cmds.profiler(addCategory='mmSolver')
maya.cmds.profiler(bufferSize=250)
maya.cmds.profiler(sampling=True)

cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
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
markers = (
    (marker_tfm, cam_shp, bundle_tfm),
)
# NOTE: All dynamic attributes must have a keyframe before starting to solve.
node_attrs = [
    (cam_tfm + '.rx', 1),
    (cam_tfm + '.ry', 1),
]

framesList = [
    [ (start), (mid), (end) ],
    [ (start), (25), (mid), (75), (end) ],
    [ (start), (12), (25), (37), (mid), (62), (75), (87), (end) ],
]
print 'framesList:', framesList
allFrames = []
for f in range(start, end+1):
    allFrames.append(f)
print 'allFrames:', allFrames

# Run solver!
errs = []
s = time.time()

# Solve primary frames (first, middle and last), and sub-divide.
for frames in framesList:
    err = maya.cmds.mmSolver(
        camera=cameras,
        marker=markers,
        attr=node_attrs,
        iterations=100,
        solverType=1,
        frame=frames,
        verbose=True,
    )
    errs.append(err)

# Solve between primary frames
for frames in framesList:
    for i in range(len(frames)-1):
        betweenFrames = []
        for j in range(frames[i]+1, frames[i+1]):
            betweenFrames.append(j)
        err = maya.cmds.mmSolver(
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            iterations=100,
            solverType=1,
            frame=betweenFrames,
            verbose=True,
        )
        errs.append(err)

# # Global Solve
# err = maya.cmds.mmSolver(
#     camera=cameras,
#     marker=markers,
#     attr=node_attrs,
#     iterations=10,
#     solverType=1,
#     frame=allFrames,
#     verbose=True,
# )
# errs.append(err)

e = time.time()
print 'total time:', e - s

# Stop the Profiler
maya.cmds.profiler(sampling=False)
if profilerOutPath is not None:
    maya.cmds.profiler(output=profilerOutPath)

# Ensure the values are correct
print 'Errors...'
for i, err in enumerate(errs):
    print i, '=', err
for i, err in enumerate(errs):
    assert approxEqual(err, 0.0, eps=0.001)

if maya.cmds.about(batch=True):
    maya.cmds.quit(force=True)
else:
    maya.cmds.lookThru(cam_tfm)
