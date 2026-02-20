// Copyright (C) 2025 David Cattermole.
//
// This file is part of mmSolver.
//
// mmSolver is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// mmSolver is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
// ====================================================================

#include <inttypes.h>
#include <stdlib.h>
#include <string.h>

#include <suitesparse/cholmod.h>

#include "constants.h"

/// @brief Holds the data for CHOLMOD solver.
struct InterfaceCHOLMOD {
    /// @brief Common CHOLMOD structure with settings and workspace.
    cholmod_common common;

    /// @brief Pointer to the factorization (L or LD or LDL').
    cholmod_factor *L;

    /// @brief Indicates that the initialization has been completed.
    C_BOOL initialized;

    /// @brief Indicates that the factorization has been completed.
    C_BOOL factorized;
};

/// @brief Allocates a new CHOLMOD solver interface.
struct InterfaceCHOLMOD *solver_cholmod_new() {
    struct InterfaceCHOLMOD *solver =
        (struct InterfaceCHOLMOD *)malloc(sizeof(struct InterfaceCHOLMOD));

    if (solver == NULL) {
        return NULL;
    }

    // Initialize CHOLMOD.
    cholmod_start(&solver->common);

    // Set default parameters.
    solver->common.print = 0;  // Suppress printing by default.

    solver->L = NULL;
    solver->initialized = C_FALSE;
    solver->factorized = C_FALSE;

    return solver;
}

/// @brief Deallocates the CHOLMOD solver interface.
void solver_cholmod_drop(struct InterfaceCHOLMOD *solver) {
    if (solver == NULL) {
        return;
    }

    if (solver->L != NULL) {
        cholmod_free_factor(&solver->L, &solver->common);
    }

    cholmod_finish(&solver->common);
    free(solver);
}

/// @brief Creates a CHOLMOD sparse matrix from CSC format.
///
/// @param nrow Number of rows.
/// @param ncol Number of columns.
/// @param nzmax Maximum number of nonzeros.
/// @param col_pointers Column pointers array (size ncol + 1).
/// @param row_indices Row indices array (size nzmax).
/// @param values Values array (size nzmax), can be NULL for pattern.
/// @param stype Symmetry type: -1 (lower), 0 (unsymmetric), 1 (upper).
/// @param xtype Value type: CHOLMOD_REAL, CHOLMOD_COMPLEX, etc.
/// @param dtype Data type: CHOLMOD_DOUBLE or CHOLMOD_SINGLE.
/// @param common CHOLMOD common structure.
/// @return Pointer to cholmod_sparse matrix, or NULL on error.
static cholmod_sparse *create_cholmod_sparse(size_t nrow, size_t ncol,
                                             size_t nzmax,
                                             const int32_t *col_pointers,
                                             const int32_t *row_indices,
                                             const double *values, int stype,
                                             int xtype, int dtype,
                                             cholmod_common *common) {
    // Allocate sparse matrix.
    cholmod_sparse *A =
        cholmod_allocate_sparse(nrow, ncol, nzmax, 1, 1, stype, xtype + dtype, common);

    if (A == NULL) {
        return NULL;
    }

    // Copy column pointers.
    int32_t *Ap = (int32_t *)A->p;
    for (size_t i = 0; i <= ncol; i++) {
        Ap[i] = col_pointers[i];
    }

    // Copy row indices.
    int32_t *Ai = (int32_t *)A->i;
    for (size_t i = 0; i < nzmax; i++) {
        Ai[i] = row_indices[i];
    }

    // Copy values if provided.
    if (values != NULL && xtype != CHOLMOD_PATTERN) {
        double *Ax = (double *)A->x;
        for (size_t i = 0; i < nzmax; i++) {
            Ax[i] = values[i];
        }
    }

    return A;
}

/// @brief Performs the symbolic factorization (analyze phase).
int32_t solver_cholmod_analyze(struct InterfaceCHOLMOD *solver, int32_t nrow,
                                int32_t ncol, int32_t nzmax,
                                const int32_t *col_pointers,
                                const int32_t *row_indices,
                                const double *values, int32_t stype,
                                C_BOOL verbose) {
    if (solver == NULL) {
        return ERROR_NULL_POINTER;
    }

    if (solver->initialized == C_TRUE) {
        return ERROR_ALREADY_INITIALIZED;
    }

    // Set verbosity.
    if (verbose == C_TRUE) {
        solver->common.print = 3;
    } else {
        solver->common.print = 0;
    }

    // Create CHOLMOD sparse matrix.
    cholmod_sparse *A =
        create_cholmod_sparse(nrow, ncol, nzmax, col_pointers, row_indices,
                              values, stype, CHOLMOD_REAL, CHOLMOD_DOUBLE, &solver->common);

    if (A == NULL) {
        return ERROR_MALLOC;
    }

    // Analyze.
    solver->L = cholmod_analyze(A, &solver->common);

    cholmod_free_sparse(&A, &solver->common);

    if (solver->L == NULL) {
        return ERROR_INVALID_INPUT;
    }

    solver->initialized = C_TRUE;
    return SUCCESSFUL_EXIT;
}

/// @brief Performs the numeric factorization.
int32_t solver_cholmod_factorize(struct InterfaceCHOLMOD *solver, int32_t nrow,
                                  int32_t ncol, int32_t nzmax,
                                  const int32_t *col_pointers,
                                  const int32_t *row_indices,
                                  const double *values, int32_t stype,
                                  C_BOOL verbose) {
    if (solver == NULL) {
        return ERROR_NULL_POINTER;
    }

    if (solver->initialized == C_FALSE) {
        return ERROR_NOT_INITIALIZED;
    }

    // Set verbosity.
    if (verbose == C_TRUE) {
        solver->common.print = 3;
    } else {
        solver->common.print = 0;
    }

    // Create CHOLMOD sparse matrix.
    cholmod_sparse *A =
        create_cholmod_sparse(nrow, ncol, nzmax, col_pointers, row_indices,
                              values, stype, CHOLMOD_REAL, CHOLMOD_DOUBLE, &solver->common);

    if (A == NULL) {
        return ERROR_MALLOC;
    }

    // Factorize.
    int status = cholmod_factorize(A, solver->L, &solver->common);

    cholmod_free_sparse(&A, &solver->common);

    if (status == 0) {
        // Check if the matrix is not positive definite.
        if (solver->common.status == CHOLMOD_NOT_POSDEF) {
            return ERROR_NOT_POSITIVE_DEFINITE;
        }
        return ERROR_INVALID_INPUT;
    }

    solver->factorized = C_TRUE;
    return SUCCESSFUL_EXIT;
}

/// @brief Solves the linear system Ax=b.
int32_t solver_cholmod_solve(struct InterfaceCHOLMOD *solver, double *x,
                              const double *rhs, int32_t n, C_BOOL verbose) {
    if (solver == NULL) {
        return ERROR_NULL_POINTER;
    }

    if (solver->factorized == C_FALSE) {
        return ERROR_NOT_FACTORIZED;
    }

    // Set verbosity.
    if (verbose == C_TRUE) {
        solver->common.print = 3;
    } else {
        solver->common.print = 0;
    }

    // Create dense vector for RHS.
    cholmod_dense *b =
        cholmod_allocate_dense(n, 1, n, CHOLMOD_REAL + CHOLMOD_DOUBLE, &solver->common);
    if (b == NULL) {
        return ERROR_MALLOC;
    }

    // Copy RHS values.
    double *bx = (double *)b->x;
    for (int32_t i = 0; i < n; i++) {
        bx[i] = rhs[i];
    }

    // Solve.
    cholmod_dense *result = cholmod_solve(CHOLMOD_A, solver->L, b, &solver->common);

    cholmod_free_dense(&b, &solver->common);

    if (result == NULL) {
        return ERROR_INVALID_INPUT;
    }

    // Copy result to output.
    double *rx = (double *)result->x;
    for (int32_t i = 0; i < n; i++) {
        x[i] = rx[i];
    }

    cholmod_free_dense(&result, &solver->common);

    return SUCCESSFUL_EXIT;
}

/// @brief Gets the reciprocal condition number estimate.
int32_t solver_cholmod_rcond(struct InterfaceCHOLMOD *solver,
                              double *rcond_estimate) {
    if (solver == NULL) {
        return ERROR_NULL_POINTER;
    }

    if (solver->factorized == C_FALSE) {
        return ERROR_NOT_FACTORIZED;
    }

    *rcond_estimate = cholmod_rcond(solver->L, &solver->common);

    return SUCCESSFUL_EXIT;
}

/// @brief Resets the solver to uninitialized state, allowing reuse.
void solver_cholmod_reset(struct InterfaceCHOLMOD *solver) {
    if (solver == NULL) {
        return;
    }

    // Free the factor if it exists.
    if (solver->L != NULL) {
        cholmod_free_factor(&solver->L, &solver->common);
        solver->L = NULL;
    }

    // Reset state flags.
    solver->initialized = C_FALSE;
    solver->factorized = C_FALSE;
}
