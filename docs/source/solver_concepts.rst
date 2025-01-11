.. _solver-concepts-heading:

Understanding the Solver Core Concepts
======================================

The Basic Idea
--------------

Think of mmSolver like a puzzle solver. You have:

- A set of 2D points in your camera view (Markers).
- A set of 3D points in space (Bundles).
- A camera looking at the scene.
- Various properties (attributes) that can be adjusted.

The solver's job is to find the perfect values for these properties so
that when you look through the camera, the 3D points line up exactly
with the 2D points.

Real-World Analogy
------------------

Imagine you're trying to take a photo of a building:

- The building's features are like your 3D Bundles.
- The spots in your viewfinder are like 2D Markers.
- You can move yourself (the camera) or the building (the object).
- Your goal is to make the photo match a reference image exactly./

Key Components
--------------

1. Markers (2D Points)
~~~~~~~~~~~~~~~~~~~~~~

- Like push-pins on a photograph.
- Represent tracked features in your footage.
- Have accurate screen positions.
- Store deviation (error) values.

See :ref:`create-marker-ref` for creating Markers.

2. Bundles (3D Points)
~~~~~~~~~~~~~~~~~~~~~~

- Like push-pins in the real world.
- Represent actual 3D positions.
- Can be connected to multiple Markers.
- Move when their attributes change.

See :ref:`create-bundle-ref` for creating Bundles.

3. Attributes
~~~~~~~~~~~~~

- Properties that can be solved.
- Examples: camera position, object rotation, focal length.
- Can be:

  - Static (one value for all frames).
  - Animated (different values per frame).
  - Locked (won't be changed by solver).

See :ref:`solver-design-attributes` for more details.

4. Deviation (Error)
~~~~~~~~~~~~~~~~~~~~

- Measures how far off the solution is.
- Calculated in pixels.
- Lower values = better solve.
- Displayed per Marker and as overall average.

How the Solver Works
--------------------

1. Initial Setup
~~~~~~~~~~~~~~~~

- You provide starting positions for everything.
- Better initial guesses = better, faster solves.
- The solver won't drastically change your initial setup.

2. Solving Process
~~~~~~~~~~~~~~~~~~

1. Measures current error.
2. Makes small adjustments to attributes.
3. Checks if error improved.
4. Repeats until error is acceptable or can't improve.

Like walking down a hill blindfolded:

- Take a small step.
- Check if you're lower than before.
- Keep going until you reach the bottom.
- Sometimes you need to try different directions.

3. Solving Strategies
~~~~~~~~~~~~~~~~~~~~~

Basic Solve
^^^^^^^^^^^

- Simplest approach.
- Solves frame-by-frame.
- Only for animated attributes.

See :ref:`basic-solver-tab-heading` for details.

Standard Solve
^^^^^^^^^^^^^^

- More sophisticated.
- Handles static and animated attributes.
- Uses key "root frames" for results stability.

See :ref:`standard-solver-tab-heading` for details.

Common Pitfalls and Solutions
-----------------------------

1. Too Few Markers
~~~~~~~~~~~~~~~~~~

- Like trying to balance a table with too few legs.
- Need enough measurements to solve your attributes.
- Rule: Measurements > Attributes being solved.

2. Poor Initial Values
~~~~~~~~~~~~~~~~~~~~~~

- Like starting a maze from the wrong entrance.
- Get camera/object roughly positioned first.
- Use known information (focal length, object size).

3. Over-constraining
~~~~~~~~~~~~~~~~~~~~

- Like trying to fit a square peg in a round hole.
- Don't solve attributes that should be fixed.
- Lock attributes when you know their values.

Best Practices
-------------

1. Start Simple
~~~~~~~~~~~~~~~

- Begin with basic solves.
- Add complexity gradually.
- Verify each step.

2. Use Root Frames
~~~~~~~~~~~~~~~~~~

- Pick frames with good parallax.
- Space them throughout the sequence.
- Use for initial static solves.

See :ref:`solver-design-time-evaluation` for details.

3. Check Your Work
~~~~~~~~~~~~~~~~~~

- Monitor deviation values.
- Visually verify results.
- Test solve stability.

Advanced Topics
---------------

1. Weight Values
~~~~~~~~~~~~~~~~

- Control Marker importance.
- Higher weight = more influence.

2. Solve Strategies
~~~~~~~~~~~~~~~~~~~

- Different approaches for different scenarios.
- Can combine multiple solve passes.
- Balance speed vs accuracy.

See :ref:`solver-design-solver-strategies` for details.

3. Hierarchical Solving
~~~~~~~~~~~~~~~~~~~~~~~

- Solve simple relationships first.
- Build up to complex relationships.
- Maintain solve stability.

For practical examples, see the :ref:`tutorial-heading` section.
