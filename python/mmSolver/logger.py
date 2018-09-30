"""
Unified logging for the mmSolver package.
"""

import logging
import inspect


def get_logger():
    """
    Returns a Logger object for logging events.

    Example usage::

        import mmSolver.logger
        LOG = mmSolver.logger.get_logger()
        LOG.info('hello world')
        LOG.warning('be careful everyone')
        LOG.error('some thing bad has happened')

    :return: a Logger object.
    """
    # The calling module name, in module hierarchy.
    # Source: https://gist.github.com/techtonik/2151727
    stack = inspect.stack()
    start = 2
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]
    module = inspect.getmodule(parentframe)
    module_name = module.__name__

    return logging.getLogger(module_name)

