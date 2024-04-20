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

- 3D Camera Solving with no known 3D positions.

- Camera line up and Lens Calibration using a single view (no
  parallax) using straight lines in the image.
