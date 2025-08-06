/*
 * Copyright (C) 2025 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 * C++ wrapper for cminpack functionality used by mmSolver.
 */

#ifndef MMSOLVERLIBS_CMINPACK_WRAPPER_H
#define MMSOLVERLIBS_CMINPACK_WRAPPER_H

namespace mmsolverlibs {
namespace cminpack {

// Forward declarations of cminpack function types.
typedef int (*lmdif_func_type)(void *p, int m, int n, const double *x,
                               double *fvec, int iflag);
typedef int (*lmder_func_type)(void *p, int m, int n, const double *x,
                               double *fvec, double *fjac, int ldfjac,
                               int iflag);

// Wrapper functions.
int lmdif(lmdif_func_type fcn, void *p, int m, int n, double *x, double *fvec,
          double ftol, double xtol, double gtol, int maxfev, double epsfcn,
          double *diag, int mode, double factor, int nprint, int *nfev,
          double *fjac, int ldfjac, int *ipvt, double *qtf, double *wa1,
          double *wa2, double *wa3, double *wa4);

int lmder(lmder_func_type fcn, void *p, int m, int n, double *x, double *fvec,
          double *fjac, int ldfjac, double ftol, double xtol, double gtol,
          int maxfev, double *diag, int mode, double factor, int nprint,
          int *nfev, int *njev, int *ipvt, double *qtf, double *wa1,
          double *wa2, double *wa3, double *wa4);

double enorm(int n, const double *x);

}  // namespace cminpack
}  // namespace mmsolverlibs

#endif  // MMSOLVERLIBS_CMINPACK_WRAPPER_H
