Selection Tools
===============

Toggle Marker / Bundle
----------------------

Select the opposite node, if a Marker is selected, select it’s connected
Bundle, and vice-versa.

Run this Python command:

.. code:: python

    import mmSolver.tools.selection.tools as selection_tool
    selection_tool.swap_between_selected_markers_and_bundles()

Select Marker + Bundle
----------------------

With either a Marker or Bundle selected, select both connected nodes.

Run this Python command:

.. code:: python

    import mmSolver.tools.selection.tools as selection_tool
    selection_tool.select_both_markers_and_bundles()
