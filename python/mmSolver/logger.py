"""
Unified logging for the mmSolver package.
"""

import logging
import inspect


def get_logger():
    # The calling module name, in module hierarchy.
    # Source: https://gist.github.com/techtonik/2151727
    stack = inspect.stack()
    start = 2
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]
    module = inspect.getmodule(parentframe)
    module_name = module.__name__

    # Logging module.
    return logging.getLogger(module_name)

