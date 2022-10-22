Input/Output Tools
==================

The tools on this page are not specific to Markers, Cameras or
Bundles, but are general tools useful in Maya for many different
tasks.

.. _copy-camera-to-clipboard-tool-ref:

Copy Camera to Clipboard
------------------------

Saves the selected camera node into a temporary file and saves the
file path onto the OS Copy/Paste clipboard.

Usage:

1) Select a Maya camera.

2) Run tool.

3) Open 3DEqualizer

4) Select Camera in Object Browser.

5) Right-click and run *Paste Camera (MM Solver)...*.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.copypastecamera.tool as tool
    tool.main()
