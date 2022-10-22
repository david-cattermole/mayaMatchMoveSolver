Input/Output Tools
==================

The tools on this page are used to import and export data from Maya
using mmSolver.

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
