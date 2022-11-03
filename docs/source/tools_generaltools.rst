General Tools
=============

The tools on this page are not specific to Markers, Cameras or
Bundles, but are general tools useful in Maya for many different
tasks.

.. _reparent-under-node-tool-ref:

Reparent Under Node
-------------------

This is equivalent to Maya's *Parent* tool (`p` hotkey), except the
tool will maintain the world-space position of the transform node for
each keyframe applied to the node.

See the :ref:`Reparent UI <reparent-window-tool-ref>` for options.

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

    import mmSolver.tools.reparent2.tool as tool
    tool.reparent_under_node()

.. _unparent-to-world-tool-ref:

Unparent to World
-----------------

This is equalivent to Maya's *Unparent* tool (`Shift + p` hotkey), except the tool will
maintain the world-space position of the transform node for each
keyframe applied to the node.

See the :ref:`Reparent UI <reparent-window-tool-ref>` for options.

Usage:

1) Select Maya transform node(s).

   - The nodes may be in a deep hierarchy, or not.

2) Run tool.

   - The nodes will maintain the same world-space position, but will
     be unparented into root Maya Outliner (the nodes will not be
     parented under any node).

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.reparent2.tool as tool
    tool.unparent_to_world()

.. _reparent-window-tool-ref:

Reparent UI
-----------

This window displays options for how to re-parent nodes.

*Reparent* is the underlying tool window used by both
:ref:`Reparent Under Node <reparent-under-node-tool-ref>`
and :ref:`Unparent to World <unparent-to-world-tool-ref>`.

.. figure:: images/tools_reparent_ui.png
    :alt: Reparent UI
    :align: center
    :width: 40%

.. list-table:: Reparent UI Options
   :widths: auto
   :header-rows: 1

   * - Name
     - Values
     - Description

   * - Children
     - *Node Names*
     - Description

   * - Parent
     - *Node Name* or empty
     - The node to place children underneath.

   * - Frame Range
     - *Timeline (Inner)*, *Timeline (Outer)* or *Custom*
     - The frame range to bake.

   * - Bake Mode
     - *Full Bake* or *Smart Bake*
     - Method for how keyframes are baked.

   * - Rotate Order
     - *Use Existing* or *XYZ*, *ZXY*, etc
     - Change the rotation order of children nodes when re-parenting.

   * - Delete Static AnimCurves
     - *Yes* or *No*
     - Baked attributes that do not animate have all keys replaced
       with a static value.

This video tutorial explains how the re-parenting tool works.

.. raw:: html

    <iframe width="720" height="405" src="https://www.youtube.com/embed/UmVu3oag_-k" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.reparent2.tool as tool
    tool.open_window()

.. _create-remove-controller-tool-ref:

Create / Remove Controller
--------------------------

Create a new transform node to control another node. The `Controller`
transform node can have a separate hierarchy than the source node.

The UI for this tool can be used control the baking method, and the
'space' of the created controller. These features create a very
powerful workflow for editing, and solving characters and objects.

.. figure:: images/tools_create_controller_ui.png
    :alt: Create Controller UI
    :align: center
    :width: 60%

.. note:: For a simple, straight-forward tool to create a world-space
    controller for each selected object, use the `Create (World-Space)
    Controllers` tool.

Usage:

1) Select a Maya transform node.

2) Open 'Create Controller' tool UI.

3) Type a name for the controller.

4) Select your `pivot object` and press `Pick Selection`.

5) Select your `main object` and press `Pick Selection`.

6) Select your options for `Type`, `Pivot`, `Bake` mode, and `Space`.

   - Use the `Controller Type` menu to change the node types created
     for the controller. Choose "Group" if you do not like to see
     locators in your viewport.

   - `Pivot` changes how the pivot object is baked; `Static` assumes
     the pivot object does not animate or is baked on the current
     frame. `Dynamic` uses an animated pivot.

   - `Bake` changes the method used to bake keyframe times. Choose
     `Full Bake` to bake every frame, and choose `Smart Bake` to bake
     some frames.

   - `Space` changes the heirachy and orientation of the Controller
     nodes. Using `Screen Space` allows you to move an object in
     screen-space, with X and Y the position on the screen, and Z the
     depth into the screen. This can be very helpful for smoothing
     Z-bumps and depth problems.

7) Press `Create Controller` button.

   - A new `Controller` node is created at the same position as the
     `pick object`.

8) Select and move the created Controller as you wish.

9) Select the Controller, run `Remove Controller` tool.

   - The source node is baked and the Controller node is deleted.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.createcontroller2.tool as tool
    tool.open_window()

To create world-space controllers for the current selection, without
using any of the UI options, use this Python command:

.. code:: python

    import mmSolver.tools.createcontroller2.tool as tool
    tool.create_world_controllers()

To remove a controller, use this Python command:

.. code:: python

    import mmSolver.tools.removecontroller2.tool as tool
    tool.main()

The tool described above is "version 2", for the older (less featured)
version 1, use this python code to run it.

.. code:: python

    import mmSolver.tools.createcontroller.tool as tool

    # Create a Controller
    tool.create()

    # Remove selected Controller
    tool.remove()

.. _marker-bundle-rename-tool-ref:

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

.. _marker-bundle-rename-with-metadata-tool-ref:

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

.. _sort-selected-nodes-in-outliner-tool-ref:

Sort Selected Nodes In Outliner
-------------------------------

Alphabetically sorts (re-orders) the selected nodes in the Maya Outliner window.

This tool avoids the Maya Outliner window's (interactive) "Sort Order" feature
and encourages an organised workflow when working with many nodes.

This tool works on *any* Transform node, not only mmSolver nodes.

.. figure:: images/sort_nodes_in_outliner_compare.png
    :alt: Before/After of all nodes sorted in the Maya Outliner.
    :align: center
    :width: 80%

Usage:

1) Select transform nodes.

2) Run tool.

   - The nodes will be sorted.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.sortoutlinernodes.tool as tool
    tool.main()

.. _remove-solver-nodes-tool-ref:

Remove Solver Nodes
-------------------

Remove Solver Nodes tool allows for the removal of
some or all nodes related to the matchmoveSolver
plugin, allowing for a clean scene to be prepped
to passed to other departments/vendors.

.. figure:: images/tools_remove_solver_nodes_ui.png
    :alt: Remove Solver Nodes UI
    :align: center
    :width: 40%

Usage:

1) Run tool.

   - A UI will open.

2) Select what type of nodes you wish to remove.

3) Click 'Clean'.

Note that if there are other nodes constrained or
connected in some way to the marker or bundle
nodes they should be cleaned or baked before
removal.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.removesolvernodes.tool as tool
    tool.main()

.. _user-preferences-tool-ref:

User Preferences
----------------

.. figure:: images/tools_user_preferences_ui.png
    :alt: User Preferences window
    :align: center
    :width: 60%

The *User Preferences* window is used to change how mmSolver tools and
general functions behave, by default.

.. list-table:: Options
   :widths: auto
   :header-rows: 1

   * - Name
     - Values
     - Description

   * - Add New Markers to
     - *None* or *Active Collection*
     - When a new Marker is created by any tool, what Collection should
       this Marker be automatically added to?

   * - Add New Lines to
     - *None* or *Active Collection*
     - When a new Line is created by any tool, what Collection should
       this Line be automatically added to?

   * - Minimal UI While Solving
     - *Yes* or *No*
     - If *Yes*, the :ref:`Solver UI <solver-ui-ref>` will only display
       the progress bar while solving, and then switch back to the full
       UI solving has finished. If *No*, the :ref:`Solver UI <solver-ui-ref>`
       will not be adjusted.

Usage:

1) Open 'User Preferences' window.

2) Change options.

3) Press "Save" button.

To run the tool, use this Python command:

.. code:: python

    import mmSolver.tools.userprefswindow.tool as tool
    tool.open_window()
