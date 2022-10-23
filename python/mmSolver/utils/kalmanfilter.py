# Copyright (C) 2020 David Cattermole.
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
Basic 1-dimensional Kalman filter.

https://towardsdatascience.com/kalman-filters-a-step-by-step-implementation-guide-in-python-91e7e123b968
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections


State = collections.namedtuple(
    'State',
    (
        'value',  # the value
        'mean',  # average or 'mu'
        'variance',  # 'sigma'
    ),
)


def update(state_a, state_b):
    """
    Update the variance and mean.

    :param state_a: First state.
    :type state_a: State

    :param state_b: Second state.
    :type state_b: State

    :return: New state.
    :rtype: State
    """
    new_mean = state_b.variance * state_a.mean + state_a.variance * state_b.mean
    new_mean /= state_b.variance + state_a.variance
    new_variance = 1.0 / (1.0 / state_b.variance + 1.0 / state_a.variance)
    new_value = state_b.value
    return State(mean=new_mean, variance=new_variance, value=new_value)


def predict(state_a, state_b):
    """
    Predict the next state, based on two gaussian distribution states.

    :param state_a: First state.
    :type state_a: State

    :param state_b: Second state.
    :type state_b: State

    :return: New state, combined of both first and second states.
    :rtype: State
    """
    new_mean = state_a.mean + state_b.mean
    new_variance = state_a.variance + state_b.variance
    new_value = state_a.value + state_b.value
    return State(mean=new_mean, variance=new_variance, value=new_value)
