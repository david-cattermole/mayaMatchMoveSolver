Tools
=====

Most users will use the tools listed below to control and manipulate
the MM Solver. There are also utilities to help the MM Solver
workflow.

Pages dedicated to specific tools:

.. toctree::
    :maxdepth: 1

   tools_solver_ui
   tools_loadmarker

Create Marker
-------------

Create a default Marker node under the active viewport's camera.

.. note::
    Default Maya cameras (such as ``persp``, ``top``, ``front``, etc)
    are not supported.

Run this Python command:

.. code:: python

    import mmSolver.tools.createmarker.tool as createmarker_tool
    createmarker_tool.main()

Convert to Marker
-----------------

Converts the selected transform nodes into screen-space Markers, as
viewed though the active viewport camera.

The created markers are named based on the selected transform nodes, and
are parented under the active viewport camera.

Run this Python command:

.. code:: python

    import mmSolver.tools.convertmarker.tool as convertmarker_tool
    convertmarker_tool.main()

Create Bundle
-------------

Create a default Bundle node.

If Markers are selected, the Bundle will attempt to attach to it, while
adhering to the rule; *a bundle can only have one marker representation
for each camera.*

Run this Python command:

.. code:: python

    import mmSolver.tools.createbundle.tool as createbundle_tool
    createbundle_tool.main()

Link Marker + Bundle
--------------------

Link the selected Marker and Bundle together.

The link will not succeed if the selected Bundle is already connected to
a Marker with the same camera, or in other words; A bundle can only have
one Marker per-camera. This tool checks and adheres to this requirement.

Run this Python command:

.. code:: python

    import mmSolver.tools.linkmarkerbundle.tool as link_mb_tool
    link_mb_tool.link_marker_bundle()

Unlink Marker from all Bundles
------------------------------

Unlink all the Bundles from all selected Markers.

Run this Python command:

.. code:: python

    import mmSolver.tools.linkmarkerbundle.tool as link_mb_tool
    link_mb_tool.unlink_marker_bundle()

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

Center 2D On Selection
----------------------

Forces the active viewport camera to lock it’s center to the currently
selected transform node.

A viewport camera can only center on one node at a time.

Usage (to *apply* centering effect):

1) Select transform node.

2) Activate a 3D viewport.

3) Run tool.
   
   - The active viewport camera will be centered on the selected
     transform node.

4) Use the Pan/Zoom tool (default hotkey is '\' key), to zoom in and
   out. Play the Maya file and use the centered view as needed.

Usage (to *remove* centering effect):

1) Activate a 3D viewport.

2) Deselect all nodes.

3) Run tool.

   - The active viewport will no longer center on an object, but will
     not reset the view.

   - To reset the viewport camera, turn off Pan/Zoom on the viewport
     camera (default hotkey is '\' key).

Run this Python command:

.. code:: python

    import mmSolver.tools.centertwodee.tool as centertwodee_tool
    centertwodee_tool.main()

Aim at Camera
-------------

Aim the selected transform nodes toward the active viewport camera.

Run this Python command:

.. code:: python

   import mmSolver.tools.cameraaim.tool as cameraaim_tool
   cameraaim_tool.main()

Channel Sensitivity
-------------------

Channel sensitivity tool helps you to change the value of sensitivity
of channel slider setting.

Run this Python command:

.. code:: python

    import mmSolver.tools.channelsen.tool as tool
    tool.main()

Toggle Bundle Lock State
------------------------

Toggle bundle lock state will toggle lock state of the selected
bundle's attributes, if any of the bundles translate attributes are
locked, running this tool will unlock all attributes on the selected
bundles, and running the tool again will lock all attributes.

Usage:

1) Select bundle nodes.

2) Run tool.
   - The selected bundle node attributes will be toggled between locked and unlocked.

Run this Python command:

.. code:: python

    import mmSolver.tools.togglebundlelock.tool as tglbndlock
    tglbndlock.toggle_bundle_lock()

Average Marker
--------------

Average Marker tool will create a new Marker with an averaged position
between all the selected Markers.

This tool must have at least two Markers selected.

Usage:

1) Select 1 or more Marker nodes.
2) Run tool.
   - A third Marker node will be created between all others.

Run this Python command:

.. code:: python

    import mmSolver.tools.averagemarker.tool
    mmSolver.tools.averagemarker.tool.main()

Duplicate marker
----------------

Duplicate marker tool will create a new markers having same position
from the selected markers, this tool will duplicate on all selected
markers.

Run this Python command:

.. code:: python

    import mmSolver.tools.duplicatemarker.tool
    mmSolver.tools.duplicatemarker.tool.main()

Screen-Z Manipulator
--------------------

Aims the move manipulator tool at the active viewport camera.
After aiming the move tool at the camera, the screen-space Z axis is
highlighted, ready to be middle-click dragged

Run this Python command:

.. code:: python

    import mmSolver.tools.screenzmanipulator.tool
    mmSolver.tools.screenzmanipulator.tool.main()

