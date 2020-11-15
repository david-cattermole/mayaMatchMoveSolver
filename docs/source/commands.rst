Commands
========

``mmSolver`` Command
++++++++++++++++++++

The command named ``mmSolver`` is the primary command used to perform a
solve.

Flags
-----

The command can be run in both MEL and Python.

Here is a table of command flags, as currently specified in the command.

======================== ========================================== ======================================================================= ==============
Flag                     Type                                       Description                                                             Default Value
======================== ========================================== ======================================================================= ==============
-camera (-c)             string, string                             Camera transform and shape nodes                                        None
-marker (-m)             string, string, string                     Marker, Camera, Bundle                                                  None
-attr (-a)               string, string, string, string, string     Node attribute, min value, max value, offset and scale                  None
-frame (-f)              long int                                   Frame number to solve with                                              1
-attrStiffness (-asf)    string, string, string, string             Node attribute, weight plug name, variance plug name, value plug name.  None
-attrSmoothness (-asm)   string, string, string, string             Node attribute, weight plug name, variance plug name, value plug name.  None
-solverType (-st)        unsigned int                               Type of solver to use.                                                  <auto detected>
-timeEvalMode (-tem)     unsigned int                               How to evalulate values at different times, 0=DG Context 1=Set TIme     0 (DG Context)
-iterations (-it)        unsigned int                               Maximum number of iterations                                            20
-tauFactor (-t)          double                                     Initial Damping Factor                                                  1E-03
-epsilon1 (-e1)          double                                     Acceptable gradient change                                              1E-06
-epsilon2 (-e2)          double                                     Acceptable parameter change                                             1E-06
-epsilon3 (-e3)          double                                     Acceptable error                                                        1E-06
-delta (-dt)             double                                     Change to the guessed parameters each iteration                         1E-04
-autoDiffType (-adt)     unsigned int                               Auto-differencing type 0=forward 1=central                              0 (forward)
-verbose (-v)            bool                                       Prints more information                                                 False
======================== ========================================== ======================================================================= ==============

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

`mmSolverType` is used to query the current plug-in's available
solvers.

This tool is commonly used to dynamically query for the different
types of solvers. See the
:ref:`solver-faq-how-to-get-supported-solver-types` for more detail on
this.

Python Example:

.. code:: python

   solvers = maya.cmds.mmSolverType(query=True, list=True)
   default_solver = maya.cmds.mmSolverType(query=True, default=True)

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
