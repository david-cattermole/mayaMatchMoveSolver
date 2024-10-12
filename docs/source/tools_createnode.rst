Create Node Tools
=================

.. figure:: images/tools_shelf_icons_creation.png
    :alt: Node Creation Shelf Icons
    :align: center
    :width: 40%

Creating various nodes and objects with mmSolver uses the tools below.

.. _create-marker-ref:

Create Marker
-------------

Create a default `Marker` node under the active viewport's `Camera`.

Usage:

1) Click in a Maya 3D viewport, to activate the `Camera`.

2) Run the `Create Marker` tool, using the shelf, menu or marking menu.

   - A `Marker` will be created in the center of the viewport.

.. note::
    Default Maya cameras (such as ``persp``, ``top``, ``front``, etc)
    are not supported to create Markers.

.. note:: To create Markers, with 2D data from external 3D software
    use the :ref:`Load Markers <load-markers-ref>` tool.

Run this Python command:

.. code:: python

    import mmSolver.tools.createmarker.tool as tool
    tool.main()

.. _create-bundle-ref:

Create Bundle
-------------

Create a default `Bundle` node.

If `Markers` are selected, the `Bundle` will attempt to attach to it,
while adhering to the rule; *a bundle can only have one marker
representation for each camera.*

Run this Python command:

.. code:: python

    import mmSolver.tools.createbundle.tool as tool
    tool.main()

.. _create-line-ref:

Create Line
-----------

Create a 2D `Line` node, made up of `Markers` and `Bundles`. The `Line`
defines a straight line between all `Markers` on the `Line`.

Adjust the Marker positions to move the `Line`.

.. note:: To display a straight line select the ``mmLineShape`` shape
   node and enable `Draw Middle`.

Run this Python command:

.. code:: python

    import mmSolver.tools.createline.tool as tool
    tool.main()

.. _create-camera-ref:

Create Camera
-------------

Create a default Camera.

Run this Python command:

.. code:: python

    import mmSolver.tools.createcamera.tool as tool
    tool.main()

.. _create-lens-ref:

Create Lens
-----------

Create a `Lens` (distortion) node.

The `Lens` node is used to distort all `Markers` attached to the
`Camera` similar to how imperfections in physical lenses distorts
light (mostly at the edges) of an image.

Usage:

1) Activate 3D viewport or select camera node(s).

2) Run the `Create Lens` tool, using the shelf or menu.

3) Adjust lens node attributes as needed, or load a lens with the
   :ref:`Load Markers in Maya <load-markers-in-maya-ref>`.

Run this Python command:

.. code:: python

    import mmSolver.tools.createlens.tool as tool
    tool.main()

.. _create-imageplane-ref:

Create ImagePlane
-----------------

Create a :ref:`MM ImagePlane <imageplane-ref>` node, with the chosen
image file (sequence) used to display a flat plane with an image
texture in the Maya 3D scene.

.. figure:: images/tools_create_mm_image_plane.png
    :alt: MM Image Plane
    :align: center
    :width: 90%

Usage:

1) Activate 3D viewport or select camera node(s).

2) Run the `Create ImagePlane` tool, using the shelf or menu.

3) Browse to image file.

   - If the image is named as an image sequence (such as
     ``file.#.ext``), it will be detected and the full image sequence
     will be loaded.

To create an image plane, you can run this Python command:

.. code:: python

    import mmSolver.tools.createimageplane.tool as tool
    tool.main()

.. _imageplane-ref:

MM ImagePlane
-------------

The `MM ImagePlane` node is an improved Image Plane, designed for
MatchMove tasks, and can be created with the :ref:`Create ImagePlane
<create-imageplane-ref>` tool.

Key features:

- **Multiple Image Slots**; Switch seamlessly between 4 different
  image sequences loaded onto the `MM ImagePlane`.

- **Memory resource control**; The :ref:`Image Cache
  <image-cache-preferences-ref>` is used to limit and detail memory
  usage for the `MM ImagePlane` allowing greater control than the
  native Maya ImagePlane.

- **Real-Time Lens Distortion**; Lenses added to the camera (with
  :ref:`Create Lens <create-lens-ref>` tool) will distort the `MM
  ImagePlane` in real-time as attributes update.

- **Frame Range controls and details**; Override the first frame of an
  image sequence to any other frame, and see the output frame number
  easily for debugging.

- **Enhanced Display controls**; Adjust the exposure, gamma,
  saturation and soft-clip of the input image data, and display
  individual colour channels.

.. _imageplane-display-attributes-ref:

Display Attributes
~~~~~~~~~~~~~~~~~~

`Display Attributes` control how the `MM ImagePlane` looks in the
viewport; use these attributes to make the image easier to see.

.. figure:: images/tools_image_plane_attributes_display.png
    :alt: MM ImagePlane Display attributes.
    :align: center
    :width: 80%

.. list-table:: Display Attributes
   :widths: auto
   :header-rows: 1

   * - Name
     - Description

   * - Visible To Camera Only
     - When enabled, this imagePlane node is not visible when viewed
       by any other camera (including ``persp`` camera).

   * - Gain
     - The color of multiplier of the displayed image.

   * - Exposure
     - Relative exposure brightness (measured in `Stops`) applied to
       the image. Negative numbers darken the image, positive values
       increase the brightness.

   * - Gamma
     - Brighten or darken the mid-tones of the image, without
       affecting the shadows or highlights as much. Do not use this
       slider to approximate a Color Space of 2.2 - use the `Input
       Color Space` attribute.

   * - Saturation
     - Adjust the color saturation of the image; 0.0 makes the image
       black and white, 1.0+ numbers make the image colors very
       vibrant.

   * - SoftClip
     - Reduce the image highlights to flatten the bright areas of an image.

   * - Alpha Gain
     - Alpha channel multiplier. Controls the opacity/transparency of
       the image.

   * - Input Color Space
     - The color space saved into the image. Left-click to choose
       color space from menu.

   * - Image Ignore Alpha
     - If the image contains an alpha channel, you can ignore it here,
       and treat the image as fully opaque.

   * - Display Channel
     - Which channel the image would you like to display? ``RGBA``
       (full), ``RGB`` (color only, disables alpha), ``Red`` only,
       ``Green`` only, ``Blue`` only, ``Alpha`` only, or ``Luminance``
       only?

.. _imageplane-image-sequence-attributes-ref:

Image Sequence Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~

`Image Sequence` attributes define the image that is loaded and the
frame number used for image look-up.

`MM ImagePlane` is designed to contain multiple image sequence
`Slots`, so that users can easily swap between different images. For
example, you may have an EXR image sequence, a lower-resolution JPEG
image sequence and a color adjusted image sequence to better see
low-contrast image details - you can easily swap between all of these
image sequences by changing the `Image Sequence Slot` attribute.

.. figure:: images/tools_image_plane_attributes_image_sequence.png
    :alt: MM ImagePlane Image Sequence attributes.
    :align: center
    :width: 80%

.. list-table:: Image Sequence Attributes
   :widths: auto
   :header-rows: 1

   * - Name
     - Description

   * - Image Sequence Slot
     - Change the `Image Sequence Slot`, between the 4 image sequences
       available; ``Main``, ``Alternate 1``, etc.

   * - Image Sequence (Main)
     - The "Main" image sequence, and the default.

   * - Image Sequence (Alt 1)
     - First alternate image sequence.

   * - Image Sequence (Alt 2)
     - Second alternate image sequence.

   * - Image Sequence (Alt 3)
     - Third alternate image sequence.

   * - Image Width
     - Resolution width of loaded image.

   * - Image Height
     - Resolution height of loaded image.

   * - Image Pixel Aspect
     - Pixel-aspect ratio loaded image. This changes the way the
       physical image plane size is calculated. For example, when
       loading raw un-squeezed Anamorphic images, set this value to
       ``2.0``.

   * - Start Frame
     - The start frame of the loaded image sequence. Will be ``0`` if
       an image sequence is not loaded.

   * - End Frame
     - The end frame of the loaded image sequence. Will be ``0`` if an
       image sequence is not loaded.

   * - Image Sequence Frame
     - The current **input** image sequence frame number.

   * - First Frame
     - What frame is the first frame in the image sequence? `MM
       ImagePlane` Offsets the `Start Frame` of the image sequence so
       it is displayed when the Maya timeline is at `First Frame`.

   * - Frame Output
     - The current **output** image sequence frame number.

   * - Image Flip (Vertical)
     - Flips the image vertically; does *not* flip any asymmetric lens
       distortion values.

   * - Image Flop (Horizontal)
     - Flops the image horizontally; does *not* flop any asymmetric
       lens distortion values.

.. _imageplane-hud-attributes-ref:

HUD (Heads-Up Display) Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HUD (Heads-Up Display) attributes control the way text is drawn in the
viewport when the `MM ImagePlane` is viewed from it's connected
camera.

The HUD displays useful information intended to help understanding of
the loaded image and help spot common issues.

.. figure:: images/tools_image_plane_attributes_hud.png
    :alt: MM ImagePlane HUD attributes.
    :align: center
    :width: 80%

.. list-table:: HUD Attributes
   :widths: auto
   :header-rows: 1

   * - Name
     - Description

   * - Draw Hud
     - Enable or disable all HUD features.

   * - Draw Camera Size
     - Enable or disable the camera size display.

   * - Draw Image Size
     - Enable or disable the image size display.

.. _imageplane-image-cache-attributes-ref:

Image Cache Attributes
~~~~~~~~~~~~~~~~~~~~~~

Provides quick access to see details and control the `Image Cache`,
and clear memory resources.

See :ref:`Image Cache Preferences <image-cache-preferences-ref>` for
details on how to control the `MM Image Plane` hardware resources
used.

.. figure:: images/tools_image_plane_attributes_image_cache.png
    :alt: MM ImagePlane Image Cache attributes.
    :align: center
    :width: 80%

.. list-table:: Image Cache Attributes
   :widths: auto
   :header-rows: 1

   * - Name
     - Description

   * - Refresh Attribute Editor (button)
     - Update the text fields in the attribute editor.

   * - Image Sequence Size
     - Breaks down the amount of memory required for the full image
       sequence currently loaded; the size of a single frame
       multiplied by the image sequence frame count.

   * - GPU Cache Used
     - Amount of GPU cache capacity is currently used.

   * - CPU Cache Used
     - Amount of CPU cache capacity is currently used.

   * - Total Memory Available
     - Amount of memory resources available on the computer.

   * - Clear... (button)
     - Left-click to open a menu; clearing all images, clearing memory
       from image sequence slots on the current `MM ImagePlane` node.

   * - Image Cache Preferences... (button)
     - Left-click to open the :ref:`Image Cache Preferences <image-cache-preferences-ref>`.

.. _imageplane-misc-attributes-ref:

Miscellaneous Attributes
~~~~~~~~~~~~~~~~~~~~~~~~

`Miscellaneous` attributes do not fit into the other categories and
are not commonly adjusted, but provided for rare use cases.

.. figure:: images/tools_image_plane_attributes_misc.png
    :alt: MM ImagePlane Miscellaneous attributes.
    :align: center
    :width: 80%

.. list-table:: Miscellaneous Attributes
   :widths: auto
   :header-rows: 1

   * - Name
     - Description

   * - Mesh Resolution
     - Used to adjust the real-time lens distortion quality. You
       should adjust the resolution with more polygons when lens
       distortion is so extreme that the lens distortion is displayed
       is not accurate. Increasing the number also slows-down the
       real-time performance.

   * - Output Color Space
     - This is the color space that Maya should work with
       internally. Left-click to choose color space from menu.

.. _imageplane-nodes-attributes-ref:

Nodes Attributes
~~~~~~~~~~~~~~~~

These attributes can be used to quickly navigate to the connected
nodes of this `MM ImagePlane` node.

The node connections cannot be adjusted using this UI. Only adjust
these attributes if you know what you are doing, or want to
experiment.

.. figure:: images/tools_image_plane_attributes_nodes.png
    :alt: MM ImagePlane Nodes attributes.
    :align: center
    :width: 80%

.. list-table:: Nodes Attributes
   :widths: auto
   :header-rows: 1

   * - Name
     - Description

   * - Geometry Node
     - Mostly used for debugging. The connected node used to extract
       mesh geometry for the `MM ImagePlane` to draw on the
       screen. This geometry node may be deformed by lens distortion.

   * - Camera Node
     - The image plane is attached to this camera node.

.. _imageplane-extended-image-details-attributes-ref:

Extended Image Details Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Extended Image Details` explain the internal and low-level details of
the loaded images, and they are used to debug and for scripting tools.

.. figure:: images/tools_image_plane_attributes_extended_image_details.png
    :alt: MM ImagePlane Extended Image Details attributes.
    :align: center
    :width: 80%

.. list-table:: Extended Image Details Attributes
   :widths: auto
   :header-rows: 1

   * - Name
     - Description

   * - Padding
     - Image sequence file path frame number padding; For example
       ``file.1001.jpg`` (``file.####.jpg``) has a padding of 4.

   * - Image Num Channels
     - The number of channels saved in the loaded image; 3 for RGB, 4
       for RGBA.

   * - Image Bytes Per Channel
     - The number of bytes that is used for each image channel. 8-bit
       is 1-byte; 32-bit is 4-bytes.

   * - Image Size Bytes
     - The calculated number of bytes for a single image. This value
       is used to make calculations for the :ref:`Image Cache
       Attributes <imageplane-image-cache-attributes-ref>` attributes,
       and is mostly intended for debugging and scripting.

   * - Input Color Space
     - The string value of the `Input Color Space` of the loaded image. Used for debugging.

   * - Output Color Space
     - The string value of the `Output Color Space` of the loaded image. Used for debugging.
