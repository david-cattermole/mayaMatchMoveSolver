//
// Copyright (C) 2023 David Cattermole.
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
//

/// This number is the hard-coded number of points in the LDPK look-up
/// table, as defined in the file "ldpk/ldpk_ldp_builtin.h", in method
/// "ldp_builtin<VEC2,MAT2>::update_lut()".
#[allow(dead_code)]
const LDPK_LOOKUP_TABLE_SIZE: usize = 45 * 45;

/// The minimum number of samples that need to be exceeded before it
/// makes sense (in terms of performance) to use multiple threads to
/// compute the lens distortion.
///
/// The Lookup Table size is multipled by 2, because we must do at
/// least LDPK_LOOKUP_TABLE_SIZE operations. If we're not doing at
/// least double that amount, it is probably faster to use a single
/// thread.
#[allow(dead_code)]
pub const MIN_DISTORT_SAMPLES: usize = LDPK_LOOKUP_TABLE_SIZE * 2;

/// Defines how many tasks are created for each requested
/// thread. The minimum allowed value is 1.
///
/// It is useful to have more tasks than threads as a form of
/// load-balancing. CPU threads that are slower than others
/// (because of the current system load) should not be given
/// the same amount of work as faster threads, because the
/// slower thread(s) will slow the overall progress while the
/// faster threads wait for the slower threads to complete.
#[allow(dead_code)]
pub const THREAD_TASK_BREAK_UP_FACTOR: usize = 4;

/// The maximum lens parameter count, used to hold at most this number
/// of lens parameter values.
pub const MAX_LENS_PARAMETER_COUNT: usize = 5;
