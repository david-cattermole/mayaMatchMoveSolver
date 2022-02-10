# Copyright (C) 2021 David Cattermole.
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
The Create Sky Dome tool.
"""

import maya.cmds
import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.createskydome.constant as const


LOG = mmSolver.logger.get_logger()


def main(preset_name=None):
    """
    Create a new Sky Dome.

    :param preset_name: The name
    """
    if preset_name is None:
        preset_name = const.PRESET_SKY_DOME_NAME
    assert preset_name in const.PRESET_NAME_LIST

    mmapi.load_plugin()
    tfm = maya.cmds.createNode("transform", name="mmSkyDome1")
    shp = maya.cmds.createNode(
        "mmSkyDomeShape", name="mmSkyDomeShape1", parent=tfm
    )

    if preset_name == const.PRESET_SKY_DOME_NAME:
        maya.cmds.setAttr(shp + '.axisEnableX', True)
        maya.cmds.setAttr(shp + '.axisEnableY', True)
        maya.cmds.setAttr(shp + '.axisEnableZ', True)
        maya.cmds.setAttr(shp + '.gridLatitudeEnable', True)
        maya.cmds.setAttr(shp + '.gridLongitudeEnable', True)
    elif preset_name == const.PRESET_AXIS_DOME_NAME:
        maya.cmds.setAttr(shp + '.axisEnableX', True)
        maya.cmds.setAttr(shp + '.axisEnableY', True)
        maya.cmds.setAttr(shp + '.axisEnableZ', True)
        maya.cmds.setAttr(shp + '.gridLatitudeEnable', False)
        maya.cmds.setAttr(shp + '.gridLongitudeEnable', False)
    elif preset_name == const.PRESET_HORIZON_LINE_NAME:
        maya.cmds.setAttr(shp + '.axisEnableX', False)
        maya.cmds.setAttr(shp + '.axisEnableY', True)
        maya.cmds.setAttr(shp + '.axisEnableZ', False)
        maya.cmds.setAttr(shp + '.gridLatitudeEnable', False)
        maya.cmds.setAttr(shp + '.gridLongitudeEnable', False)
        maya.cmds.setAttr(shp + '.axisColorY', 1.0, 0.0, 0.0, type='double3')
    else:
        assert False

    maya.cmds.select(tfm, replace=True)
    return
