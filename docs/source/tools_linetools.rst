Line Tools
==========

Line tools offer the ability to create and edit 2D lines on an
image. These 2D lines can be used visualise straight lines and solve
lens distortion, and are used as part of the Camera Calibration
tool-set.

.. _toggle-line-lock-state-tool-ref:

Toggle Line Lock State
------------------------

Toggle line lock state will toggle lock state of the selected line's
attributes, if any of the lines attributes are locked, running this
tool will unlock all attributes on the selected lines, and running the
tool again will lock all attributes.

Usage:

1) Select line nodes, or the markers/bundles below a line node.

2) Run tool.

   - The selected line node attributes will be toggled between locked and unlocked.

Run this Python command:

.. code:: python

    import mmSolver.tools.togglelinelock.tool as tool
    tool.main()


.. _subdivide-line-tool-ref:

Subdivide Line
--------------

The `Subdivide Line` tool is used to add more 2D points (`Markers`) to
an existing `Line` to define a straight line in an image with lens
distortion.

.. note:: To display a straight line select the ``mmLineShape`` shape
   node and enable `Draw Middle`.

Usage:

1) Select `Line` or `Markers` on a `Line`.

2) Run tool.

   - New `Markers` are created on the `Line` and selected.

3) Re-position the created `Markers` to match a straight line visible
   in an image plane.

4) Use :ref:`Solver UI <solver-ui-ref>` with `Line Markers` to solve
   `Lens` distortion attributes.


To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.subdivideline.tool as tool
    tool.main()

.. _camera-calibration-tool-ref:

Camera Calibration
------------------

The Camera calibration toolset can be used to estimate the position
and rotation of a camera using parallel lines in an image - as is
common in city-scape or architectural photographs.

No 3D (survey or LIDAR) information of the 3D scene is required, this
tool works from a single image only.

Other terms for this "calibration" process is camera "line up".

.. _camera-calibration-use-cases-tool-ref:

Calibration Use Cases
~~~~~~~~~~~~~~~~~~~~~

The tool is very helpful for as an aid for modeling buildings or any
other environment that contains a flat rectangular surface.

.. _camera-calibration-use-cases-one-point-tool-ref:

Calibration Use Cases - One Point Perspective
+++++++++++++++++++++++++++++++++++++++++++++

.. list-table::

    * - .. figure:: https://upload.wikimedia.org/wikipedia/commons/7/75/SketchVP.jpg
            :alt: Diagram of one point perspective
            :align: center
            :scale: 50%

        Diagram of one point perspective.

      - .. figure:: https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Railroad_in_Northumberland_County%2C_Pennsylvania.JPG/512px-Railroad_in_Northumberland_County%2C_Pennsylvania.JPG
            :alt: Photograph of one point perspective.
            :align: center
            :scale: 50%

        Photograph of one point perspective.

With 2 parallel lines the image contains one point perspective: also
known as one vanishing point.

In this case the tool can estimate the translation and rotation (tilt
and pan) of the camera, but a known lens focal length and camera film
back must be given - field of view cannot be estimated.

Additional to the one vanishing point, the tool can use a horizon line
to estimate the camera roll.

.. _camera-calibration-use-cases-two-point-tool-ref:

Calibration Use Cases - Two Point Perspective
+++++++++++++++++++++++++++++++++++++++++++++

.. list-table::

    * - .. figure:: https://upload.wikimedia.org/wikipedia/commons/4/4e/Perspective1.jpg
            :alt: Diagram of two point perspective.
            :align: center
            :scale: 50%

        Diagram of two point perspective.

      - .. figure:: https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/2016_Parker_Building_-_Davenport%2C_Iowa.jpg/1024px-2016_Parker_Building_-_Davenport%2C_Iowa.jpg
            :alt: Photograph of two point perspective.
            :align: center
            :scale: 50%

        Photograph of two point perspective.

With 2 sets of perpendicular parallel lines (4 lines all together),
will create two point perspective; two vanishing points.

With these
extra lines the tool can estimate the camera translation, rotation
(tilt, pan, and roll), and lens focal length. The horizon line is not
used when two vanishing points are used.

A common type of image with perpendicular lines is a bathroom tiles,
or the ground or wall of a room. The tiles, walls or ground do not
need to square.

.. _camera-calibration-tool-usage-tool-ref:

Tool Usage
~~~~~~~~~~

.. figure:: images/tools_camera_calibration_setup.png
    :alt: Camera Calibration Setup
    :align: center
    :width: 90%

1) Create a Calibration set up with the ``mmSolver > Line Tools >
   Create Camera Calibration Setup`` menu.

2) Select the ``mmImagePlane1`` node and set the image to point to your image(s).
   Add image plane file path.

3) Select the ``calibrationCamera`` node, and navigate to the
   ``mmCameraCalibrate1`` node - this node is reponsible for
   calculating the camera translation, rotation, focal length, and
   film back (camera aperture).

   - Change *Calibration Mode* depending on how many lines you can see
     in your image: ``OneVanishingPoint``,
     ``OneVanishingPointAndHorizon`` or ``TwoVanishingPoints``. See
     :ref:`Calibration Use Cases
     <camera-calibration-use-cases-tool-ref>` (above) to understand
     the meaning of vanishing points. This value changes which *Axis*
     lines are used to compute the camera calibration and imposes
     limitations on what can be computed by the tool - for example the
     Camera focal length cannot be estimated using only 1 vanishing
     point.

   - Change *Camera Aperture* width if the value is known.

   - Change *Image Pixel Aspect Ratio* to a value other than 1.0 (such
     as 2.0 or 1.8) depending on the shot/image you are using. For
     example if your image was captured using an Anamorphic lens and
     the input image is not "desqueezed" set your pixel aspect ratio
     here.

4) Set the lines based on the parallel lines in the shot.

   - Move the ``origin_point`` to the intended (2D) origin. This 2D
     point is where the 3D origin (0.0, 0.0, 0.0) will be placed. For
     example, place the origin at a corner of a building to make it
     easier to easily create models that line up with the corner of
     the building.

   - Select Markers under ``axis1_lineA_LN`` and adjust to align the
     Line with the a parallel line that is visible in your
     shot. Repeat for ``axis1_lineB_LN`` so that both lines are aimed
     along the same axis.

   - If the *Calibration Mode* is ``TwoVanishingPoints``, align the
     ``axis2`` lines as well.

   - If the *Calibration Mode* is ``OneVanishingPointAndHorizon``,
     unhide ``horizon_line_LN`` and set the line to match the horizon
     line.

5) "Update" the calibration with the ``mmSolver > Line Tools > Update
   Camera Calibration`` menu to calculate the camera orientation.

6) Repeat steps 3 to 5 until the desired calibration is found.

   - If the parallel lines in your image are long enough, you can
     estimate lens distortion values using the following steps.

8) Select the Line nodes in the Outliner and use the
   :ref:`subdivide-line-tool-ref` tool to add more Markers to define the
   line.

   - Move the Markers to match the straight edges in your image and
     repeat by adding more Markers as needed.

9) Select the camera node in the Outliner and use the *Camera Context
   Menu* to add a *Lens* to the camera.

10) Then open the :ref:`solver-ui-ref` and add the *Lines* you want to
    solve with to the *Input Objects*.

11) Select the lens distortion attributes (in the channel box), and
    add them to the Solver UI *Output Attributes*.

12) Switch to the :ref:`standard-solver-tab-heading` and press
    *Solve*.

13) After the lens distortion is solved, use ``mmSolver > Line Tools >
    Update Camera Calibration`` menu to update the camera again with
    the straightened lines.

.. _camera-calibration-node-options-tool-ref:

Node Options
~~~~~~~~~~~~

The *Camera Calibration* tool is driven by the `mmCameraCalibrate`
node and calculates the camera translation, rotation, and focal
length. The options below explain how the camera values are calculated
using this.

.. figure:: images/tools_camera_calibration_node_options.png
    :alt: Calibration Node Options
    :align: center
    :width: 60%

.. list-table:: Calibration Node Options
   :widths: auto
   :header-rows: 1

   * - Attribute
     - Description

   * - Calibration Mode
     - Controls how the axis lines are used to calculate the camera
       calibration. ``OneVanishingPoint`` will use just ``axis1``
       lines to calculate the camera tilt and pan (rotation X and Y)
       and translation. Addtionally ``OneVanishingPointAndHorizon``
       uses the ``horizon_line_LN`` line to define the camera roll
       (rotation Z). ``TwoVanishingPoints`` uses only ``axis1`` and
       ``axis2`` lines to compute the camera tilt, pan, roll (rotation
       X, Y and Z), translation as well as the camera focal length.

   * - Focal Length
     - Defines the camera focal length, when ``OneVanishingPoint`` or
       ``OneVanishingPointAndHorizon`` is used.

   * - Camera Aperture
     - Defines the camera aperture (film back or sensor size)
       width. The height is automatically calculated from the loaded
       image width and height.

   * - Image Width/Height
     - Used to define teh *Camera Aperture* height and is
       automatically connected to the MM Image Plane outputs.

   * - Image Pixel Aspect Ratio
     - The pixel aspect ratio of the input image. For example if your
       image was captured using an Anamorphic lens and the input image
       is not "desqueezed" set the pixel aspect ratio.

   * - Scene Scale Mode
     - The scale of the computed translation values is can be
       calculated with ``UniformScale`` or
       ``CameraHeight``. ``CameraHeight`` should be used if the height
       of camera taking the image is (roughly) known, in all other
       cases, ``Uniform Scale`` is the best option.

   * - Uniform Scale
     - When ``UniformScale`` *Scene Scale Mode* is used, this
       attribute scales the camera translations by this number.

   * - Camera Height
     - When ``CameraHeight`` *Scene Scale Mode* is used, this value
       defines the exact distance of the camera in the Y axis. Use
       this value if you know (or roughly know) the height of the
       camera. The distance is measured in Maya units.

   * - Rotate Plane
     - The calculated Camera Calibration can sometimes have a strange
       axis - for example the camera is upside down. To fix this, use
       the *Rotate Plane* to offset the axis values. Use multiples of
       90 degrees, or hold-CTRL-middle-mouse-click-drag to shift the
       values in each X, Y and Z field.

.. _camera-calibration-limitations-tool-ref:

Calibration Tool Limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tool has a number of limitations and known issues, and a future
version of mmSolver may fix or reduce these issues.

- The camera does not yet update automatically while dragging the 2D
  points.

- Only 2 vanishing points (2 sets of parallel lines or 4 lines) can be
  used.

  Some images may require 3 vanishing points, if the center of the
  lens ("principal point" or "camera film offsets") is not in the
  center of the image.

  This is fine for most use-cases with (typical) un-cropped images,
  however issues may arise when a Tilt-Shift lens was used for the
  image, or the image has been cropped non-uniformly.

  If you have this problem it is recommended to use `fSpy`_ to
  calibrate the camera, and `maya_fspy`_ to import the camera into
  Maya.


.. _fSpy:
   https://fspy.io/

.. _maya_fspy:
   https://github.com/JustinPedersen/maya_fspy
