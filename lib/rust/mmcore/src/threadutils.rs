//
// Copyright (C) 2026 David Cattermole.
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

/// Get the current thread's numeric ID.
///
/// `std::thread::current().id().as_u64()` is nightly-only, so we
/// parse the number from the `Debug` representation `ThreadId(N)`.
pub fn thread_id_u64() -> u64 {
    let id = std::thread::current().id();
    let s = format!("{:?}", id);
    s.trim_start_matches("ThreadId(")
        .trim_end_matches(')')
        .parse::<u64>()
        .unwrap_or(0)
}
