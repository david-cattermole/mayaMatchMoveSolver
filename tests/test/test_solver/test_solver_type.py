# Copyright (C) 2018, 2019 David Cattermole.
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
Testing 'mmSolverType' command.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

try:
    import maya.standalone

    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds


import mmSolver.utils.python_compat as pycompat
import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestMMSolverType(solverUtils.SolverTestCase):
    def test_command_exists(self):
        """
        The command must exist as maya.cmds.mmSolverType
        """
        cmd_name = 'mmSolverType'
        assert cmd_name in dir(maya.cmds)
        return

    def test_get_list(self):
        """
        Test listing solver types works.
        """
        a_list = maya.cmds.mmSolverType(
            query=True,
            list=True,
        )
        assert len(a_list) > 0
        for solver_type in a_list:
            assert '=' in solver_type
            assert isinstance(solver_type, pycompat.TEXT_TYPE)

        b_list = maya.cmds.mmSolverType(
            query=True,
            list=True,
            name=True,
            index=False,
        )
        assert len(b_list) > 0
        assert len(a_list) == len(b_list)
        for solver_name in b_list:
            assert '=' not in solver_name
            assert isinstance(solver_name, pycompat.TEXT_TYPE)

        c_list = maya.cmds.mmSolverType(
            query=True,
            list=True,
            name=False,
            index=True,
        )
        assert len(c_list) > 0
        assert len(a_list) == len(c_list)
        for solver_index in c_list:
            assert isinstance(solver_index, pycompat.INT_TYPES)
        return

    def test_get_list_invalid_input(self):
        """
        Test the command correctly errors when given bad input
        """
        # Not asking for a name or index is an error.
        with self.assertRaises(RuntimeError):
            maya.cmds.mmSolverType(query=True, list=True, name=False, index=False)
        return

    def test_get_default(self):
        """
        Test getting the default solver type.
        """
        solver_type = maya.cmds.mmSolverType(query=True, default=True)
        assert '=' in solver_type
        assert isinstance(solver_type, pycompat.TEXT_TYPE)

        solver_name = maya.cmds.mmSolverType(
            query=True,
            default=True,
            name=True,
            index=False,
        )
        assert len(solver_name) < len(solver_type)
        assert '=' not in solver_name
        assert isinstance(solver_name, pycompat.TEXT_TYPE)

        solver_index = maya.cmds.mmSolverType(
            query=True,
            default=True,
            name=False,
            index=True,
        )
        assert isinstance(solver_index, pycompat.INT_TYPES)
        return


if __name__ == '__main__':
    prog = unittest.main()
