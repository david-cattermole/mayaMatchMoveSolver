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
 * C++ wrapper implementation for cminpack functionality.
 */

#include "mmsolverlibs/cminpack_wrapper.h"

#include <cminpack.h>

namespace mmsolverlibs {
namespace cminpack {

int lmdif(lmdif_func_type fcn, void *p, int m, int n, double *x, double *fvec,
          double ftol, double xtol, double gtol, int maxfev, double epsfcn,
          double *diag, int mode, double factor, int nprint, int *nfev,
          double *fjac, int ldfjac, int *ipvt, double *qtf, double *wa1,
          double *wa2, double *wa3, double *wa4) {
    // Call the actual cminpack library function directly to avoid
    // recursion.
    return ::lmdif(fcn, p, m, n, x, fvec, ftol, xtol, gtol, maxfev, epsfcn,
                   diag, mode, factor, nprint, nfev, fjac, ldfjac, ipvt, qtf,
                   wa1, wa2, wa3, wa4);
}

int lmder(lmder_func_type fcn, void *p, int m, int n, double *x, double *fvec,
          double *fjac, int ldfjac, double ftol, double xtol, double gtol,
          int maxfev, double *diag, int mode, double factor, int nprint,
          int *nfev, int *njev, int *ipvt, double *qtf, double *wa1,
          double *wa2, double *wa3, double *wa4) {
    // Call the actual cminpack library function directly to avoid
    // recursion.
    return ::lmder(fcn, p, m, n, x, fvec, fjac, ldfjac, ftol, xtol, gtol,
                   maxfev, diag, mode, factor, nprint, nfev, njev, ipvt, qtf,
                   wa1, wa2, wa3, wa4);
}

double enorm(int n, const double *x) {
    // Call the actual cminpack library function directly to avoid
    // recursion.
    return ::enorm(n, x);
}

}  // namespace cminpack
}  // namespace mmsolverlibs
