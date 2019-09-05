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

import collections
import importlib


Action = collections.namedtuple(
    'Action',
    ('func', 'args', 'kwargs')
)


def action_func_is_mmSolver(action):
    func = action.func
    func_is_mmsolver = isinstance(func, basestring) and '.mmSolver' in func
    return func_is_mmsolver


def action_to_components(action):
    func = action.func
    args = list(action.args)
    kwargs = action.kwargs.copy()
    if isinstance(func, basestring):
        # Look up callable function from name at run-time.
        mod_name, func_name = func.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
    return func, args, kwargs
