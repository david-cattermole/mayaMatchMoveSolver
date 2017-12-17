
import maya.cmds

import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filternodes


def get_bundles_from_markers(nodes):
    mkr_nodes = filternodes.get_marker_nodes(nodes)
    bnd_nodes = []
    for mkr_node in mkr_nodes:
        mkr = mmapi.Marker(mkr_node)
        bnd = mkr.get_bundle()
        bnd_node = bnd.get_node()
        if bnd_node not in bnd_nodes:
            bnd_nodes.append(bnd_node)
    return bnd_nodes


def get_markers_from_bundles(nodes):
    bnd_nodes = filternodes.get_bundle_nodes(nodes)
    mkr_nodes = []
    for bnd_node in bnd_nodes:
        bnd = mmapi.Bundle(bnd_node)
        mkr_list = bnd.get_marker_list()
        for mkr in mkr_list:
            mkr_node = mkr.get_node()
            if mkr_node not in mkr_nodes:
                mkr_nodes.append(mkr_node)
    return mkr_nodes


def get_cameras_from_markers(nodes):
    mkr_nodes = filternodes.get_marker_nodes(nodes)
    cam_nodes = []
    cam_nodes_tmp = {}
    for mkr_node in mkr_nodes:
        mkr = mmapi.Marker(mkr_node)
        cam = mkr.get_camera()
        cam_tfm_node = cam.get_transform_node()
        cam_shp_node = cam.get_shape_node()
        if cam_shp_node not in cam_nodes_tmp:
            cam_nodes_tmp[cam_shp_node] = (cam_tfm_node, cam_shp_node)
    for key, value in cam_nodes_tmp.iteritems():
        cam_nodes.append(value)
    return cam_nodes
