.. _frame-tools-heading:

Frame Tools
===========

.. figure:: images/tools_shelf_icons_frames.png
    :alt: Node Frame Shelf Icons
    :align: center
    :width: 30%

.. _next-user-frame-tool-ref:

Next User Frame
---------------

Move the current Maya frame to the **next** user frame, for the currently
active Collection.

Run this Python command:

.. code:: python

    import mmSolver.tools.navigaterootframes.tool as tool
    tool.main_next_frame()

.. _previous-user-frame-tool-ref:

Previous User Frame
-------------------

Move the current Maya frame to the **previous** user frame, for the currently
active Collection.

Run this Python command:

.. code:: python

    import mmSolver.tools.navigaterootframes.tool as tool
    tool.main_prev_frame()

.. _add-user-frame-tool-ref:

Add User Frame
--------------

Adds the current Maya frame into the currently active Collection's
user frame list. The Solver UI will update automatically with the new frames.

Run this Python command:

.. code:: python

    import mmSolver.tools.editrootframes.tool as tool
    tool.main_add_frame()

.. _remove-user-frame-tool-ref:

Remove User Frame
-----------------

Removes the current Maya frame from the currently active Collection's
user frame list. The Solver UI will update automatically with the
current frame removed.

Run this Python command:

.. code:: python

    import mmSolver.tools.editrootframes.tool as tool
    tool.main_remove_frame()
