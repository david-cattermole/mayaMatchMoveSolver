"""
Marker utilities functions; Raw computations to be used without the Marker class.
"""

import math
import maya.cmds
import mmSolver.logger


LOG = mmSolver.logger.get_logger()


def calculate_marker_deviation(mkr_node,
                               bnd_node,
                               cam_tfm, cam_shp,
                               times,
                               image_width,
                               image_height):
    """
    Calculate the 2D-to-3D pixel distance for the given marker.

    :param mkr_node: The marker transform node to compute with.
    :type mkr_node: str
    
    :param bnd_node: The bundle transform node to compute with.
    :type bnd_node: str

    :param cam_tfm: The camera transform node to compute with.
    :type cam_tfm: str

    :param cam_shp: The camera shape node to compute with.
    :type cam_shp: str
    
    :param times: The times to query the deviation.
    :type times: [float, ..]

    :param image_width: The width of the matchmove image plate.
    :type image_width: float
    
    :param image_height: The height of the matchmove image plate.
    :type image_height: float

    :returns: List of pixel deviation values for given times.
    :rtype: [float, ..]
    """
    dev = [None] * len(times)

    # Compute the pixel values.
    mkr_pos = maya.cmds.mmReprojection(
        mkr_node,
        camera=(cam_tfm, cam_shp),
        time=times,
        imageResolution=(image_width, image_height),
        asPixelCoordinate=True,
    )
    bnd_pos = maya.cmds.mmReprojection(
        bnd_node,
        camera=(cam_tfm, cam_shp),
        time=times,
        imageResolution=(image_width, image_height),
        asPixelCoordinate=True,
    )
    assert len(mkr_pos) == len(bnd_pos)

    # 2D Distance
    mkr_x = mkr_pos[0:len(mkr_pos):3]
    mkr_y = mkr_pos[1:len(mkr_pos):3]
    bnd_x = bnd_pos[0:len(mkr_pos):3]
    bnd_y = bnd_pos[1:len(mkr_pos):3]
    for i, (mx, my, bx, by) in enumerate(zip(mkr_x, mkr_y, bnd_x, bnd_y)):
        dx = mx - bx
        dy = my - by
        dev[i] = math.sqrt((dx * dx) + (dy * dy))
        
    return dev
