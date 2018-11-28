# Planned Features

- Solver Plug-in
  - Evaluation of complex character rigs for soft-deformation.
  - Smoothness / Jerkiness error metric to enable the solver reduce
    bumpy solves, especially for multi-frame solves.
  - Sparse curve solving - solving attributes at only specific frames,
    rather than per-frame.
  - Error weighting based on un-realistic Center-Of-Mass trajectory
    velocities.

- Python API
  - Returning, storing and parsing output data from a mmSolve
    execution.

- User Tools
  - GUI to select camera and object channels to solve.
    - GUI to link/unlink 2D markers and 3D bundles.
  - 2D markers can either be locators or special objects that look
    like 2D tracks with pattern/search boxes.
    - Dynamic lines to visually connect the display of the 2D and 3D
      points.
  - Tool to project 2D markers onto polygons, creating associated
    static or animated locators.
  - Graphing Solve information including errors per-frame, solve
    time taken, etc.

Note: Due to the complexity of integrating Lens Distortion into Maya
and the MM Solver, Lens Distortion is not handled by this solver. It
is possible to be added later, but for now such a feature is out of
the scope of this project.
