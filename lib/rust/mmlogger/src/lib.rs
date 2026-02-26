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

/// Log severity level, ordered from least to most severe.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum LogLevel {
    Debug = 0,
    Info = 1,
    Progress = 2,
    Warn = 3,
    Error = 4,
}

impl LogLevel {
    fn as_str(self) -> &'static str {
        match self {
            LogLevel::Debug => "DEBUG",
            LogLevel::Info => "INFO",
            LogLevel::Progress => "PROGRESS",
            LogLevel::Warn => "WARN",
            LogLevel::Error => "ERROR",
        }
    }
}

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
    pub const NONE: LevelFilter = LevelFilter(0b00000);
    pub const DEBUG: LevelFilter = LevelFilter(0b00001);
    pub const INFO: LevelFilter = LevelFilter(0b00010);
    pub const PROGRESS: LevelFilter = LevelFilter(0b00100);
    pub const WARN: LevelFilter = LevelFilter(0b01000);
    pub const ERROR: LevelFilter = LevelFilter(0b10000);
    pub const ALL: LevelFilter = LevelFilter(0b11111);

    pub fn allows(self, level: LogLevel) -> bool {
        let bit: u8 = match level {
            LogLevel::Debug => 0b00001,
            LogLevel::Info => 0b00010,
            LogLevel::Progress => 0b00100,
            LogLevel::Warn => 0b01000,
            LogLevel::Error => 0b10000,
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
    /// Full debug format:
    /// `YYYY-MM-DD HH:MM:SS [LEVEL] [#thread_id] [file_path:line_number] Message here`
    Full,
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

/// Optional source location and timing metadata for a log message.
pub struct LogMetadata {
    /// Unix timestamp in seconds (captured at log call site).
    pub timestamp_secs: u64,
    /// OS thread ID of the calling thread.
    pub thread_id: u64,
    /// Source file name (from `file!()`).
    pub file_path: &'static str,
    /// Source line number (from `line!()`).
    pub line_number: u32,
}

impl LogMetadata {
    /// Capture metadata at the current call site. Thread ID and
    /// timestamp are recorded immediately.
    ///
    /// `file_path` and `line_number` must be provided by the caller (via
    /// `file!()` / `line!()` macros).
    pub fn capture(file_path: &'static str, line_number: u32) -> Self {
        let timestamp_secs = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        let thread_id = thread_id_u64();
        Self {
            timestamp_secs,
            thread_id,
            file_path,
            line_number,
        }
    }
}

use mmcore::threadutils::thread_id_u64;

fn write_formatted<W: Write>(
    writer: &mut W,
    format: &LogFormat,
    level: LogLevel,
    msg: &str,
    meta: Option<&LogMetadata>,
) {
    match format {
        LogFormat::Plain => match level {
            LogLevel::Warn => {
                let _ = writeln!(writer, "Warning: {}", msg);
            }
            LogLevel::Error => {
                let _ = writeln!(writer, "Error: {}", msg);
            }
            _ => {
                // Debug, Info, and Progress use plain text with no prefix.
                let _ = writeln!(writer, "{}", msg);
            }
        },
        LogFormat::LevelPrefix => {
            let _ = writeln!(writer, "[{}] {}", level.as_str(), msg);
        }
        LogFormat::Timestamp => {
            let secs = match meta {
                Some(m) => m.timestamp_secs,
                None => SystemTime::now()
                    .duration_since(SystemTime::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs(),
            };
            let mut buf = [0u8; 19];
            format_unix_timestamp(secs, &mut buf);
            let ts = std::str::from_utf8(&buf).unwrap_or("0000-00-00 00:00:00");
            let _ = writeln!(writer, "[{}] [{}] {}", ts, level.as_str(), msg);
        }
        LogFormat::Full => {
            let secs = match meta {
                Some(m) => m.timestamp_secs,
                None => SystemTime::now()
                    .duration_since(SystemTime::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs(),
            };
            let mut buf = [0u8; 19];
            format_unix_timestamp(secs, &mut buf);
            let ts = std::str::from_utf8(&buf).unwrap_or("0000-00-00 00:00:00");
            match meta {
                Some(m) => {
                    let _ = writeln!(
                        writer,
                        "[{}] [{}] [#{}] [{}:{}] {}",
                        ts,
                        level.as_str(),
                        m.thread_id,
                        m.file_path,
                        m.line_number,
                        msg
                    );
                }
                None => {
                    let _ = writeln!(
                        writer,
                        "[{}] [{}] {}",
                        ts,
                        level.as_str(),
                        msg
                    );
                }
            }
        }
    }
}

// ====================================================================
// Logger trait
// ====================================================================

/// Trait for structured logging with zero-cost when disabled.
pub trait Logger {
    fn log(&self, level: LogLevel, msg: &str, file: &'static str, line: u32);
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
    pub fn write_log(
        &mut self,
        level: LogLevel,
        msg: &str,
        meta: Option<&LogMetadata>,
    ) {
        if self.levels1.allows(level) {
            write_formatted(&mut self.writer1, &self.format1, level, msg, meta);
        }
        if self.levels2.allows(level) {
            write_formatted(&mut self.writer2, &self.format2, level, msg, meta);
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
    fn log(
        &self,
        _level: LogLevel,
        _msg: &str,
        _file: &'static str,
        _line: u32,
    ) {
    }
}

// ====================================================================
// ChannelLogger
// ====================================================================

/// A log message sent through the channel.
struct LogMessage {
    level: LogLevel,
    msg: String,
    timestamp_secs: u64,
    thread_id: u64,
    file_path: &'static str,
    line_number: u32,
}

/// Thread-safe logger that sends messages through an MPSC channel.
///
/// Cloning a `ChannelLogger` clones the sender, allowing multiple
/// threads to log concurrently without blocking.
#[derive(Clone)]
pub struct ChannelLogger {
    sender: mpsc::Sender<LogMessage>,
}

impl ChannelLogger {
    /// Send a log message with full source location metadata.
    ///
    /// Prefer using the `mm_*_log!` macros which call this
    /// automatically with correct `file!()` and `line!()` values.
    fn send_log(
        &self,
        level: LogLevel,
        msg: &str,
        file_path: &'static str,
        line_number: u32,
    ) {
        let timestamp_secs = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        let thread_id = thread_id_u64();
        let _ = self.sender.send(LogMessage {
            level,
            msg: msg.to_owned(),
            timestamp_secs,
            thread_id,
            file_path,
            line_number,
        });
    }
}

impl Logger for ChannelLogger {
    fn log(
        &self,
        level: LogLevel,
        msg: &str,
        file_path: &'static str,
        line_number: u32,
    ) {
        self.send_log(level, msg, file_path, line_number);
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
            let meta = LogMetadata {
                timestamp_secs: msg.timestamp_secs,
                thread_id: msg.thread_id,
                file_path: msg.file_path,
                line_number: msg.line_number,
            };
            backend.write_log(msg.level, &msg.msg, Some(&meta));
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
///
/// If the logger has a `log` method (e.g.
/// `ChannelLogger`), source file and line are captured automatically.
#[macro_export]
macro_rules! mm_debug_log {
    ($logger:expr, $msg:literal) => {
        if DEBUG {
            $logger.log(
                $crate::LogLevel::Debug, $msg, file!(), line!());
        }
    };
    ($logger:expr, $fmt:literal, $($arg:tt)*) => {
        if DEBUG {
            $logger.log(
                $crate::LogLevel::Debug,
                &format!($fmt, $($arg)*),
                file!(), line!());
        }
    };
}

/// Info log macro — captures source location for `Full` format.
#[macro_export]
macro_rules! mm_info_log {
    ($logger:expr, $msg:literal) => {
        $logger.log(
            $crate::LogLevel::Info, $msg, file!(), line!());
    };
    ($logger:expr, $fmt:literal, $($arg:tt)*) => {
        $logger.log(
            $crate::LogLevel::Info,
            &format!($fmt, $($arg)*),
            file!(), line!());
    };
}

/// Progress log macro — captures source location for `Full` format.
#[macro_export]
macro_rules! mm_progress_log {
    ($logger:expr, $msg:literal) => {
        $logger.log(
            $crate::LogLevel::Progress, $msg, file!(), line!());
    };
    ($logger:expr, $fmt:literal, $($arg:tt)*) => {
        $logger.log(
            $crate::LogLevel::Progress,
            &format!($fmt, $($arg)*),
            file!(), line!());
    };
}

/// Warn log macro — captures source location for `Full` format.
#[macro_export]
macro_rules! mm_warn_log {
    ($logger:expr, $msg:literal) => {
        $logger.log(
            $crate::LogLevel::Warn, $msg, file!(), line!());
    };
    ($logger:expr, $fmt:literal, $($arg:tt)*) => {
        $logger.log(
            $crate::LogLevel::Warn,
            &format!($fmt, $($arg)*),
            file!(), line!());
    };
}

/// Error log macro — captures source location for `Full` format.
#[macro_export]
macro_rules! mm_error_log {
    ($logger:expr, $msg:literal) => {
        $logger.log(
            $crate::LogLevel::Error, $msg, file!(), line!());
    };
    ($logger:expr, $fmt:literal, $($arg:tt)*) => {
        $logger.log(
            $crate::LogLevel::Error,
            &format!($fmt, $($arg)*),
            file!(), line!());
    };
}
