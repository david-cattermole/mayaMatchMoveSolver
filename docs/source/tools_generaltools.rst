General Tools
=============

The tools on this page are not specific to Markers, Cameras or
Bundles, but are general tools useful in Maya for many different
tasks.

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
   to zoom in and out. Play the Maya file and use the centered view as
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

Smooth Keyframes
----------------

Smooth the selected keyframes in the Graph Editor, along with a UI to
change the affect of the Smoothing function. The UI values are saved
into the home directory and will be re-used when a new Maya session is
opened.

The Smooth Keyframes tool allows smoothing of only specific keyframes,
even if the curve is not baked per-frame. The tool will also attempt
to control the smoothed values as they blend into unsmoothed
values. This allows smoothing a specific area of an animation curve,
while preserving other parts and avoiding bumps at the boundry.

Usage:

1) Use the menu ``mmSolver > General Tools > Smooth Keyframes UI``.

2) Edit the options in the UI.

   - *Function* controls the type of smoothing that is calculated.

   - *Smooth Width* controls how much the smoothing function will be
     applied. The width is number of frames to be used for smoothing,
     for example a value of 1 means "no smoothing", a value of 2 means
     "use previous and next frame", and 5 means "use previous 4 and
     next 4 frames".

   - *Blend Width* controls the blend, in frames, between the smoothed
     values and the surrounding values.

3) Select keyframes in Graph Editor.

4) Run 'Smooth Selected Keyframes' tool.

5) Keyframe values will be smoothed.

6) Repeat steps 3 to 5 as required.

You can use the below Python code on a hotkey of your choosing. To
run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.smoothkeyframes.tool as tool

    # Smooth the selected Keyframes
    tool.smooth_selected_keyframes()

    # Open the Smooth Keyframes UI.
    tool.main()

Blend Width
+++++++++++

When the *Smooth Keyframes* tool is run the selected keyframes are
smoothed as well as frames surrounding the selected keyframes. The
surrounding keyframes are blended together with the smoothed
keyframes. The *Blend Width* value controls the number of frames to
blend.

The image below shows the effect of the *Blend Width* value.

.. figure:: images/tools_smooth_keyframes_blend.gif
    :alt: Selected Keyframes Blending Value
    :align: center
    :width: 90%

Function Average
++++++++++++++++

The *Average* smoothing function will average the surrounding keyframe
values equally.

The image below shows the effect of the *Smooth Width* with the
*Average* function.

.. figure:: images/tools_smooth_keyframes_average.gif
    :alt: Smooth Keyframes with Average
    :align: center
    :width: 90%

            Function Gaussian
+++++++++++++++++

The *Gaussian* smoothing function performs a strong smooth on the
keyframes. The *Gaussian* function can be used to make a curve very
flat, without any changes. Unlike the *Fourier* function, the
*Gaussian* function will change already smooth keyframes.

This function is similar to 2D image Gaussian blurring.

The image below shows the effect of the *Smooth Width* with the
*Gaussian* function.

.. figure:: images/tools_smooth_keyframes_gaussian.gif
    :alt: Smooth Keyframes with Gaussian
    :align: center
    :width: 90%

Function Fourier
++++++++++++++++

The *Fourier* smoothing function performs a high-pass-filter to the
selected keyframes. Keyframes with rapid changes are smoothed more
than already smoothed values.

This function is similar to 2D image high-pass filtering techniques,
to remove *high-contrast* edge detail.

The image below shows the effect of the *Smooth Width* with the
*Fourier* function.

.. figure:: images/tools_smooth_keyframes_fourier.gif
    :alt: Smooth Keyframes with Fourier
    :align: center
    :width: 90%

.. _screen-space-transform-ref:

Screen-Space Transform
----------------------

Convert a Maya transform node into a screen-space transform. This tool
will not modify the originally selected node, but will only create a
new node with new values.

When converting to Screen-Space the Screen Depth is calculated and the
transform node will still match the original transform in World-Space.

This tool may be used to convert an animated object into a
screen-space, then clean up or solve specific attributes, such as
screen X/Y or screen depth.

Usage:

1) Select transform nodes.

2) Activate viewport.

3) Run *Screen-Space Transform Bake* tool.

   - A new locator is created under the active Camera.

4) Delete the keyframes/connects on the selected transform node, using
   ``Channel Box > (Right Click) > Break Connections``.

5) Use a Maya *Point Constraint* to drive the transform(s) from step
   1, with the screen-space transform as the driver.

   - Select screen-space transform node first, then select (step 1)
     transform nodes second and create a *Point Constraint*.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.screenspacetransform.tool as tool
    tool.main()

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

Beware of small `increment` values, and large frame ranges. These will
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

Channel Sensitivity
-------------------

Channel sensitivity tool helps you to change the value of sensitivity
of channel slider setting. Using this tool the user to adjust
attributes in the Channel Box by very small increments, which is
useful for manually adjusting or matching parameters interactively.

Usage:

1) Run tool.

   - A UI will open, click the `Increase` or `Decrease` buttons to
     change the sensitivity.

2) Select an Attribute in the Channel Box.

3) Middle-mouse drag in the viewport to change the attribute value.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.channelsen.tool as tool
    tool.main()

Copy Camera to Clipboard
------------------------

Saves the selected camera node into a temporary file and saves the
file path onto the OS Copy/Paste clipboard.

Usage:

1) Select a Maya camera.

2) Run tool.

3) Open 3DEqualizer

4) Select Camera in Object Browser.

5) Right-click and run "Paste Camera (MM Solver)...".

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.copypastecamera.tool as tool
    tool.main()

Marker Bundle Rename
--------------------

Renames selected markers and bundles connected, takes the input name
given in prompt window.

Usage:

1) Select Marker (or Bundle) nodes.

2) Run tool.

   - A prompt is displayed to enter the new name for the Marker and Bundles.

   - If the prompt is left at the default value ``marker``, then the
     Markers will named ``marker`` and Bundles will be named
     ``bundle``.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.markerbundlerename.tool as tool
    tool.main()

Marker Bundle Rename (with Metadata)
------------------------------------

Renames the selected Markers and Bundles using only the metadata saved
onto the Marker nodes.

For example, metadata from 3DEqualizer is saved onto the Marker node.

Usage:

1) Select Marker (or Bundle) nodes.

2) Run tool.

   - Markers and Bundles are renamed based on metadata, if metadata is
     not found, the Marker/Bundle is not renamed.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.markerbundlerenamewithmetadata.tool as tool
    tool.main()

Reparent Under Node
-------------------

This is equalivent to Maya's *Parent* tool (`p` hotkey), except the
tool will maintain the world-space position of the transform node for
each keyframe applied to the node.

Usage:

1) Select nodes to change parent, then select the new parent node.

   - The first nodes will become the children of the last selected node.

   - The last node is the new parent.

2) Run tool.

   - The first nodes are now parented under the last selected node,
     and will stay in the same position in world-space for all
     keyframes.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.reparent.tool as tool
    tool.reparent_under_node()

Unparent to World
-----------------

This is equalivent to Maya's *Unparent* tool (`Shift + p` hotkey), except the tool will
maintain the world-space position of the transform node for each
keyframe applied to the node.

Usage:

1) Select Maya transform node(s).

   - The nodes may be in a deep hierarchy, or not.

2) Run tool.

   - The nodes will maintain the same world-space position, but will
     be unparented into root Maya Outliner (the nodes will not be
     parented under any node).

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.reparent.tool as tool
    tool.unparent_to_world()

Create / Remove Controller
--------------------------

Create a new transform node to control another node. The `Controller`
transform node can have a separate hierarchy than the source node.

Usage:

1) Select a Maya transform node.

2) Run 'Create Controller' tool.

   - A new 'Controller' locator node is created at the same position
     as the source transform.

3) Select and move the created Controller as you wish.

4) Select the Controller, run 'Remove Controller' tool.

   - The source node is baked at the same times as the Controller is
     keyed, and the Controller is deleted.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.createcontroller.tool as tool

    # Create a Controller
    tool.create()

    # Remove selected Controller
    tool.remove()
