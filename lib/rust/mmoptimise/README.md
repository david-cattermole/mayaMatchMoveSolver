# mmoptimise - Rust Optimization Library

A sophisticated, high-performance Rust library providing non-linear
least-squares optimization algorithms with automatic differentiation. Built for
demanding optimization problems in computer vision as part of the mmSolver
project for camera tracking and matchmoving applications.

The library implements a robust Levenberg-Marquardt solver with trust region
management, QR decomposition, and machine-precision gradient computation using
dual numbers.

## Quick Start

```rust
use mmoptimise_rust::{LevenbergMarquardt, OptimisationProblem, SolverWorkspace};

// 1. Implement OptimisationProblem trait for your problem
// 2. Create solver and workspace
let solver = LevenbergMarquardt::with_defaults();
let mut workspace = SolverWorkspace::new(&problem, &initial_params)?;

// 3. Solve
let result = solver.solve_problem(&problem, &mut workspace)?;
```

**For detailed usage examples, implementation guides, troubleshooting tips,
  and configuration options, see the comprehensive documentation in the source
  code:**

## Benchmarking

This library includes comprehensive benchmarking tools to evaluate solver
performance across various challenging optimization problems.

### Running Benchmarks

#### Quick Benchmarks with Criterion
```bash
# Run all benchmarks
cargo bench

# Run specific benchmark groups
cargo bench rosenbrock
cargo bench curve_fitting
cargo bench extended_rosenbrock
```

## Development & Contributing

### Running Tests
```bash
# Run all tests
cargo test

# Run tests with output (useful for debugging)
cargo test -- --nocapture

# Run specific test module
cargo test rosenbrock

# Run tests in release mode (faster)
cargo test --release
```

### Performance Analysis
```bash
# Run benchmarks
cargo bench

# Profile specific benchmark
cargo bench -- rosenbrock --profile-time=10

# Memory usage analysis
cargo run --example comprehensive_benchmark --release -- --memory-profile
```
