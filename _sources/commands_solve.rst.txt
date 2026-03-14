Solve Commands
==============

``mmSolver`` Command
++++++++++++++++++++

The command named ``mmSolver`` is the primary command used to perform a
solve.

Flags
-----

The command can be run in both MEL and Python.

Here is a table of command flags, as currently specified in the command.

======================== ===================== ========================================== ======================================================================= ==============
Command Flag             Command Flag (short)  Type                                       Description                                                             Default Value
======================== ===================== ========================================== ======================================================================= ==============
-camera                  -c                    string, string                             Camera transform and shape nodes.                                       None
-marker                  -m                    string, string, string                     Marker, Camera, Bundle.                                                 None
-attr                    -a                    string, string, string, string, string     Node attribute, min value, max value, offset and scale.                 None
-frame                   -f                    long int                                   Frame number to solve with.                                             1
-attrStiffness           -asf                  string, string, string, string             Node attribute, weight plug name, variance plug name, value plug name.  None
-attrSmoothness          -asm                  string, string, string, string             Node attribute, weight plug name, variance plug name, value plug name.  None
-solverType              -st                   unsigned int                               Type of solver to use.                                                  <auto detected>
-sceneGraphMode          -sgm                  unsigned int                               The Scene Graph used; 0=Maya DAG, 1=MM Scene Graph.                     0 (Maya DAG)
-timeEvalMode            -tem                  unsigned int                               How to evalulate values at different times, 0=DG Context 1=Set Time.    0 (DG Context)
-iterations              -it                   unsigned int                               Maximum number of iterations.                                           20
-tauFactor               -t                    double                                     Initial Damping Factor.                                                 1E-03
-functionTolerance       -ftl                  double                                     Acceptable function change.                                             1E-06
-parameterTolerance      -ptl                  double                                     Acceptable parameter change.                                            1E-06
-gradientTolerance       -gtl                  double                                     Acceptable gradient error.                                              1E-06
-delta                   -dt                   double                                     Change to the guessed parameters each iteration.                        1E-04
-autoDiffType            -adt                  unsigned int                               Auto-differencing type 0=forward 1=central.                             0 (forward)
-verbose                 -v                    bool                                       Prints more information.                                                False
======================== ===================== ========================================== ======================================================================= ==============

Return
------

The ``mmSolver`` command will return a list of strings.

The list of strings has a specific structure and stores all the data
from the core solver engines, so the user can do whatever they wish to.

Example
-------

Python Example:

.. code:: python

   maya.cmds.mmSolver(
       camera=('camera1', 'cameraShape1'),
       marker=(
           ('marker1', 'camera1', 'bundle1'),
           ('marker2', 'camera1', 'bundle2'),
       ),
       attr=(
           ('node.attr', 'None', 'None', 'None', 'None'),
           ('bundle1.tx', 'None', 'None', 'None', 'None'),
           ('bundle1.ty', 'None', 'None', 'None', 'None'),
           ('camera1.rx', '-10.0', '25.0', '360.0', '1.0'),
       ),
       frame=(1, 12, 24,),
       iterations=10,
   )

MEL Example:

.. code:: text

   mmSolver
       -camera "camera1" "cameraShape1"
       -marker "marker1" "camera1" "bundle1"
       -marker "marker2" "camera1" "bundle2"
       -attr "node.attr" "None" "None" "None" "None"
       -attr "bundle1.tx" "None" "None" "None" "None"
       -attr "bundle1.ty" "None" "None" "None" "None"
       -attr "camera1.rx" "-10.0" "25.0" "360.0" "1.0"
       -frame 1
       -frame 12
       -frame 24
       -iterations 10;

``mmSolverType`` Command
++++++++++++++++++++++++

``mmSolverType`` queries the available solver back-ends compiled into
the plug-in and reports which one is used by default.

This command is commonly used to adapt scripts to whichever solvers
are present. See :ref:`solver-faq-how-to-get-supported-solver-types`
for more detail.

Flags
-----

All flags require ``-query`` mode (the command does not support edit
mode).

========================= ===================== ======== ============================================================= =============
Command Flag              Command Flag (short)  Type     Description                                                   Default Value
========================= ===================== ======== ============================================================= =============
-list                     -ls                   bool     Return a list of all available solver types.                  False
-default                  -def                  bool     Return the default solver type.                               False
-name                     -n                    string   Filter output to include the solver name.                     (auto)
-index                    -idx                  unsigned Filter output to include the solver index.                    (auto)
========================= ===================== ======== ============================================================= =============

.. note::

   ``-list`` and ``-default`` are mutually exclusive.  When either is
   given without ``-name`` or ``-index``, both name and index are
   returned by default.

Return
------

Returns a string array (when ``-list`` is used) or a single string
(when ``-default`` is used).  Each entry has the form
``<index>=<name>`` when both ``-name`` and ``-index`` are active,
otherwise just the index or name alone.

Example
-------

Python Example:

.. code:: python

   # List all available solvers (returns e.g. ["0=cminpack_lm", "1=ceres"])
   solvers = maya.cmds.mmSolverType(query=True, list=True)

   # Query the default solver
   default_solver = maya.cmds.mmSolverType(query=True, default=True)

MEL Example:

.. code:: text

   // List all available solvers
   mmSolverType -query -list true;

   // Get default solver
   mmSolverType -query -default true;


``mmSolverAffects`` Command
+++++++++++++++++++++++++++

``mmSolverAffects`` analyses the dependency relationships between
markers and attributes and caches those relationships as custom
attributes on the marker nodes. The solver uses this cached data to
partition a solve into independent sub-problems, improving performance.

The command accepts the same ``-camera``, ``-marker``, ``-attr``, and
``-frame`` flags as ``mmSolver``. The ``-frame`` flag is optional; the
command works with time-independent data.

Flags
-----

==================== ==================== ========================= ============================================================= =================
Command Flag         Command Flag (short) Type                      Description                                                   Default Value
==================== ==================== ========================= ============================================================= =================
-camera              -c                   string, string            Camera transform and shape nodes.                              None
-marker              -m                   string, string, string    Marker, Camera, Bundle.                                        None
-attr                -a                   string × 5                Node attribute, min, max, offset, scale.                       None
-frame               -f                   long int                  Frame number (optional).                                       None
-mode                -md                  string                    Operation mode; see values below.                              None
-graphMode           -gmd                 string                    Graph representation mode; see values below.                   ``"node_name"``
==================== ==================== ========================= ============================================================= =================

**Mode values** (``-mode``):

- ``"addAttrsToMarkers"`` — compute the affects relationship and write
  it as custom attributes on each marker node. This is the normal use
  case and the operation is undoable.
- ``"returnString"`` — return the relationship data as a string instead
  of modifying nodes.

**Graph mode values** (``-graphMode``):

- ``"normal"`` — full graph with all details.
- ``"node_name"`` — identify graph nodes by their Maya node name
  (default).
- ``"object"`` — identify graph nodes by their Python object
  representation.
- ``"simple"`` — simplified graph with minimal detail.

Return
------

With ``-mode "addAttrsToMarkers"``: modifies marker nodes in-place and
returns nothing.

With ``-mode "returnString"``: returns a string encoding the
affects-relationship graph.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   maya.cmds.mmSolverAffects(
       camera=('camera1', 'camera1Shape'),
       marker=('myMarker', 'camera1Shape', 'myBundle'),
       attr=('myBundle.translateX', 'None', 'None', 'None', 'None'),
       mode='addAttrsToMarkers',
   )

MEL Example:

.. code:: text

   mmSolverAffects
       -camera "camera1" "camera1Shape"
       -marker "myMarker" "camera1Shape" "myBundle"
       -attr "myBundle.translateX" "None" "None" "None" "None"
       -mode "addAttrsToMarkers";


``mmSolverSceneGraph`` Command
++++++++++++++++++++++++++++++

``mmSolverSceneGraph`` validates whether the given scene objects can be
used to construct a scene graph of the requested type. It accepts the
same object and frame flags as ``mmSolver`` and returns ``true`` if
construction succeeds, or ``false`` otherwise.

This is useful for detecting in advance whether the MM Scene Graph
(``-sceneGraphMode 1``) will work for a given set of inputs, so that
calling code can fall back to the Maya DAG scene graph if needed.

The command is not undoable.

Flags
-----

==================== ==================== ========================= ============================================================= =============
Command Flag         Command Flag (short) Type                      Description                                                   Default Value
==================== ==================== ========================= ============================================================= =============
-camera              -c                   string, string            Camera transform and shape nodes.                              None
-marker              -m                   string, string, string    Marker, Camera, Bundle.                                        None
-attr                -a                   string × 5                Node attribute, min, max, offset, scale.                       None
-frame               -f                   long int                  Frame number to test with.                                     None
-sceneGraphMode      -sgm                 unsigned int              Scene graph type; 0=Maya DAG, 1=MM Scene Graph.                0 (Maya DAG)
-mode                -md                  string                    Operation mode; only ``"debugConstruct"`` is currently valid.  None
==================== ==================== ========================= ============================================================= =============

Return
------

Returns ``true`` if the scene graph was constructed without errors,
``false`` otherwise.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   result = maya.cmds.mmSolverSceneGraph(
       camera=('camera1', 'camera1Shape'),
       marker=('myMarker', 'camera1Shape', 'myBundle'),
       attr=('myBundle.translateX', 'None', 'None', 'None', 'None'),
       frame=1,
       sceneGraphMode=1,
       mode='debugConstruct',
   )
   if not result:
       print('MM Scene Graph is not supported; falling back to Maya DAG.')

MEL Example:

.. code:: text

   int $ok = `mmSolverSceneGraph
       -camera "camera1" "camera1Shape"
       -marker "myMarker" "camera1Shape" "myBundle"
       -attr "myBundle.translateX" "None" "None" "None" "None"
       -frame 1
       -sceneGraphMode 1
       -mode "debugConstruct"`;


``mmCameraRelativePose`` Command
++++++++++++++++++++++++++++++++

``mmCameraRelativePose`` computes the relative pose (position and
rotation) of one camera with respect to another using 2D marker
correspondences observed at two different frames. This is a Structure
from Motion (SfM) operation based on the essential matrix.

At least five marker correspondences are required. When
``-setValues true`` is given the computed poses are written to the
camera transform nodes (undoable).

Flags
-----

======================= ===================== ========================= ==================================================================== =============
Command Flag            Command Flag (short)  Type                      Description                                                          Default Value
======================= ===================== ========================= ==================================================================== =============
-cameraA                -ca                   selection item            Camera A transform node.                                             None
-cameraB                -cb                   selection item            Camera B transform node.                                             None
-frameA                 -fa                   long int                  Frame number for camera A.                                           1
-frameB                 -fb                   long int                  Frame number for camera B.                                           10
-markerBundle           -mb                   string, string, string    Marker on frame A, marker on frame B, bundle (multi-use).            None
-bundlePosition         -bp                   double, double, double    World-space XYZ of a bundle (multi-use, optional).                   None
-setValues              -sv                   bool                      Write computed poses to the camera transform nodes.                  False
-useCameraTransform     -ct                   bool                      Use an existing camera world-space transform as the reference frame.  False
======================= ===================== ========================= ==================================================================== =============

Return
------

Returns an empty result. Camera transform values are set directly on
the nodes when ``-setValues true`` is given.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   maya.cmds.mmCameraRelativePose(
       cameraA='cameraA',
       cameraB='cameraB',
       frameA=1,
       frameB=10,
       markerBundle=[
           ('markerA1', 'markerB1', 'bundle1'),
           ('markerA2', 'markerB2', 'bundle2'),
           ('markerA3', 'markerB3', 'bundle3'),
           ('markerA4', 'markerB4', 'bundle4'),
           ('markerA5', 'markerB5', 'bundle5'),
       ],
       setValues=True,
   )

MEL Example:

.. code:: text

   mmCameraRelativePose
       -cameraA "cameraA"
       -cameraB "cameraB"
       -frameA 1
       -frameB 10
       -markerBundle "markerA1" "markerB1" "bundle1"
       -markerBundle "markerA2" "markerB2" "bundle2"
       -markerBundle "markerA3" "markerB3" "bundle3"
       -markerBundle "markerA4" "markerB4" "bundle4"
       -markerBundle "markerA5" "markerB5" "bundle5"
       -setValues true;


``mmCameraPoseFromPoints`` Command
++++++++++++++++++++++++++++++++++

``mmCameraPoseFromPoints`` computes a camera pose (position and
rotation) at one or more frames from known 3D bundle positions and
their corresponding 2D marker positions (Perspective-n-Point, PnP).

Paired ``-marker`` (2D) and ``-bundle`` (3D) inputs must be provided
in matching order. When ``-setValues true`` is given the result is
written to the camera transform node at each frame (undoable).

Flags
-----

==================== ==================== ==================== ======================================================== =============
Command Flag         Command Flag (short) Type                 Description                                              Default Value
==================== ==================== ==================== ======================================================== =============
-camera              -c                   selection item       Camera transform node to solve.                          None
-frame               -f                   unsigned int         Frame number to compute the pose at (multi-use).         None
-marker              -m                   string, string       Marker node and camera shape node (multi-use).           None
-bundle              -b                   string               Bundle node corresponding to each marker (multi-use).    None
-setValues           -sv                  bool                 Write the computed pose to the camera transform node.    False
==================== ==================== ==================== ======================================================== =============

Return
------

Returns an empty result. Camera transform values are set directly on
the node at each frame when ``-setValues true`` is given.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   maya.cmds.mmCameraPoseFromPoints(
       camera='camera1',
       frame=(1, 2, 3),
       marker=[
           ('marker1', 'camera1Shape'),
           ('marker2', 'camera1Shape'),
           ('marker3', 'camera1Shape'),
           ('marker4', 'camera1Shape'),
       ],
       bundle=['bundle1', 'bundle2', 'bundle3', 'bundle4'],
       setValues=True,
   )

MEL Example:

.. code:: text

   mmCameraPoseFromPoints
       -camera "camera1"
       -frame 1
       -frame 2
       -frame 3
       -marker "marker1" "camera1Shape"
       -marker "marker2" "camera1Shape"
       -marker "marker3" "camera1Shape"
       -marker "marker4" "camera1Shape"
       -bundle "bundle1"
       -bundle "bundle2"
       -bundle "bundle3"
       -bundle "bundle4"
       -setValues true;


``mmCameraSolve`` Command
+++++++++++++++++++++++++

``mmCameraSolve`` is the higher-level camera solver command used by the
:ref:`Camera Solver <camera-solver-overview-heading>` tool. It accepts a
selection list of camera transform nodes and marker nodes, reads the
marker 2D positions at the given frame range, and runs the SfM-based
camera solve pipeline.

.. note::

   The full solve is currently implemented in Python (see
   ``python/mmSolver/_api/solvercamerautils.py``). This C++ command
   handles argument parsing and data preparation but delegates the
   heavy computation to the Python layer. The command is not undoable.

Flags
-----

==================== ==================== ============ ============================================== =============
Command Flag         Command Flag (short) Type         Description                                    Default Value
==================== ==================== ============ ============================================== =============
-startFrame          -sf                  unsigned int First frame of the range to solve.              1
-endFrame            -ef                  unsigned int Last frame of the range to solve.               120
==================== ==================== ============ ============================================== =============

In addition to the flags, pass the camera transform and marker nodes
as command objects (the selection list).

Return
------

Returns an empty array. Results are applied to the scene by the
calling Python code.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   maya.cmds.mmCameraSolve(
       'camera1',
       'marker1', 'marker2', 'marker3',
       startFrame=1,
       endFrame=120,
   )

MEL Example:

.. code:: text

   mmCameraSolve
       -startFrame 1
       -endFrame 120
       camera1 marker1 marker2 marker3;


``mmSolver_v2`` Command
+++++++++++++++++++++++

``mmSolver_v2`` is the second iteration of the ``mmSolver`` command
with a cleaner flag syntax. It performs the same non-linear
least-squares solve but drops the deprecated ``-verbose``,
``-attrStiffness``, ``-attrSmoothness``, and ``-removeUnused*`` flags,
and adds flags for results output and marker-deviation attributes.

The command is undoable.

Flags
-----

========================= ===================== ========================= ========================================================================== ========================
Command Flag              Command Flag (short)  Type                      Description                                                                Default Value
========================= ===================== ========================= ========================================================================== ========================
-camera                   -c                    string, string            Camera transform and shape nodes.                                           None
-marker                   -m                    string, string, string    Marker, Camera, Bundle.                                                     None
-attr                     -a                    string × 5                Node attribute, min, max, offset, scale.                                    None
-frame                    -f                    long int                  Frame number to solve with (multi-use).                                     None
-solverType               -st                   unsigned int              Solver back-end to use; see ``mmSolverType`` for available values.          (auto-detected)
-sceneGraphMode           -sgm                  unsigned int              Scene graph; 0=Maya DAG, 1=MM Scene Graph.                                  0 (Maya DAG)
-timeEvalMode             -tem                  unsigned int              Time evaluation; 0=DG Context, 1=Set Time.                                  0 (DG Context)
-frameSolveMode           -fsm                  unsigned int              Frame order; 0=all frames at once, 1=per frame.                             0 (all at once)
-iterations               -it                   unsigned int              Maximum solver iterations.                                                  (solver-dependent)
-tauFactor                -t                    double                    Initial damping factor (LM trust-region size).                              (solver-dependent)
-functionTolerance        -ftl                  double                    Acceptable function-value change to stop.                                   (solver-dependent)
-parameterTolerance       -ptl                  double                    Acceptable parameter change to stop.                                        (solver-dependent)
-gradientTolerance        -gtl                  double                    Acceptable gradient magnitude to stop.                                      (solver-dependent)
-delta                    -dt                   double                    Finite-difference step size for numerical derivatives.                      (solver-dependent)
-autoDiffType             -adt                  unsigned int              Differentiation method; 0=forward, 1=central.                               0 (forward)
-autoParamScaling         -aps                  unsigned int              Parameter auto-scaling; 0=off, 1=on.                                        (solver-dependent)
-robustLossType           -rlt                  unsigned int              Robust loss function; 0=trivial, 1=soft_l1, 2=cauchy.                       0 (trivial)
-robustLossScale          -rls                  double                    Scale factor for the robust loss function.                                  (solver-dependent)
-acceptOnlyBetter         -aob                  bool                      Only apply solve results if quality improved.                               True
-imageWidth               -imw                  double                    Image width in pixels, used to compute per-pixel deviation display.         2048.0
-printStatistics          -pst                  string (multi-use)        Print solver statistics; values: ``"inputs"``, ``"results"``, ``"solver"``. None
-logLevel                 -lgl                  unsigned int              Verbosity; 0=error, 1=warning, 2=info, 3=verbose.                           2 (info)
-resultsNode              -rsn                  string                    Maya node to receive solve-result attributes.                               None
-setMarkerDeviationAttrs  -smd                  bool                      Write deviation values as attributes on marker nodes after solve.           True
========================= ===================== ========================= ========================================================================== ========================

Return
------

Returns ``true`` (integer ``1``) if the solve completed without error,
``false`` (``0``) otherwise. Solve quality statistics are printed
according to ``-logLevel`` and written to ``-resultsNode`` when
provided.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   result = maya.cmds.mmSolver_v2(
       camera=('camera1', 'cameraShape1'),
       marker=(
           ('marker1', 'camera1', 'bundle1'),
           ('marker2', 'camera1', 'bundle2'),
       ),
       attr=(
           ('bundle1.tx', 'None', 'None', 'None', 'None'),
           ('bundle1.ty', 'None', 'None', 'None', 'None'),
           ('camera1.rx', '-10.0', '25.0', 'None', 'None'),
       ),
       frame=(1, 12, 24),
       iterations=20,
       logLevel=2,
       setMarkerDeviationAttrs=True,
   )
   print('Solve succeeded:', result)

MEL Example:

.. code:: text

   int $ok = `mmSolver_v2
       -camera "camera1" "cameraShape1"
       -marker "marker1" "camera1" "bundle1"
       -marker "marker2" "camera1" "bundle2"
       -attr "bundle1.tx" "None" "None" "None" "None"
       -attr "bundle1.ty" "None" "None" "None" "None"
       -attr "camera1.rx" "-10.0" "25.0" "None" "None"
       -frame 1
       -frame 12
       -frame 24
       -iterations 20
       -logLevel 2
       -setMarkerDeviationAttrs true`;
