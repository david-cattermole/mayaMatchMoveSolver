#!/usr/bin/env python
#
# Copyright (C) 2025 David Cattermole.
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
#
"""
Converts a Python pstat file (from cProfile) into a human readable text file.

Usage:
> python convertPythonProfileToHumanReadable.py <pstat_file> --sort cumulative --limit 30 --output <output_file> --callers --callees

NOTE: It is important that the same Python interpreter version is used
to read the cProfile files - Python 2.7 and 3.x use a different
format, and this tool is intended to work with both formats, but it
must be run under the same Python interpreter.
"""

from __future__ import print_function  # For Python 2.7 compatibility

import pstats
import argparse
import sys


def process_pstat(
    path,
    sort_key='cumulative',
    limit=None,
    output_file=None,
    strip_paths=True,
    show_callers=False,
    show_callees=False,
):
    """
    Process a pstat file and print the statistics.

    Args:
        path (str): Path to the pstat file
        sort_key (str): Key to sort the statistics by
        limit (int): Number of functions to show (None for all)
        output_file (str): Path to save the output (None for stdout)
        strip_paths (bool): Whether to strip full file paths in the output
        show_callers (bool): Whether to show the callers of each function
        show_callees (bool): Whether to show the functions called by each function
    """
    try:
        # Load the stats from the file
        main_stats = pstats.Stats(path)

        # Now strip directories
        if strip_paths:
            main_stats.strip_dirs()

        # Sort the stats
        main_stats = main_stats.sort_stats(sort_key)

        # Set output stream
        original_stream = main_stats.stream
        if output_file:
            main_stats.stream = open(output_file, 'w')

        # Print header with file info
        if output_file:
            main_stats.stream.write("Profile data from: {}\n".format(path))
            main_stats.stream.write("Sorted by: {}\n\n\n".format(sort_key))

        # Print the main stats
        main_stats.stream.write("#" * 80)
        main_stats.stream.write("\nMain:\n\n")
        main_stats.print_stats(limit)

        # Print the stats with callers/callees if requested
        if show_callers:
            main_stats.stream.write("#" * 80)
            main_stats.stream.write("\nCallers:\n\n")
            main_stats = main_stats.sort_stats(sort_key)
            main_stats.print_callers(limit)
            main_stats.stream.write("\n\n")

        if show_callees:
            main_stats.stream.write("#" * 80)
            main_stats.stream.write("\nCallees:\n\n")
            main_stats.stream.write("\n\n")
            main_stats.print_callees(limit)

        # Close the file if opened
        if output_file and main_stats.stream != sys.stdout:
            main_stats.stream.close()
            main_stats.stream = original_stream
            print("Results saved to {}".format(output_file))

    except IOError as e:
        print("Error: File operation failed: {}".format(e))
        sys.exit(1)
    except Exception as e:
        print("Error processing {}: {}".format(path, e))
        import traceback

        traceback.print_exc()
        sys.exit(1)


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Generate human-readable output from Python cProfile pstat files"
    )

    # Add arguments
    parser.add_argument("file", help="Path to the pstat file")
    parser.add_argument(
        "-s",
        "--sort",
        default="cumulative",
        choices=[
            "cumulative",
            "time",
            "calls",
            "pcalls",
            "name",
            "nfl",
            "stdname",
            "file",
            "line",
            "module",
        ],
        help="Sort key for the statistics (default: cumulative)",
    )
    parser.add_argument(
        "-n", "--limit", type=int, help="Limit the number of functions shown"
    )
    parser.add_argument(
        "-o", "--output", help="Save the output to a file instead of printing to stdout"
    )
    parser.add_argument(
        "--full-paths",
        action="store_true",
        help="Show full file paths instead of just filenames",
    )
    parser.add_argument(
        "--callers",
        action="store_true",
        help="Show the callers of each function",
    )
    parser.add_argument(
        "--callees",
        action="store_true",
        help="Show the functions called by each function",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Process the file
    process_pstat(
        args.file,
        sort_key=args.sort,
        limit=args.limit,
        output_file=args.output,
        strip_paths=not args.full_paths,
        show_callers=args.callers,
        show_callees=args.callees,
    )


if __name__ == "__main__":
    main()
