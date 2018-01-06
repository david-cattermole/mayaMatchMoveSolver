"""
Marker and the related objects, Camera and Bundle.
"""

import maya.OpenMaya as Opavailablemport maya.cmds

import mmSolver._api.utils as api_utils
import mmSolver._api.excep as excep
import mmSolver._api.bundle
import mmSolver._api.camera as camera
import mmSolver._api.markergroup as markergroup


class Marker(object):
    """
    The 2D Marker object.
    """
    def __init__(self, name=None):
        if isinstance(name, (str, unicode)):
            dag = api_utils.get_as_dag_path(name)
            self._mfn = OpenMaya.MFnDagNode(dag)
        else:
            self._mfn = OpenMaya.MFnDagNode()
        return

    def get_node(self):
        """
        Get the Maya node this object is bound to.

        :return: The node this Marker object is bound to, or None.
        :rtype: None or str or unicode
        """
        node = None
        try:
            obj = self._mfn.object()
        except RuntimeError:
            obj = None
        if obj is not None and obj.isNull() is False:
            try:
                node = self._mfn.fullPathName()
            except RuntimeError:
                pass
        if isinstance(node, (str, unicode)) and len(node) == 0:
            node = None
        return node

    def set_node(self, name):
        assert isinstance(name, (str, unicode))
        dag = api_utils.get_as_dag_path(name)
        try:
            self._mfn = OpenMaya.MFnDagNode(dag)
        except RuntimeError:
            raise
        return

    ############################################################################

    def create_node(self,
                    name='marker1',
                    colour=None,
                    cam=None,
                    mkr_grp=None,
                    bnd=None):
        assert isinstance(name, (str, unicode))
        if cam is not None:
            if mkr_grp is not None:
                raise excep.NotValid('Cannot specify both camera and marker group, please choose only 1.')
            assert isinstance(cam, camera.Camera)
        if mkr_grp is not None:
            if cam is not None:
                raise excep.NotValid('Cannot specify both camera and marker group, please choose only 1.')
            assert isinstance(mkr_grp, markergroup.MarkerGroup)
        if bnd is not None:
            assert isinstance(bnd, mmSolver._api.bundle.Bundle)
        if colour is not None:
            assert isinstance(colour, str)

        # Transform
        tfm = maya.cmds.createNode('transform', name=name)
        tfm = api_utils.get_long_name(tfm)
        maya.cmds.setAttr(tfm + '.tz', -1.0)
        maya.cmds.setAttr(tfm + '.tz', lock=True)
        maya.cmds.setAttr(tfm + '.rx', lock=True)
        maya.cmds.setAttr(tfm + '.ry', lock=True)
        maya.cmds.setAttr(tfm + '.rz', lock=True)
        maya.cmds.setAttr(tfm + '.sx', lock=True)
        maya.cmds.setAttr(tfm + '.sy', lock=True)
        maya.cmds.setAttr(tfm + '.sz', lock=True)
        maya.cmds.setAttr(tfm + '.tz', keyable=False, channelBox=False)
        maya.cmds.setAttr(tfm + '.rx', keyable=False, channelBox=False)
        maya.cmds.setAttr(tfm + '.ry', keyable=False, channelBox=False)
        maya.cmds.setAttr(tfm + '.rz', keyable=False, channelBox=False)
        maya.cmds.setAttr(tfm + '.sx', keyable=False, channelBox=False)
        maya.cmds.setAttr(tfm + '.sy', keyable=False, channelBox=False)
        maya.cmds.setAttr(tfm + '.sz', keyable=False, channelBox=False)

        # Shape Node
        shp_name = tfm.rpartition('|')[-1] + 'Shape'
        shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)
        maya.cmds.setAttr(shp + '.localScaleX', 0.01)
        maya.cmds.setAttr(shp + '.localScaleY', 0.01)
        maya.cmds.setAttr(shp + '.localScaleZ', 0.0)
        maya.cmds.setAttr(shp + '.localScaleZ', lock=True)

        # Add attrs
        maya.cmds.addAttr(tfm, longName='enable', at='short',
                          minValue=0,
                          maxValue=1,
                          defaultValue=1)
        maya.cmds.addAttr(tfm, longName='weight', at='double',
                          minValue=0.0,
                          defaultValue=1.0)
        maya.cmds.addAttr(tfm, longName='bundle', at='message')
        maya.cmds.addAttr(tfm, longName='markerName', dt='string')

        maya.cmds.setAttr(tfm + '.enable', keyable=True, channelBox=True)
        maya.cmds.setAttr(tfm + '.weight', keyable=True, channelBox=True)
        maya.cmds.setAttr(tfm + '.markerName', lock=True)
        maya.cmds.connectAttr(tfm + '.enable', tfm + '.lodVisibility')

        self.set_node(tfm)

        # Link to Camera
        if cam is not None:
            self.set_camera(cam)

        # Link to MarkerGroup
        if mkr_grp is not None:
            self.set_marker_group(mkr_grp)

        # Link to Bundle
        if bnd is not None:
            self.set_bundle(bnd)

        return self

    def delete_node(self):
        node = self.get_node()
        maya.cmds.delete(node)
        return self

    ############################################################################

    # def get_node_colour(self):
    #     pass

    # def set_node_colour(self, name):
    #     # TODO: should we allow RGB values directly?
    #     # TODO: Look up the colour value from a string.
    #     pass

    ############################################################################

    def get_bundle(self):
        bnd = None
        node = self.get_node()
        if node is not None:
            assert maya.cmds.objExists(node)
            bnd_node = None
            bnd_nodes = maya.cmds.listConnections(node + '.bundle') or []
            if len(bnd_nodes) > 0:
                bnd_node = bnd_nodes[0]
            if bnd_node is not None and len(bnd_node) > 0:
                bnd = mmSolver._api.bundle.Bundle(bnd_node)
        return bnd

    def set_bundle(self, bnd):
        if bnd is None:
            self._unlink_from_bundle()
        elif isinstance(bnd, mmSolver._api.bundle.Bundle):
            self._link_to_bundle(bnd)
        return

    def _link_to_bundle(self, bnd):
        # output message to marker.bundle attr
        assert isinstance(bnd, mmSolver._api.bundle.Bundle)

        bnd_node = bnd.get_node()
        assert isinstance(bnd_node, (str, unicode))
        assert maya.cmds.objExists(bnd_node)

        mkr_node = self.get_node()
        assert isinstance(mkr_node, (str, unicode))
        assert maya.cmds.objExists(mkr_node)

        attr_name = 'bundle'
        attr_names = maya.cmds.listAttr(mkr_node)
        if attr_name not in attr_names:
            maya.cmds.addAttr(mkr_node, longName=attr_name, at='message')

        src = bnd_node+'.message'
        dst = mkr_node + '.' + attr_name
        if not maya.cmds.isConnected(src, dst):
            maya.cmds.connectAttr(src, dst)
        else:
            msg = 'Marker and Bundle are already linked; '
            msg += 'marker={0}, bundle={1}'
            msg = msg.format(repr(mkr_node), repr(bnd_node))
            raise excep.AlreadyLinked(msg)
        return

    def _unlink_from_bundle(self):
        bnd = self.get_bundle()
        mkr_node = self.get_node()
        bnd_node = bnd.get_node()

        src = bnd_node + '.message'
        dst = mkr_node + '.bundle'
        if maya.cmds.isConnected(src, dst):
            maya.cmds.disconnectAttr(src, dst)
        return

    ############################################################################

    def get_camera(self):
        mkr_node = self.get_node()

        cam_tfm, cam_shp = api_utils.get_camera_above_node(mkr_node)

        # Make the camera object.
        cam = None
        if cam_tfm is not None and cam_shp is not None:
            cam = camera.Camera(transform=cam_tfm, shape=cam_shp)
        return cam

    def set_camera(self, cam):
        if cam is None:
            self._unlink_from_camera()
        elif isinstance(cam, camera.Camera):
            self._link_to_camera(cam)
        return

    def _link_to_camera(self, cam):
        """
        Parent a marker under the marker group which is under the given camera.
        If there is no marker group, one is created.
        """
        assert isinstance(cam, camera.Camera)

        mkr_node = self.get_node()
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        # Make sure the camera is valid for us to link to.
        if cam.is_valid() is False:
            msg = 'Cannot link Marker to Camera; Camera is not valid.'
            msg += ' marker={0} camera={1}'
            msg = msg.format(repr(mkr_node), repr(cam_shp))
            raise excep.NotValid(msg)

        # Check if we're trying to link the the camera that we're already
        # linked to.
        current_cam = self.get_camera()
        if current_cam is not None:
            assert isinstance(current_cam, camera.Camera)
            current_cam_shp = current_cam.get_shape_node()
            if current_cam_shp == cam_shp:
                msg = 'Marker is already linked to camera, skipping.'
                msg += ' marker={0} camera={1}'
                msg = msg.format(repr(mkr_node), repr(cam_shp))
                raise excep.AlreadyLinked(msg)

        # Create Marker Group
        mkr_grp = None
        mkr_grp_nodes = maya.cmds.ls(cam_tfm, dag=True, long=True,
                                     type='mmMarkerGroupTransform') or []
        mkr_grp_nodes = sorted(mkr_grp_nodes)
        if len(mkr_grp_nodes) == 0:
            mkr_grp = markergroup.MarkerGroup().create_node(cam=cam)
        else:
            mkr_grp = markergroup.MarkerGroup(name=mkr_grp_nodes[0])

        # Link to Marker Group
        self.set_marker_group(mkr_grp)
        return

    def _unlink_from_camera(self):
        """
        Re-parent the current marker to the world; it will live under no camera.
        """
        mkr_node = self.get_node()
        cam = self.get_camera()
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()
        if ((cam_tfm is None) or
                (cam_shp is None) or
                (maya.cmds.objExists(cam_tfm) is False) or
                (maya.cmds.objExists(cam_shp) is False)):
            msg = 'Marker is already unlinked from all cameras, skipping.'
            msg += ' marker={0} camera={1}'
            msg = msg.format(repr(mkr_node), repr(cam_shp))
            raise excep.AlreadyUnlinked(msg)

        # Move the marker under the world root, don't modify the marker in
        # any way otherwise (so we use 'relative' flag).
        maya.cmds.parent(mkr_node, relative=True, world=True)
        pass

    ############################################################################

    def get_marker_group(self):
        mkr_node = self.get_node()

        mkr_grp_node = api_utils.get_marker_group_above_node(mkr_node)

        # Make the marker group object.
        mkr_grp = None
        if mkr_grp_node is not None:
            mkr_grp = markergroup.MarkerGroup(name=mkr_grp_node)
        return mkr_grp

    def set_marker_group(self, mkr_grp):
        if mkr_grp is None:
            self._unlink_from_marker_group()
        elif isinstance(mkr_grp, markergroup.MarkerGroup):
            self._link_to_marker_group(mkr_grp)
        return

    def _link_to_marker_group(self, mkr_grp):
        """
        Parent a marker under a Marker Group.
        """
        assert isinstance(mkr_grp, markergroup.MarkerGroup)

        mkr_node = self.get_node()
        mkr_grp_node = mkr_grp.get_node()

        # Make sure the camera is valid for us to link to.
        if mkr_grp.is_valid() is False:
            msg = 'Cannot link Marker to Marker Group; Marker Group is not valid.'
            msg += ' marker={0} marker group={1}'
            msg = msg.format(repr(mkr_node), repr(mkr_grp_node))
            raise excep.NotValid(msg)

        # Check if we're trying to link the the camera that we're already
        # linked to.
        current_mkr_grp = self.get_marker_group()
        if current_mkr_grp is not None:
            assert isinstance(current_mkr_grp, markergroup.MarkerGroup)
            current_mkr_grp = current_mkr_grp.get_node()
            if current_mkr_grp == mkr_grp_node:
                msg = 'Marker is already linked to Marker Group, skipping.'
                msg += ' marker={0} marker group={1}'
                msg = msg.format(repr(mkr_node), repr(mkr_grp_node))
                raise excep.AlreadyLinked(msg)

        # Move the marker under the marker group, make sure the relative
        # marker attribute values are maintained.
        maya.cmds.parent(mkr_node, mkr_grp_node, relative=True)
        return

    def _unlink_from_marker_group(self):
        """
        Re-parent the current marker to the world; it will live under no
        """
        mkr_node = self.get_node()
        cam = self.get_camera()
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()
        if ((cam_tfm is None) or
                (cam_shp is None) or
                (maya.cmds.objExists(cam_tfm) is False) or
                (maya.cmds.objExists(cam_shp) is False)):
            msg = 'Marker is already unlinked from all cameras, skipping.'
            msg += ' marker={0} camera={1}'
            msg = msg.format(repr(mkr_node), repr(cam_shp))
            raise excep.AlreadyUnlinked(msg)

        # Move the marker under the world root, don't modify the marker in
        # any way otherwise.
        maya.cmds.parent(mkr_node, relative=True, world=True)
        pass
