# Copyright (C) 2022 David Cattermole.
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
Set the colour of selected objects.
"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtGui as QtGui

import maya.cmds

import mmSolver.logger
import mmSolver.tools.setobjectcolour.lib as lib

LOG = mmSolver.logger.get_logger()


def reset_colour():
    sel = maya.cmds.ls(sl=True, long=True) or []

    tfm_nodes = maya.cmds.ls(sl=True, long=True, type='transform') or []
    if len(tfm_nodes) == 0:
        LOG.warn('Please select shape nodes.')
        return

    lib.reset_nodes_colour(tfm_nodes)

    if len(sel) > 0:
        maya.cmds.select(sel, replace=True)
    return


def open_window(mini_ui=None):
    if mini_ui is None:
        mini_ui = False

    sel = maya.cmds.ls(sl=True, long=True) or []

    tfm_nodes = maya.cmds.ls(sl=True, long=True, type='transform') or []
    if len(tfm_nodes) == 0:
        LOG.warn('Please select shape nodes.')
        return

    # Initial colour to start the 'colorEditor' with.
    rgba = lib.get_first_node_colour(tfm_nodes)
    rgb = (rgba[0], rgba[1], rgba[2])
    alpha = rgba[3]

    kwargs = {'mini': False}
    if mini_ui is True:
        cursor_point = QtGui.QCursor().pos()
        window_pos = (cursor_point.x() - 50, cursor_point.y() - 50)
        kwargs = {'mini': True, 'position': window_pos}

    maya.cmds.colorEditor(rgbValue=rgb, alpha=alpha, **kwargs)
    if not maya.cmds.colorEditor(query=True, result=True):
        LOG.warn('Color editor cancelled.')
        return

    rgb = maya.cmds.colorEditor(query=True, rgbValue=True)
    alpha = maya.cmds.colorEditor(query=True, alpha=True)

    rgba = (rgb[0], rgb[1], rgb[2], alpha)
    lib.set_nodes_colour(tfm_nodes, rgba)

    if len(sel) > 0:
        maya.cmds.select(sel, replace=True)
    return


def open_mini_window():
    open_window(mini_ui=True)
