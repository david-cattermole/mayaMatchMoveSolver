// Ceres Solver - A fast non-linear least squares minimizer
// Copyright 2015 Google Inc. All rights reserved.
// http://ceres-solver.org/
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// * Redistributions of source code must retain the above copyright notice,
//   this list of conditions and the following disclaimer.
// * Redistributions in binary form must reproduce the above copyright notice,
//   this list of conditions and the following disclaimer in the documentation
//   and/or other materials provided with the distribution.
// * Neither the name of Google Inc. nor the names of its contributors may be
//   used to endorse or promote products derived from this software without
//   specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//
// Author: alexs.mac@gmail.com (Alex Stewart)

// Static configuration options for Ceres in mmSolver.
//
// This file contains a fixed configuration that matches mmSolver's
// requirements. It replaces the dynamic configuration generation
// for simplicity and consistency.

#ifndef CERES_PUBLIC_INTERNAL_CONFIG_H_
#define CERES_PUBLIC_INTERNAL_CONFIG_H_

// mmSolver uses Eigen for sparse linear algebra
#define CERES_USE_EIGEN_SPARSE

// mmSolver does not use LAPACK
#define CERES_NO_LAPACK

// mmSolver does not use SuiteSparse
#define CERES_NO_SUITESPARSE

// mmSolver does not use CXSparse
#define CERES_NO_CXSPARSE

// mmSolver uses C++11 features
#define CERES_USE_CXX11

// mmSolver disables threading for simplicity and Maya compatibility
#define CERES_NO_THREADS

// mmSolver uses std::unordered_map (C++11)
#define CERES_STD_UNORDERED_MAP

// mmSolver uses std::shared_ptr (C++11)
// (No additional defines needed for std namespace)

// mmSolver builds Ceres as a static library
// (CERES_USING_SHARED_LIBRARY is not defined)

// mmSolver does not use custom BLAS (uses Eigen's implementation)
#define CERES_NO_CUSTOM_BLAS

#endif  // CERES_PUBLIC_INTERNAL_CONFIG_H_