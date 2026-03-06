Other Commands
==============

This page documents utility commands that do not fit into the solve or
image categories. They cover reprojection, animation-curve analysis and
filtering, geometry fitting, colour-space queries, and memory
statistics.

``mmReprojection`` Command
++++++++++++++++++++++++++

``mmReprojection`` reprojects 3D world-space points (or Maya transform
nodes) into 2D screen-space coordinates for a given camera at one or
more times. It is a key utility for scripting deviation calculations
and for checking whether a transform lies in front of or behind the
camera.

Flags
-----

========================== ===================== ======================= ====================================================================================================================== ==============
Command Flag               Command Flag (short)  Type                    Description                                                                                                            Default Value
========================== ===================== ======================= ====================================================================================================================== ==============
-worldPoint                -wp                   double, double, double  A world-space XYZ point to reproject instead of supplying a node.                                                      None
-camera                    -c                    string, string          Camera transform and shape nodes.                                                                                      None
-time                      -t                    double (multi-use)      Frame time(s) at which to evaluate. Can be given multiple times.                                                       None
-imageResolution           -ir                   double, double          Image width and height in pixels, used for pixel-coordinate output.                                                    2048, 2048
-asCameraPoint             -cpt                  bool                    Return position in camera space (X, Y, Z).                                                                             False
-asWorldPoint              -wpt                  bool                    Return position in world space (X, Y, Z).                                                                              False
-asCoordinate              -cd                   bool                    Return as film-back coordinate (0–1 range on each axis).                                                               False
-asNormalizedCoordinate    -ncd                  bool                    Return as normalised coordinate (−0.5 to 0.5 on the short axis).                                                       False
-asMarkerCoordinate        -mcd                  bool                    Return as mmSolver marker coordinate (same range as normalised, used by the solver).                                   False
-asPixelCoordinate         -pcd                  bool                    Return as pixel coordinate based on ``-imageResolution``.                                                              False
-withCameraDirectionRatio  -wcd                  bool                    Append a camera-direction ratio value; negative means the point is behind the camera.                                  False
-distortMode               -dsm                  unsigned int            Apply lens distortion: 0 = none, 1 = distort, 2 = undistort. Requires an ``outLens`` connection on the camera shape.   0 (none)
========================== ===================== ======================= ====================================================================================================================== ==============

Return
------

Returns a flat list of doubles. For each input point and each
requested time the values for every requested output type are
appended in order. For example, if ``-asCoordinate`` is requested
for two frames the result is ``[u0, v0, u1, v1]``.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   # Reproject a bundle node at frames 1, 12 and 24 as marker coordinates.
   result = maya.cmds.mmReprojection(
       'myBundle',
       camera=('camera1', 'cameraShape1'),
       time=(1, 12, 24),
       asMarkerCoordinate=True,
   )
   # result is [u1, v1, u12, v12, u24, v24]

   # Reproject a raw world-space point, returning pixel coordinates.
   result = maya.cmds.mmReprojection(
       worldPoint=(10.0, 5.0, -3.0),
       camera=('camera1', 'cameraShape1'),
       time=(1,),
       imageResolution=(1920, 1080),
       asPixelCoordinate=True,
   )

MEL Example:

.. code:: text

   mmReprojection myBundle
       -camera "camera1" "cameraShape1"
       -time 1
       -time 12
       -asMarkerCoordinate true;


``mmAnimCurveStatistics`` Command
++++++++++++++++++++++++++++++++++

``mmAnimCurveStatistics`` computes statistical measures over the
keyframe values of one or more animation curves within an optional
frame range. It can also operate on raw lists of X/Y values instead
of curve nodes.

Flags
-----

======================================= ========================= ======== ================================================================== =============
Command Flag                            Command Flag (short)      Type     Description                                                        Default Value
======================================= ========================= ======== ================================================================== =============
-startFrame                             -sf                       unsigned First frame of the evaluation range.                               (all keys)
-endFrame                               -ef                       unsigned Last frame of the evaluation range.                                (all keys)
-mean                                   -m                        bool     Calculate and return the mean (average) value.                     False
-median                                 -md                       bool     Calculate and return the median value.                             False
-populationVariance                     -pvr                      bool     Calculate and return the population variance.                      False
-populationStandardDeviation            -psd                      bool     Calculate and return the population standard deviation.            False
-signalToNoiseRatio                     -snr                      bool     Calculate and return the signal-to-noise ratio.                    False
-xValues                                -xv                       double   (multi-use) Provide raw X (time) values instead of a curve node.   None
-yValues                                -yv                       double   (multi-use) Provide raw Y (value) values instead of a curve node.  None
======================================= ========================= ======== ================================================================== =============

Return
------

Returns a flat list of doubles. Each requested statistic contributes
two values to the list: a type identifier followed by the computed
value. The type identifiers are: 0 = mean, 1 = median, 2 = population
variance, 3 = population standard deviation, 4 = signal-to-noise
ratio.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   # Compute mean and standard deviation of an animation curve.
   result = maya.cmds.mmAnimCurveStatistics(
       'myAnimCurve',
       startFrame=1,
       endFrame=100,
       mean=True,
       populationStandardDeviation=True,
   )
   # result: [0.0, <mean_value>, 3.0, <std_dev_value>]

MEL Example:

.. code:: text

   mmAnimCurveStatistics myAnimCurve
       -startFrame 1
       -endFrame 100
       -mean true
       -populationStandardDeviation true;


``mmAnimCurveDiffStatistics`` Command
++++++++++++++++++++++++++++++++++++++

``mmAnimCurveDiffStatistics`` computes difference-based statistical
measures between two animation curves (or two sets of raw values)
over an optional frame range. It is useful for quantifying how closely
a solved curve matches a reference.

Flags
-----

=============================== ===================== ======== ============================================================= =============
Command Flag                    Command Flag (short)  Type     Description                                                   Default Value
=============================== ===================== ======== ============================================================= =============
-startFrame                     -sf                   unsigned First frame of the evaluation range.                          (all keys)
-endFrame                       -ef                   unsigned Last frame of the evaluation range.                           (all keys)
-meanAbsoluteDifference         -mad                  bool     Return the mean absolute difference between the two curves.   False
-rootMeanSquareDifference       -rsd                  bool     Return the root-mean-square difference.                       False
-meanDifference                 -mnf                  bool     Return the mean signed difference.                            False
-medianDifference               -mdf                  bool     Return the median signed difference.                          False
-populationVariance             -pvr                  bool     Return the population variance of the differences.            False
-populationStandardDeviation    -psd                  bool     Return the population standard deviation of the differences.  False
-peakToPeak                     -ptp                  bool     Return the peak-to-peak (max minus min) difference.           False
-signalToNoiseRatio             -snr                  bool     Return the signal-to-noise ratio.                             False
-meanAbsoluteError              -mae                  bool     Return the mean absolute error.                               False
-rootMeanSquareError            -rme                  bool     Return the root-mean-square error.                            False
-normalizedRootMeanSquareError  -nse                  bool     Return the normalised root-mean-square error.                 False
-rSquared                       -r2                   bool     Return the R² (coefficient of determination).                 False
-xValues                        -xv                   double   (multi-use) Raw X values shared by both curves.               None
-yValuesA                       -yva                  double   (multi-use) Raw Y values for curve A.                         None
-yValuesB                       -yvb                  double   (multi-use) Raw Y values for curve B.                         None
=============================== ===================== ======== ============================================================= =============

Return
------

Returns a flat list of doubles. Each requested statistic contributes a
type-identifier / value pair. Select curves are passed as the first
two objects in the selection list; alternatively, supply raw values
via ``-xValues``, ``-yValuesA``, and ``-yValuesB``.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   result = maya.cmds.mmAnimCurveDiffStatistics(
       'curveA', 'curveB',
       startFrame=1,
       endFrame=100,
       meanAbsoluteDifference=True,
       rootMeanSquareError=True,
   )

MEL Example:

.. code:: text

   mmAnimCurveDiffStatistics curveA curveB
       -startFrame 1 -endFrame 100
       -meanAbsoluteDifference true
       -rootMeanSquareError true;


``mmAnimCurveFilterPops`` Command
++++++++++++++++++++++++++++++++++

``mmAnimCurveFilterPops`` detects and removes single-frame *pops*
(outlier keyframe values) from an animation curve. The command is
undoable. When ``-returnResultOnly`` is set the curve is not modified
and the detected pop frames are returned instead.

Flags
-----

====================== ====================== ======== ========================================================================= =============
Command Flag           Command Flag (short)   Type     Description                                                               Default Value
====================== ====================== ======== ========================================================================== =============
-startFrame            -sf                    unsigned First frame of the evaluation range.                                       (all keys)
-endFrame              -ef                    unsigned Last frame of the evaluation range.                                        (all keys)
-threshold             -th                    double   Deviation threshold above which a keyframe is considered a pop.            1.0
-returnResultOnly      -rro                   bool     When true, return the affected frame numbers without modifying the curve.  False
====================== ====================== ======== ========================================================================== =============

Return
------

When ``-returnResultOnly`` is ``True``, returns a list of frame
numbers where pops were detected. Otherwise returns an empty result
after modifying the curve in-place.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   # Remove pops from a curve (undoable).
   maya.cmds.mmAnimCurveFilterPops('myAnimCurve', threshold=2.0)

   # Detect pops without modifying the curve.
   pop_frames = maya.cmds.mmAnimCurveFilterPops(
       'myAnimCurve',
       threshold=1.5,
       returnResultOnly=True,
   )

MEL Example:

.. code:: text

   mmAnimCurveFilterPops myAnimCurve -threshold 2.0;

   // Detect only
   mmAnimCurveFilterPops myAnimCurve
       -threshold 1.5
       -returnResultOnly true;


``mmAnimCurveSimplify`` Command
++++++++++++++++++++++++++++++++

``mmAnimCurveSimplify`` reduces an animation curve to a specified
number of control points using a chosen point distribution and
interpolation method. The command is undoable. When
``-returnResultOnly`` is set the curve is not modified and the
simplified key times and values are returned instead.

Flags
-----

====================== ====================== ======== ===================================================================================== =============
Command Flag           Command Flag (short)   Type     Description                                                                           Default Value
====================== ====================== ======== ===================================================================================== =============
-startFrame            -sf                    unsigned First frame of the evaluation range.                                                  (all keys)
-endFrame              -ef                    unsigned Last frame of the evaluation range.                                                   (all keys)
-controlPointCount     -cpc                   unsigned Number of control points (keyframes) in the simplified curve.                         0
-distribution          -dtr                   string   Distribution of control points: ``"uniform"`` or ``"auto_keypoints"``.                (none)
-interpolation         -int                   string   Interpolation method: ``"linear"``, ``"quadratic_nubs"``, or ``"cubic_nubs"``.        (none)
-returnResultOnly      -rro                   bool     When true, return the simplified key times and values without modifying the curve.    False
====================== ====================== ======== ===================================================================================== =============

Return
------

When ``-returnResultOnly`` is ``True``, returns a flat list of
alternating time/value pairs for the simplified keys. Otherwise
modifies the curve in-place and returns nothing.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   # Simplify a curve to 5 uniformly-distributed linear keys.
   maya.cmds.mmAnimCurveSimplify(
       'myAnimCurve',
       startFrame=1,
       endFrame=100,
       controlPointCount=5,
       distribution='uniform',
       interpolation='linear',
   )

   # Return simplified values without modifying the curve.
   result = maya.cmds.mmAnimCurveSimplify(
       'myAnimCurve',
       controlPointCount=5,
       distribution='uniform',
       interpolation='cubic_nubs',
       returnResultOnly=True,
   )

MEL Example:

.. code:: text

   mmAnimCurveSimplify myAnimCurve
       -startFrame 1 -endFrame 100
       -controlPointCount 5
       -distribution "uniform"
       -interpolation "linear";


``mmBestFitPlane`` Command
++++++++++++++++++++++++++

``mmBestFitPlane`` fits a plane to a set of 3D points using a
least-squares method and returns the plane's position and orientation.
It is useful for establishing a ground plane or reference surface from
tracked 3D bundles.

Flags
-----

================= ====================== ======== ===================================================================================================================== ============================
Command Flag      Command Flag (short)   Type     Description                                                                                                           Default Value
================= ====================== ======== ===================================================================================================================== ============================
-pointComponent   -pc                    double   (multi-use) Flat list of XYZ components of the input points (i.e. X0, Y0, Z0, X1, Y1, Z1, …).                         None
-withScale        -wsc                   bool     Include a scale value in the output when using ``position_direction_and_scale`` output mode.                          False
-outputValuesAs   -ova                   string   Format of the return value: ``"position_and_direction"``, ``"position_direction_and_scale"``, or ``"matrix_4x4"``.    ``"position_and_direction"``
-outputRmsError   -ore                   bool     Append the RMS fit error to the output.                                                                               True
================= ====================== ======== ===================================================================================================================== ============================

Return
------

Returns a flat list of doubles. The content depends on
``-outputValuesAs``:

- ``"position_and_direction"``: ``[px, py, pz, nx, ny, nz]`` plus
  optional RMS error.
- ``"position_direction_and_scale"``: as above with a scale value
  appended before the optional RMS error.
- ``"matrix_4x4"``: 16 matrix values in row-major order plus optional
  RMS error.

Returns ``None`` if the plane could not be fit (e.g. fewer than 3
non-collinear points).

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   nodes = maya.cmds.ls(sl=True, long=True) or []
   points_flat = []
   for node in nodes:
       pos = maya.cmds.xform(node, query=True, worldSpace=True, translation=True)
       points_flat.extend(pos)

   result = maya.cmds.mmBestFitPlane(
       pointComponent=points_flat,
       outputValuesAs='matrix_4x4',
       outputRmsError=True,
   )
   if result and len(result) == 17:
       maya.cmds.xform('pPlane1', worldSpace=True, matrix=result[:16])

MEL Example:

.. code:: text

   mmBestFitPlane
       -pointComponent 0.0 0.0 0.0
       -pointComponent 1.0 0.0 0.0
       -pointComponent 0.5 1.0 0.0
       -outputValuesAs "position_and_direction"
       -outputRmsError true;


``mmMarkerHomography`` Command
++++++++++++++++++++++++++++++

``mmMarkerHomography`` computes a 2D homography matrix from
corresponding marker positions in two views (two different frames or
two different cameras). It is used to warp one frame's image into
alignment with another for planar surfaces.

Flags
-----

============== ====================== =================== ====================================================================================================== =============
Command Flag   Command Flag (short)   Type                Description                                                                                            Default Value
============== ====================== =================== ====================================================================================================== =============
-cameraA       -ca                    string              Camera transform node for view A.                                                                      None
-cameraB       -cb                    string              Camera transform node for view B.                                                                      None
-frameA        -fa                    unsigned int        Frame number for view A.                                                                               1
-frameB        -fb                    unsigned int        Frame number for view B.                                                                               1
-markerPair    -mp                    string, string      Pair of marker node names (markerA, markerB). Can be given multiple times (minimum 4 pairs required).  None
============== ====================== =================== ====================================================================================================== =============

Return
------

Returns a flat list of 9 doubles representing the 3×3 homography
matrix in row-major order, or ``None`` if the computation fails
(e.g. insufficient or degenerate correspondences).

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   result = maya.cmds.mmMarkerHomography(
       cameraA='cameraA',
       cameraB='cameraB',
       frameA=21,
       frameB=29,
       markerPair=[
           ('markerA1', 'markerB1'),
           ('markerA2', 'markerB2'),
           ('markerA3', 'markerB3'),
           ('markerA4', 'markerB4'),
       ],
   )

MEL Example:

.. code:: text

   mmMarkerHomography
       -cameraA "cameraA"
       -cameraB "cameraB"
       -frameA 21
       -frameB 29
       -markerPair "markerA1" "markerB1"
       -markerPair "markerA2" "markerB2"
       -markerPair "markerA3" "markerB3"
       -markerPair "markerA4" "markerB4";


``mmColorIO`` Command
+++++++++++++++++++++

``mmColorIO`` exposes OpenColorIO (OCIO) colour-space information from
within Maya. It can query the active OCIO configuration, list available
colour spaces, guess a colour space from a file path, and look up
standard OCIO role names.

Flags
-----

=========================== ===================== ======== ===================================================================================================== =============
Command Flag                Command Flag (short)  Type     Description                                                                                           Default Value
=========================== ===================== ======== ===================================================================================================== =============
-colorSpaceExists           -ce                   bool     Return ``True`` if the named colour space (given as a string argument) exists in the active config.   False
-configDescription          -de                   bool     Return the description string of the active OCIO config.                                              False
-configName                 -nm                   bool     Return the name of the active OCIO config.                                                            False
-configSearchPath           -sp                   bool     Return the search paths defined in the active OCIO config.                                            False
-configWorkingDirectory     -wd                   bool     Return the working directory of the active OCIO config.                                               False
-guessColorSpaceFromFile    -gc                   bool     Guess the colour space for the file path supplied as a string argument.                               False
-listColorSpacesActive      -la                   bool     Return the list of active colour space names.                                                         False
-listColorSpacesAll         -lc                   bool     Return the list of all colour space names (active and inactive).                                      False
-listColorSpacesInactive    -li                   bool     Return the list of inactive colour space names.                                                       False
-roleColorPicking           -rp                   bool     Return the colour space name assigned to the ``color_picking`` role.                                  False
-roleColorTiming            -rt                   bool     Return the colour space name assigned to the ``color_timing`` role.                                   False
-roleCompositingLog         -rg                   bool     Return the colour space name assigned to the ``compositing_log`` role.                                False
-roleData                   -ra                   bool     Return the colour space name assigned to the ``data`` role.                                           False
-roleDefault                -rd                   bool     Return the colour space name assigned to the ``default`` role.                                        False
-roleMattePaint             -ri                   bool     Return the colour space name assigned to the ``matte_paint`` role.                                    False
-roleReference              -rr                   bool     Return the colour space name assigned to the ``reference`` role.                                      False
-roleRendering              -rn                   bool     Return the colour space name assigned to the ``rendering`` role.                                      False
-roleSceneLinear            -rl                   bool     Return the colour space name assigned to the ``scene_linear`` role.                                   False
-roleTexturePaint           -rx                   bool     Return the colour space name assigned to the ``texture_paint`` role.                                  False
=========================== ===================== ======== ===================================================================================================== =============

Return
------

Depending on the flags used, returns a string, a string array, or a
boolean. Multiple flags may be combined in a single call; results are
concatenated in the order the flags appear.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   # List all colour spaces in the active config.
   spaces = maya.cmds.mmColorIO(listColorSpacesAll=True)

   # Get the scene-linear role name.
   linear_cs = maya.cmds.mmColorIO(roleSceneLinear=True)

   # Check whether a colour space exists.
   exists = maya.cmds.mmColorIO('ACEScg', colorSpaceExists=True)

   # Guess the colour space of a file.
   cs = maya.cmds.mmColorIO(
       '/path/to/image.exr',
       guessColorSpaceFromFile=True,
   )

MEL Example:

.. code:: text

   mmColorIO -listColorSpacesAll true;
   mmColorIO -roleSceneLinear true;
   mmColorIO -configName true;


``mmMemoryGPU`` Command
++++++++++++++++++++++++

``mmMemoryGPU`` queries GPU (VRAM) memory statistics reported by
Maya's Viewport 2.0 renderer. It operates in query mode only.

Flags
-----

=============== ====================== ======== =================================== =============
Command Flag    Command Flag (short)   Type     Description                         Default Value
=============== ====================== ======== =================================== =============
-total          -tot                   (none)   Query total GPU memory.             -
-free           -fre                   (none)   Query free (available) GPU memory.  -
-used           -usd                   (none)   Query used GPU memory.              -
-asKiloBytes    -kb                    (none)   Return the result in kilobytes.     -
-asMegaBytes    -mb                    (none)   Return the result in megabytes.     -
-asGigaBytes    -gb                    (none)   Return the result in gigabytes.     -
=============== ====================== ======== =================================== =============

.. note::

   The command requires ``-query`` mode. Exactly one of ``-total``,
   ``-free``, or ``-used`` must be given, combined with exactly one
   unit flag.

Return
------

Returns a single double value representing the requested memory amount
in the chosen unit.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   total_mb  = maya.cmds.mmMemoryGPU(query=True, total=True,  asMegaBytes=True)
   free_mb   = maya.cmds.mmMemoryGPU(query=True, free=True,   asMegaBytes=True)
   used_mb   = maya.cmds.mmMemoryGPU(query=True, used=True,   asMegaBytes=True)

MEL Example:

.. code:: text

   mmMemoryGPU -query -total -asMegaBytes;
   mmMemoryGPU -query -free  -asMegaBytes;
   mmMemoryGPU -query -used  -asMegaBytes;


``mmMemorySystem`` Command
+++++++++++++++++++++++++++

``mmMemorySystem`` queries system (RAM) memory statistics, including
total, free, and used physical memory as well as the memory used by
the current Maya process. It operates in query mode only.

Flags
-----

=========================== ===================== ======== ================================================= =============
Command Flag                Command Flag (short)  Type     Description                                       Default Value
=========================== ===================== ======== ================================================= =============
-systemPhysicalMemoryTotal  -tot                  (none)   Query total physical (RAM) memory on the system.  -
-systemPhysicalMemoryFree   -fre                  (none)   Query free physical memory on the system.         -
-systemPhysicalMemoryUsed   -usd                  (none)   Query used physical memory on the system.         -
-processMemoryUsed          -pud                  (none)   Query memory used by the current Maya process.    -
-asKiloBytes                -kb                   (none)   Return the result in kilobytes.                   -
-asMegaBytes                -mb                   (none)   Return the result in megabytes.                   -
-asGigaBytes                -gb                   (none)   Return the result in gigabytes.                   -
=========================== ===================== ======== ================================================= =============

.. note::

   The command requires ``-query`` mode. Combine a memory-type flag
   with a unit flag in each call.

Return
------

Returns a single double value representing the requested memory amount
in the chosen unit.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   total_mb   = maya.cmds.mmMemorySystem(query=True, systemPhysicalMemoryTotal=True, asMegaBytes=True)
   free_mb    = maya.cmds.mmMemorySystem(query=True, systemPhysicalMemoryFree=True,  asMegaBytes=True)
   used_mb    = maya.cmds.mmMemorySystem(query=True, systemPhysicalMemoryUsed=True,  asMegaBytes=True)
   process_mb = maya.cmds.mmMemorySystem(query=True, processMemoryUsed=True,         asMegaBytes=True)

MEL Example:

.. code:: text

   mmMemorySystem -query -systemPhysicalMemoryTotal -asMegaBytes;
   mmMemorySystem -query -systemPhysicalMemoryFree  -asMegaBytes;
   mmMemorySystem -query -systemPhysicalMemoryUsed  -asMegaBytes;
   mmMemorySystem -query -processMemoryUsed         -asMegaBytes;


``mmTestCameraMatrix`` Command
++++++++++++++++++++++++++++++

`mmTestCameraMatrix` calculates an matrix (not returned) from the
given camera transform and shape nodes. If the matrix matches the same
matrix produced by Maya's API, then the command returns true.

This command is used for internal tests only, it has no practical use
for users.

Python Example:

.. code:: python

   cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
   cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
   result = maya.cmds.mmTestCameraMatrix(cam_tfm, cam_shp)
   assert result == True
