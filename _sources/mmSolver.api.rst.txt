mmSolver.api
============

By convention the mmSolver.api functions are expected to be imported into
the alias `mmapi`, examples assume this is done.

.. code:: python

   import maya.cmds
   import mmSolver.api as mmapi
   mmapi.load_plugin()  # Force load the mmSolver plug-in.

Object Overview
```````````````

|API Classes Image|

==================================== ==============================================================
Class                                Description
==================================== ==============================================================
:py:class:`mmSolver.api.Marker`      2D point to determine screen-space features
:py:class:`mmSolver.api.Bundle`      3D point to determine real-location of 2D feature
:py:class:`mmSolver.api.Attribute`   Attribute that will be solved
:py:class:`mmSolver.api.Camera`      Camera to view the world
:py:class:`mmSolver.api.Frame`       Point in time
:py:class:`mmSolver.api.SolverBase`  Options that describe how the solving algorithm will run
:py:class:`mmSolver.api.Collection`  A set of Markers, Attributes and Solvers to use during solving
:py:class:`mmSolver.api.SolveResult` Output of the solver; Details of what happened in a solve
==================================== ==============================================================

The above list of classes is simplified.
The full list of classes and functions exposed are detailed in :ref:`mmSolver-api-heading`.

Example
```````

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
   sol = mmapi.SolverStep()
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

.. _mmSolver-api-heading:

mmSolver API
````````````

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

.. autofunction:: mmSolver.api.update_deviation_on_markers

.. autofunction:: mmSolver.api.calculate_marker_deviation

.. autofunction:: mmSolver.api.get_markers_start_end_frames

.. autofunction:: mmSolver.api.find_marker_attr_mapping

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

Solvers are compiled into individual Python functions to be run.
To compile the Solvers with a consistent interface and manage new
solver processes, a `SolverBase` class has been created.

Users are expected to sub-class `SolverBase` and add functionality.
Pre-existing classes already provide functionality for common solving
needs.

Solver Base
-----------

.. autoclass:: mmSolver.api.SolverBase
   :members:
   :undoc-members:
   :special-members: __init__

Solver Basic
------------

.. autoclass:: mmSolver.api.SolverBasic
   :members:
   :undoc-members:
   :special-members: __init__

Solver Standard
---------------

.. autoclass:: mmSolver.api.SolverStandard
   :members:
   :undoc-members:
   :special-members: __init__

Solver Step
-----------

The :py:class:`mmSolver.api.SolverStep` is used to represent frames
to be solved.

.. note::

    For backwards compatibility the SolverStep class can also be accessed
    with the class name ``mmSolver.api.Solver``. This is deprecated
    and will be removed in a future version.

.. autoclass:: mmSolver.api.SolverStep
   :members:
   :undoc-members:
   :special-members: __init__

Collection
++++++++++

.. autoclass:: mmSolver.api.Collection
   :members:
   :undoc-members:
   :special-members: __init__

.. autofunction:: mmSolver.api.update_deviation_on_collection

.. autofunction:: mmSolver.api.run_progress_func

.. autofunction:: mmSolver.api.run_status_func

.. autofunction:: mmSolver.api.is_single_frame

.. autofunction:: mmSolver.api.disconnect_animcurves

.. autofunction:: mmSolver.api.reconnect_animcurves

.. autofunction:: mmSolver.api.clear_attr_keyframes

.. autofunction:: mmSolver.api.generate_isolate_nodes

Action
+++++++

.. autoclass:: mmSolver.api.Action
   :members:
   :undoc-members:
   :special-members: __init__

.. autofunction:: mmSolver.api.action_func_is_mmSolver

.. autofunction:: mmSolver.api.func_str_to_callable

.. autofunction:: mmSolver.api.action_to_components

Execute
+++++++

.. autoclass:: mmSolver.api.ExecuteOptions
   :members:
   :undoc-members:
   :special-members: __init__

.. autofunction:: mmSolver.api.createExecuteOptions

.. autofunction:: mmSolver.api.validate

.. autofunction:: mmSolver.api.execute

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

.. autofunction:: mmSolver.api.merge_marker_error_list

.. autofunction:: mmSolver.api.merge_marker_node_list

.. autofunction:: mmSolver.api.format_timestamp

Naming
++++++

.. autofunction:: mmSolver.api.find_valid_maya_node_name

.. autofunction:: mmSolver.api.get_new_marker_name

.. autofunction:: mmSolver.api.get_new_bundle_name

Utilities
+++++++++

.. autofunction:: mmSolver.api.load_plugin

.. autofunction:: mmSolver.api.get_object_type

.. autofunction:: mmSolver.api.get_marker_group_above_node

State
+++++

The state functions are used for getting and setting global states
(global variables).

.. note::

   Global state must be used carefully. We recommend using
   try-except-finally_ blocks to ensure global state is returned to the
   intended values if any exception is raised.

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
   :special-members: __init__

.. autoclass:: mmSolver.api.NotValid
   :members:
   :undoc-members:
   :special-members: __init__

.. autoclass:: mmSolver.api.AlreadyLinked
   :members:
   :undoc-members:
   :special-members: __init__

.. autoclass:: mmSolver.api.AlreadyUnlinked
   :members:
   :undoc-members:
   :special-members: __init__

.. autoclass:: mmSolver.api.NotEnoughMarkers
   :members:
   :undoc-members:
   :special-members: __init__

.. autoclass:: mmSolver.api.SolverNotAvailable
   :members:
   :undoc-members:
   :special-members: __init__

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

.. autoattribute:: mmSolver.api.SOLVER_TYPE_CMINPACK_LM

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_FORWARD

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_CENTRAL

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_LIST

.. |API Classes Image| image:: images/api_classes_overview.png

.. _try-except-finally:
    https://www.w3schools.com/python/python_try_except.asp