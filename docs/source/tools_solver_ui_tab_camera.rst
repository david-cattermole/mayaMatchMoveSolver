.. _camera-solver-tab-heading:

Camera Solver Tab
=================

.. figure:: images/tools_solver_ui_solver_tab_camera.png
    :alt: Solver Camera Tab
    :align: center
    :width: 90%

    Solver Camera Tab

The `Camera Solver` is designed to solve a "free move" Camera using no
known 3D `Bundle` positions.

The `Camera Solver` assumes:

- The current `Camera` focal length value is an approximation of the
  focal length used in the solver.

- The current `Lens` distortion values will be used by the `Camera
  Solver`, or refined if `Lens` attributes are included in the `Output
  Attributes`.

- If the `Camera` focal length is added to the `Output Attributes`, the
  `Camera` focal length will be refined during `Camera` solving.

- All `Bundle` attributes are assumed to be static - with no keyframe
  animation.

- All `Camera` translate and rotate attributes will be animated.

- The solved `Camera` and `Bundle` nodes share the same parent
  transform values. The `Camera` and `Bundle` world-space values are
  *not* used - only the attribute values themselves.

To position, scale and orient the solved camera and bundles the
:ref:`Set Camera Origin Frame <set-camera-origin-frame-tool-ref>` tool
is automatically used. This is intended to provide some world-space
stability to the `Camera Solver` avoids a random transform each time
the Camera Solver is run.

After solving with the `Camera Solver` it is intended to refine the
solve with more flexibility using the :ref:`Standard Solver
<standard-solver-tab-heading>` and :ref:`Basic Solver
<basic-solver-tab-heading>`.

.. note:: Although technically possible to solve lens distortion
   attributes during the Camera Solve, results are currently (as of
   2022-11-06) not very accurate. This limitation may be improved in
   the future.

Solver Options
--------------

The solver options below are extra options used to change how the
solver works internally.

Origin Frame
++++++++++++

The `Origin Frame` is the 'current frame' from the :ref:`Set Camera
Origin Frame <set-camera-origin-frame-tool-ref>` tool and signifies
the frame number where the solved `Camera` transform will be zero
(identity).

This frame number can often be associated with a 'line-up frame'.

Scene Scale
+++++++++++

The `Scene Scale` (same as the option in the :ref:`Set Camera Origin
Frame <set-camera-origin-frame-tool-ref>` tool) normalises the maximum
camera distance to this value.
