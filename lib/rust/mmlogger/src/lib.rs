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

//! Zero-cost structured logger with compile-time feature gating.
//!
//! All types are generic over `std::io::Write` with static dispatch
//! (no vtable overhead). When using `NoOpLogger`, calls are
//! completely eliminated by the compiler.

use std::io::Write;

/// Trait for structured logging with zero-cost when disabled.
pub trait Logger {
    fn log(&mut self, level: &str, msg: &str);
}

/// Logger that writes to any `Write` implementor.
pub struct BaseLogger<W: Write> {
    writer: W,
}

impl<W: Write> BaseLogger<W> {
    pub fn new(writer: W) -> Self {
        Self { writer }
    }
}

impl<W: Write> Logger for BaseLogger<W> {
    fn log(&mut self, level: &str, msg: &str) {
        let _ = writeln!(self.writer, "[{}] {}", level, msg);
    }
}

/// Logger that writes to two outputs simultaneously.
pub struct TeeLogger<W1: Write, W2: Write> {
    writer1: W1,
    writer2: W2,
}

impl<W1: Write, W2: Write> TeeLogger<W1, W2> {
    pub fn new(writer1: W1, writer2: W2) -> Self {
        Self { writer1, writer2 }
    }
}

impl<W1: Write, W2: Write> Logger for TeeLogger<W1, W2> {
    fn log(&mut self, level: &str, msg: &str) {
        let _ = writeln!(self.writer1, "[{}] {}", level, msg);
        let _ = writeln!(self.writer2, "[{}] {}", level, msg);
    }
}

/// No-op logger with zero runtime cost.
pub struct NoOpLogger;

impl Logger for NoOpLogger {
    #[inline(always)]
    fn log(&mut self, _level: &str, _msg: &str) {}
}
