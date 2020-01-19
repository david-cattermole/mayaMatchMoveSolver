Create Node Tools
=================

.. figure:: images/tools_shelf_icons_creation.png
    :alt: Node Creation Shelf Icons
    :align: center
    :width: 30%

Creating various nodes and objects with mmSolver uses the tools below.

Create Marker
-------------

Create a default Marker node under the active viewport's camera.

Usage:

1) Click in a Maya 3D viewport, to activate the camera.

2) Run the Create Marker tool, using the shelf, menu or marking menu.

   - A Marker will be created in the center of the viewport.

.. note::
    Default Maya cameras (such as ``persp``, ``top``, ``front``, etc)
    are not supported to create Markers.

Run this Python command:

.. code:: python

    import mmSolver.tools.createmarker.tool as tool
    tool.main()

.. _load-markers-ref:

Load Markers
------------

.. figure:: images/tools_loadmarker_overview.png
    :alt: Load Markers UI
    :align: right
    :scale: 50%

    Load Markers UI

The Load Markers UI allows loading of ``.uv`` (mmSolver), ``.txt``
(3DEqualizer4), ``.rz2`` (Autodesk MatchMover) formated files.

When opening the UI, the contents of the user’s clipboard is
queried. If the clipboard is a valid file path, it will be
automatically pasted into the “File Path”, so you won’t need to
“Browse” for the file.

In 3DEqualizer, the "Copy 2D Tracks (MM Solver)" is designed to copy
the selected 2D points to a temporary file path and then place that
file path on the clipboard automatically. Once the file path is on the
clipboard, just open the Maya Load Marker tool and the path will be
read automatically.

The "Camera" list contains all the cameras currently in the Maya
scene. If no cameras are available (persp, front, top, left do not
count), the default option is to create a new camera. The "Update"
button refreshes the "Camera" list without needing to close and
re-open the UI.

Once a file path is given, press the “Load” button.
For ``.txt`` format you will need to enter the Width / Height of the input
format.

Run this Python command:

.. code:: python

    import mmSolver.tools.loadmarker.ui.loadmarker_window as tool
    tool.main()

Copy 2D Tracks from 3DEqualizer
+++++++++++++++++++++++++++++++

.. figure:: images/tools_loadmarker_tde_copyTracks.png
    :alt: Copy a 2D Track in 3DE
    :align: right
    :scale: 20%

To create a ``.uv`` file, you may use the 3DEqualizer ``Copy Tracks
(MM Solver)`` script (see mmSolver installation to install this
script).

1) In 3DEqualizer, select a 2D Point in the Object or Point Browser.

2) Right-click the point and run ``Copy Tracks (MM Solver)``.

   - A ``.uv`` file will be saved into a temporary file, and the file
     path will be on your system copy/paste clipboard, ready to be used in
     Maya.

3) Next Open Maya and use the file path in the Load Markers UI.


Loading Markers in Maya
+++++++++++++++++++++++

Loading Markers into Maya from external Tracking software is a common
task needed for solving 3D objects and cameras.

1) Open the Load Marker UI, for example use the menu ``mmSolver > Load
   Marker...``.

   - If you already have a valid file path on your Copy/Paste
     Clipboard, then the Load Marker UI will auto-load the file path.

   - The file contents will be displayed below the file path.

2) Choose your options.

3) Press the **Load** button.

When the **Load** button is run, the options used in the Load Marker UI
will be saved to the user's home directory. The saved options are
automatically restored when the Load Marker UI is re-opened.

.. list-table:: Load Marker Options
   :widths: auto
   :header-rows: 1

   * - Option
     - Description

   * - Mode
     - allows you to create new Markers or replace data on selected
       Markers.

   * - Camera
     - is the camera node you wish to place the newly created Markers
       under. You may also create a new camera node.

   * - Marker Group
     - is the Marker Group (under the **Camera**) that you wish to
       create the Markers underneath. You may create a new Marker
       Group, using the ``<Create New>`` option.

   * - Distortion Mode
     - will allow choosing the type of 2D point data to create or
       load. Some formats (for example ``.uv``) can store both
       undistorted and distorted 2D data.

   * - Use Embedded Overscan
     - will use the camera field of view (FOV) embedded inside the
       file to automatically calculate the correct 2D
       position. ``.uv`` is the only currently supported format. Use
       ``Copy Tracks (MM Solver)`` or ``Export Tracks (MM Solver)``
       version 1.7+ inside 3DEqualizer for this feature to be enabled.

   * - Load Bundle Positions
     - will allow loading 3D point information saved along with the 2D
       Marker data. Only some formats (for example ``.uv``) can store
       both 2D and 3D data in one file.

   * - Image Resolution
     - is for use with 3DEqualizer4 ``.txt`` files, which are stored
       with plate resolution embedded into the 2D data. Use this field
       to choose the correct plate resolution for the 2D data that was
       exported.


Updating / Replacing Markers in Maya
++++++++++++++++++++++++++++++++++++

.. figure:: images/tools_loadmarker_load_mode_replace.png
    :alt: Replace the selected Marker nodes.
    :align: right
    :scale: 40%

    Replace the selected Marker nodes.

Marker nodes in Maya can be overwritten with newly tracked data.

1) Open the Load Marker UI.

2) Set the **File Path** for the UI.

3) Change **Mode** to *Replace Selected Markers*.

4) Select Marker nodes using the Maya Outliner.

5) Press **Load** button.

   The Selected Markers will be considered for update.

   If you have select one Marker node, and the loaded file contains
   one 2D Track, then the 2D Track data will overwrite the selected
   Marker node.

   If you have multiple Marker nodes, selected then the Load Marker
   tool will try to match the pre-existing Marker name or metadata
   with the 2D Tracking data in the file. When using 3DEqualizer the
   2D Tracking data is loaded onto the Marker node that was already
   loaded using 3DEqualizer - there is a link between the 2D data in
   3DEqualizer and the Marker node in Maya.


Convert to Marker
-----------------

Converts the selected transform nodes into screen-space Markers, as
viewed though the active viewport camera.

The created markers are named based on the selected transform nodes, and
are parented under the active viewport camera.

Usage:

1) Click into an active 3D viewport.

2) Select one or more Maya transform nodes.

3) Run tool.

   - A Marker will be created for each Maya transform node selected,
     across the current timeline's frame range.

Run this Python command:

.. code:: python

    import mmSolver.tools.convertmarker.tool as tool
    tool.main()

Create Bundle
-------------

Create a default Bundle node.

If Markers are selected, the Bundle will attempt to attach to it, while
adhering to the rule; *a bundle can only have one marker representation
for each camera.*

Run this Python command:

.. code:: python

    import mmSolver.tools.createbundle.tool as tool
    tool.main()
