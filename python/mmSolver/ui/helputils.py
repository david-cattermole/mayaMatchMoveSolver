"""
Utilities for 'user help' functions.
"""

import os
import webbrowser
import mmSolver.logger

LOG = mmSolver.logger.get_logger()

HELP_SOURCE_LOCAL = 'local'
HELP_SOURCE_INTERNET = 'internet'
HELP_SOURCE_LIST = [
    HELP_SOURCE_LOCAL,
    HELP_SOURCE_INTERNET,
]
HELP_SOURCE_FALLBACK = 'local'

ENV_VAR_NAME_LOCATION = 'MMSOLVER_LOCATION'
ENV_VAR_NAME_HELP_SOURCE = 'MMSOLVER_HELP_SOURCE'

WEB_SITE_HELP_LOCATION = 'https://david-cattermole.github.io/mayaMatchMoveSolver/'


def get_help_source():
    """
    Determine the user's perfered help source, or fallback to a
    preselected source.
    
    :return: The help source to search for, a value in
             HELP_SOURCE_LIST.

    """
    src = os.environ.get(ENV_VAR_NAME_HELP_SOURCE, None)
    if src is None:
        msg = (
            'Preferred help source was not found with environment' 
            ' variable MM_SOLVER_HELP_SOURCE, falling back to %r.'
        )
        LOG.warning(msg, HELP_SOURCE_FALLBACK)
        return HELP_SOURCE_FALLBACK
    assert isinstance(src, (str, unicode))
    src = src.lower()
    if src not in HELP_SOURCE_LIST:
        msg = 'Could not find help source %r, falling back to %r.'
        LOG.warning(msg, src, HELP_SOURCE_FALLBACK)
        src = HELP_SOURCE_FALLBACK
    return src


def get_help_base_location(help_source=None):
    """Get the file path to the help documentation.

    :param help_source: Must be given! A value in HELP_SOURCE_LIST,
                        denoting the help documentation source to use
                        (but not the source itself.)

    :return: URL able to be opened by a web-browser, expected to point
             to a .html file, on a network, or on the local file
             system.
    :rtype: str

    """
    assert help_source in HELP_SOURCE_LIST
    url = None
    if help_source == HELP_SOURCE_LOCAL:
        url = os.environ.get(ENV_VAR_NAME_LOCATION, None)
        if url is None:
            msg = (
                'The help URL cannot be found from environment variables,'
                'Your mmSolver installation may be incorrect?'
                ' name=%r value=%r'
            )
            LOG.warning(msg, ENV_VAR_NAME_LOCATION, url)
            return None
        url = os.path.join(url, 'docs/html/')
        if os.path.isdir(url) is False:
            msg = (
                'The help URL cannot be found! '
                'Your installation may be missing documentation. '
                'url=%r'
            )
            LOG.warning(msg, url)
            return None
    elif help_source == HELP_SOURCE_INTERNET:
        url = str(WEB_SITE_HELP_LOCATION)
    else:
        msg = 'Help source is not valid: %r'
        LOG.error(msg, help_source)
        raise ValueError(msg % help_source)
    return url
    

def open_help_in_browser(page=None, help_source=None):
    """
    Open help to a specific page.
    """
    assert page is None or isinstance(page, basestring)
    url = get_help_base_location(help_source=help_source)
    if url is None:
        LOG.warning('Could not find help documentation.')
        return
    if page is None:
        page = 'index.html'
    url = os.path.join(url, page)
    msg = 'Opening Help Documentation: %r'
    LOG.info(msg, url)
    webbrowser.open(url)
    return
