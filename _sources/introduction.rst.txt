Introduction
============

The Maya MatchMove Solver (or `mmSolver` for short), is a tool to
MatchMove cameras and objects in Autodesk Maya. The `mmSolver` takes a
different approach than most other software (Commercial or Free Open
Source Software).

Most other software will calculate a 3D camera or 3D
object track by throwing away the initial camera/object trajectory,
and creating the solve brand new each time. This technique can be very
efficient in some cases, however sometimes you wish to *incrementally*
build a solve, by animating a rough solve first, and giving that as a
'hint' to the solver; "the camera should be moving approximately like
this, now refine it."

In addition to incremental solving, a common limitation of other
software, is the inability to represent complex relationships of
objects, such as object hierarchy, line constraints or plane
constraints. `mmSolver` can model all of these types of constraints
and relationships using Autodesk Maya's DAG nodes and connections.

Finally, `mmSolver` also allows solving of *specific attributes* of
any node, so you can solve only Translate X, Rotate Y or Scale Z
independently, or any combination of attributes all at the same
time. Even custom attributes are supported. *Animated attributes* can
be solved as well as *static attributes*, meaning a Camera Translate Z
attribute may be solved animated while solving the non-animated
Camera Focal Length.

`mmSolver` allows all of these features and more!

Use Cases
+++++++++

- Solving camera or object transforms based on 2D to 3D positions.

- Using DAG hierarchies to solve objects in specific spaces (for example object or camera space).

- Generation of 3D positions from 2D screen-space positions.

- Reconstruction of multi-camera shooting environments (photogrammetry).

Features
++++++++

- Solver User Interface

  - Uses Plug-In to set up and run solver.

  - Displays relationships of Cameras, (2D) Markers and (3D) Bundles
    nodes.

  - Lists Maya Attributes used for solving.

  - Lists individual Solver 'steps' depicting how the Solver will execute.

  - Supports creation of mmSolver arguments using a GUI.

  - Single-Frame solve override

- User Tools

  - Load 2D Tracks (Markers) from Third-Party software

    - Supports 3DEqualizer *.txt, MatchMover *.rz2 and custom *.uv file formats.

  - Convert from 3D Transform Nodes to 2D Markers.

  - Center Viewport on 3D Transform Node

  - Maya Shelf for quick access to tools

  - Selection tools

    - Toggle Selection between 2D and 3D nodes

    - Select connected 2D and 3D nodes

  - Control 2D and 3D node relationships; linking and unlinking nodes.

  - And more...

- Solver Plug-in

  - Maya DG and DAG evaluation support.

  - Options to tune the required solver iterations and error thresholds.

  - Minimising residual error between 2D and 3D positions.

  - Solving translate, rotate, scale and any custom floating point values, including camera focal length.

  - Static and animated attribute solving.

  - Per-frame, single-frame and multi-frame solving is supported.

  - Multi-camera solving (photogrammetry).

  - Marker weights support (force a point to solve with higher weight
    than others).

  - Marker 'validity' support - frames where markers are occluded.

  - Full undo/redo support.

- Python API

  - Object-Oriented helper classes to create node networks and store the data structure inside a Maya scene.

  - Allows storage of multiple 'collections' of solver arguments in one Maya scene file - all data is stored in the Maya scene file.

  - Creates Maya nodes to represent Markers and Bundles.

For a list of future features please see the GitHub issues_ page.

.. _issues:
   https://github.com/david-cattermole/mayaMatchMoveSolver/issues
