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

2) Run tool.

Run this Python command:

.. code:: python

    import mmSolver.tools.reprojectbundle.tool as tool
    tool.main()

Triangulate Bundle
------------------

Calculate a 3D position of a bundle, based on the camera and 2D markers.

The *Triangulate Bundle* tool will calculate a 3D position for a
bundle, based on the 2D positions of the Markers.

The current implementation uses the first and last enabled frames of
the Marker to calculate the triangulation. No iterative solver is used
for the triangulation.

Usage:

1) Select Markers or Bundles (or both)

2) Run *Triangulate Bundle* tool.

   - The Bundles are triangulated in TX, TY and TZ.

Run this Python command:

.. code:: python

    import mmSolver.tools.triangulatebundle.tool as tool
    tool.main()

Aim at Camera
-------------

Aim the selected transform nodes toward the active viewport camera.

Usage:

1) Select a transform node.

2) Select active viewport.

3) Run *Aim at Camera* tool.

   - The selected transform nodes will be aimed at the active
     viewport's camera.

.. note::

    This tool is deprecated and hidden from the menus. Use the
    "Screen-Z Manipulator" tool instead.

Run this Python command:

.. code:: python

    import mmSolver.tools.cameraaim.tool as tool
    tool.main()

Screen-Z Manipulator
--------------------

Aims the Maya *Move manipulator* tool at the active viewport camera.

After aiming the move tool at the camera, the screen-space Z axis is
highlighted, ready to be middle-click dragged. When the user
de-selects the object, the previous manipulator mode is reverted.

This tool can be used for interactive node depth editing on a single
frame. For example this tool can be used for a character's hand, or or
body control, it does not need to be used with mmSolver nodes.  For
real-time interactive Screen-Space modifications of transform nodes,
please use the :ref:`screen-space-transform-ref` tool.

Usage:

1) Select a transform node.

2) Run *Screen-Z Manipulator* tool.

   - The current tool is changed to *Move*.

3) Middle-click in the active viewport to move the object in
   screen-space depth.

4) De-select the node.

   - The *Move* manipulator will be reverted to the previous settings
     from step 1.

Run this Python command:

.. code:: python

    import mmSolver.tools.screenzmanipulator.tool
    mmSolver.tools.screenzmanipulator.tool.main()

Attach Bundle to Curve
----------------------

The *Attach Bundle to Curve* tool will connect a Bundle to Maya NURBS
curve, and provide an attribute *Along Curve* used to position the
Bundle along the curve.

The *Along Curve* attribute can be solved in mmSolver with other
parameters, and may be solved either static or animated.

Usage:

1) Select a NURBS curve and a Bundle node

2) Run *Attach Bundle to Curve* tool.

   - The Bundle TX, TY, and TZ are connected to the NURBS curve.

   - An *Along Curve* attribute is created.

3) Add *Along Curve* attribute into the Solver UI.

4) Solve the *Along Curve* attribute.

   - The *Along Curve* attribute may be solved animated or static.

.. note::

    The Bundle will be connected to the curve in world-space. This
    means the bundle may be unparented from any transform and will
    still follow the curve in world-space.

Run this Python command:

.. code:: python

    import mmSolver.tools.attachbundletocurve.tool
    mmSolver.tools.attachbundletocurve.tool.main()
