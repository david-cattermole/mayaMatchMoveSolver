Selection Tools
===============

.. _toggle-marker-bundle-selection-tool-ref:

Toggle Marker / Bundle Selection
--------------------------------

Select the opposite node, if a Marker is selected, select it’s connected
Bundle, and vice-versa.

Run this Python command:

.. code:: python

    import mmSolver.tools.selection.tools as selection_tool
    selection_tool.swap_between_selected_markers_and_bundles()

.. _select-marker-and-bundle-tool-ref:

Select Marker + Bundle
----------------------

With either a Marker or Bundle selected, select both connected nodes.

Run this Python command:

.. code:: python

    import mmSolver.tools.selection.tools as selection_tool
    selection_tool.select_both_markers_and_bundles()
