"""
This tool averages markers position from selected markers.
"""

import maya.cmds
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.logger
import mmSolver.tools.createmarker.tool
import maya.mel
import mmSolver.api as mmapi

LOG = mmSolver.logger.get_logger()


def average_marker():
    """
    Averages marker position from selected markers.
    :return: None
    """

    selection = maya.cmds.ls(sl=True)

    selected_markers = filternodes.get_marker_nodes(selection)

    if not selected_markers:
        LOG.warning('Please select more than 2 markers ')
        return

    if len(selected_markers) < 2:
        LOG.warning('Please select more than 2 markers')
        return

    mkr_selection = selected_markers[0]
    mkr = mmapi.Marker(name=mkr_selection)
    # getting camera from the selected marker
    cam_from_mkr = mkr.get_camera()
    mkr_name = mmapi.get_marker_name('marker1')
    new_mkr = mmapi.Marker().create_node(cam=cam_from_mkr,
                                         name=mkr_name)

    new_mkr_node = new_mkr.get_node()
    bnd_name = mmapi.get_bundle_name('bundle1')
    new_bnd = mmapi.Bundle().create_node(name=bnd_name)
    # connecting bundle to the marker
    new_mkr.set_bundle(new_bnd)
    # getting first frame and last frame from the selected markers
    first_frame = []
    last_frame = []
    for marker in selected_markers:
        plugs = [
            '%s.translateX' % marker,
            '%s.translateY' % marker,
        ]
        plug_lock_state = {}
        for plug_name in plugs:
            value = maya.cmds.getAttr(plug_name, lock=True)
            plug_lock_state[plug_name] = value
            maya.cmds.setAttr(plug_name, lock=False)

        first = maya.cmds.findKeyframe(marker, which='first')
        first_frame.append(first)

        last = maya.cmds.findKeyframe(marker, which='last')
        last_frame.append(last)

        for plug_name in plugs:
            value = plug_lock_state.get(plug_name)
            maya.cmds.setAttr(plug_name, lock=value)

    start_frame = max(first_frame)
    end_frame = min(last_frame)

    # Running average from selected markers for giving frame range
    for frame in range(int(start_frame), int(end_frame) + 1):
        count = len(selected_markers)
        sums = [0, 0]

        for item in selected_markers:
            pos_x = maya.cmds.getAttr('%s.translateX' % item,
                                      time=frame)

            pos_y = maya.cmds.getAttr('%s.translateY' % item,
                                      time=frame)
            sums[0] += pos_x
            sums[1] += pos_y
            center = [sums[0] / count, sums[1] / count]

            maya.cmds.setKeyframe('%s.translateX' % new_mkr_node,
                                  v=center[0], time=frame)

            maya.cmds.setKeyframe('%s.translateY' % new_mkr_node,
                                  v=center[1], time=frame)

    maya.cmds.select(new_mkr_node)
    # dgdirty for Channel box value update
    maya.cmds.dgdirty(new_mkr_node)
    return None
