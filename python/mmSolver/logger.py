"""
Unified logging for the mmSolver package.
"""

import logging
import inspect


def get_logger(level=None):
    """
    Returns a Logger object for logging events.

    Example usage::

        import mmSolver.logger
        LOG = mmSolver.logger.get_logger()
        LOG.info('hello world')
        LOG.warning('be careful everyone')
        LOG.error('some thing bad has happened')

    :param level: Set the level for the newly created Logger object.
    :type level: str or None

    :return: A Logger object.
    """
    # The calling module name, in module hierarchy.
    # Source: https://gist.github.com/techtonik/2151727
    stack = inspect.stack()
    start = 1
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]
    module = inspect.getmodule(parentframe)
    module_name = 'root'
    if module is not None:
        module_name = module.__name__

    log = logging.getLogger(module_name)
    if level is not None:
        log.setLevel(level)
    return log

