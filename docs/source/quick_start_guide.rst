.. _quick-start-guide-heading:

Quick Start Guide
=================

Overview
--------

mmSolver is a bundle adjustment solver for Maya that helps you solve
camera and object motion based on 2D to 3D point correspondences. This
guide will help you get started with the basic workflow.

Prerequisites
-------------

- Linux or Microsoft Windows OS.
- Maya 2019 or later
- mmSolver installed correctly (see :ref:`download-heading`)
- Basic understanding of 3D matchmove concepts.

Basic Workflow
--------------

Setting Up Your Scene
~~~~~~~~~~~~~~~~~~~~~

1. Import your image sequence using the :ref:`Create ImagePlane <create-imageplane-ref>` tool
2. Create or import a camera using the :ref:`Create Camera <create-camera-ref>` tool
3. Ensure your scene units and frame range are set correctly

Creating Tracking Points
~~~~~~~~~~~~~~~~~~~~~~~~

There are two main ways to create tracking data:
- Import from external tracking software (3DEqualizer, Blender, etc.)
- Create tracking points manually in Maya

To Import Tracking Data
^^^^^^^^^^^^^^^^^^^^^^^

1. Export your 2D tracks from your tracking software
2. Use :ref:`Load Markers <load-markers-ref>` tool (``mmSolver > Load Marker...``)
3. Select your camera and import options
4. Click "Load" to create Markers

See :ref:`Copy 2D Tracks from 3DEqualizer <copy-3de4-2d-tracks-ref>`
or :ref:`Copy 2D Tracks from Blender <copy-blender-2d-tracks-ref>` for
software-specific details.

To Create Manual Tracks
^^^^^^^^^^^^^^^^^^^^^^^

1. Select your camera in the viewport
2. Use :ref:`Create Marker <create-marker-ref>` tool
3. Position the Marker on a trackable feature
4. Create a Bundle using :ref:`Create Bundle <create-bundle-ref>` tool

Basic Solving
~~~~~~~~~~~~~

1. Open the :ref:`Solver UI <solver-ui-ref>` (``mmSolver > Solver UI``)
2. Add your Markers to "Input Objects"
3. Select attributes you want to solve in the Channel Box
4. Add selected attributes to "Output Attributes"
5. Choose your solving frames
6. Click "Solve"

For deeper understanding, see :ref:`solver-design-heading`.

Evaluating Results
~~~~~~~~~~~~~~~~~~

- Check the solver feedback in the status bar
- Review deviation values for each Marker
- Visually verify the solve by playing through the timeline
- Use viewport toggles to show/hide various elements

See :ref:`Toggle Viewport Node Types <toggle-viewport-node-types-ref>` for display options.

Common Tools Reference
----------------------

Essential Hotkeys
~~~~~~~~~~~~~~~~~

See :ref:`default-hotkeys-heading` for the complete list.

- **M** - Toggle between Marker/Bundle selection.
- **C** - Center on selected Marker.
- **Z** - Maya's standard zoom/pan tool.

Frequently Used Tools
~~~~~~~~~~~~~~~~~~~~~

- :ref:`Center 2D on Selection <center-2d-on-selection-tool-ref>` - Centers viewport on selected object
- :ref:`Toggle Marker Lock <toggle-marker-lock-state-tool-ref>` - Locks/unlocks Marker positions
- :ref:`Screen Z Manipulator <screen-z-manipulator-tool-ref>` - Controls depth of objects relative to camera

Next Steps
----------

- Watch the :ref:`Tutorial Videos <tutorial-heading>` for detailed workflow examples
- Learn about Camera Solving Techniques
- Explore :ref:`Advanced Solver Options <solver-ui-ref>`

Tips for Better Solves
----------------------

- Start with simple solves (few parameters) and gradually add complexity
- Use the :ref:`Standard Solver Tab <standard-solver-tab-heading>` for static + animated attributes
- Ensure adequate parallax for 3D position solving
- Lock attributes that shouldn't change during solving
- Use appropriate Marker weights for different quality tracks

See :ref:`solver-design-solving` for more solving strategies.

Common Issues and Solutions
---------------------------

- **High Deviation Values**: Check for incorrect 2D tracking or constraints
- **Unstable Solves**: Reduce the number of attributes being solved
- **Slow Performance**: Use "Solve Only Root Frames" for initial tests
- **Failed Solves**: Verify you have enough Markers for the attributes being solved

For more detailed explanations of solver concepts, see :ref:`solver-design-heading`.
