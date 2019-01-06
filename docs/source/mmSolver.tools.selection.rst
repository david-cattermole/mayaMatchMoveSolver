mmSolver.tools.selection
========================

This package contains all selection tools related to solver, marker, and bundle.

Tools
+++++

.. automodule:: mmSolver.tools.selection.tools
   :members:
   :undoc-members:

Convert
+++++++

The :mod:`mmSolver.tools.selection.convert` module provides functions
to convert between various node types. Currently the following
convertions are supported:

- Markers -> Bundles
- Bundles -> Markers
- Markers -> Cameras

.. autofunction:: mmSolver.tools.selection.convert.get_bundles_from_markers

.. autofunction:: mmSolver.tools.selection.convert.get_markers_from_bundles

.. autofunction:: mmSolver.tools.selection.convert.get_cameras_from_markers

Filter Nodes
++++++++++++

.. automodule:: mmSolver.tools.selection.filternodes
   :members:
   :undoc-members:
