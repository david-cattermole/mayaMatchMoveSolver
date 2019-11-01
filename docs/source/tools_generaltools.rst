General Tools
=============

Smooth Keyframes
----------------

Smooth the selected keyframes in the Graph Editor.

Usage:

1) Select keyframes in Graph Editor.

2) Run tool.

3) Keyframe values will be smoothed.


Run this Python command:

.. code:: python

    import mmSolver.tools.smoothkeyframes.tool as smoothkeys_tool
    smoothkeys_tool.main()

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

Channel Sensitivity
-------------------

Channel sensitivity tool helps you to change the value of sensitivity
of channel slider setting.

Run this Python command:

.. code:: python

    import mmSolver.tools.channelsen.tool as tool
    tool.main()
