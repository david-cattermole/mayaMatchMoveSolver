mmSolver.api
============

By convention the mmSolver.api functions are expected to be imported into the alias `mmapi`, examples assume this is done.

.. code:: python

   import maya.cmds
   import mmSolver.api as mmapi
   mmapi.load_plugin()  # Force load the mmSolver plug-in.

Object Overview
+++++++++++++++

|API Classes Image|

=========== =========================================================
Class       Description
=========== =========================================================
Marker      2D point to determine screen-space features
Bundle      3D point to determine real-location of 2D feature
Attribute   Attribute that will be solved
Camera      Camera to view the world
Frame       Point in time
Solver      Options that describe how the solving algorithm will run
Collection  A set of Markers and Attributes to use during solving
SolveResult Output of the solver; Details of what happened in a solve
=========== =========================================================


Example
+++++++

Here is a example of how to use the ``mmSolver`` Python API.
First a ``Camera``, ``Bundle`` and ``Marker`` are created, these
are used to define the re-projection and perspective.
Next, ``Attributes``, ``Solvers`` and ``Frames`` must be created.
All API objects are then added into the ``Collection``, and the collection
is executed.
Finally, a ``SolverResult`` is returned from the executed Collection and
an be used to check the Solver output (for example, did an error occur?).

.. code:: python

   # Camera
   cam_tfm = maya.cmds.createNode('transform',
                                  name='cam_tfm')
   cam_shp = maya.cmds.createNode('camera',
                                  name='cam_shp',
                                  parent=cam_tfm)
   cam = mmapi.Camera(shape=cam_shp)
   maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
   maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
   maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

   # Bundle
   bnd = mmapi.Bundle().create_node()
   bundle_tfm = bnd.get_node()
   maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
   maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
   maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)

   # Marker
   mkr = mmapi.Marker().create_node()
   maya.cmds.setAttr(marker_tfm + '.tx', -2.5)
   maya.cmds.setAttr(marker_tfm + '.ty', 1.3)
   maya.cmds.setAttr(marker_tfm + '.tz', -10)
   mkr.set_bundle(bnd)
   mkr.set_camera(bnd)

   # Attributes
   attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
   attr_ty = mmapi.Attribute(bundle_tfm + '.ty')

   # Solver
   sol = mmapi.Solver()
   sol.set_verbose(True)
   sol.add_frame(1)
   sol.set_frame_list([1])

   # Collection
   col = mmapi.Collection()
   col.create('mySolveCollection')
   col.set_solver(sol)
   col.add_marker(marker_tfm)
   col.add_attribute(attr_tx)
   col.add_attribute(attr_ty)

   # Run solver!
   result = col.execute()
   print 'Solve Error:', result.get_error()

Camera
++++++

.. autoclass:: mmSolver.api.Camera
   :members:
   :undoc-members:
   :special-members: __init__

Bundle
++++++

.. autoclass:: mmSolver.api.Bundle
   :members:
   :undoc-members:
   :special-members: __init__

Marker
++++++

2D point to determine screen-space features.

.. autoclass:: mmSolver.api.Marker
   :members:
   :undoc-members:
   :special-members: __init__

MarkerGroup
+++++++++++

A group containing Marker nodes.

.. autoclass:: mmSolver.api.MarkerGroup
   :members:
   :undoc-members:
   :special-members: __init__

Attribute
+++++++++

Attribute that will be solved.

.. autoclass:: mmSolver.api.Attribute
   :members:
   :undoc-members:
   :special-members: __init__

Frame
+++++

.. autoclass:: mmSolver.api.Frame
   :members:
   :undoc-members:
   :special-members: __init__

Solver
++++++

.. autoclass:: mmSolver.api.Solver
   :members:
   :undoc-members:
   :special-members: __init__

Collection
++++++++++

.. autoclass:: mmSolver.api.Collection
   :members:
   :undoc-members:
   :special-members: __init__

SolveResult
+++++++++++

.. autoclass:: mmSolver.api.SolveResult
   :members:
   :undoc-members:
   :special-members: __init__

.. autofunction:: mmSolver.api.combine_timer_stats

.. autofunction:: mmSolver.api.merge_frame_error_list

.. autofunction:: mmSolver.api.get_average_frame_error_list

.. autofunction:: mmSolver.api.get_max_frame_error

Utilities
+++++++++

.. autofunction:: mmSolver.api.get_long_name

.. autofunction:: mmSolver.api.get_as_selection_list

.. autofunction:: mmSolver.api.get_as_dag_path

.. autofunction:: mmSolver.api.get_as_object

.. autofunction:: mmSolver.api.get_as_plug

.. autofunction:: mmSolver.api.get_object_type

.. autofunction:: mmSolver.api.convert_valid_maya_name

.. autofunction:: mmSolver.api.get_marker_name

.. autofunction:: mmSolver.api.get_bundle_name

.. autofunction:: mmSolver.api.load_plugin

.. autofunction:: mmSolver.api.get_data_on_node_attr

.. autofunction:: mmSolver.api.set_data_on_node_attr

.. autofunction:: mmSolver.api.get_value_on_node_attr

.. autofunction:: mmSolver.api.set_value_on_node_attr

.. autofunction:: mmSolver.api.is_solver_running

.. autofunction:: mmSolver.api.set_solver_running

Constants
+++++++++

There are constants used in mmSolver. These constants represent
configuration or an enumeration of options. These constants are
referenced inside the documentation.

.. autoattribute:: mmSolver.api.OBJECT_TYPE_UNKNOWN

.. autoattribute:: mmSolver.api.OBJECT_TYPE_ATTRIBUTE

.. autoattribute:: mmSolver.api.OBJECT_TYPE_MARKER

.. autoattribute:: mmSolver.api.OBJECT_TYPE_CAMERA

.. autoattribute:: mmSolver.api.OBJECT_TYPE_MARKER_GROUP

.. autoattribute:: mmSolver.api.OBJECT_TYPE_BUNDLE

.. autoattribute:: mmSolver.api.OBJECT_TYPE_COLLECTION

.. autoattribute:: mmSolver.api.OBJECT_TYPE_LIST

.. autoattribute:: mmSolver.api.ATTR_STATE_INVALID

.. autoattribute:: mmSolver.api.ATTR_STATE_STATIC

.. autoattribute:: mmSolver.api.ATTR_STATE_ANIMATED

.. autoattribute:: mmSolver.api.ATTR_STATE_LOCKED

.. autoattribute:: mmSolver.api.SOLVER_TYPE_LEVMAR

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_FORWARD

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_CENTRAL

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_LIST

.. |API Classes Image| image:: https://raw.githubusercontent.com/david-cattermole/mayaMatchMoveSolver/master/design/api/api_classes_overview.png
