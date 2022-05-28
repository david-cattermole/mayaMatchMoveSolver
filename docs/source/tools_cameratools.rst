Camera Tools
============

Camera tools are tools specifically designed to create or edit cameras
in some way.

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

1) Create default setup.

2) Add image plane file path.

3) Set markers for lines.

4) Press "update".

.. _camera-calibration-limitations-tool-ref:

Calibration Tool Limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tool has a number of limitations and known issues, and a future
version of mmSolver may fix or reduce these issues.

- The camera does not yet update automatically while dragging the 2D points.

- Only 2 vanishing points can be used.

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
