"""
Test multi-camera solving on a single frame.
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

fileName = 'test7.ma'
scenePath = ''
if '__file__' in dir():
    scenePath = os.path.join(os.path.dirname(__file__), fileName)
if os.path.isfile(scenePath) is False:
    maya.cmds.error('Cannot find {0}, cannot run test.'.format(fileName))
    if maya.cmds.about(batch=True):
        maya.cmds.quit(force=True)

# Open File Path
maya.cmds.file(new=True, force=True)
maya.cmds.unloadPlugin('mmSolver')
maya.cmds.file(scenePath, open=True, force=True, typ='mayaAscii', ignoreVersion=True, options='v=0')
maya.cmds.loadPlugin('mmSolver')

# Start the Profiler
profilerOutPath = None
if '__file__' in dir():
    profilerOutPath = os.path.join(os.path.dirname(__file__), 'test7.data')
maya.cmds.profiler(addCategory='mmSolverCategory')
maya.cmds.profiler(bufferSize=250)
maya.cmds.profiler(sampling=True)

# Get cameras
cameras = []
nodes = maya.cmds.ls('|cam_tfm*', type='transform', long=True)
for node in nodes:
    print "camera node:", node
    camTfm = node
    camShape = maya.cmds.listRelatives(node, children=True, type='camera', fullPath=True)[0]
    print 'nodes', (camTfm, camShape)
    cameras.append((camTfm, camShape))

# Get Markers
markers = []
nodes = maya.cmds.ls('|cam_tfm*|marker_tfm*', type='transform', long=True)
for node in nodes:
    markerTfm = node
    camTfm = maya.cmds.listRelatives(node, parent=True, type='transform', fullPath=True)[0]
    camShape = maya.cmds.listRelatives(camTfm, children=True, type='camera', fullPath=True)[0]
    bundleName = markerTfm.rpartition('|')[-1]
    bundleName = bundleName.replace('marker', 'bundle')
    bundleTfm = maya.cmds.ls(bundleName, type='transform')[0]
    markers.append((markerTfm, camShape, bundleTfm))

# Get Attrs
node_attrs = [
    (cameras[0][0] + '.tx', 0),
    (cameras[0][0] + '.ty', 0),
    (cameras[0][0] + '.tz', 0),
    (cameras[0][0] + '.rx', 0),
    (cameras[0][0] + '.ry', 0),
    (cameras[0][0] + '.rz', 0),

    (cameras[1][0] + '.tx', 0),
    (cameras[1][0] + '.ty', 0),
    (cameras[1][0] + '.tz', 0),
    (cameras[1][0] + '.rx', 0),
    (cameras[1][0] + '.ry', 0),
    (cameras[1][0] + '.rz', 0),
]
frames = [1]

# Run solver!
s = time.time()
err = maya.cmds.mmSolver(
camera=cameras,
    marker=markers,
    attr=node_attrs,
    frame=frames,
    solverType=0,
    iterations=1000,
    verbose=True,
)
e = time.time()
print 'total time:', e - s

# Stop the Profiler
maya.cmds.profiler(sampling=False)
if profilerOutPath is not None:
    maya.cmds.profiler(output=profilerOutPath)

# Ensure the values are correct
print 'Error:', err
assert err < 0.001

if maya.cmds.about(batch=True):
    maya.cmds.quit(force=True)
else:
    maya.cmds.lookThru(cameras[0][0])
