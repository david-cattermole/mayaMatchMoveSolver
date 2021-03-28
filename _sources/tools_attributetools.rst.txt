Attribute Tools
=================

Attribute tools are used to create and modify attributes, and
attribute values.

Bake Attributes
---------------

.. figure:: images/tools_bake_attributes_ui.png
    :alt: Bake Attributes UI
    :align: center
    :scale: 50%

Bake Attributes will bake the values of an attribute on each frame and
replace the connection with an animation curve.

This tool is almost identical to the default Maya `Edit > Keys > Bake
Simulation` tool, but has additional features.

- The viewport is always disabled while baking.

- The tool is optimised for speed of baking.

- The tool UI is reduced to only the nessarary features for matchmove
  tasks.

Usage:

#. Select 1 or more nodes.

#. Select attributes in channel box (if required).

#. Open `Bake Attributes` UI.

   - Enable the `Smart Bake` to set keyframes only on some keyframes.

   - Disable `From Channel Box` to bake all keyable attributes, not
     just the selected attributes.

#. Press `Bake` button.

.. note:: In Maya scenes that rely on legacy viewport update for
          correct evaluation, this tool may produce incorrect results
          (because the viewport is disabled). If this happens, please
          use Maya's default `Edit > Keys > Bake Simulation` tool. In
          the experience of the tool authors, this has never happened
          and this tool is a faster baking tool.

Run this Python command:

.. code:: python

    import mmSolver.tools.fastbake.tool as tool    
    tool.open_window()

    # To run the "fast bake" tool directly (with currently set
    # options).
    tool.main()


Set Attribute Details
---------------------

.. figure:: images/tools_set_attribute_details_ui.png
    :alt: Set Attribute Details UI
    :align: center
    :scale: 50%

The Attribute Details tool is used to add details (properties) to an
individual Attribute. Details are stored per-collection, therefore a
Collection must exist to use the tool.

This tool can be used to:

- Set Attribute Details on individual Attributes.

- Change Attribute states; to lock an attribute, or set a keyframe on
  the attribute.

- View the current Attribute Details on an Attribute.

- View the Animation Curve statistics;

  - Minimum value of the animation curve.

  - Maximum value of the animation curve.

  - Mean (Average) value of the animation curve.

  - Variance of the total animation curve.

  - Variance (per-frame) of the animation curve; how much does the
    animation curve change per-frame.


Attribute Details are used by mmSolver to ensure properties are
maintained while solving. See the Solver Design
:ref:`solver-design-attribute-details` page for more information.

Usage:

#. Ensure a Collection exists.

   - Open Solver UI, and create Collection node with menu; `File > New
     Collection`.

#. Select nodes (and attributes in channel box, if required).

#. Open `Set Attribute Details` UI.

#. Select an Attribute (left-hand side) and modify the Details (right-hand side).

#. Click 'Ok' to accept the changes.


Run this Python command:

.. code:: python

    import mmSolver.tools.setattributedetails.tool as tool
    tool.open_window()
