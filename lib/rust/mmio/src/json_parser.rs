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

//! Minimal recursive-descent JSON parser.
//!
//! Produces a `JsonValue` enum tree. No external dependencies needed.

use std::collections::BTreeMap;

pub use super::json_common::*;

/// Strip C-style line comments (`// ...`) from a string.
///
/// This is a simple pre-processor that removes `//` comments that
/// appear outside of JSON string literals, allowing JSON-with-comments
/// files (like `.mmsettings`) to be parsed by the standard JSON parser.
pub fn strip_json_comments(input: &str) -> String {
    let mut result = String::with_capacity(input.len());
    let mut in_string = false;
    let mut chars = input.chars().peekable();

    while let Some(ch) = chars.next() {
        if in_string {
            result.push(ch);
            if ch == '\\' {
                // Push the escaped character too.
                if let Some(escaped) = chars.next() {
                    result.push(escaped);
                }
            } else if ch == '"' {
                in_string = false;
            }
        } else if ch == '"' {
            in_string = true;
            result.push(ch);
        } else if ch == '/' {
            if chars.peek() == Some(&'/') {
                // Consume rest of line.
                for c in chars.by_ref() {
                    if c == '\n' {
                        result.push('\n');
                        break;
                    }
                }
            } else {
                result.push(ch);
            }
        } else {
            result.push(ch);
        }
    }

    result
}

/// Parse a JSON string (with optional `//` comments) into a `JsonValue`.
pub fn parse_json_with_comments(
    input: &str,
) -> Result<JsonValue, JsonParseError> {
    let stripped = strip_json_comments(input);
    parse_json(&stripped)
}

/// Parse a JSON string into a `JsonValue`.
pub fn parse_json(input: &str) -> Result<JsonValue, JsonParseError> {
    let mut parser = Parser::new(input);
    let value = parser.parse_value()?;
    parser.skip_whitespace();
    if parser.pos < parser.input.len() {
        return Err(parser.error("unexpected trailing content"));
    }
    Ok(value)
}

struct Parser<'a> {
    input: &'a [u8],
    pos: usize,
}

impl<'a> Parser<'a> {
    fn new(input: &'a str) -> Self {
        Parser {
            input: input.as_bytes(),
            pos: 0,
        }
    }

    fn error(&self, message: &str) -> JsonParseError {
        JsonParseError {
            message: message.to_string(),
            position: self.pos,
        }
    }

    fn peek(&self) -> Option<u8> {
        self.input.get(self.pos).copied()
    }

    fn advance(&mut self) -> Option<u8> {
        let ch = self.input.get(self.pos).copied();
        if ch.is_some() {
            self.pos += 1;
        }
        ch
    }

    fn expect(&mut self, ch: u8) -> Result<(), JsonParseError> {
        match self.advance() {
            Some(c) if c == ch => Ok(()),
            Some(c) => Err(self.error(&format!(
                "expected '{}', found '{}'",
                ch as char, c as char
            ))),
            None => {
                Err(self
                    .error(&format!("expected '{}', found EOF", ch as char)))
            }
        }
    }

    fn skip_whitespace(&mut self) {
        while self.pos < self.input.len() {
            match self.input[self.pos] {
                b' ' | b'\t' | b'\n' | b'\r' => self.pos += 1,
                _ => break,
            }
        }
    }

    fn parse_value(&mut self) -> Result<JsonValue, JsonParseError> {
        self.skip_whitespace();
        match self.peek() {
            Some(b'"') => self.parse_string().map(JsonValue::String),
            Some(b'{') => self.parse_object(),
            Some(b'[') => self.parse_array(),
            Some(b't') => self.parse_literal("true", JsonValue::Bool(true)),
            Some(b'f') => self.parse_literal("false", JsonValue::Bool(false)),
            Some(b'n') => self.parse_literal("null", JsonValue::Null),
            Some(c) if c == b'-' || c.is_ascii_digit() => self.parse_number(),
            Some(c) => {
                Err(self
                    .error(&format!("unexpected character '{}'", c as char)))
            }
            None => Err(self.error("unexpected EOF")),
        }
    }

    fn parse_literal(
        &mut self,
        expected: &str,
        value: JsonValue,
    ) -> Result<JsonValue, JsonParseError> {
        for byte in expected.bytes() {
            match self.advance() {
                Some(c) if c == byte => {}
                _ => {
                    return Err(self.error(&format!("expected '{}'", expected)))
                }
            }
        }
        Ok(value)
    }

    fn parse_string(&mut self) -> Result<String, JsonParseError> {
        self.expect(b'"')?;
        let mut result = String::new();
        loop {
            match self.advance() {
                Some(b'"') => return Ok(result),
                Some(b'\\') => match self.advance() {
                    Some(b'"') => result.push('"'),
                    Some(b'\\') => result.push('\\'),
                    Some(b'/') => result.push('/'),
                    Some(b'b') => result.push('\u{08}'),
                    Some(b'f') => result.push('\u{0C}'),
                    Some(b'n') => result.push('\n'),
                    Some(b'r') => result.push('\r'),
                    Some(b't') => result.push('\t'),
                    Some(b'u') => {
                        let hex = self.parse_hex4()?;
                        if let Some(ch) = char::from_u32(hex as u32) {
                            result.push(ch);
                        } else {
                            result.push('\u{FFFD}');
                        }
                    }
                    _ => return Err(self.error("invalid escape sequence")),
                },
                Some(c) => result.push(c as char),
                None => return Err(self.error("unterminated string")),
            }
        }
    }

    fn parse_hex4(&mut self) -> Result<u16, JsonParseError> {
        let mut val: u16 = 0;
        for _ in 0..4 {
            let c = self
                .advance()
                .ok_or_else(|| self.error("unexpected EOF in hex escape"))?;
            let digit = match c {
                b'0'..=b'9' => c - b'0',
                b'a'..=b'f' => c - b'a' + 10,
                b'A'..=b'F' => c - b'A' + 10,
                _ => return Err(self.error("invalid hex digit")),
            };
            val = (val << 4) | digit as u16;
        }
        Ok(val)
    }

    fn parse_number(&mut self) -> Result<JsonValue, JsonParseError> {
        let start = self.pos;
        let mut is_float = false;

        // Optional minus
        if self.peek() == Some(b'-') {
            self.pos += 1;
        }

        // Integer part
        match self.peek() {
            Some(b'0') => {
                self.pos += 1;
            }
            Some(c) if c.is_ascii_digit() => {
                while self.pos < self.input.len()
                    && self.input[self.pos].is_ascii_digit()
                {
                    self.pos += 1;
                }
            }
            _ => return Err(self.error("expected digit")),
        }

        // Fractional part
        if self.peek() == Some(b'.') {
            is_float = true;
            self.pos += 1;
            if !self.peek().map_or(false, |c| c.is_ascii_digit()) {
                return Err(self.error("expected digit after decimal point"));
            }
            while self.pos < self.input.len()
                && self.input[self.pos].is_ascii_digit()
            {
                self.pos += 1;
            }
        }

        // Exponent part
        if self.peek() == Some(b'e') || self.peek() == Some(b'E') {
            is_float = true;
            self.pos += 1;
            if self.peek() == Some(b'+') || self.peek() == Some(b'-') {
                self.pos += 1;
            }
            if !self.peek().map_or(false, |c| c.is_ascii_digit()) {
                return Err(self.error("expected digit in exponent"));
            }
            while self.pos < self.input.len()
                && self.input[self.pos].is_ascii_digit()
            {
                self.pos += 1;
            }
        }

        let s = std::str::from_utf8(&self.input[start..self.pos])
            .map_err(|_| self.error("invalid UTF-8 in number"))?;

        if is_float {
            let n: f64 = s.parse().map_err(|_| self.error("invalid number"))?;
            Ok(JsonValue::Number(n))
        } else {
            // Try integer first, fall back to float for very large numbers
            if let Ok(n) = s.parse::<i64>() {
                Ok(JsonValue::Integer(n))
            } else {
                let n: f64 =
                    s.parse().map_err(|_| self.error("invalid number"))?;
                Ok(JsonValue::Number(n))
            }
        }
    }

    fn parse_array(&mut self) -> Result<JsonValue, JsonParseError> {
        self.expect(b'[')?;
        self.skip_whitespace();

        let mut items = Vec::new();
        if self.peek() == Some(b']') {
            self.pos += 1;
            return Ok(JsonValue::Array(items));
        }

        loop {
            items.push(self.parse_value()?);
            self.skip_whitespace();
            match self.peek() {
                Some(b',') => {
                    self.pos += 1;
                }
                Some(b']') => {
                    self.pos += 1;
                    return Ok(JsonValue::Array(items));
                }
                _ => return Err(self.error("expected ',' or ']'")),
            }
        }
    }

    fn parse_object(&mut self) -> Result<JsonValue, JsonParseError> {
        self.expect(b'{')?;
        self.skip_whitespace();

        let mut map = BTreeMap::new();
        if self.peek() == Some(b'}') {
            self.pos += 1;
            return Ok(JsonValue::Object(map));
        }

        loop {
            self.skip_whitespace();
            let key = self.parse_string()?;
            self.skip_whitespace();
            self.expect(b':')?;
            let value = self.parse_value()?;
            map.insert(key, value);
            self.skip_whitespace();
            match self.peek() {
                Some(b',') => {
                    self.pos += 1;
                }
                Some(b'}') => {
                    self.pos += 1;
                    return Ok(JsonValue::Object(map));
                }
                _ => return Err(self.error("expected ',' or '}'")),
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_null() {
        assert_eq!(parse_json("null").unwrap(), JsonValue::Null);
    }

    #[test]
    fn test_bools() {
        assert_eq!(parse_json("true").unwrap(), JsonValue::Bool(true));
        assert_eq!(parse_json("false").unwrap(), JsonValue::Bool(false));
    }

    #[test]
    fn test_integers() {
        assert_eq!(parse_json("42").unwrap(), JsonValue::Integer(42));
        assert_eq!(parse_json("-7").unwrap(), JsonValue::Integer(-7));
        assert_eq!(parse_json("0").unwrap(), JsonValue::Integer(0));
    }

    #[test]
    fn test_floats() {
        assert_eq!(parse_json("3.14").unwrap(), JsonValue::Number(3.14));
        assert_eq!(parse_json("-0.5").unwrap(), JsonValue::Number(-0.5));
        assert_eq!(parse_json("1e10").unwrap(), JsonValue::Number(1e10));
        assert_eq!(parse_json("2.5E-3").unwrap(), JsonValue::Number(2.5e-3));
    }

    #[test]
    fn test_strings() {
        assert_eq!(
            parse_json(r#""hello""#).unwrap(),
            JsonValue::String("hello".to_string())
        );
        assert_eq!(
            parse_json(r#""he\"llo""#).unwrap(),
            JsonValue::String("he\"llo".to_string())
        );
        assert_eq!(
            parse_json(r#""tab\there""#).unwrap(),
            JsonValue::String("tab\there".to_string())
        );
    }

    #[test]
    fn test_array() {
        let v = parse_json("[1, 2, 3]").unwrap();
        let arr = v.as_array().unwrap();
        assert_eq!(arr.len(), 3);
        assert_eq!(arr[0].as_i64(), Some(1));
        assert_eq!(arr[2].as_i64(), Some(3));
    }

    #[test]
    fn test_empty_array() {
        let v = parse_json("[]").unwrap();
        assert_eq!(v.as_array().unwrap().len(), 0);
    }

    #[test]
    fn test_object() {
        let v = parse_json(r#"{"a": 1, "b": "two"}"#).unwrap();
        assert_eq!(v.get("a").unwrap().as_i64(), Some(1));
        assert_eq!(v.get("b").unwrap().as_str(), Some("two"));
    }

    #[test]
    fn test_nested() {
        let v = parse_json(r#"{"arr": [1, {"x": true}], "n": null}"#).unwrap();
        let arr = v.get("arr").unwrap().as_array().unwrap();
        assert_eq!(arr[0].as_i64(), Some(1));
        assert_eq!(arr[1].get("x").unwrap().as_bool(), Some(true));
        assert!(v.get("n").unwrap().is_null());
    }

    #[test]
    fn test_whitespace() {
        let v = parse_json("  {  \"a\" : [ 1 , 2 ]  }  ").unwrap();
        assert_eq!(v.get("a").unwrap().as_array().unwrap().len(), 2);
    }

    #[test]
    fn test_error_trailing() {
        assert!(parse_json("42 extra").is_err());
    }

    #[test]
    fn test_error_unterminated_string() {
        assert!(parse_json(r#""hello"#).is_err());
    }
}
