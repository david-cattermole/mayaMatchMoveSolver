//
// Copyright (C) 2025, 2026 David Cattermole.
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

//! JSON serializer for `JsonValue`.

use super::json_common::JsonValue;

/// Serialize a `JsonValue` to a JSON string.
pub fn write_json(value: &JsonValue) -> String {
    let mut out = String::new();
    write_value(&mut out, value);
    out
}

fn write_value(out: &mut String, value: &JsonValue) {
    match value {
        JsonValue::Null => out.push_str("null"),
        JsonValue::Bool(true) => out.push_str("true"),
        JsonValue::Bool(false) => out.push_str("false"),
        JsonValue::Integer(n) => {
            out.push_str(&n.to_string());
        }
        JsonValue::Number(n) => {
            // Use full precision repr to ensure round-trip fidelity.
            let s = format!("{}", n);
            out.push_str(&s);
            // Ensure it looks like a float if it has no decimal point.
            if !s.contains('.') && !s.contains('e') && !s.contains('E') {
                out.push_str(".0");
            }
        }
        JsonValue::String(s) => {
            write_string(out, s);
        }
        JsonValue::Array(items) => {
            out.push('[');
            for (i, item) in items.iter().enumerate() {
                if i > 0 {
                    out.push_str(", ");
                }
                write_value(out, item);
            }
            out.push(']');
        }
        JsonValue::Object(map) => {
            out.push('{');
            for (i, (key, val)) in map.iter().enumerate() {
                if i > 0 {
                    out.push_str(", ");
                }
                write_string(out, key);
                out.push_str(": ");
                write_value(out, val);
            }
            out.push('}');
        }
    }
}

fn write_string(out: &mut String, s: &str) {
    out.push('"');
    for ch in s.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{08}' => out.push_str("\\b"),
            '\u{0C}' => out.push_str("\\f"),
            c if c.is_control() => {
                out.push_str(&format!("\\u{:04x}", c as u32));
            }
            c => out.push(c),
        }
    }
    out.push('"');
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::json_parser::parse_json;

    #[test]
    fn test_write_null() {
        assert_eq!(write_json(&JsonValue::Null), "null");
    }

    #[test]
    fn test_write_bool() {
        assert_eq!(write_json(&JsonValue::Bool(true)), "true");
        assert_eq!(write_json(&JsonValue::Bool(false)), "false");
    }

    #[test]
    fn test_write_integer() {
        assert_eq!(write_json(&JsonValue::Integer(42)), "42");
        assert_eq!(write_json(&JsonValue::Integer(-7)), "-7");
    }

    #[test]
    fn test_write_number() {
        assert_eq!(write_json(&JsonValue::Number(3.14)), "3.14");
    }

    #[test]
    fn test_write_string_escaping() {
        let val = JsonValue::String("he\"llo\nworld".to_string());
        assert_eq!(write_json(&val), r#""he\"llo\nworld""#);
    }

    #[test]
    fn test_roundtrip_object() {
        let input = r#"{"a": 1, "b": "two", "c": [true, null, 3.14]}"#;
        let parsed = parse_json(input).unwrap();
        let written = write_json(&parsed);
        let reparsed = parse_json(&written).unwrap();
        assert_eq!(parsed, reparsed);
    }

    #[test]
    fn test_roundtrip_nested() {
        let input = r#"{"arr": [1, {"x": true}], "n": null}"#;
        let parsed = parse_json(input).unwrap();
        let written = write_json(&parsed);
        let reparsed = parse_json(&written).unwrap();
        assert_eq!(parsed, reparsed);
    }
}
