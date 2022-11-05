Camera Tools
============

Camera tools are tools specifically designed to create or edit cameras
in some way.

.. _toggle-camera-lens-distortion-tool-ref:

Toggle Camera Lens Distortion
-----------------------------

The `Toggle Camera Lens Distortion` tool is used to quickly enable or
disable the effect of lens distortion on `Markers` and/or `MM
ImagePlane` nodes.

Usage:

1) Activate 3D Viewport or select camera node(s).

2) Run tool (with shelf or menu).

   - The effect of lens distortion for the given cameras is toggled;
     all Markers and MM ImagePlanes will have lens distortion enabled
     or disabled.

   - Press the Maya "g" hotkey on your keyboard to repeat the last
     command, to toggle back and forth.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.togglecameradistort.tool as tool
    tool.main()


.. _set-camera-origin-frame-tool-ref:

Set Camera Origin Frame
-----------------------

*To be written*

.. figure:: images/tools_set_camera_origin_frame.png
    :alt: Node Solver Shelf Icons
    :align: center
    :width: 60%

Usage:

1) ...


To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.setcameraoriginframe.tool as tool
    tool.main()
