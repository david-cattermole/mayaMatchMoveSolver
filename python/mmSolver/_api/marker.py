"""
Marker and the related objects, Camera and Bundle.
"""

import maya.OpenMaya as OpenMaya
import maya.cmds

import mmSolver._api.utils as api_utils
import mmSolver._api.bundle
import mmSolver._api.camera


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
                    bnd=None):
        assert isinstance(name, (str, unicode))
        if cam is not None:
            assert isinstance(cam, mmSolver._api.camera.Camera)
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

        # Shape Node
        shp_name = tfm.rpartition('|')[-1] + 'Shape'
        shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)
        maya.cmds.setAttr(shp + '.localScaleZ', 0.0)
        maya.cmds.setAttr(shp + '.localScaleZ', lock=True)

        # Add attrs
        maya.cmds.addAttr(tfm, longName='enable', at='bool',
                          defaultValue=True)
        maya.cmds.addAttr(tfm, longName='weight', at='double',
                          minValue=0.0, defaultValue=1.0)
        maya.cmds.addAttr(tfm, longName='bundle', at='message')

        self.set_node(tfm)

        # Link to Camera
        if cam is not None:
            self.set_camera(cam)

        # Link to Bundle
        if bnd is not None:
            self.set_bundle(bnd)

        return self

    def convert_to_node(self):
        # TODO: Is this needed???
        # TODO: This function will convert a ordanary node into a marker. It
        # will:
        # - Add custom attributes.
        pass

    def delete_node(self):
        node = self.get_node()
        maya.cmds.delete(node)
        return self

    def get_node_colour(self):
        pass

    def set_node_colour(self, name):
        # TODO: should we allow RGB values directly?
        # TODO: Look up the colour value from a string.
        pass

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
            # TODO: Should we raise instead of printing a warning?
            msg = 'Marker and Bundle are already linked; '
            msg += 'marker={0}, bundle={1}'
            maya.cmds.warning(msg.format(repr(mkr_node), repr(bnd_node)))
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
            cam = mmSolver._api.camera.Camera(transform=cam_tfm, shape=cam_shp)
        return cam

    def set_camera(self, cam):
        if cam is None:
            self._unlink_from_camera()
        elif isinstance(cam, mmSolver._api.camera.Camera):
            self._link_to_camera(cam)
        return

    def _link_to_camera(self, cam):
        """
        Parent a marker under a
        If a 'markerGroup' node exists, we parent under than too.
        """
        assert isinstance(cam, mmSolver._api.camera.Camera)

        mkr_node = self.get_node()
        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        # Make sure the camera is valid for us to link to.
        if cam.is_valid() is False:
            # TODO: Should we use warnings? Or should we raise exceptions?
            msg = 'Cannot link Marker to Camera; Camera is not valid.'
            msg += ' marker={0} camera={1}'
            maya.cmds.warning(msg.format(repr(mkr_node), repr(cam_shp)))
            return

        # Check if we're trying to link the the camera that we're already
        # linked to.
        current_cam = self.get_camera()
        if current_cam is not None:
            assert isinstance(current_cam, mmSolver._api.camera.Camera)
            current_cam_shp = current_cam.get_shape_node()
            if current_cam_shp == cam_shp:
                # TODO: Should we use warnings? Or should we raise exceptions?
                msg = 'Marker is already linked to camera, skipping.'
                msg += ' marker={0} camera={1}'
                maya.cmds.warning(msg.format(repr(mkr_node), repr(cam_shp)))
                return

        # TODO: Find any 'markerGroup' nodes under the camera transform, parent
        # the marker under that node instead of the camera transform.

        # Move the marker under the camera transform, make sure the relative
        # marker attribute values are maintained.
        maya.cmds.parent(mkr_node, cam_tfm, relative=True)
        return

    def _unlink_from_camera(self):
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
            # TODO: Should we use warnings? Or should we raise exceptions?
            msg = 'Marker is already unlinked from all cameras, skipping.'
            msg += ' marker={0} camera={1}'
            maya.cmds.warning(msg.format(repr(mkr_node), repr(cam_shp)))
            return

        # Move the marker under the world root, don't modify the marker in
        # any way otherwise.
        maya.cmds.parent(mkr_node, cam_tfm, relative=True, world=True)
        pass
