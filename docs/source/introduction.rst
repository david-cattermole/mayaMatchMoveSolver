Introduction
============

The Maya MatchMove Solver (or `mmSolver` for short), is a tool to
MatchMove cameras and objects in Autodesk Maya. The `mmSolver` takes a
different approach than most other software (Commerical or Free Open
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
indepentantly, or any combination of attributes all at the same
time. Even custom attributes are supported. *Animated attributes* can
be solved as well as *static attributes*, meaning a Camera Translate Z
attribute may be solved animated while solving the best attribute
value for the non-animated Camera Focal Length.

`mmSolver` allows all of these features and more!
