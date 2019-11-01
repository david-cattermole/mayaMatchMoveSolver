Marker Tools
============

Marker Bundle Rename
--------------------

Renames selected markers and bundles connected, takes the input name
given in prompt window.

Run this Python command:

.. code:: python

    import mmSolver.tools.markerbundlerename.tool
    mmSolver.tools.markerbundlerename.tool.main()

Ray-Cast Marker
---------------

Ray casts (project) the selected marker's bundle nodes on mesh nodes
from the associated camera.

Select markers and mesh objects to ray cast on, if not mesh objects
tool will ray cast on all visible mesh objects.

If a bundle translate attribute is locked, it will be unlocked, then
projected, and then the lock state will be reverted to the original
value.

The viewport camera does not need to be active for this tool to
project. The tool will work on the current frame only.

Usage:

1) Select Markers

2) (Optional) Select Mesh nodes

3) Run tool.


Run this Python command:

.. code:: python

    import mmSolver.tools.raycastmarker.tool as raycast_tool
    raycast_tool.main()

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

Toggle Marker Lock State
------------------------

Toggle marker lock state will toggle lock state of the selected
marker's attributes, if any of the marker translate attributes are
locked, running this tool will unlock translateX, translateX and
enable attributes on the selected markers, and running the tool again
will lock same attributes.

Usage:

1) Select marker nodes.

2) Run tool.
   - The selected marker node attributes will be toggled between locked and unlocked.

Run this Python command:

.. code:: python

    import mmSolver.tools.togglemarkerlock.tool as tglmkrlock
    tglmkrlock.toggle_marker_lock()

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

Duplicate Marker
----------------

Duplicate marker tool will create a new markers having same position
from the selected markers, this tool will duplicate on all selected
markers.

Run this Python command:

.. code:: python

    import mmSolver.tools.duplicatemarker.tool
    mmSolver.tools.duplicatemarker.tool.main()
