# Solver Design

Many users of MatchMove software find that by understanding how the underlying
processes of the software work they are able to obtain better results by
utilising the software as it's intended to work.

This document tries to answer that question;
> _How does the MM Solver work?_

# How does the solver work?

The solver inside MM Solver is an _optimisation_ solver. The solver attempts to
optimise the _measured error_ with various _unknown parameter_ values. The
solver's purpose is to find the parameter values which minimise the _measured
error_.

The process of applying an _optimisation_ solver to 3D perspective cameras, 2D
points and 3D points is called Bundle Adjustment (BA). BA is traditionally the
last step of MatchMove and Photogrammetry solvers where the parameter of 3D
points (Bundles) and cameras are solved to produce a 3D Scene with the least
possible error.

## Attributes

In the MM Solver, we refer to _unknown parameters_ as Attributes. Attributes
are the Maya attributes that are allowed to be modified inside the solver.
Maya attributes that are not added into the solver will still be used, but
cannot be modified.

The Attributes modified in the MM Solver may be ***any*** attribute in Maya.
Likewise the attributes may be in any space required, for example;
object-space, world-space or normal/vertex space. The only requirement is that
the Attribute modifies the _Bundle_ position (see below for detail on
_Bundles_). _Bundle_ positions may be modified indirectly using hierarchies or
rigs of Maya transform nodes. The true power of the solver comes from the
evaluation environment, Maya, and the node networks/hierarchies created by the
MatchMove artist.

Like Maya attributes, MM Solver Attributes can also change over-time using an
_animated_ curve, or just have a single _static_ value, or they can be be
_locked_. _Locked_ attributes cannot be modified by Maya and therefore cannot
be modified in the solver either. Due to underlying solving algorithm only
floating-point attribute values can be solved. Commonly solved Attributes are
3D translate and rotate axes.

## Markers and Bundles

_Markers_ and _Bundles_ are used to compute the _measured error_ inside the
solver. The word _Marker_ is used to describe a 2D point on an image plane, and
_Bundle_ to describe the 3D Point.

 _Markers_ have had different names in various MatchMove software applications;
 Track, feature, 2D point, etc. For the purposes of MM Solver name _Marker_ is
 used for the tracking markers placed on the set of a film production.
 _Bundles_ are named as such because they represent a bundle of light forming
 on the imaging sensor.

_Markers_ and _Bundles_ are linked together. The _Marker_ is the representation
of the _Bundle_ from a camera's point of view. There may be multiple 2D
_Marker_ representations of the same 3D _Bundle_.

Having known 2D Markers of a 3D Bundle looking through a known perspective
_Camera_ we can calculate a 3D _Bundle_ position by moving the _Bundle_ until
the difference between all Markers and Bundles is zero when looking through
each perspective _Camera_. Another way to say this is that the _measured error_
is the distance between the screen-space re-projected 3D Bundles with the
linked 2D Markers.

## Solving

Once the solver has _Attributes_, _Cameras_ and _Markers_ and linked _Bundles_,
the solver can start a solve.

The solver may only start if some conditions are met. One important condition
is the number of Attributes verses the number of Markers or specifically:

> The number of _measured errors_ must be equal to or greater than the number
> of _Attribute_ values you're solving.

All 3D MatchMove software has this limitation, MM Solver is no different. There
is a minimum number of Markers required to solve for a 3D Camera that can move
in 6 degrees of freedom (6 DOF: translate X, Y and Z, rotate X, Y and Z). For
MM Solver this number is a ***minimum*** of 3 Markers. 3 Markers are required
to solve for 6 attributes.

Since each _Marker_ measures 2 errors (X and Y distance to _Bundle_),
the marker can solve for 2 attributes. For example, 1 _Marker_ can be
used to solve a _Camera_ transform rotate X and Y (tilt and pan)
attributes.

When the user gives a _Marker_ as input for MM Solver, the position is
assumed to be correct. Some 3D MatchMove software applications use
many 2D Markers and filter out the badly tracked points (the
_outliers_), MM Solver does not work like this. Badly tracked
_Markers_ will affect the solve badly.

This solver is an optimiser and it needs to be provided with an approximation
of input attribute values, or in other words; we need to animate the camera(s),
and place the bundles in the roughly correct positions. You don't need to do
the job of the solver, which is to make the _Cameras_ and _Bundles_ match
perfectly, but you are required to at least have _Bundles_ positioned inside
the FOV of the camera, and an approximate animation of the camera if you're
solving the camera parameters.

The approximate _Camera_ and _Bundle_ positions is why the MM Solver
is so different from traditional MatchMove solutions, especially
Auto-Tracking 3D MatchMove software; there is no one-click
solution. But this can be a good thing!

Remember the solver is an optimiser and it re-uses the input
parameters and refines them rather than re-starting the solve from
scratch. This type of solver enables customised, layered solving. For
example, you may solve for a small number of individual Attributes
with specific sets of _Markers_ and _Bundles_, or you could use it in
a similar way to other 3D MatchMove software where all parameters are
added into the solver.

Due to the inherent refinement nature of the solver, a general process
for solving will be:

1. Add Cameras, Bundles and Markers.
2. Track 2D _Markers_.
3. Place _Cameras_ and _Bundles_ into approximate positions.
4. Set up movement constraints or node hierarchies for _Cameras_
   and / or _Bundles_.
5. Solve for Attribute values.
6. Repeat steps 2-5 until desired result is achieved.

### Solving Process

Each time you execute a solve, the solver goes though a number of steps
to perform the optimisation and reduce the error.

This is an overview of the solver's process:

1. Initialises input data.
2. Solve.
   1. Measure Initial Error.
      1. Set all the initial Attribute values.
      2. Measure the initial re-projection error.
   2. Discover how each Attribute changes the _measured error_.
   3. Iterate.
      1. Based on the discovered value/error changes predict better
         Attribute values.
      2. Set all Attribute values with the predicted Attribute values.
      3. Measure the re-projection error.
      4. Check if the error is low enough, if so stop solving,
         otherwise repeat the iteration.
3. Get solver information.
   1. Set attributes values as calculated.
   2. Measure Final Error.
   3. Get number of iterations.
4. Return Solver information to the user.

The slowest step of the solving process is step 2 as it may be executed
hundreds or thousands of times, depending on the number of _Attributes_ and
_Markers_ that are in the solve.

### Time - Static and Animated Attributes

Up until now we've been concerned with solving a single frame in
time. Now we need to extend that into multiple frames. In the MM
Solver there are _animated Attributes_ that change per-frame and
_static Attributes_ that only have one value. Using _static
Attributes_ complicates the solving process.

If we are to solve only per-frame that would mean Attribute values
from one frame would never affect another frame and therefore we can
safely loop over each frame and solve each frame individually. When
including _static Attributes_, the _static Attributes_ affect all
frames in the solve.

Consider a simple example; 1 _animated Attribute_ and 1 _static
Attribute_, solving on three frames, frame 1, 2 and 3. The animated
attribute contains 3 values, an individual value for each frame, and
so each value affects the _measured error_ on each frame. But the
_static Attribute_ contains only one value, not one for each frame,
and therefore the single value affects the _measured error_ on all
frames.  To solve for the minimum possible _measured error_ for all
values it is necessary to consider all 4 values together (3 animated
values, 1 static value), and all combinations of the values. Solving
for 4 values rather than 3 values doesn't sound like it would take
much longer to compute, but in fact it takes 3 times longer (3 * 3);
this problem is squared each time a static value is added. The more
static values added to the solve increases the number of possible
combinations and increases the number of solver evaluations required
for a low _measured error_. Solving Animated and Static values as
described is a **Brute Force** approach, but other strategies may be
used.

### Solver Strategies

Solver strategies are patterns of evaluation that attempt to solve the
input attributes across time while reducing the number of evaluations
and increasing solve quality.

To reduce _measured error_, the ideal strategy for solves with only
animated attributes is the **Per-Frame** strategy, while the ideal
strategy for animated and static attributes is **All Frames**

- Per-Frame
- Two Frames (Forward / Backward)
- Three Frames (Forward / Backward)
- All Frames (Brute-force)

In practise, a mixture of multiple strategies may be the best approach.

## Frequently Asked Questions

> What transform space does _MM Solver_ solve in?

_MM Solver_ evaluates all _Marker_ and _Bundle_ screen-space errors
 in **world-space**, but solving is not performed in a transform
 space. Solving is performed directly on _Attribute_ values.

> How can I use a DAG hierarchy to reduce the number of _Attributes_?

**To be written**

### Solver Options

Like many solvers, the MM Solver has options.

|  Option        |  Description                                                           |
| -------------- | ---------------------------------------------------------------------- |
| Max Iterations | The maximum number of iterations that the solver is allowed to perform |
| Solver Type    | Which algorithm will be used, 'dense' or 'sparse' Lev-Mar?             |
| Tau            | Scale factor for initialTransform mu                                   |
| Delta          | Step used in difference approximation to the Jacobian                  |
| Epsilon 1      | Stopping threshold for `J^T e_inf`                                     |
| Epsilon 2      | Stopping threshold for `Dp_2`                                          |
| Epsilon 3      | Stopping threshold for `e_2`                                           |

### General Solving Concepts

**To be written**

#### Over-parameterization

Parameters-errors ratio is too high

**To be written**

#### Plane, Line and Curve Constraints

**To be written**

#### Upper and Lower Value Bounds

**To be written**

# Related Books and Papers

The listed books and papers here were inspirational to this solver design.

- [Multiple view geometry in computer vision](http://www.robots.ox.ac.uk/~vgg/hzbook/)
- [Structure-from-Motion Revisited](https://demuc.de/papers/schoenberger2016sfm.pdf)
- [SBA: A Software Package for Generic
 Sparse Bundle Adjustment](http://users.ics.forth.gr/~lourakis/sba/sba-toms.pdf)
- [Methods for Non-Linear Least Squares Problems](http://www.imm.dtu.dk/pubdb/views/edoc_download.php/3215/pdf/imm3215.pdf)
- [Sparse Non-linear Least Squares Optimization
   for Geometric Vision](http://users.ics.forth.gr/~lourakis/sparseLM/sparselm_eccv10.pdf)
