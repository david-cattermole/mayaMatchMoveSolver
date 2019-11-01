Bundle Tools
============

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

Re-Project Bundle
-----------------

Position Bundle under the Marker, in screen-space.

Usage:

1) Select Markers or Bundles

3) Run tool.

Run this Python command:

.. code:: python

    import mmSolver.tools.reprojectbundle.tool as reprojbnd_tool
    reprojbnd_tool.main()

Triangulate Bundle
------------------

Calculate a 3D position of a bundle, based on the camera and 2D marker.

Usage:

1) Select Markers or Bundles

3) Run tool.


Run this Python command:

.. code:: python

    import mmSolver.tools.triangulatebundle.tool as tribnd_tool
    tribnd_tool.main()

Aim at Camera
-------------

Aim the selected transform nodes toward the active viewport camera.

.. note::

    This tool is deprecated. Use the "Screen-Z Manipulator" tool
    instead.

Run this Python command:

.. code:: python

    import mmSolver.tools.cameraaim.tool as cameraaim_tool
    cameraaim_tool.main()

Screen-Z Manipulator
--------------------

Aims the move manipulator tool at the active viewport camera.
After aiming the move tool at the camera, the screen-space Z axis is
highlighted, ready to be middle-click dragged

Run this Python command:

.. code:: python

    import mmSolver.tools.screenzmanipulator.tool
    mmSolver.tools.screenzmanipulator.tool.main()

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
