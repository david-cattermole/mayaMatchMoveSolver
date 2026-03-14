.. _global-optimization-heading:

Global Optimization
===================

The core :ref:`camera solver <camera-solver-overview-heading>` assumes
known camera intrinsics. When intrinsic parameters such as focal
length are unknown or only approximate, the **Global Optimization**
step wraps the core solver to search for the values that produce the
best reconstruction.

Overview
--------

Global optimization treats the core camera solver as a black box. It
repeatedly runs the full solve pipeline with different candidate
parameter values, searching for the parameters that minimize overall
reprojection error across the entire sequence.

This is computationally expensive -- each evaluation requires a
complete camera solve -- but it allows the solver to recover
parameters that cannot be estimated within the incremental SfM
pipeline itself.

Search Strategies
-----------------

Two search strategies are available:

**Differential Evolution (DE)** -- A population-based evolutionary
optimization algorithm. A population of candidate parameter sets
evolves over multiple generations, with mutation and crossover
operators exploring the search space. Supports coarse-then-refined
passes: a broad initial search narrows the parameter range, followed
by a finer search within the narrowed bounds. This is generally the
preferred strategy for efficiency.

**Uniform Grid Search (UGS)** -- Exhaustive evaluation at regular
intervals across the parameter range. Simpler and easier to reason
about, but slower than Differential Evolution for high-dimensional or
wide-range searches.

Parameters
----------

Currently, the global optimization step supports searching for
**focal length** (applied uniformly across the sequence).

*Further detail on configuration, parameter ranges, and performance
characteristics will be added in future.*

See Also
--------

- :ref:`camera-solver-overview-heading` -- The core camera solver
  pipeline that is evaluated at each optimization step.
