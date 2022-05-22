# Copyright (C) 2020, 2022 David Cattermole.
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
Library functions for creating and modifying image planes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import maya.cmds

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat

LOG = mmSolver.logger.get_logger()


def add_attr_float3_color(node, attr_name, default_value):
    min_value = 0.0
    maya.cmds.addAttr(
        node,
        longName=attr_name,
        usedAsColor=True,
        attributeType='float3')

    maya.cmds.addAttr(
        node,
        longName=attr_name + 'R',
        attributeType='float',
        minValue=min_value,
        defaultValue=default_value,
        parent=attr_name)
    maya.cmds.addAttr(
        node,
        longName=attr_name + 'G',
        attributeType='float',
        minValue=min_value,
        defaultValue=default_value,
        parent=attr_name)
    maya.cmds.addAttr(
        node,
        longName=attr_name + 'B',
        attributeType='float',
        minValue=min_value,
        defaultValue=default_value,
        parent=attr_name)

    node_attr = node + '.' + attr_name
    maya.cmds.setAttr(node_attr + 'R', keyable=True)
    maya.cmds.setAttr(node_attr + 'G', keyable=True)
    maya.cmds.setAttr(node_attr + 'B', keyable=True)
    return


def force_connect_attr(src_attr, dst_attr):
    """Disconnect attribute that is already connected to dst_attr, before
    creating the connection.
    """
    dst_lock_state = maya.cmds.getAttr(dst_attr, lock=True)

    if dst_lock_state is True:
        maya.cmds.setAttr(dst_attr, lock=False)

    conns = maya.cmds.listConnections(
        dst_attr,
        source=True,
        plugs=True,
        skipConversionNodes=True) or []
    conns = [x for x in conns if maya.cmds.isConnected(x, dst_attr)]
    for conn in conns:
        maya.cmds.disconnectAttr(conn, dst_attr)
    maya.cmds.connectAttr(src_attr, dst_attr, force=True)

    if dst_lock_state is True:
        maya.cmds.setAttr(dst_attr, lock=True)
    return


def get_default_image_path():
    base_install_location = os.environ.get('MMSOLVER_LOCATION', None)
    assert base_install_location is not None
    fallback = os.path.join(base_install_location, 'resources')

    dir_path = os.environ.get('MMSOLVER_RESOURCE_PATH', fallback)
    assert isinstance(dir_path, pycompat.TEXT_TYPE)

    file_name = 'default_mmSolver_1920x1080_hd.iff'
    file_path = os.path.join(dir_path, file_name)
    return os.path.abspath(file_path)
