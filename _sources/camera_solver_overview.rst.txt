.. _camera-solver-overview-heading:

Camera Solver Overview
======================

The camera solver performs **incremental Structure-from-Motion (SfM)**,
reconstructing camera motion and 3D point positions from 2D marker
tracks in an image sequence.

**Input:**

- 2D marker tracks (per-frame screen-space positions).
- Known camera intrinsics (focal length, film back size).

**Output:**

- Per-frame camera poses (rotation and translation).
- 3D bundle positions (world-space coordinates for each tracked marker).

The solver is **deterministic** -- the same input data will always
produce the same output. There is no random seeding or
non-deterministic behaviour.

An optional :ref:`global-optimization-heading` step can wrap the
solver to search for optimal global parameters (such as focal length).

Pipeline Overview
-----------------

The solver runs in six phases:

1. Frame Analysis and Marker Selection
2. Initial Two-Camera Reconstruction
3. Incremental Camera Addition
4. Bundle Validation and Filtering
5. Final Global Bundle Adjustment
6. Origin Frame Transform and Scale

Phase 1: Frame Analysis and Marker Selection
---------------------------------------------

The solver analyzes all frames to select the best markers and frames
for reconstruction, scoring by two criteria:

- **Parallax** -- how much markers move between frames. More motion
  provides more information for recovering 3D structure.

- **Uniformity** -- how evenly markers are spread across the image,
  measured by dividing the image into a grid and checking the
  distribution of points across cells. Well-spread markers give
  stronger geometric constraints than clustered ones.

The result is a selected subset of markers and the frames where
those markers are visible.

Phase 2: Initial Two-Camera Reconstruction
-------------------------------------------

A good starting pair is critical -- errors here propagate through
the entire reconstruction.

The solver builds a frame graph evaluating all frame pairs by
parallax and marker overlap, then selects the best pair. The
relative pose between the two cameras is estimated using the
**Essential Matrix** (computed via the 5-point or 8-point algorithm
depending on the number of correspondences), which is decomposed
into candidate rotation and translation solutions. The correct
solution is chosen by triangulating points and verifying they are
in front of both cameras.

Initial 3D points are triangulated using the **optimal angular
method**, and a two-camera **bundle adjustment** refines the result.

Phase 3: Incremental Camera Addition
--------------------------------------

With an initial reconstruction established, the solver adds cameras
incrementally in two passes:

- **Pass 1 (Draft):** Adds skeleton key frames spread across the
  sequence, building a stable backbone.
- **Pass 2 (Final):** Fills in all remaining frames.

For each new frame, the solver runs **PnP (Perspective-n-Point)**
using the **SQPnP** algorithm to compute the camera pose from known
3D points, validates the result, and refines with a single-camera
bundle adjustment.

After each round of camera additions, a **global bundle adjustment**
refines all cameras and points together. Additional markers are then
triangulated and added to the reconstruction. Markers that fail
geometric triangulation are placed at the **mean scene depth** as
an initial estimate and refined by subsequent bundle adjustment --
this ensures as many markers as possible contribute to the result.

Phase 4: Bundle Validation and Filtering
-----------------------------------------

The solver validates the reconstruction by filtering out 3D bundles
with high reprojection error or degenerate geometry, and checking for
cameras converging to the same position, indicating a failed solve.

Phase 5: Final Global Bundle Adjustment
----------------------------------------

A final bundle adjustment refines all cameras and 3D points
together. Small noise is added to parameters to help escape local
minima, and remaining markers are retriangulated and included.

Phase 6: Origin Frame Transform and Scale
-------------------------------------------

SfM reconstructions live in an arbitrary coordinate system with no
meaningful relationship to the real-world scene. The solver transforms
the result to align with a user-specified **origin frame** and applies
a **scene scale factor**, so the solved camera output is consistently
scaled for use in MatchMove workflows.

Key Algorithms
--------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Algorithm
     - Purpose
   * - Essential Matrix (5-point / 8-point)
     - Initial relative pose between two cameras
   * - SQPnP
     - Camera pose from 3D-2D correspondences
   * - Optimal Angular Triangulation
     - 3D point estimation from multiple views
   * - Depth-based Triangulation
     - Fallback for points that fail geometric triangulation
   * - Levenberg-Marquardt Bundle Adjustment
     - Non-linear refinement of all parameters; dense or sparse
       depending on problem size
   * - Bundle Validation
     - Reprojection error filtering and collapse detection

Bundle Adjustment
-----------------

Bundle adjustment minimizes **reprojection error** -- the distance
between where a 3D point projects into each camera and where the
marker was observed. It jointly optimizes camera poses (rotation and
translation) and 3D point positions using the Levenberg-Marquardt
algorithm, with a dense or sparse solver selected based on problem
size.

See Also
--------

- :ref:`global-optimization-heading` -- Optional focal length
  optimization wrapping the core solver.
