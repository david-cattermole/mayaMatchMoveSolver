.. _frame-tools-heading:

Frame Tools
===========

.. figure:: images/tools_shelf_icons_frames.png
    :alt: Node Frame Shelf Icons
    :align: center
    :width: 30%

.. _next-root-frame-tool-ref:

Next Root Frame
---------------

Move the current Maya frame to the **next** root frame, for the currently
active Collection.

Run this Python command:

.. code:: python

    import mmSolver.tools.navigaterootframes.tool as tool
    tool.main_next_frame()

.. _previous-root-frame-tool-ref:

Previous Root Frame
-------------------

Move the current Maya frame to the **previous** root frame, for the currently
active Collection.

Run this Python command:

.. code:: python

    import mmSolver.tools.navigaterootframes.tool as tool
    tool.main_prev_frame()

.. _add-root-frame-tool-ref:

Add Root Frame
--------------

Adds the current Maya frame into the currently active Collection's
root frame list. The Solver UI will update automatically with the new frames.

Run this Python command:

.. code:: python

    import mmSolver.tools.editrootframes.tool as tool
    tool.main_add_frame()

.. _remove-root-frame-tool-ref:

Remove Root Frame
-----------------

Removes the current Maya frame from the currently active Collection's
root frame list. The Solver UI will update automatically with the
current frame removed.

Run this Python command:

.. code:: python

    import mmSolver.tools.editrootframes.tool as tool
    tool.main_remove_frame()