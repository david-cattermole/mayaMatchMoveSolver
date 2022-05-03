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
Tool for finding and editing nodes connected cameras.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import maya.cmds

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.cameramenu.constant as const
import mmSolver.tools.cameramenu.lib as lib

LOG = mmSolver.logger.get_logger()


def _generate_nice_name(node):
    assert isinstance(node, pycompat.TEXT_TYPE)
    assert maya.cmds.objExists(node)
    name = maya.cmds.ls(node)[0]
    arrow_str = '->'
    if arrow_str in name:
        # Image planes have node names like
        # 'cameraShape1->imagePlaneShape1', but we strip the camera
        # name off for brevity.
        name = name.split(arrow_str)[-1]
    return name


def _create_image_plane_menu_items(parent, camera_shape_node, image_plane_nodes):
    camera_shape_name = _generate_nice_name(camera_shape_node)
    items = []

    item = maya.cmds.menuItem(
        parent=parent,
        divider=True,
        dividerLabel='Image Planes',
        subMenu=False,
    )
    items.append(item)

    for num, node in enumerate(image_plane_nodes):
        name = _generate_nice_name(node)
        type_name = lib.get_image_plane_type_name_label(node)

        tooltip = const.SELECT_IMAGE_PLANE_NODE_TOOLTIP.format(name=name)
        cmd = const.SELECT_IMAGE_PLANE_NODE_CMD.format(node=node)
        cmd_lang = const.SELECT_IMAGE_PLANE_NODE_CMD_LANG
        label = '{name} ({type_name})'.format(name=name, type_name=type_name)
        item = maya.cmds.menuItem(
            parent=parent,
            label=label,
            annotation=tooltip,
            command=cmd,
            sourceType=cmd_lang,
            subMenu=False,
        )
        items.append(item)

        tooltip = const.SELECT_NODE_AND_SHOW_IN_ATTRIBUTE_EDITOR_TOOLTIP
        cmd = const.SELECT_NODE_AND_SHOW_IN_ATTRIBUTE_EDITOR_CMD.format(node=node)
        cmd_lang = const.SELECT_NODE_AND_SHOW_IN_ATTRIBUTE_EDITOR_CMD_LANG
        item = maya.cmds.menuItem(
            parent=parent,
            annotation=tooltip,
            command=cmd,
            sourceType=cmd_lang,
            optionBox=True,
            subMenu=False,
        )
        items.append(item)

    tooltip = const.CREATE_IMAGE_PLANE_TOOLTIP.format(camera_shape_name=camera_shape_name)
    cmd = const.CREATE_IMAGE_PLANE_CMD.format(camera_shape_node=camera_shape_node)
    cmd_lang = const.CREATE_IMAGE_PLANE_CMD_LANG
    label = const.CREATE_IMAGE_PLANE_LABEL
    item = maya.cmds.menuItem(
        parent=parent,
        label=label,
        annotation=tooltip,
        command=cmd,
        sourceType=cmd_lang,
        subMenu=False,
    )
    items.append(item)
    return items


def _create_lens_menu_items(parent, camera_shape_node, lens_nodes):
    camera_shape_name = _generate_nice_name(camera_shape_node)

    items = []
    item = maya.cmds.menuItem(
        parent=parent,
        divider=True,
        dividerLabel='Lens Layers',
        subMenu=False,
    )
    items.append(item)

    base_lens_node = camera_shape_node
    if len(lens_nodes) > 0:
        base_lens_node = lens_nodes[0]

    label = "Open in Node Graph..."
    enabled = len(lens_nodes) > 0
    tooltip = const.OPEN_NODE_IN_NODE_EDITOR_TOOLTIP
    cmd = const.OPEN_NODE_IN_NODE_EDITOR_CMD.format(node=base_lens_node)
    cmd_lang = const.OPEN_NODE_IN_NODE_EDITOR_CMD_LANG
    item = maya.cmds.menuItem(
        parent=parent,
        enable=enabled,
        label=label,
        annotation=tooltip,
        command=cmd,
        sourceType=cmd_lang,
        subMenu=False,
    )
    items.append(item)

    camera_lenses_enabled = lib.camera_lens_distortion_enabled(camera_shape_node)
    label = const.TOGGLE_CAMERA_LENS_DISTORTION_ENABLED_LABEL
    tooltip = const.TOGGLE_CAMERA_LENS_DISTORTION_ENABLED_TOOLTIP
    cmd = const.TOGGLE_CAMERA_LENS_DISTORTION_ENABLED_CMD.format(camera_shape_node=camera_shape_node)
    cmd_lang = const.TOGGLE_CAMERA_LENS_DISTORTION_ENABLED_CMD_LANG
    item = maya.cmds.menuItem(
        parent=parent,
        label=label,
        annotation=tooltip,
        command=cmd,
        sourceType=cmd_lang,
        checkBox=camera_lenses_enabled,
        subMenu=False,
    )
    items.append(item)

    # Note the order of the lenses matter
    for num, node in enumerate(lens_nodes):
        name = _generate_nice_name(node)

        reverse_num = (len(lens_nodes) - 1) - num
        label = 'Layer {num}: {name}'
        if reverse_num == 0:
            label = 'Base: {name}'
        label = label.format(num=reverse_num, name=name)

        tooltip = const.SELECT_LENS_NODE_TOOLTIP.format(name=name)
        cmd = const.SELECT_LENS_NODE_CMD.format(node=node)
        cmd_lang = const.SELECT_LENS_NODE_CMD_LANG
        item = maya.cmds.menuItem(
            parent=parent,
            label=label,
            annotation=tooltip,
            command=cmd,
            sourceType=cmd_lang,
            enable=camera_lenses_enabled,
            subMenu=False,
        )
        items.append(item)

        tooltip = const.SELECT_NODE_AND_SHOW_IN_ATTRIBUTE_EDITOR_TOOLTIP.format(name=name)
        cmd = const.SELECT_NODE_AND_SHOW_IN_ATTRIBUTE_EDITOR_CMD.format(node=node)
        cmd_lang = const.SELECT_NODE_AND_SHOW_IN_ATTRIBUTE_EDITOR_CMD_LANG
        item = maya.cmds.menuItem(
            parent=parent,
            annotation=tooltip,
            command=cmd,
            sourceType=cmd_lang,
            optionBox=True,
            subMenu=False,
        )
        items.append(item)

    label = const.CREATE_LENS_LABEL
    tooltip = const.CREATE_LENS_TOOLTIP.format(camera_shape_name=camera_shape_name)
    cmd = const.CREATE_LENS_CMD.format(camera_shape_node=camera_shape_node)
    cmd_lang = const.CREATE_LENS_CMD_LANG
    item = maya.cmds.menuItem(
        parent=parent,
        label=label,
        annotation=tooltip,
        command=cmd,
        sourceType=cmd_lang,
        subMenu=False,
    )
    items.append(item)

    return items


def create_camera_menu_items(parent, camera_shape_nodes):
    items = []

    item = maya.cmds.menuItem(
        parent=parent,
        divider=True,
        dividerLabel='Camera',
        subMenu=False,
    )
    items.append(item)

    if len(camera_shape_nodes) == 0:
        tooltip = const.CREATE_CAMERA_TOOLTIP.format(name='')
        cmd = const.CREATE_CAMERA_CMD.format(name='')
        cmd_lang = const.CREATE_CAMERA_CMD_LANG
        label = 'Create Camera'
        item = maya.cmds.menuItem(
            parent=parent,
            label=label,
            annotation=tooltip,
            command=cmd,
            sourceType=cmd_lang,
            subMenu=False,
        )
        items.append(item)
        return items

    # Only choose the first camera. We don't want to overwhelm the
    # user with lots of menu items.
    camera_shape_nodes = sorted(camera_shape_nodes)[:1]

    for num, node in enumerate(camera_shape_nodes):
        name = _generate_nice_name(node)

        label = name
        tooltip = const.SELECT_CAMERA_NODE_TOOLTIP.format(name=name)
        cmd = const.SELECT_CAMERA_NODE_CMD.format(camera_shape_node=node)
        cmd_lang = const.SELECT_CAMERA_NODE_CMD_LANG
        item = maya.cmds.menuItem(
            parent=parent,
            label=label,
            annotation=tooltip,
            command=cmd,
            sourceType=cmd_lang,
            subMenu=False,
        )
        items.append(item)

        tooltip = const.SELECT_NODE_AND_SHOW_IN_ATTRIBUTE_EDITOR_TOOLTIP.format(name=name)
        cmd = const.SELECT_NODE_AND_SHOW_IN_ATTRIBUTE_EDITOR_CMD.format(node=node)
        cmd_lang = const.SELECT_NODE_AND_SHOW_IN_ATTRIBUTE_EDITOR_CMD_LANG
        item = maya.cmds.menuItem(
            parent=parent,
            annotation=tooltip,
            command=cmd,
            sourceType=cmd_lang,
            optionBox=True,
            subMenu=False,
        )
        items.append(item)

        tooltip = const.CREATE_CAMERA_TOOLTIP.format(name='')
        cmd = const.CREATE_CAMERA_CMD.format(name='')
        cmd_lang = const.CREATE_CAMERA_CMD_LANG
        label = 'Create Camera'
        item = maya.cmds.menuItem(
            parent=parent,
            label=label,
            annotation=tooltip,
            command=cmd,
            sourceType=cmd_lang,
            subMenu=False,
        )
        items.append(item)

        image_plane_nodes = lib.get_camera_image_planes(
            node)
        items += _create_image_plane_menu_items(
            parent,
            node,
            image_plane_nodes)

        lens_nodes = lib.get_camera_lens_nodes(
            node)
        items += _create_lens_menu_items(
            parent,
            node,
            lens_nodes)

    return items
