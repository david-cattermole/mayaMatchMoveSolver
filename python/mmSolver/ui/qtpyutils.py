"""
Helper utils for Qt.py module.

This module will *not* import Qt.py, and contains functions designed to be
run before Qt.py is imported.
"""

import os

PREFERRED_BINDING = 'QT_PREFERRED_BINDING'
BINDING_ORDER = ['PySide2', 'PyQt5', 'PySide', 'PyQt4']


def override_binding_order(binding_order=None):
    """
    Change the expected order of Qt bindings used by Qt.py.


    """
    if binding_order is None:
        binding_order = BINDING_ORDER
    if PREFERRED_BINDING not in os.environ:
        os.environ[PREFERRED_BINDING] = os.pathsep.join(binding_order)
    return
