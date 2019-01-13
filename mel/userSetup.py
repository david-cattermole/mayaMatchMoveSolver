"""
A start-up script for mmSolver.

We use the Python 'userSetup.py' file rather than 'userSetup.mel'
because of the message here:
https://around-the-corner.typepad.com/adn/2012/07/distributing-files-on-maya-maya-modules.html

"""

import os
import maya.cmds
import maya.utils
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def create_shelf():
    """
    Build the mmSolver shelf.
    """
    import mmSolver.tools.mmshelf.tool
    mmSolver.tools.mmshelf.tool.build_shelf()


def startup():
    LOG.info('MM Solver Startup...')

    # Only run GUI code when the Maya interactive GUI opens.
    is_batch_mode = maya.cmds.about(batch=True)
    LOG.debug('Batch Mode: %r', is_batch_mode)
    if is_batch_mode is False:

        # Create Shelf.
        build_shelf = os.environ.get('MMSOLVER_CREATE_SHELF', False)
        LOG.debug('Build Shelf: %r', build_shelf)
        if bool(build_shelf) is True:
            maya.utils.executeDeferred(create_shelf)

# Run Start up Function after Maya has loaded.
maya.utils.executeDeferred(startup)
