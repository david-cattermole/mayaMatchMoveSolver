Display Tools
=============

The tools on this page are not specific to Markers, Cameras or
Bundles, but are general tools useful in Maya for many different
tasks.

.. _center-2d-on-selection-tool-ref:

Center 2D On Selection
----------------------

Forces the active viewport camera to lock it’s center to the currently
selected transform node.

A viewport camera can only center on one node at a time.

While centering is turned on, it overrides Maya's normal 2D Pan/Zoom
settings.

Usage to *apply* the centering effect:

1) Select transform node.

2) Activate a 3D viewport.

3) Run 'Apply 2D Center' tool.

   - The active viewport camera will be centered on the selected
     transform node.

4) Use the Pan/Zoom tool (default hotkey is backslash (' \\ ') key),
   to zoom in and out. Play the Maya timeline and use the centered view as
   needed.

Usage to *remove* centering effect:

1) Run 'Remove 2D Center' tool.

   - The active viewport will no longer center on an object, but will
     not reset the view.

   - The pan/zoom will still be active. To reset the viewport camera,
     turn off Pan/Zoom on the viewport camera (default hotkey is
     backslash (' \\ ') key).

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.centertwodee.tool as tool

    # Apply Centering onto active camera
    tool.main()

    # Remove Centering from active camera
    tool.remove()


.. _set-object-colour-tool-ref:

Set Object Colour / Reset Object Colour
---------------------------------------

*To be written*

Usage:

1) ...


To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.setobjectcolour.tool as tool
    tool.main()


.. _create-screen-space-motion-trail-tool-ref:

Create Screen-Space Motion Trail
--------------------------------

The Screen-Space Motion Trail tool creates a non-editable curve that
shows the screen-space position of a transform across multiple frames.

With default options the tool can be used to visualise the shutter
time of a Marker (or any other transform), assuming a shutter angle of
180 degrees (half a frame).

The user may change the default options after the motion trail is
created by selecting the Motion Trail node under the camera and
editing the attributes in the Channel Box.

Beware of small *increment* values, and large frame ranges. These will
cause slow-downs in the playback of the Maya scene.

.. list-table:: Motion Trail Attributes
   :widths: auto
   :header-rows: 1

   * - Attribute
     - Type
     - Description

   * - Use Frame Range
     - On/Off
     - Use the frame range, or the pre/post-frame values.

   * - Pre-Frame
     - Number
     - The number of frames to display before the current frame.

   * - Post-Frame
     - Number
     - The number of frames to display after the current frame.

   * - Frame Range Start
     - Number
     - The starting frame number, if Use Frame Range is on.

   * - Frame Range Start
     - Number
     - The ending frame number, if Use Frame Range is on.

   * - Increment
     - Number
     - The increment for each sample of the motion trail.

Usage:

1) Select transform nodes.

2) Activate viewport.

3) Run tool.

4) A temporary null is created (required for the tool to work), and a
   motion trail parented under the camera is created.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.screenspacemotiontrail.tool as tool
    tool.main()
