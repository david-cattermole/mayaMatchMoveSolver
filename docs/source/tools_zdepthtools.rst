Z-Depth Tools
=============

The tools on this page are not specific to Markers, Cameras or
Bundles, but are general tools useful in Maya for many different
tasks.

.. _screen-z-manipulator-tool-ref:

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
please use the :ref:`screen-space-transform-tool-ref` tool.

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

.. _screen-space-transform-tool-ref:

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

.. _screen-space-rig-bake-tool-ref:

Screen-Space Rig Bake
---------------------

The `Screen-Space Rig Bake` tool allows users to bake and manipulate
transforms with a `screen-space` rig, separating the X, Y and Z-Depth
components.

The tool can be use to:

- Smooth a bumpy Z-depth curve.

- Freeze a transform to a static Z-depth.

.. figure:: images/tools_screen_space_rig_bake_ui.png
    :alt: Screen-Space Rig Bake UI
    :align: center
    :width: 80%

Usage:

1) Select a transform node.

2) Open the `Screen-Space Rig Bake` UI.

3) Type a name in the `Name` field (at the bottom of the window).

4) Right-click the `Rigs` pane and select `Create Screen-Space Rig`.

   - Make sure to activate the viewport with a camera to bake the
     object into.

   - A set of nodes named `NAME_screenSpaceRig` will be created.

5) Edit the created `NAME_screenSpaceRig` node.

6) Once finished editing, open the UI again, select the screen-space
   rig control, right-click the `Rigs` pane and select `Bake Rig`.

   - This will bake the original transform node, and delete the nodes.

   - Set the option `Full bake` or `Smart bake` to choose how many
     keyframes will be baked.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.screenspacerigbake.tool as tool
    tool.open_window()

.. _adjust-camera-object-scale-tool-ref:

Adjust Camera/Object Scale
--------------------------

The `Adjust Camera/Object Scale` tool is used to change the scale of a
camera matchmove while maintaining the matchmove of a object, or vice
versa.

This tool is very helpful for correcting the scale/depth of a camera
or object. When the camera scale is known (because LiDAR geometry was
used during camera solving), the object scale can be adjusted. If an
object with a known scale is visible in a camera, the camera scale can
be adjusted to match the object.

.. figure:: images/tools_camera_object_scale_adjust_ui.png
    :alt: Adjust the scale of a Camera/Object
    :align: center
    :width: 80%

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.cameraobjectscaleadjust.tool as tool
    tool.open_window()

Scale a Camera
++++++++++++++

In this example, the object will stay same scale, and the camera will be scaled.

Usage:

1) Set your current frame to the frame you want to scale/pivot from.

2) Open the `Adjust Camera/Object Scale` UI.

   - Type a unique name for `Scale Rig Name`.

   - Choose `Adjust Camera Scale` mode.

   - Select the top level `Scene` node that contains all 3D
     transforms/bundles.

   - Select the `Camera` that will adjust scale.

   - Select the `Objects` that will `not` change scale.

3) Press `Create` button.

4) Move your current frame to a frame where parallax can be seen in
   the camera, and use the Maya Scale manipulator tool to scale newly
   created Scale Rig until the desired scale is found.

5) When desired scale is found, select the created `Scale Rig` and use
   the `Remove Camera/Object Scale` tool.

Scale an Object
+++++++++++++++

In this example camera will stay the same scale, and the object will
be scaled.

Usage:

1) Set your current frame to the frame you want to scale/pivot from.

2) Open the `Adjust Camera/Object Scale` UI.

   - Type a unique name for `Scale Rig Name`.

   - Choose `Adjust Object Scale` mode.

   - Select the `Camera` that will `not` change scale.

   - Select the `Objects` that will adjust scale.

3) Press `Create` button.

4) Move your current frame to a frame where parallax can be seen in
   the camera, and use the Maya Scale manipulator tool to scale newly
   created Scale Rig until the desired scale is found.

5) When desired scale is found, select the created `Scale Rig` and use
   the `Remove Camera/Object Scale` tool.
