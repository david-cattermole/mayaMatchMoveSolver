"""
Convert a transform into a screen-space transform.
"""

import itertools

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.utils.viewport as viewport_utils
import mmSolver.utils.time as utils_time
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.screenzbake.lib as lib


LOG = mmSolver.logger.get_logger()


def main():
    """
    Screen-Space Bake.

    Usage:

    1) Select transform nodes.
    2) Activate viewport.
    3) Run tool.
    4) A new locator is created under the active camera
    """
    mmapi.load_plugin()

    editor = viewport_utils.get_active_model_editor()
    if editor is None:
        LOG.error('Please select an active viewport; editor=%r', editor)
        return
    cam_tfm, cam_shp = viewport_utils.get_viewport_camera(editor)
    if cam_tfm is None or cam_shp is None:
        LOG.error('Please select a camera; cam_tfm=%r cam_shp=%r', cam_tfm, cam_shp)
        return
    cam = mmapi.Camera(transform=cam_tfm, shape=cam_shp)
    img_width = maya.cmds.getAttr(cam_shp + '.horizontalFilmAperture') * 100.0
    img_height = maya.cmds.getAttr(cam_shp + '.verticalFilmAperture') * 100.0

    nodes = maya.cmds.ls(
        selection=True,
        long=True,
        type='transform'
    ) or []
    if len(nodes) == 0:
        LOG.error('Please select transform nodes; %r', nodes)
        return

    start_frame, end_frame = utils_time.get_maya_timeline_range_inner()
    times = range(start_frame, end_frame+1)

    for node in nodes:
        grp_node, depth_tfm, loc_tfm, loc_shp = lib.createScreenSpaceLocator(cam)

        values = maya.cmds.mmReprojection(
            node,
            camera=(cam_tfm, cam_shp),
            time=times,
            asMarkerCoordinate=True,
            imageResolution=(int(img_width), int(img_height)),
        )
        LOG.warning('len(values)=%r', len(values))
        LOG.warning('values=%r', values)
        stop = len(values)
        step = 3

        plug = loc_tfm + '.translateX'
        values_x = values[0:stop:step]
        LOG.warning('len(values_x)=%r', len(values_x))
        LOG.warning('values_x=%r', values_x)
        animfn_x = mmapi.create_anim_curve_node(
            times, values_x,
            node_attr=plug
        )

        plug = loc_tfm + '.translateY'
        values_y = values[1:stop:step]
        LOG.warning('len(values_y)=%r', len(values_y))
        LOG.warning('values_y=%r', values_y)
        animfn_y = mmapi.create_anim_curve_node(
            times, values_y,
            node_attr=plug
        )

        plug = depth_tfm + '.scaleX'
        values_z = values[2:stop:step]
        LOG.warning('len(values_z)=%r', len(values_z))
        LOG.warning('values_z=%r', values_z)
        animfn_z = mmapi.create_anim_curve_node(
            times, values_z,
            node_attr=plug
        )
    return
