.. _standard-solver-tab-heading:

Standard Solver Tab
===================

.. figure:: images/tools_solver_ui_solver_tab_standard.png
    :alt: Solver Standard Tab
    :align: center
    :width: 90%

    Solver Standard Tab

The Standard solver tab can solve both animated and static attributes.

When the Standard solver is executed, first the static and animated
attributes are solved using the 'Root Frames' option. After the 'Root
Frames' are solved, the animated attributes are solved per-frame using
the 'Frames' option.

If 'Frames' is set to 'Current Frame', then both static and animated
attributes are solved on the current frame. The user must take care to
ensure it is possible to solve the static attributes using only this
frame.

If the 'Solve Only Root Frames' option is checked, the second solve
using the Frames is not run, only the Root Frames are solved.

If 'Solve All At Once' option is checked, the Root Frames and Frames
are combined and both static and animated attributes are solved in one
solve process. Solving many attributes and frames in this way is very
slow and should be avoided.
