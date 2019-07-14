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
   :special-members:

Bundle
++++++

.. autoclass:: mmSolver.api.Bundle
   :members:
   :undoc-members:
   :special-members:

Marker
++++++

2D point to determine screen-space features.

.. autoclass:: mmSolver.api.Marker
   :members:
   :undoc-members:
   :special-members:

.. autofunction:: mmSolver.api.update_deviation_on_markers

.. autofunction:: mmSolver.api.calculate_marker_deviation

.. autofunction:: mmSolver.api.get_markers_start_end_frames

MarkerGroup
+++++++++++

A group containing Marker nodes.

.. autoclass:: mmSolver.api.MarkerGroup
   :members:
   :undoc-members:
   :special-members:

Attribute
+++++++++

Attribute that will be solved.

.. autoclass:: mmSolver.api.Attribute
   :members:
   :undoc-members:
   :special-members:

Frame
+++++

.. autoclass:: mmSolver.api.Frame
   :members:
   :undoc-members:
   :special-members:

Solver
++++++

.. autoclass:: mmSolver.api.Solver
   :members:
   :undoc-members:
   :special-members:

Collection
++++++++++

.. autoclass:: mmSolver.api.Collection
   :members:
   :undoc-members:
   :special-members:

.. autofunction:: mmSolver.api.update_deviation_on_collection

SolveResult
+++++++++++

.. autoclass:: mmSolver.api.SolveResult
   :members:
   :undoc-members:
   :special-members:

.. autofunction:: mmSolver.api.combine_timer_stats

.. autofunction:: mmSolver.api.merge_frame_error_list

.. autofunction:: mmSolver.api.get_average_frame_error_list

.. autofunction:: mmSolver.api.get_max_frame_error

Naming
++++++

.. autofunction:: mmSolver.api.find_valid_maya_node_name

.. autofunction:: mmSolver.api.get_new_marker_name

.. autofunction:: mmSolver.api.get_new_bundle_name


Utilities
+++++++++

.. autofunction:: mmSolver.api.load_plugin

.. autofunction:: mmSolver.api.get_object_type


State
+++++

.. autofunction:: mmSolver.api.is_solver_running

.. autofunction:: mmSolver.api.set_solver_running

.. autofunction:: mmSolver.api.get_user_interrupt

.. autofunction:: mmSolver.api.set_user_interrupt

Node Conversions
++++++++++++++++

The :mod:`mmSolver.api` module provides functions to convert between
various node types. Currently the following conversions are supported:

- Bundles -> Markers
- Markers -> Bundles
- Markers -> Cameras

.. autofunction:: mmSolver.api.get_marker_nodes_from_bundle_nodes

.. autofunction:: mmSolver.api.get_bundle_nodes_from_marker_nodes

.. autofunction:: mmSolver.api.get_camera_nodes_from_marker_nodes

Nodes Filter
++++++++++++

.. autofunction:: mmSolver.api.filter_nodes_into_categories

.. autofunction:: mmSolver.api.filter_marker_nodes

.. autofunction:: mmSolver.api.filter_marker_group_nodes

.. autofunction:: mmSolver.api.filter_bundle_nodes

.. autofunction:: mmSolver.api.filter_camera_nodes

.. autofunction:: mmSolver.api.filter_collection_nodes

Exceptions
++++++++++

.. autoclass:: mmSolver.api.MMException
   :members:
   :undoc-members:
   :special-members:

.. autoclass:: mmSolver.api.NotValid
   :members:
   :undoc-members:
   :special-members:

.. autoclass:: mmSolver.api.AlreadyLinked
   :members:
   :undoc-members:
   :special-members:

.. autoclass:: mmSolver.api.AlreadyUnlinked
   :members:
   :undoc-members:
   :special-members:

.. autoclass:: mmSolver.api.NotEnoughMarkers
   :members:
   :undoc-members:
   :special-members:

.. autoclass:: mmSolver.api.SolverNotAvailable
   :members:
   :undoc-members:
   :special-members:

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

.. autoattribute:: mmSolver.api.SOLVER_TYPE_CMINPACK_LM

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_FORWARD

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_CENTRAL

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_LIST

.. |API Classes Image| image:: https://raw.githubusercontent.com/david-cattermole/mayaMatchMoveSolver/master/design/api/api_classes_overview.png
