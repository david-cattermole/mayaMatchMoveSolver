# Copyright (C) 2019 David Cattermole.
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
Actions - a wrapper tuple for a callable function with positional and keyword arguments.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import importlib

import mmSolver.utils.python_compat as pycompat


Action = collections.namedtuple(
    'Action',
    ('func', 'args', 'kwargs')
)


def action_func_is_mmSolver(action):
    return _action_func_is_name(action, 'mmSolver')


def action_func_is_mmSolverAffects(action):
    return _action_func_is_name(action, 'mmSolverAffects')


def _action_func_is_name(action, name):
    if action is None:
        return False
    func = action.func
    if func is None:
        return False
    if isinstance(func, pycompat.TEXT_TYPE):
        func_is_mmsolver = func.endswith('.' + name)
    elif callable(func):
        func_is_mmsolver = func.__name__ == name
    else:
        func_is_mmsolver = False
    return func_is_mmsolver


def func_str_to_callable(func_str):
    """
    Convert a function written as a string, to be a callable object.
    """
    assert isinstance(func_str, pycompat.TEXT_TYPE) is True
    # Look up callable function from name at run-time.
    mod_name, func_name = func_str.rsplit('.', 1)
    mod = importlib.import_module(mod_name)
    func = getattr(mod, func_name)
    return func


def action_to_components(action):
    func = action.func
    args = list(action.args)
    kwargs = action.kwargs.copy()
    if isinstance(func, pycompat.TEXT_TYPE):
        func = func_str_to_callable(func)
    assert callable(func)
    return func, args, kwargs
