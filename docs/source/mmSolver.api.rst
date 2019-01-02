mmSolver.api
============

.. automodule:: mmSolver.api

Camera
++++++

.. autoclass:: mmSolver.api.Camera
   :members:
   :undoc-members:

Bundle
++++++

.. autoclass:: mmSolver.api.Bundle
   :members:
   :undoc-members:

Marker & MarkerGroup
++++++++++++++++++++

.. autoclass:: mmSolver.api.Marker
   :members:
   :undoc-members:

.. autoclass:: mmSolver.api.MarkerGroup
   :members:
   :undoc-members:

Attribute
+++++++++

.. autoclass:: mmSolver.api.Attribute
   :members:
   :undoc-members:

Frame
+++++

.. autoclass:: mmSolver.api.Frame
   :members:
   :undoc-members:

Solver
++++++

.. autoclass:: mmSolver.api.Solver
   :members:
   :undoc-members:


Collection
++++++++++

.. autoclass:: mmSolver.api.Collection
   :members:
   :undoc-members:

SolveResult
+++++++++++

.. autoclass:: mmSolver.api.SolveResult
   :members:
   :undoc-members:

Utilities
+++++++++

.. autofunction:: mmSolver.api.get_long_name

.. autofunction:: mmSolver.api.get_as_selection_list

.. autofunction:: mmSolver.api.get_dag_path

.. autofunction:: mmSolver.api.get_object

.. autofunction:: mmSolver.api.get_plug

.. autofunction:: mmSolver.api.get_object_type

.. autofunction:: mmSolver.api.convert_valid_maya_name

.. autofunction:: mmSolver.api.get_marker_name

.. autofunction:: mmSolver.api.get_bundle_name

.. autofunction:: mmSolver.api.load_plugin

.. autofunction:: mmSolver.api.get_data_on_node_attr

.. autofunction:: mmSolver.api.set_data_on_node_attr

.. autofunction:: mmSolver.api.get_value_on_node_attr

.. autofunction:: mmSolver.api.set_value_on_node_attr

Constants
+++++++++

There are constants used in mmSolver. These constants represent
configuration or an enumeration of options. These constants are
referenced inside the documentation.

.. autoattribute:: mmSolver.api.OBJECT_TYPE_UNKNOWN
   :annotation:

.. autoattribute:: mmSolver.api.OBJECT_TYPE_ATTRIBUTE
   :annotation:

.. autoattribute:: mmSolver.api.OBJECT_TYPE_MARKER
   :annotation:

.. autoattribute:: mmSolver.api.OBJECT_TYPE_CAMERA
   :annotation:

.. autoattribute:: mmSolver.api.OBJECT_TYPE_MARKER_GROUP
   :annotation:

.. autoattribute:: mmSolver.api.OBJECT_TYPE_BUNDLE
   :annotation:

.. autoattribute:: mmSolver.api.OBJECT_TYPE_COLLECTION
   :annotation:

.. autoattribute:: mmSolver.api.OBJECT_TYPE_LIST
   :annotation: List containing all OBJECT_TYPE_* constant values.

.. autoattribute:: mmSolver.api.ATTR_STATE_INVALID
   :annotation:

.. autoattribute:: mmSolver.api.ATTR_STATE_STATIC
   :annotation:

.. autoattribute:: mmSolver.api.ATTR_STATE_ANIMATED
   :annotation:

.. autoattribute:: mmSolver.api.ATTR_STATE_LOCKED
   :annotation:

.. autoattribute:: mmSolver.api.SOLVER_TYPE_LEVMAR
   :annotation:

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_FORWARD
   :annotation:

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_CENTRAL
   :annotation:

.. autoattribute:: mmSolver.api.AUTO_DIFF_TYPE_LIST
   :annotation: List containing all AUTO_DIFF_TYPE_* constant values.
