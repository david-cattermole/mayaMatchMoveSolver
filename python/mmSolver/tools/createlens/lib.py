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
Library functions for creating and modifying Lenses.


Use Case::

1) Select a camera.

2) Add a Lens node to the camera.

   - This will convert the image plane(s) to polygons.

   - This will convert the markers to be undistorted.

3) Solve the lens distortion.

4) Select Camera, switch to 'distorted' mode.

   - The Markers under the camera are now distorted.

   - When solving a lens node, the lens model is always turned on
     before solving.

5) Change the Marker positions however needed.

6) Solve the lens distortion.

   - Lens distortion is automatically turned on before solving.

"""

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.node as node_utils

LOG = mmSolver.logger.get_logger()


def create_marker_connections(cam):
    """
    Create connections between the camera and markers.

    Adds a special lens attribute to the camera. This dynamic lens
    attribute will fan-out and connect to each Marker as needed.
    """
    assert isinstance(cam, mmapi.Camera)

    # Get all markers under the camera.
    mkr_list = cam.get_marker_list()
    mkr_nodes = [mkr.get_node() for mkr in mkr_list]

    for mkr_node in mkr_nodes:
        dst = mkr_node + '.inLens'
        conns = (
            maya.cmds.listConnections(
                dst,
                source=True,
                destination=False,
                connections=True,
                plugs=True,
            )
            or []
        )
        src_list = conns[1::2]
        dst_list = conns[0::2]
        for src, dst in zip(src_list, dst_list):
            maya.cmds.disconnectAttr(src, dst)

    cam_shp = cam.get_shape_node()
    in_lens_attr_exists = node_utils.attribute_exists('inLens', cam_shp)
    if in_lens_attr_exists is False:
        LOG.warn(
            'Cannot create marker connections, camera is missing "inLens" attribute; '
            'cam_shp=%r',
            cam_shp,
        )
        return

    # Ensure Marker have connections to the camera lens.
    src = cam_shp + '.outLens'
    for mkr_node in mkr_nodes:
        dst = mkr_node + '.inLens'
        if not maya.cmds.isConnected(src, dst):
            maya.cmds.connectAttr(src, dst)
    return


def create_lens_on_camera(cam, force_create_new=None):
    """
    Create a lens node and connect it to the given camera.

    :param cam: The camera to create a lens for.
    :type cam: mmSolver.api.Camera

    :param force_create_new: Should the function create a new lens
        node, even if a node already exists?
    :type force_create_new: bool or None

    :rtype: mmSolver.api.Lens
    """
    assert isinstance(cam, mmapi.Camera)
    if force_create_new is None:
        force_create_new = False
    assert isinstance(force_create_new, bool)
    create_marker_connections(cam)
    lens = cam.get_lens()
    if lens is None or force_create_new is True:
        lens = mmapi.Lens().create_node()
        cam.set_lens(lens)
    return lens


def add_lens_layer_on_camera(cam):
    """
    Create a new lens node as a 'layer' on the the given camera.

    :param cam: The camera to create a lens for.
    :type cam: mmSolver.api.Camera

    :rtype: mmSolver.api.Lens
    """
    assert isinstance(cam, mmapi.Camera)
    create_marker_connections(cam)
    lens = None
    existing_lens = cam.get_lens()
    if existing_lens is None:
        lens = mmapi.Lens().create_node()
        cam.set_lens(lens)
    else:
        assert isinstance(cam, mmapi.Camera)
        lens = mmapi.Lens().create_node()
        cam.set_lens(lens)
        lens.set_input_lens(existing_lens)
    return lens
