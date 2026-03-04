# Copyright (C) 2026 David Cattermole.
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
Data types for the Camera Solver.
"""

import mmSolver.utils.python_compat as pycompat

import mmSolver.tools.camerasolver.constant as const


class AdjustmentSolver(object):
    def __init__(self):
        # type: () -> None
        self.__adjustment_solver_type = None
        self.__thread_count = None
        self.__evolution_value_range_estimate = None
        self.__evolution_generation_count = None
        self.__evolution_population_count = None

    def get_adjustment_solver_type(self):
        # type: (AdjustmentSolver) -> str | None
        return self.__adjustment_solver_type

    def set_adjustment_solver_type(self, value):
        # type: (AdjustmentSolver, str) -> None
        assert value in const.ADJUSTMENT_SOLVER_TYPE_LIST
        self.__adjustment_solver_type = value

    def get_thread_count(self):
        # type: (AdjustmentSolver) -> int | None
        return self.__thread_count

    def set_thread_count(self, value):
        # type: (...) -> None
        assert isinstance(value, int)
        assert value > 0
        self.__thread_count = value

    def get_evolution_value_range_estimate(self):
        # type: (AdjustmentSolver) -> int | None
        return self.__evolution_value_range_estimate

    def set_evolution_value_range_estimate(self, value):
        # type: (...) -> None
        assert isinstance(value, int)
        assert value > 0
        self.__evolution_value_range_estimate = value

    def get_evolution_generation_count(self):
        # type: (AdjustmentSolver) -> int | None
        return self.__evolution_generation_count

    def set_evolution_generation_count(self, value):
        # type: (...) -> None
        assert isinstance(value, int)
        assert value > 0
        self.__evolution_generation_count = value

    def get_evolution_population_count(self):
        # type: (AdjustmentSolver) -> int | None
        return self.__evolution_population_count

    def set_evolution_population_count(self, value):
        # type: (...) -> None
        assert isinstance(value, int)
        assert value > 0
        self.__evolution_population_count = value


class AdjustmentAttributes(object):
    def __init__(self):
        # type: () -> None
        self.__attribute_to_bounds = {}
        self.__attribute_to_sample_count = {}

    def get_attribute_names(self):
        # type: (AdjustmentAttributes) -> list[str]
        return list(self.__attribute_to_bounds.keys())

    def get_attribute_bounds(self, attr_name):
        # type: (...) -> list[float] | None
        assert isinstance(attr_name, pycompat.TEXT_TYPE)
        return self.__attribute_to_bounds.get(attr_name)

    def set_attribute_bounds(self, attr_name, min_value, max_value):
        # type: (...) -> None
        assert isinstance(attr_name, pycompat.TEXT_TYPE)
        assert isinstance(min_value, float)
        assert isinstance(max_value, float)
        self.__attribute_to_bounds[attr_name] = [min_value, max_value]

    def get_attribute_sample_count(self, attr_name):
        # type: (...) -> int | None
        assert isinstance(attr_name, pycompat.TEXT_TYPE)
        return self.__attribute_to_sample_count.get(attr_name)

    def set_attribute_sample_count(self, attr_name, value):
        # type: (...) -> None
        assert isinstance(attr_name, pycompat.TEXT_TYPE)
        assert isinstance(value, int)
        assert value > 0
        self.__attribute_to_sample_count[attr_name] = value
