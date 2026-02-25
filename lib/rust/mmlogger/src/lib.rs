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
use std::sync::mpsc;
use std::thread;
use std::time::SystemTime;

// ====================================================================
// Log level filter
// ====================================================================

/// Bitmask of allowed log levels for a stream.
///
/// Combine levels with `|`:
/// ```
/// use mmlogger::LevelFilter;
/// let filter = LevelFilter::INFO | LevelFilter::WARN | LevelFilter::ERROR;
/// ```
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct LevelFilter(u8);

impl LevelFilter {
    pub const NONE: LevelFilter = LevelFilter(0b0000);
    pub const DEBUG: LevelFilter = LevelFilter(0b0001);
    pub const INFO: LevelFilter = LevelFilter(0b0010);
    // TODO: Add "PROGRESS" level between INFO and WARN.
    pub const WARN: LevelFilter = LevelFilter(0b0100);
    pub const ERROR: LevelFilter = LevelFilter(0b1000);
    pub const ALL: LevelFilter = LevelFilter(0b1111);

    pub fn allows(self, level: &str) -> bool {
        let bit: u8 = match level {
            "DEBUG" => 0b0001,
            "INFO" => 0b0010,
            "WARN" => 0b0100,
            "ERROR" => 0b1000,
            _ => 0,
        };
        self.0 & bit != 0
    }
}

impl std::ops::BitOr for LevelFilter {
    type Output = Self;
    fn bitor(self, rhs: Self) -> Self {
        LevelFilter(self.0 | rhs.0)
    }
}

// ====================================================================
// Log format
// ====================================================================

/// Output format for a log stream.
pub enum LogFormat {
    /// Plain message with no prefix: `Message here`
    ///
    /// WARN and ERROR levels are prefixed with `Warning: ` and `Error: `
    /// respectively.
    Plain,
    /// Level-prefixed: `[LEVEL] Message here`
    LevelPrefix,
    /// Timestamped: `YYYY-MM-DD HH:MM:SS [LEVEL] Message here`
    Timestamp,
}

// ====================================================================
// Timestamp helpers (stdlib only, no extra dependencies)
// ====================================================================

/// Format a Unix timestamp (seconds since epoch) as `YYYY-MM-DD HH:MM:SS`.
///
/// Uses the Gregorian calendar proleptic algorithm (valid for all
/// positive Unix timestamps).
fn format_unix_timestamp(secs: u64, buf: &mut [u8; 19]) {
    // Time-of-day components.
    let time_of_day = secs % 86400;
    let hh = time_of_day / 3600;
    let mm = (time_of_day % 3600) / 60;
    let ss = time_of_day % 60;

    // Date components via the civil calendar algorithm.
    //
    // http://howardhinnant.github.io/date_algorithms.html
    let days = (secs / 86400) as i64 + 719468; // shift epoch to 0000-03-01
    let era = if days >= 0 { days } else { days - 146096 } / 146097;
    let doe = days - era * 146097; // day of era [0, 146096]
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365; // [0, 399]
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100); // [0, 365]
    let mp = (5 * doy + 2) / 153; // [0, 11]
    let d = doy - (153 * mp + 2) / 5 + 1; // [1, 31]
    let m = if mp < 10 { mp + 3 } else { mp - 9 }; // [1, 12]
    let y = if m <= 2 { y + 1 } else { y };

    // Write directly into the fixed-size buffer.
    //
    // Format: YYYY-MM-DD HH:MM:SS  (19 bytes)
    let write2 = |buf: &mut [u8], offset: usize, v: u64| {
        buf[offset] = b'0' + (v / 10) as u8;
        buf[offset + 1] = b'0' + (v % 10) as u8;
    };
    let write4 = |buf: &mut [u8], offset: usize, v: i64| {
        buf[offset] = b'0' + (v / 1000) as u8;
        buf[offset + 1] = b'0' + (v / 100 % 10) as u8;
        buf[offset + 2] = b'0' + (v / 10 % 10) as u8;
        buf[offset + 3] = b'0' + (v % 10) as u8;
    };

    write4(buf, 0, y);
    buf[4] = b'-';
    write2(buf, 5, m as u64);
    buf[7] = b'-';
    write2(buf, 8, d as u64);
    buf[10] = b' ';
    write2(buf, 11, hh);
    buf[13] = b':';
    write2(buf, 14, mm);
    buf[16] = b':';
    write2(buf, 17, ss);
}

fn write_formatted<W: Write>(
    writer: &mut W,
    format: &LogFormat,
    level: &str,
    msg: &str,
) {
    match format {
        LogFormat::Plain => match level {
            "WARN" => {
                let _ = writeln!(writer, "Warning: {}", msg);
            }
            "ERROR" => {
                let _ = writeln!(writer, "Error: {}", msg);
            }
            _ => {
                let _ = writeln!(writer, "{}", msg);
            }
        },
        LogFormat::LevelPrefix => {
            let _ = writeln!(writer, "[{}] {}", level, msg);
        }
        LogFormat::Timestamp => {
            let secs = SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs();
            let mut buf = [0u8; 19];
            format_unix_timestamp(secs, &mut buf);
            let ts = std::str::from_utf8(&buf).unwrap_or("0000-00-00 00:00:00");
            let _ = writeln!(writer, "[{}] [{}] {}", ts, level, msg);
        }
    }
}

// ====================================================================
// Logger trait
// ====================================================================

/// Trait for structured logging with zero-cost when disabled.
pub trait Logger {
    // TODO: Get rid of this general method and force people to either
    // create a new level, or reuse an existing one. We need to have a
    // trade-off between flexibility and performance and simplicity,
    // and I think the `log` method is simply too flexible and adds
    // the cost of a string rather than a well defined enum that we
    // can exhaustively match and ensure all cases are covered.
    fn log(&self, level: &str, msg: &str);

    fn info(&self, msg: &str) {
        self.log("INFO", msg);
    }

    // TODO: Add "progress" method between info and warn.

    fn warn(&self, msg: &str) {
        self.log("WARN", msg);
    }

    fn error(&self, msg: &str) {
        self.log("ERROR", msg);
    }

    fn debug(&self, msg: &str) {
        self.log("DEBUG", msg);
    }
}

// ====================================================================
// DualStreamLogger
// ====================================================================

/// Logger that writes to two outputs simultaneously, with independent
/// level filtering and output formatting per stream.
///
/// Default construction via [`DualStreamLogger::new`] uses:
/// - Stream 1: plain format (`Message here`), all levels allowed.
/// - Stream 2: timestamped format (`YYYY-MM-DD HH:MM:SS [LEVEL] Message here`),
///   all levels allowed.
///
pub struct DualStreamLogger<W1: Write, W2: Write> {
    writer1: W1,
    format1: LogFormat,
    levels1: LevelFilter,
    writer2: W2,
    format2: LogFormat,
    levels2: LevelFilter,
}

impl<W1: Write, W2: Write> DualStreamLogger<W1, W2> {
    /// Create a `DualStreamLogger` with explicit format and level
    /// configuration for each stream.
    pub fn new(
        writer1: W1,
        format1: LogFormat,
        levels1: LevelFilter,
        writer2: W2,
        format2: LogFormat,
        levels2: LevelFilter,
    ) -> Self {
        Self {
            writer1,
            format1,
            levels1,
            writer2,
            format2,
            levels2,
        }
    }

    /// Write a log message directly (used by the channel writer thread).
    pub fn write_log(&mut self, level: &str, msg: &str) {
        if self.levels1.allows(level) {
            write_formatted(&mut self.writer1, &self.format1, level, msg);
        }
        if self.levels2.allows(level) {
            write_formatted(&mut self.writer2, &self.format2, level, msg);
        }
    }
}

// ====================================================================
// NoOpLogger
// ====================================================================

/// No-op logger with zero runtime cost.
#[derive(Clone)]
pub struct NoOpLogger;

impl Logger for NoOpLogger {
    #[inline(always)]
    fn log(&self, _level: &str, _msg: &str) {}
}

// ====================================================================
// ChannelLogger
// ====================================================================

/// A log message sent through the channel.
struct LogMessage {
    level: String,
    msg: String,
}

/// Thread-safe logger that sends messages through an MPSC channel.
///
/// Cloning a `ChannelLogger` clones the sender, allowing multiple
/// threads to log concurrently without blocking.
#[derive(Clone)]
pub struct ChannelLogger {
    sender: mpsc::Sender<LogMessage>,
}

impl Logger for ChannelLogger {
    fn log(&self, level: &str, msg: &str) {
        let _ = self.sender.send(LogMessage {
            level: level.to_owned(),
            msg: msg.to_owned(),
        });
    }
}

/// Handle for the log writer thread.
///
/// Call [`LogHandle::shutdown`] to flush remaining messages and join
/// the writer thread. If dropped without calling `shutdown`, the
/// writer thread will exit once all senders are dropped.
pub struct LogHandle {
    join_handle: Option<thread::JoinHandle<()>>,
}

impl LogHandle {
    /// Wait for the writer thread to finish.
    ///
    /// All `ChannelLogger` clones must be dropped before calling this,
    /// otherwise it will block forever (the writer thread exits only
    /// when the channel closes, which requires all senders to be dropped).
    pub fn shutdown(mut self) {
        if let Some(handle) = self.join_handle.take() {
            let _ = handle.join();
        }
    }
}

impl Drop for LogHandle {
    fn drop(&mut self) {
        if let Some(handle) = self.join_handle.take() {
            let _ = handle.join();
        }
    }
}

/// Create a channel-based logger with a dedicated writer thread.
///
/// Returns a `ChannelLogger` (cloneable, `Send + Sync`) and a
/// `LogHandle` that owns the writer thread.
pub fn channel_logger<W1, W2>(
    writer1: W1,
    format1: LogFormat,
    levels1: LevelFilter,
    writer2: W2,
    format2: LogFormat,
    levels2: LevelFilter,
) -> (ChannelLogger, LogHandle)
where
    W1: Write + Send + 'static,
    W2: Write + Send + 'static,
{
    let (sender, receiver) = mpsc::channel::<LogMessage>();

    let join_handle = thread::spawn(move || {
        let mut backend = DualStreamLogger::new(
            writer1, format1, levels1, writer2, format2, levels2,
        );
        while let Ok(msg) = receiver.recv() {
            backend.write_log(&msg.level, &msg.msg);
        }
    });

    let logger = ChannelLogger { sender };
    let handle = LogHandle {
        join_handle: Some(join_handle),
    };

    (logger, handle)
}

// ====================================================================
// Macros
// ====================================================================

/// Debug print macro that expands to `if DEBUG { eprintln!(...) }`.
///
/// Requires a `const DEBUG: bool` in the calling scope. When `DEBUG`
/// is `false`, the compiler optimizes the branch away entirely.
#[macro_export]
macro_rules! mm_debug_eprintln {
    ($($arg:tt)*) => {
        if DEBUG {
            eprintln!($($arg)*);
        }
    };
}

/// Debug log macro that routes through a logger instead of eprintln.
///
/// Requires a `const DEBUG: bool` in the calling scope and a
/// logger as the first argument. When `DEBUG` is `false`, the compiler
/// optimizes the entire call away.
#[macro_export]
macro_rules! mm_debug_log {
    ($logger:expr, $msg:literal) => {
        if DEBUG {
            $logger.debug($msg);
        }
    };
    ($logger:expr, $fmt:literal, $($arg:tt)*) => {
        if DEBUG {
            $logger.debug(&format!($fmt, $($arg)*));
        }
    };
}

/// Info log macro — avoids the `&format!(...)` boilerplate.
#[macro_export]
macro_rules! mm_info_log {
    ($logger:expr, $msg:literal) => {
        $logger.info($msg);
    };
    ($logger:expr, $fmt:literal, $($arg:tt)*) => {
        $logger.info(&format!($fmt, $($arg)*));
    };
}

/// Warn log macro — avoids the `&format!(...)` boilerplate.
#[macro_export]
macro_rules! mm_warn_log {
    ($logger:expr, $msg:literal) => {
        $logger.warn($msg);
    };
    ($logger:expr, $fmt:literal, $($arg:tt)*) => {
        $logger.warn(&format!($fmt, $($arg)*));
    };
}

/// Error log macro — avoids the `&format!(...)` boilerplate.
#[macro_export]
macro_rules! mm_error_log {
    ($logger:expr, $msg:literal) => {
        $logger.error($msg);
    };
    ($logger:expr, $fmt:literal, $($arg:tt)*) => {
        $logger.error(&format!($fmt, $($arg)*));
    };
}
