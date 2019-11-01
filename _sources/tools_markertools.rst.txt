Marker Tools
============

The tools used to manipulate 2D Marker nodes.

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

    import mmSolver.tools.togglemarkerlock.tool as tool
    tool.toggle_marker_lock()

Place Marker Manipulator
------------------------

Place a Marker at a position of a mouse click.

Usage:

1) Click to active a 3D Maya Viewport containing Marker nodes.

2) Select one or more Marker nodes in the viewport.

3) Run tool.

   - The current tool will change to `Place Marker`.

4) Left-click in the viewport to place the Marker node under the
   mouse.

   - The user may also hold the left-click button down to move the
     Marker to a new screen position in real-time.

Run this Python command:

.. code:: python

    import mmSolver.tools.placemarkermanip.tool as tool
    tool.main()

Duplicate Marker
----------------

Duplicate marker tool will create a new markers having same position
from the selected markers, this tool will duplicate on all selected
markers.

Usage:

1) Select Marker nodes

2) Run tool.

   - New Marker nodes are created as exact copies of the selected Marker nodes.

Run this Python command:

.. code:: python

    import mmSolver.tools.duplicatemarker.tool
    mmSolver.tools.duplicatemarker.tool.main()

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

Project Marker on Mesh (Ray-Cast)
---------------------------------

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

1) Select Markers.

2) (Optional) Select Mesh nodes.

   - Selecting Mesh nodes will limit the nodes used for ray-casting
     computation.

3) Run tool.

   - The Bundles connected to the selected Markers will be projected
     from the currently active viewport camera onto the mesh in the
     scene

Run this Python command:

.. code:: python

    import mmSolver.tools.raycastmarker.tool as tool
    tool.main()

Deform Marker
-------------

Marker Deformation is a process of offsetting a Marker's 2D position
at specific times, and allowing higher-frequency positional data to
flow in-between the specific times.

Usage:

1) Select Marker nodes.

2) Run 'Deform Create' tool.

   - The selected Marker nodes are added into the Deform mode.

   - A new Maya Animation Layer is created if it does not exist.

3) Modify the Marker node's 2D position.

4) Select Marker node(s).

4) Run 'Deform Bake' tool.

   - Sets keys for the Marker's 2D position deformation.

5) Run 'Deform Remove' tool

   - Removes the Deformation Maya Animation Layer.

Run this Python command:

.. code:: python

    import mmSolver.tools.deformmarker.tool as tool

    # Deform Create
    tool.create_offset_layer()
    
    # Deform Bake
    tool.bake_offset()

    # Deform Remove
    tool.remove_layer_override()


Show / Hide Deviation Curves
----------------------------

Show and Hide the Deviation (error level) curves that is saved on the Marker nodes.

1) Select Marker nodes.

2) Run 'Show Deviation Curves' tool.

   - The Maya Graph Editor will be displayed, with only deviation
     curves visible.

3) Once you are finished reviewing the Marker Deviation curves, run
   'Hide Deviation Curves' tool to revert the Maya Graph Editor to
   normal visibility.

Run this Python command:

.. code:: python

    import mmSolver.tools.showdeviationcurves.tool as tool

    # Show Deviation Curves
    tool.show_deviation()

    # Hide Deviation Curves
    tool.hide_deviation()
