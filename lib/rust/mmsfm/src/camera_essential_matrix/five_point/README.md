# Five-Point Relative Pose Estimation in Rust

A robust, production-ready implementation of the five-point algorithm for
relative camera pose estimation, based on Nistér's seminal 2004 paper "An
Efficient Solution to the Five-Point Relative Pose Problem" with improvements
from Hartley's implementation.

## Overview

This library provides efficient algorithms for estimating the relative pose
(rotation and translation) between two calibrated cameras from point
correspondences:

- **Minimal 5-point solver**  The full polynomial constraint system.
- **6-point algorithm** - Simpler linear solution for 6 points.
- **Overdetermined solution** - Least-squares solution for 7+ points.
- **Robust Sturm sequences** - Modified regula falsi for accurate root finding.
- **Numerical conditioning** - Improved stability for real-world data.

## Algorithm Details

### Five-Point Algorithm

The algorithm solves for the essential matrix E that satisfies:
- Epipolar constraint: `x'ᵀ E x = 0` for corresponding points.
- Essential matrix constraint: `2EEᵀE - tr(EEᵀ)E = 0` (equal singular values)
- Determinant constraint: `det(E) = 0` (rank 2)

Steps:
1. Build 5×9 constraint matrix from point correspondences.
2. Extract 4D nullspace basis using QR decomposition.
3. Apply cubic constraints to get 10 polynomial equations.
4. Gauss-Jordan elimination to reduce system.
5. Extract 10th degree polynomial determinant.
6. Find real roots using Sturm sequences.
7. Recover essential matrices and decompose to R, t.
8. Apply cheirality constraint for valid poses.

### Numerical Improvements

1. **Modified Regula Falsi**: Adaptive root finding that handles intervals beyond [-1,1]
2. **Polynomial Normalization**: Scaling for numerical stability.
3. **Illinois Algorithm**: Modification to prevent slow convergence.
4. **Sturm Chain Optimization**: Efficient recursive evaluation.

## Performance

The algorithm is highly optimized:
- SVD for minimal case (5 points)
- SVD for overdetermined case (7+ points)
- Efficient Sturm sequences with ~40 ops per evaluation
- Partial pivoting in Gauss-Jordan elimination
- Early termination in root finding

## Mathematical Background

The essential matrix E encodes the epipolar geometry between two views:

```
E = [t]ₓR
```

Where R is the rotation and [t]ₓ is the skew-symmetric matrix of translation.

For calibrated cameras with normalized image coordinates, the essential matrix satisfies:
- Rank 2 (determinant = 0)
- Two non-zero singular values are equal
- Can have up to 10 solutions (roots of 10th degree polynomial)
- Typically 2-4 real physically valid solutions

## Limitations

1. **Calibrated cameras required** - Intrinsic parameters must be known
2. **Planar degeneracy** - Coplanar points lead to ambiguity (2 solutions)
3. **Pure rotation** - Cannot determine translation scale
4. **Noise sensitivity** - Minimal solver sensitive to noise (use RANSAC)

## Testing

The library includes comprehensive examples demonstrating:
- Synthetic data with ground truth.
- Noisy measurements.
- Planar scenes (degenerate case).
- Performance benchmarks.

## References

1. Nistér, D. (2004). "An efficient solution to the five-point relative pose problem." IEEE TPAMI.
2. Hartley, R., Zisserman, A. (2003). "Multiple View Geometry in Computer Vision."
3. Li, H., Hartley, R. (2006). "Five-point motion estimation made easy." ICPR.
