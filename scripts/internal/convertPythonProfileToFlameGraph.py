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
Converts a Python pstat file (from cProfile) into the FlameGraph format (.folded).

Usage:
> python convertPythonProfileToFlamegraph.py <pstat_file> <output_file>

FlameGraph:
https://www.brendangregg.com/flamegraphs.html
https://github.com/brendangregg/FlameGraph
"""

from __future__ import print_function  # For Python 2.7 compatibility

import sys
import pstats
from collections import defaultdict


def pstat_to_flamegraph(pstat_file, output_file):
    """
    Convert a Python pstat file to FlameGraph folded format.

    Args:
        pstat_file (str): Path to the pstat file
        output_file (str): Path to write the FlameGraph folded output
    """
    print("Loading pstat file: {}".format(pstat_file))

    # Load the pstat file
    try:
        p = pstats.Stats(pstat_file)
    except Exception as e:
        print("Error loading pstat file: {}".format(e), file=sys.stderr)
        return False

    # Dictionary to store call stacks and their time values.
    stacks = defaultdict(float)

    # Process the profiling data to extract call stacks.
    call_graph = {}

    # Function to get a readable name for a function tuple.
    def get_func_name(func):
        return func[2]

    # First pass: Build a call graph and collect self times.
    for func, (cc, nc, tt, ct, callers) in p.stats.items():
        func_name = get_func_name(func)
        self_time = tt  # Time spent in this function excluding subcalls

        # Record the callers and their contributions
        call_graph[func] = {
            "name": func_name,
            "callers": list(callers.keys()),
            "self_time": self_time,
            "cum_time": ct,
        }

    # Second pass: Identify root functions (functions with no callers
    # or only called by themselves).
    roots = []
    for func in call_graph:
        has_real_callers = False
        for caller in call_graph[func]["callers"]:
            if caller != func:  # Skip self-recursion
                has_real_callers = True
                break

        if not has_real_callers:
            roots.append(func)

    # Third pass: For each root, generate all paths through the call
    # graph.
    def traverse_call_graph(current_func, path=None, visited=None):
        if path is None:
            path = []
        if visited is None:
            visited = set()

        # Avoid cycles.
        if current_func in visited:
            return
        visited.add(current_func)

        current_name = call_graph[current_func]["name"]
        new_path = path + [current_name]

        # Stats data.
        cc, nc, tt, ct, callers = p.stats[current_func]

        # For leaf nodes or nodes where children are fully accounted
        # for elsewhere, record the full path with its self time.
        self_time = call_graph[current_func]["self_time"]  # or "cum_time"

        # Only record stacks with non-zero time.
        if self_time > 0.0:
            # Create flamegraph stack format (root;caller;caller;function)
            stack_key = ";".join(new_path)
            stacks[stack_key] += self_time * 1000  # Convert to milliseconds

        # Find all callees for further traversal.
        for callee, (
            callee_cc,
            callee_nc,
            callee_tt,
            callee_ct,
            callee_callers,
        ) in p.stats.items():
            if current_func in callee_callers:
                traverse_call_graph(callee, new_path, visited.copy())

    # Start traversal from all root functions.
    for root in roots:
        traverse_call_graph(root)

    # Write the output file.
    print("Writing output to: {}".format(output_file))
    try:
        with open(output_file, 'w') as f:
            for stack, time in stacks.items():
                if time > 0:
                    f.write("{} {}\n".format(stack, int(time)))
    except IOError:
        print(
            "Error: Could not write to output file '{}'".format(output_file),
            file=sys.stderr,
        )
        return False

    print("Conversion complete!")
    return True


def main():
    """Main function to handle command-line arguments."""
    if len(sys.argv) < 3:
        print("Usage: {} <pstat_file> <output_file>".format(sys.argv[0]))
        return 1

    pstat_file = sys.argv[1]
    output_file = sys.argv[2]

    success = pstat_to_flamegraph(pstat_file, output_file)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
