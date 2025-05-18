#!/usr/bin/env python
#
# Copyright (C) 2022, 2025 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------
#
"""
This tool is designed to help embed Python modules inside other
Python scripts, so they can be flattened into a single Python file for
easy distribution.

Example usage:

$ cd <project root>
$ python share/3dequalizer/python/generate_code.py -i share/3dequalizer/python/import_tracks_mmsolver.py -o share/3dequalizer/scriptdb/import_tracks_mmsolver.py

$ python share/3dequalizer/python/generate_code.py -i share/3dequalizer/python/copy_track_mmsolver.py -o share/3dequalizer/scriptdb/copy_track_mmsolver.py

$ python share/3dequalizer/python/generate_code.py -i share/3dequalizer/python/export_track_mmsolver.py -o share/3dequalizer/scriptdb/export_track_mmsolver.py

The generated output code will still need to be manually edited before
the file can be run properly. This includes:
- Removing unneeded Python imports.
- Removing unneeded variables/functions.
- Remove/rename conflicting function names.
- etc...
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os


WRITE_FLAG = '--write'
NEW_LINE = '\n'
TRIPLE_DOUBLE_QUOTES = '"""'
TRIPLE_SINGLE_QUOTES = "'''"
TOKEN_FILTER_LINE = '# GENERATE_FILTER_LINE'
TOKEN_INCLUDE_FILE = '# INCLUDE_FILE'
TOKEN_BEGIN_FILE = '# BEGIN_FILE'
TOKEN_END_FILE = '# END_FILE'


def _find_injection_sub_file_path_tokens_in_text(text_contents):
    sub_file_path_tokens = []
    parse_index = 0
    while True:
        include_index = text_contents.find(TOKEN_INCLUDE_FILE, parse_index)
        if include_index == -1:
            break
        parse_index = include_index + 1

        # The line may not end with a new line character at all.
        new_line_index = text_contents.find(NEW_LINE, include_index)
        if new_line_index == -1:
            sub_file_path_token = text_contents[include_index:]
        else:
            sub_file_path_token = text_contents[include_index:new_line_index]
            parse_index = new_line_index + 1

        sub_file_path_tokens.append(sub_file_path_token.strip())
    return sub_file_path_tokens


def _inject_text_into_text(base_text_contents, file_path_token, sub_text_contents):
    token_index = base_text_contents.find(file_path_token)
    if token_index == -1:
        print('Injecting text failed. Could not find token: %r' % file_path_token)
        return base_text_contents
    new_text_contents = str(base_text_contents)

    new_line_index = base_text_contents.find(NEW_LINE, token_index)
    if new_line_index == -1:
        new_text_contents.replace(file_path_token, file_path_token + NEW_LINE)
        new_line_index = token_index + len(file_path_token) + 1

    file_begin_index = base_text_contents.find(TOKEN_BEGIN_FILE, new_line_index)
    file_end_index = base_text_contents.find(TOKEN_END_FILE, new_line_index)
    if file_begin_index != -1 and file_end_index != -1:
        begin_str = new_text_contents[:file_begin_index] + TOKEN_BEGIN_FILE + NEW_LINE
        end_str = new_text_contents[file_end_index:]
    elif file_begin_index == -1 and file_end_index == -1:
        begin_str = (
            new_text_contents[:new_line_index] + NEW_LINE + TOKEN_BEGIN_FILE + NEW_LINE
        )
        end_str = NEW_LINE + TOKEN_END_FILE + new_text_contents[new_line_index:]
    else:
        print(
            'Injecting text failed: begin and end tokens not found: %r'
            % file_path_token
        )
        return base_text_contents

    new_text_contents = begin_str + sub_text_contents + end_str
    return new_text_contents


def _resolve_file_path(base_directory, file_path_token):
    file_path = file_path_token.strip(TOKEN_INCLUDE_FILE).strip()
    full_path = os.path.join(base_directory, file_path)
    if not os.path.isfile(full_path):
        return None
    return full_path


def _read_text_file(file_path):
    text_contents = None
    with open(file_path, 'r') as f:
        text_contents = f.read()
    return text_contents


def _pre_remove_filtered_lines_from_python_script(text_contents):
    new_lines = []
    lines = text_contents.split(NEW_LINE)
    for line in lines:
        if line.strip().endswith(TOKEN_FILTER_LINE):
            continue
        if '3DE4.script.hide' in line:
            continue
        new_lines.append(line)
    new_text_contents = NEW_LINE.join(new_lines)

    return new_text_contents


def _post_remove_filtered_lines_from_python_script(text_contents):
    new_lines = []
    lines = text_contents.split(NEW_LINE)
    for line in lines:
        if line.strip().startswith(TOKEN_INCLUDE_FILE):
            continue
        if line.strip().startswith(TOKEN_BEGIN_FILE):
            continue
        if line.strip().startswith(TOKEN_END_FILE):
            continue
        new_lines.append(line)
    new_text_contents = NEW_LINE.join(new_lines)

    return new_text_contents


def _remove_import_use_lines_from_python_script(text_contents, python_module_name):
    python_module_use = python_module_name + '.'

    new_lines = []
    lines = text_contents.split(NEW_LINE)
    for line in lines:
        new_line = line.replace(python_module_use, '')
        new_lines.append(new_line)
    new_text_contents = NEW_LINE.join(new_lines)

    return new_text_contents


def _remove_comments_from_python_script(
    text_contents, file_begin_index=None, file_end_index=None
):
    # Remove line comments.
    new_lines = []
    lines = text_contents.split(NEW_LINE)
    for line in lines:
        new_line = _remove_comment_from_python_line(line)
        new_lines.append(new_line)
    new_text_contents = NEW_LINE.join(new_lines)

    triple_single_quote_count = new_text_contents.count(
        TRIPLE_SINGLE_QUOTES, file_begin_index, file_end_index
    )
    triple_double_quote_count = new_text_contents.count(
        TRIPLE_DOUBLE_QUOTES, file_begin_index, file_end_index
    )
    assert triple_single_quote_count % 2 == 0
    assert triple_double_quote_count % 2 == 0

    quotes = []
    if triple_single_quote_count > 0:
        quotes.append((triple_single_quote_count, TRIPLE_SINGLE_QUOTES))
    if triple_double_quote_count > 0:
        quotes.append((triple_double_quote_count, TRIPLE_DOUBLE_QUOTES))

    # Replace all quote-commented code.
    for count, quote in quotes:
        last_index = 0
        if file_begin_index is not None:
            last_index = file_begin_index
        for i in range(count // 2):
            begin_index = new_text_contents.find(quote, last_index)
            if begin_index == -1:
                break

            end_index = new_text_contents.find(quote, begin_index)
            if end_index == -1:
                break
            end_index += len(quote)

            if file_end_index is not None:
                if (begin_index > file_end_index) or (end_index > file_end_index):
                    break

            begin_str = new_text_contents[begin_index:]
            end_str = new_text_contents[:end_index]
            new_text_contents = begin_str + end_str

            last_index = end_index

    # print("Commented code:")
    # print(new_text_contents)

    return new_text_contents


def _remove_comment_from_python_line(line_text):
    return line_text.partition('#')[0]


def _find_python_imports(text_contents):
    import_lines = set()

    edited_text_contents = _remove_comments_from_python_script(text_contents)

    lines = edited_text_contents.split(NEW_LINE)
    for line in lines:
        if 'import ' not in line:
            continue
        import_lines.add(line)

    return import_lines


def _startswith_triple_quotes(text):
    a = text.startswith(TRIPLE_DOUBLE_QUOTES)
    b = text.startswith(TRIPLE_SINGLE_QUOTES)
    return a or b


def _filter_python_script(existing_import_lines, text_contents):
    new_lines = []

    text_contents = _pre_remove_filtered_lines_from_python_script(text_contents)

    # Filter all import lines that are already existing in the parent
    # file.
    lines = text_contents.split(NEW_LINE)
    for line in lines:
        edited_line = _remove_comment_from_python_line(line)
        if edited_line in existing_import_lines:
            continue
        new_lines.append(line)

    # Remove the copyright and license information from the text
    # contents as it's being copied.
    #
    # We assume that the license block is first, followed by the
    # module doc-string, as is convention in MM Solver.
    license_block_begin_line = None
    license_block_end_line = None
    docs_block_begin_line = None
    docs_block_end_line = None
    for i, line in enumerate(new_lines):
        # print('line %r: %r' %(i, line))
        if line.startswith('#'):
            if license_block_begin_line is None:
                license_block_begin_line = i
            license_block_end_line = i
        elif _startswith_triple_quotes(line):
            if docs_block_begin_line is None:
                docs_block_begin_line = i
            elif docs_block_end_line is None:
                docs_block_end_line = i
                break

    # print('license block: %r-%r' % (license_block_begin_line, license_block_end_line))
    # print('docs block: %r-%r' % (docs_block_begin_line, docs_block_end_line))

    begin_lines = new_lines[:license_block_begin_line]
    end_lines = new_lines[license_block_end_line + 1 :]
    new_lines = begin_lines + end_lines

    license_block_line_count = license_block_end_line - license_block_begin_line
    docs_block_begin_line = docs_block_begin_line - license_block_line_count - 1
    docs_block_end_line = docs_block_end_line - license_block_line_count - 1

    begin_lines = new_lines[:docs_block_begin_line]
    end_lines = new_lines[docs_block_end_line + 1 :]
    new_lines = begin_lines + end_lines

    new_text_contents = NEW_LINE.join(new_lines)
    return new_text_contents


def main(input_file_path, output_file_path):
    print('File Path: %r' % input_file_path)
    base_directory = os.path.dirname(input_file_path)
    print('Dir Path: %r' % base_directory)

    assert input_file_path.endswith('.py')
    base_text_contents = _read_text_file(input_file_path)
    base_text_contents = _pre_remove_filtered_lines_from_python_script(
        base_text_contents
    )
    existing_import_lines = _find_python_imports(base_text_contents)

    file_path_tokens = _find_injection_sub_file_path_tokens_in_text(base_text_contents)
    for file_path_token in file_path_tokens:
        print('Include File Path: %r' % file_path_token)
        sub_file_path = _resolve_file_path(base_directory, file_path_token)
        assert sub_file_path.endswith(
            '.py'
        ), 'Only Python scripts are currently supported.'

        sub_text_contents = _read_text_file(sub_file_path)
        sub_text_contents = _filter_python_script(
            existing_import_lines, sub_text_contents
        )
        base_text_contents = _inject_text_into_text(
            base_text_contents, file_path_token, sub_text_contents
        )

        module_file_name = os.path.basename(sub_file_path)
        module_name, _ = os.path.splitext(module_file_name)
        base_text_contents = _remove_import_use_lines_from_python_script(
            base_text_contents, module_name
        )

    base_text_contents = _post_remove_filtered_lines_from_python_script(
        base_text_contents
    )

    if output_file_path is not None:
        with open(output_file_path, 'w') as f:
            f.write(base_text_contents)

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '-i', '--input', dest='in_file', nargs=1, help='The file parsed as input.'
    )
    parser.add_argument(
        '-o',
        '--output',
        dest='out_file',
        type=str,
        nargs='?',
        help='file to write generated code to.',
    )
    args = parser.parse_args()
    input_file = args.in_file[0]
    output_file = args.out_file
    main(input_file, output_file)
