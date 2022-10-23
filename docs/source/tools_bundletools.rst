Bundle Tools
============

The tools used to manipulate 3D Bundle nodes.

.. _toggle-bundle-lock-state-tool-ref:

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
    tool.main()

.. _move-bundle-to-marker-tool-ref:

Move Bundle to Marker (current frame)
-------------------------------------

Moves the Bundle under it's attached Marker, in screen-space. This
will make the Marker and Bundle line up perfectly, but will remove
depth information from the Bundle. This tool only works on the
**current frame**.

The Bundle is placed at a distance 10 times the distance between the
Camera and Marker.

An alternative name for this tool is `Re-Project Bundle`.

Usage:

1) Select Markers or Bundles

2) Run tool.

Run this Python command:

.. code:: python

    import mmSolver.tools.reprojectbundle.tool as tool
    tool.main()

.. _triangulate-bundle-tool-ref:

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

.. _attach-bundle-to-curve-tool-ref:

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
