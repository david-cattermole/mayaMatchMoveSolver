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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.createlens.lib as createlens_lib

LOG = mmSolver.logger.get_logger()


def create_lens(camera_shape_node):
    """Create a new lens on the top of any existing lenses."""
    cam = mmapi.Camera(shape=camera_shape_node)
    lens = createlens_lib.add_lens_layer_on_camera(cam)
    return lens


def get_camera_lens_nodes(camera_shape_node):
    nodes = []

    cam = mmapi.Camera(shape=camera_shape_node)
    lens = cam.get_lens()
    if lens is None:
        return nodes

    lenses = [lens]
    while lens.get_node() is not None:
        input_node = lens.get_input_node()
        if input_node is None:
            break
        lens = mmapi.Lens(node=input_node)
        lenses.append(lens)

    nodes = [x.get_node() for x in lenses if x.get_node()]
    return nodes


def lens_node_enabled(lens_node):
    lens = mmapi.Lens(node=lens_node)
    return bool(lens.get_enable())


def toggle_lens_enabled(lens_node=None):
    assert lens_node is not None
    lens = mmapi.Lens(node=lens_node)
    enabled = lens.get_enable()
    lens.set_enable(not enabled)
