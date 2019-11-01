Node Creation Tools
===================

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

