# Copyright (C) 2025 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------
#
# CMake build for vendored Ceres Solver (version 1.14.0)
#
# This is a simplified build of Ceres Solver, configured for use with mmSolver.
# It builds only the core functionality needed by OpenMVG and mmSolver.
#
# Key simplifications made:
# - Uses fixed configuration instead of dynamic feature detection
# - Automatically discovers source files instead of manual listing
# - Directly links with vendored glog and Eigen
# - Removes tests, examples, documentation, and optional features
# - Optimized for Maya plugin compatibility
#

set(CERES_VERSION "1.14.0")
set(CERES_VERSION_MAJOR "1")
set(CERES_VERSION_MINOR "14")
set(CERES_VERSION_PATCH "0")

# Define the source files for Ceres (from internal/ceres/CMakeLists.txt)
set(CERES_INTERNAL_SRC
    internal/ceres/array_utils.cc
    internal/ceres/blas.cc
    internal/ceres/block_evaluate_preparer.cc
    internal/ceres/block_jacobi_preconditioner.cc
    internal/ceres/block_jacobian_writer.cc
    internal/ceres/block_random_access_dense_matrix.cc
    internal/ceres/block_random_access_diagonal_matrix.cc
    internal/ceres/block_random_access_matrix.cc
    internal/ceres/block_random_access_sparse_matrix.cc
    internal/ceres/block_sparse_matrix.cc
    internal/ceres/block_structure.cc
    internal/ceres/c_api.cc
    internal/ceres/canonical_views_clustering.cc
    internal/ceres/cgnr_solver.cc
    internal/ceres/callbacks.cc
    internal/ceres/compressed_col_sparse_matrix_utils.cc
    internal/ceres/compressed_row_jacobian_writer.cc
    internal/ceres/compressed_row_sparse_matrix.cc
    internal/ceres/conditioned_cost_function.cc
    internal/ceres/conjugate_gradients_solver.cc
    internal/ceres/context.cc
    internal/ceres/context_impl.cc
    internal/ceres/coordinate_descent_minimizer.cc
    internal/ceres/corrector.cc
    internal/ceres/covariance.cc
    internal/ceres/covariance_impl.cc
    internal/ceres/dense_normal_cholesky_solver.cc
    internal/ceres/dense_qr_solver.cc
    internal/ceres/dense_sparse_matrix.cc
    internal/ceres/detect_structure.cc
    internal/ceres/dogleg_strategy.cc
    internal/ceres/dynamic_compressed_row_jacobian_writer.cc
    internal/ceres/dynamic_compressed_row_sparse_matrix.cc
    internal/ceres/dynamic_sparse_normal_cholesky_solver.cc
    internal/ceres/evaluator.cc
    internal/ceres/eigensparse.cc
    internal/ceres/file.cc
    internal/ceres/function_sample.cc
    internal/ceres/gradient_checker.cc
    internal/ceres/gradient_checking_cost_function.cc
    internal/ceres/gradient_problem.cc
    internal/ceres/gradient_problem_solver.cc
    internal/ceres/implicit_schur_complement.cc
    internal/ceres/inner_product_computer.cc
    internal/ceres/is_close.cc
    internal/ceres/iterative_schur_complement_solver.cc
    internal/ceres/levenberg_marquardt_strategy.cc
    internal/ceres/lapack.cc
    internal/ceres/line_search.cc
    internal/ceres/line_search_direction.cc
    internal/ceres/line_search_minimizer.cc
    internal/ceres/line_search_preprocessor.cc
    internal/ceres/linear_least_squares_problems.cc
    internal/ceres/linear_operator.cc
    internal/ceres/linear_solver.cc
    internal/ceres/local_parameterization.cc
    internal/ceres/loss_function.cc
    internal/ceres/low_rank_inverse_hessian.cc
    internal/ceres/minimizer.cc
    internal/ceres/normal_prior.cc
    internal/ceres/parallel_for_cxx.cc
    internal/ceres/parallel_for_tbb.cc
    internal/ceres/parallel_utils.cc
    internal/ceres/parameter_block_ordering.cc
    internal/ceres/partitioned_matrix_view.cc
    internal/ceres/polynomial.cc
    internal/ceres/preconditioner.cc
    internal/ceres/preprocessor.cc
    internal/ceres/problem.cc
    internal/ceres/problem_impl.cc
    internal/ceres/program.cc
    internal/ceres/reorder_program.cc
    internal/ceres/residual_block.cc
    internal/ceres/residual_block_utils.cc
    internal/ceres/schur_complement_solver.cc
    internal/ceres/schur_eliminator.cc
    internal/ceres/schur_jacobi_preconditioner.cc
    internal/ceres/schur_templates.cc
    internal/ceres/scratch_evaluate_preparer.cc
    internal/ceres/single_linkage_clustering.cc
    internal/ceres/solver.cc
    internal/ceres/solver_utils.cc
    internal/ceres/sparse_cholesky.cc
    internal/ceres/sparse_matrix.cc
    internal/ceres/sparse_normal_cholesky_solver.cc
    internal/ceres/subset_preconditioner.cc
    internal/ceres/split.cc
    internal/ceres/stringprintf.cc
    internal/ceres/thread_pool.cc
    internal/ceres/thread_token_provider.cc
    internal/ceres/triplet_sparse_matrix.cc
    internal/ceres/trust_region_preprocessor.cc
    internal/ceres/trust_region_minimizer.cc
    internal/ceres/trust_region_step_evaluator.cc
    internal/ceres/trust_region_strategy.cc
    internal/ceres/types.cc
    internal/ceres/visibility.cc
    internal/ceres/visibility_based_preconditioner.cc
    internal/ceres/wall_time.cc
)

# Include essential SchurEliminator and PartitionedMatrixView specializations
set(CERES_INTERNAL_SCHUR_FILES
    # SchurEliminator specializations
    internal/ceres/generated/schur_eliminator_2_2_2.cc
    internal/ceres/generated/schur_eliminator_2_2_3.cc
    internal/ceres/generated/schur_eliminator_2_2_4.cc
    internal/ceres/generated/schur_eliminator_2_2_d.cc
    internal/ceres/generated/schur_eliminator_2_3_3.cc
    internal/ceres/generated/schur_eliminator_2_3_4.cc
    internal/ceres/generated/schur_eliminator_2_3_6.cc
    internal/ceres/generated/schur_eliminator_2_3_9.cc
    internal/ceres/generated/schur_eliminator_2_3_d.cc
    internal/ceres/generated/schur_eliminator_2_4_3.cc
    internal/ceres/generated/schur_eliminator_2_4_4.cc
    internal/ceres/generated/schur_eliminator_2_4_6.cc
    internal/ceres/generated/schur_eliminator_2_4_8.cc
    internal/ceres/generated/schur_eliminator_2_4_9.cc
    internal/ceres/generated/schur_eliminator_2_4_d.cc
    internal/ceres/generated/schur_eliminator_2_d_d.cc
    internal/ceres/generated/schur_eliminator_4_4_2.cc
    internal/ceres/generated/schur_eliminator_4_4_3.cc
    internal/ceres/generated/schur_eliminator_4_4_4.cc
    internal/ceres/generated/schur_eliminator_4_4_d.cc
    internal/ceres/generated/schur_eliminator_d_d_d.cc
    # PartitionedMatrixView specializations
    internal/ceres/generated/partitioned_matrix_view_2_2_2.cc
    internal/ceres/generated/partitioned_matrix_view_2_2_3.cc
    internal/ceres/generated/partitioned_matrix_view_2_2_4.cc
    internal/ceres/generated/partitioned_matrix_view_2_2_d.cc
    internal/ceres/generated/partitioned_matrix_view_2_3_3.cc
    internal/ceres/generated/partitioned_matrix_view_2_3_4.cc
    internal/ceres/generated/partitioned_matrix_view_2_3_6.cc
    internal/ceres/generated/partitioned_matrix_view_2_3_9.cc
    internal/ceres/generated/partitioned_matrix_view_2_3_d.cc
    internal/ceres/generated/partitioned_matrix_view_2_4_3.cc
    internal/ceres/generated/partitioned_matrix_view_2_4_4.cc
    internal/ceres/generated/partitioned_matrix_view_2_4_6.cc
    internal/ceres/generated/partitioned_matrix_view_2_4_8.cc
    internal/ceres/generated/partitioned_matrix_view_2_4_9.cc
    internal/ceres/generated/partitioned_matrix_view_2_4_d.cc
    internal/ceres/generated/partitioned_matrix_view_2_d_d.cc
    internal/ceres/generated/partitioned_matrix_view_4_4_2.cc
    internal/ceres/generated/partitioned_matrix_view_4_4_3.cc
    internal/ceres/generated/partitioned_matrix_view_4_4_4.cc
    internal/ceres/generated/partitioned_matrix_view_4_4_d.cc
    internal/ceres/generated/partitioned_matrix_view_d_d_d.cc
)

# Create the ceres static library
add_library(ceres STATIC ${CERES_INTERNAL_SRC} ${CERES_INTERNAL_SCHUR_FILES})

# Set library properties
set_target_properties(ceres PROPERTIES
  VERSION ${CERES_VERSION}
  SOVERSION ${CERES_VERSION_MAJOR}
)

# Use static configuration instead of dynamic generation
# This simplifies the build and ensures consistent behavior
set(CERES_CONFIG_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/config_static")
set(CERES_CONFIG_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/config")

# Copy the static config.h to the build directory
file(COPY "${CERES_CONFIG_SOURCE_DIR}/" 
     DESTINATION "${CERES_CONFIG_OUTPUT_DIR}")

# Configure include directories
# PUBLIC directories are available to both Ceres and its consumers
target_include_directories(ceres PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>   # Public API headers
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/internal> # Internal headers
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/config>   # Generated config.h
  $<INSTALL_INTERFACE:include>                            # Install location
)

# Configure compile definitions for mmSolver build environment
# All definitions consolidated into a single call for clarity
target_compile_definitions(ceres PUBLIC
  # Vendored glog configuration
  GLOG_STATIC_DEFINE
  GLOG_USE_GLOG_EXPORT
  GOOGLE_GLOG_DLL_DECL=
  GOOGLE_GLOG_DLL_DECL_FOR_UNITTESTS=
  GLOG_EXPORT=
  GLOG_NO_EXPORT=
  # C++ Standard Library namespace configuration
  CERES_HASH_NAMESPACE_START=namespace\ std\ {
  CERES_HASH_NAMESPACE_END=}
  # Platform-specific definitions
  $<$<PLATFORM_ID:Windows>:NOMINMAX>
  $<$<PLATFORM_ID:Windows>:WIN32_LEAN_AND_MEAN>
  $<$<PLATFORM_ID:Windows>:_USE_MATH_DEFINES>
)

# Set position independent code if needed
if(CMAKE_POSITION_INDEPENDENT_CODE)
  set_target_properties(ceres PROPERTIES
    POSITION_INDEPENDENT_CODE ON
  )
endif()

# Link with vendored dependencies
# PUBLIC linking ensures these dependencies are available to consumers
target_link_libraries(ceres PUBLIC
  glog::glog         # Vendored glog for logging
  Eigen3::Eigen      # Vendored Eigen for linear algebra
)

# Threading support is intentionally disabled (CERES_NO_THREADS)
# This simplifies the build and ensures Maya plugin compatibility

# Create an alias to match the expected target name from FindCeres
add_library(ceres::ceres ALIAS ceres)

# Install headers (public API)
install(DIRECTORY include/ceres
  DESTINATION include
  FILES_MATCHING PATTERN "*.h"
)

# Install the static config.h (required by internal headers)
install(FILES ${CERES_CONFIG_OUTPUT_DIR}/ceres/internal/config.h
  DESTINATION include/ceres/internal
)

# Install the library as part of mmsolverlibs
# Note: The following is only used when building as part of mmSolver
if(COMMAND mm_common_install_target_library)
  include(MMCommonUtils)
  mm_common_install_target_library("mmsolverlibs_cpp" ceres)
else()
  # Standalone installation
  install(TARGETS ceres
    EXPORT CeresTargets
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
  )
endif()