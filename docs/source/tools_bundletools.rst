Bundle Tools
============

The tools used to manipulate 3D Bundle nodes.

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

    import mmSolver.tools.togglebundlelock.tool as tool
    tool.toggle_bundle_lock()

Move Bundle to Marker (current frame)
-------------------------------------

Moves the Bundle under it's attached Marker, in screen-space. This
will make the Marker and Bundle line up perfectly, but will remove
depth information from the Bundle.

An alternative name for this tool is `Re-Project Bundle`.

Usage:

1) Select Markers or Bundles

3) Run tool.

Run this Python command:

.. code:: python

    import mmSolver.tools.reprojectbundle.tool as tool
    tool.main()

Triangulate Bundle
------------------

Calculate a 3D position of a bundle, based on the camera and 2D marker.

Usage:

1) Select Markers or Bundles

3) Run tool.


Run this Python command:

.. code:: python

    import mmSolver.tools.triangulatebundle.tool as tool
    tool.main()

Aim at Camera
-------------

Aim the selected transform nodes toward the active viewport camera.

.. note::

    This tool is deprecated and hidden from the menus. Use the
    "Screen-Z Manipulator" tool instead.

Run this Python command:

.. code:: python

    import mmSolver.tools.cameraaim.tool as tool
    tool.main()

Screen-Z Manipulator
--------------------

Aims the move manipulator tool at the active viewport camera.
After aiming the move tool at the camera, the screen-space Z axis is
highlighted, ready to be middle-click dragged

Run this Python command:

.. code:: python

    import mmSolver.tools.screenzmanipulator.tool
    mmSolver.tools.screenzmanipulator.tool.main()

Attach Bundle to Curve
----------------------

Run this Python command:

.. code:: python

    import mmSolver.tools.attachbundletocurve.tool
    mmSolver.tools.attachbundletocurve.tool.main()
    
