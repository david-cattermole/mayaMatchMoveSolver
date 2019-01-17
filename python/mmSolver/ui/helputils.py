"""
Utilities for 'user help' functions.
"""

import os
import webbrowser
import mmSolver.logger


WEB_SITE_HELP_LOCATION = 'https://david-cattermole.github.io/mayaMatchMoveSolver/'
LOG = mmSolver.logger.get_logger()


def get_help_base_location(local=True):
    """
    Get the file path to the help documentation.
    """
    assert isinstance(local, bool) is True
    url = None
    if local is True:
        url = os.environ.get('MMSOLVER_LOCATION', None)
        if url is None:
            return None
        url = os.path.join(url, 'docs/html/')
        if os.path.isdir(url) is False:
            return None
    else:
        url = str(WEB_SITE_HELP_LOCATION)
    return url
    

def open_help_in_browser(page=None, local=True):
    """
    Open help to a specific page.
    """
    assert page is None or isinstance(page, basestring)
    url = get_help_base_location(local=local)
    if url is None:
        LOG.warning('Could not find help documentation.')
        return
    if page is None:
        page = 'index.html'
    url = os.path.join(url, page)
    webbrowser.open(url)
    return
