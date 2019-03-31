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
MMSOLVER_STARTED = False


def mmsolver_create_shelf():
    """
    Build the mmSolver shelf.
    """
    import mmSolver.tools.mmshelf.tool
    mmSolver.tools.mmshelf.tool.build_shelf()


def mmsolver_create_menu():
    """
    Build the mmSolver menu.
    """
    import mmSolver.tools.mmmenu.tool
    mmSolver.tools.mmmenu.tool.build_menu()


def mmsolver_startup():
    """
    Responsible for starting up mmSolver.
    """
    LOG.info('MM Solver Startup...')

    global MMSOLVER_STARTED
    MMSOLVER_STARTED = True

    # Only run GUI code when the Maya interactive GUI opens.
    is_batch_mode = maya.cmds.about(batch=True)
    LOG.debug('Batch Mode: %r', is_batch_mode)
    if is_batch_mode is False:
        # Create Menu.
        build_menu = bool(int(os.environ.get('MMSOLVER_CREATE_MENU', 1)))
        LOG.debug('Build Menu: %r', build_menu)
        if build_menu is True:
            maya.utils.executeDeferred(mmsolver_create_menu)

        # Create Shelf.
        build_shelf = bool(int(os.environ.get('MMSOLVER_CREATE_SHELF', 1)))
        LOG.debug('Build Shelf: %r', build_shelf)
        if build_shelf is True:
            maya.utils.executeDeferred(mmsolver_create_shelf)
    return


# Run Start up Function after Maya has loaded.
load_at_startup = bool(int(os.environ.get('MMSOLVER_LOAD_AT_STARTUP', 1)))
if load_at_startup is True:
    maya.utils.executeDeferred(mmsolver_startup)
