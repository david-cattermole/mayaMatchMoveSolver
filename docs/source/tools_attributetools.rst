Attribute Tools
=================

Attribute tools are used to create and modify attributes, and
attribute values.

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
