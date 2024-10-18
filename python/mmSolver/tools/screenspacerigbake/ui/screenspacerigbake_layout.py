# Copyright (C) 2020, 2022 Patcha Saheb Binginapalli.
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

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as cmds
import maya.mel as mel

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.constant as const_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.ui.helputils as helputils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.tools.screenspacerigbake.constant as const
import mmSolver.tools.screenspacerigbake.ui.ui_screenspacerigbake_layout as ui_layout
import mmSolver.tools.loadmarker.lib.utils as cam_lib
import mmSolver.tools.attributebake.lib as fastbake_lib

LOG = mmSolver.logger.get_logger()


def transform_has_constraints(tfm_node):
    constraints = (
        cmds.listRelatives(tfm_node, children=True, type='pointConstraint') or []
    )
    constraints += (
        cmds.listRelatives(tfm_node, children=True, type='parentConstraint') or []
    )
    has_constraints = len(constraints) > 0
    return has_constraints


def set_z_depth_keyframes(node, start_frame, end_frame, values, anim_layer_name=None):
    kwargs = {}
    if anim_layer_name is not None:
        kwargs = {'animLayer': anim_layer_name}

    frames = range(start_frame, end_frame + 1)
    for i, frame in enumerate(frames):
        oma.MAnimControl.setCurrentTime(om.MTime(frame))
        cmds.setKeyframe(
            node, attribute=const.SCREEN_Z_DEPTH_ATTR_NAME, value=values[i], **kwargs
        )
    return


def _open_help():
    src = helputils.get_help_source()
    # TODO: Add correct URL.
    page = 'tools_attributetools.html#attribute-bake'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


class ScreenSpaceRigBakeLayout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(ScreenSpaceRigBakeLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.options_menu = self.menu_bar.addMenu('Freeze')
        self.refresh_menu = self.menu_bar.addMenu('Refresh')

        # Freeze options actions
        self.animlayer_action = QtWidgets.QAction('Add to AnimLayer', self)
        self.animlayer_action.setCheckable(True)
        self.options_menu.addAction(self.animlayer_action)
        self.options_menu.addSeparator()
        self.freeze_action_group = QtWidgets.QActionGroup(self.options_menu)

        self.camera_space_action = QtWidgets.QAction('Freeze in Camera Space', self)
        self.camera_space_action.setCheckable(True)
        self.options_menu.addAction(self.camera_space_action)
        self.camera_space_action.setActionGroup(self.freeze_action_group)

        self.world_space_action = QtWidgets.QAction('Freeze in World Space', self)
        self.world_space_action.setCheckable(True)
        self.world_space_action.setChecked(True)
        self.options_menu.addAction(self.world_space_action)
        self.world_space_action.setActionGroup(self.freeze_action_group)

        # Refresh action
        self.refresh_action = QtWidgets.QAction('Refresh Rigs List', self)
        self.refresh_menu.addAction(self.refresh_action)

        # Help menu
        help_menu = QtWidgets.QMenu('Help', self.menu_bar)
        commonmenus.create_help_menu_items(help_menu, tool_help_func=_open_help)

        # Add menus
        self.menu_bar.addMenu(self.options_menu)
        self.menu_bar.addMenu(self.refresh_menu)
        self.menu_bar.addMenu(help_menu)

        # Cache the icon.
        self.transform_icon = QtGui.QIcon(':transform.svg')

        self.create_connections()
        self.refresh_rigsList()
        self.populate_ui()

    def create_connections(self):
        # Button clicked
        self.createScreenSpaceRigButton.clicked.connect(
            self.create_screen_space_rig_clicked
        )
        self.matchScreenZDepthButton.clicked.connect(self.match)
        self.createFreezeRigButton.clicked.connect(self.create_freeze_rig_clicked)
        self.bakeRigButton.clicked.connect(self.bake_rig_clicked)
        self.deleteRigButton.clicked.connect(self.delete_rig_clicked)
        self.selectInOutlinerButton.clicked.connect(self.select_in_outliner_clicked)

        # Menu action triggered
        self.refresh_action.triggered.connect(self.refresh_rigsList)
        self.animlayer_action.triggered.connect(self.freeze_options_update)
        self.world_space_action.triggered.connect(self.freeze_options_update)
        self.camera_space_action.triggered.connect(self.freeze_options_update)
        self.nameLineEdit.editingFinished.connect(self.clear_focus)

    def populate_ui(self):
        # Add camera items
        all_camera_nodes = cam_lib.get_cameras()
        active_camera = cam_lib.get_active_viewport_camera()
        for cam in all_camera_nodes:
            cam_tfm = cam.get_transform_node()
            self.cameraListComboBox.addItem(str(cam_tfm))
        if active_camera:
            active_camera_tfm = active_camera.get_transform_node()
            for count, cam in enumerate(all_camera_nodes):
                if cam.get_transform_node() == active_camera_tfm:
                    self.cameraListComboBox.setCurrentIndex(count)
                    break
        return

    def get_vp_camera(self):
        cam_tfm = self.cameraListComboBox.currentText() or None
        return cam_tfm

    def select_in_outliner_clicked(self):
        selected_items = self.rigsList.selectedItems()
        if len(selected_items) == 0:
            LOG.warn('Atleast one rig must be selected from UI.')
            return
        cmds.select(clear=True)
        for item in selected_items:
            name = item.text(0)
            cmds.select(name, add=True)
        return

    def refresh_rigsList(self):
        self.rigsList.clear()
        mItDag = om.MItDag(om.MItDag.kDepthFirst, om.MFn.kTransform)
        while not mItDag.isDone():
            depNode = om.MFnDependencyNode(mItDag.currentItem())
            if depNode.hasAttribute(const.ATTRIBUTE_IDENTIFIER_NAME):
                name = depNode.name()
                item = self.create_item(name)
                self.rigsList.addTopLevelItem(item)
                mItDag.prune()
            mItDag.next()
        top_level_item_count = self.rigsList.topLevelItemCount()
        for i in range(top_level_item_count + 1):
            top_level_item = self.rigsList.topLevelItem(i)
            if top_level_item:
                top_level_item.setExpanded(True)

    def create_item(self, name):
        item = QtWidgets.QTreeWidgetItem([name])
        self.add_children(item)
        item.setIcon(0, self.transform_icon)
        return item

    def add_children(self, item):
        children = cmds.listRelatives(item.text(0), c=True) or []
        for child in children:
            if const.ATTRIBUTE_IDENTIFIER_NAME in cmds.listAttr(child):
                child_item = self.create_item(child)
                item.addChild(child_item)
        return

    def freeze_options_update(self):
        if self.world_space_action.isChecked():
            self.animlayer_action.setEnabled(True)
        else:
            self.animlayer_action.setEnabled(False)
            self.animlayer_action.setChecked(False)
        return

    def clear_focus(self):
        self.nameLineEdit.clearFocus()

    def get_bake_options(self):
        bake_options = None
        if self.fullBakeRadioButton.isChecked():
            bake_options = 'full_bake'
        else:
            bake_options = 'smart_bake'
        return bake_options

    def get_prebake_frames_list_from_node(self, node):
        frames_list = []
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        keys_list = cmds.keyframe(node, q=True, time=(start_frame, end_frame)) or []
        if len(keys_list) == 0:
            frames_list = [start_frame, end_frame]
        bake_options = self.get_bake_options()
        if bake_options == 'full_bake':
            for frame in range(start_frame, end_frame + 1):
                if frame not in frames_list:
                    frames_list.append(frame)
        if bake_options == 'smart_bake':
            keys_list = cmds.keyframe(node, q=True, time=(start_frame, end_frame)) or []
            for frame in keys_list:
                if frame not in frames_list:
                    frames_list.append(frame)
        return sorted(frames_list)

    def offset_vector(self, a, b):
        assert isinstance(a, pycompat.TEXT_TYPE)
        assert isinstance(b, pycompat.TEXT_TYPE)
        assert cmds.objExists(a) and cmds.objExists(b)
        a_pos = cmds.xform(a, q=True, ws=True, t=True)
        b_pos = cmds.xform(b, q=True, ws=True, t=True)
        a_vector = om.MVector(a_pos[0], a_pos[1], a_pos[2])
        b_vector = om.MVector(b_pos[0], b_pos[1], b_pos[2])
        length = (b_vector - a_vector).length()
        return length

    def calc_distance(self, cam_tfm, tfm_node, offset):
        """
        Calculate the distance between cam_tfm and tfm_node.

        .. note::
           'offset' is not yet used, but may be implemented in future.
        """
        depth_list = []
        frames_list = self.get_prebake_frames_list_from_node(tfm_node)
        if len(frames_list) > 0:
            current_time = cmds.currentTime(query=True)
            for frame in frames_list:
                oma.MAnimControl.setCurrentTime(om.MTime(float(frame)))
                vector = self.offset_vector(cam_tfm, tfm_node)
                depth_list.append(vector + offset)
            oma.MAnimControl.setCurrentTime(om.MTime(float(current_time)))

        return depth_list

    def create_rig(self, camera, object, dlist, name, rigName):
        ctx = tools_utils.tool_context(
            use_undo_chunk=True,
            restore_current_frame=True,
            use_dg_evaluation_mode=True,
            disable_viewport=True,
            disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE,
        )
        with ctx:
            start_frame, end_frame = time_utils.get_maya_timeline_range_inner()

            # Create main group
            main_grp = cmds.group(empty=True, n=name + rigName)

            # Delete all transform attributes
            attr_list = const.TRANSFORM_ATTR_LIST + ['visibility']
            for attr in attr_list:
                cmds.setAttr(main_grp + '.' + attr, keyable=False, lock=True)

            # Add custom attributes
            cmds.addAttr(main_grp, ln='screenX', nn='Screen X', at='float', k=True)
            cmds.addAttr(main_grp, ln='screenY', nn='Screen Y', at='float', k=True)
            cmds.addAttr(
                main_grp,
                ln=const.SCREEN_Z_DEPTH_ATTR_NAME,
                nn='Screen Z depth',
                at='float',
                k=True,
            )
            cmds.addAttr(
                main_grp,
                ln=const.ATTRIBUTE_IDENTIFIER_NAME,
                nn=const.ATTRIBUTE_IDENTIFIER_NICE_NAME,
                dt='string',
                k=False,
            )
            cmds.setAttr(
                main_grp + '.' + const.ATTRIBUTE_IDENTIFIER_NAME,
                str(object),
                type='string',
            )

            # Set keyframes on screezdepth attribute
            frames_list = self.get_prebake_frames_list_from_node(object)
            for i, frame in enumerate(frames_list):
                cmds.setKeyframe(
                    main_grp, at=const.SCREEN_Z_DEPTH_ATTR_NAME, t=frame, v=dlist[i]
                )

            # Clear name text
            self.nameLineEdit.clear()
            self.nameLineEdit.clearFocus()

            # Create screez master group
            screenz_master_grp = cmds.group(
                em=True, n=name + const.SCREEN_Z_MASTER_NAME
            )
            cmds.setAttr(screenz_master_grp + '.visibility', 0)

            # Add screen X/Y copy attributes
            cmds.addAttr(
                screenz_master_grp, ln='copyScreenX', nn='Screen X copy', at='float'
            )
            cmds.addAttr(
                screenz_master_grp, ln='copyScreenY', nn='Screen Y copy', at='float'
            )
            cmds.setAttr(screenz_master_grp + '.copyScreenX', cb=False)
            cmds.setAttr(screenz_master_grp + '.copyScreenY', cb=False)
            cmds.parent(screenz_master_grp, main_grp)
            con = cmds.parentConstraint(self.get_vp_camera(), screenz_master_grp)
            fastbake_lib.bake_attributes(
                [screenz_master_grp], [], start_frame, end_frame, smart_bake=False
            )
            cmds.delete(con)

            # Create screen Z-depth connections
            cmds.connectAttr(
                main_grp + '.' + const.SCREEN_Z_DEPTH_ATTR_NAME,
                screenz_master_grp + '.scaleX',
                f=True,
            )
            cmds.connectAttr(
                main_grp + '.' + const.SCREEN_Z_DEPTH_ATTR_NAME,
                screenz_master_grp + '.scaleY',
                f=True,
            )
            cmds.connectAttr(
                main_grp + '.' + const.SCREEN_Z_DEPTH_ATTR_NAME,
                screenz_master_grp + '.scaleZ',
                f=True,
            )

            # Create screen X/Y master group
            screen_xy_master_grp = cmds.group(
                em=True, n=name + const.SCREEN_XY_MASTER_NAME
            )
            cmds.setAttr(screen_xy_master_grp + '.visibility', 0)
            attr_list = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'visibility']
            for attr in attr_list:
                cmds.setAttr(
                    screen_xy_master_grp + '.' + attr, keyable=False, lock=True
                )
            cmds.parent(screen_xy_master_grp, screenz_master_grp, r=True)
            con = cmds.pointConstraint(object, screen_xy_master_grp)
            fastbake_lib.bake_attributes(
                [screen_xy_master_grp], [], start_frame, end_frame, smart_bake=False
            )
            cmds.delete(con)
            cmds.setAttr(screen_xy_master_grp + '.translateZ', lock=True)

            # Create screen X/Y connections
            cmds.connectAttr(
                screen_xy_master_grp + '.translateX', main_grp + '.screenX', f=True
            )
            cmds.connectAttr(
                screen_xy_master_grp + '.translateY', main_grp + '.screenY', f=True
            )
            cmds.connectAttr(
                screen_xy_master_grp + '.translateX',
                screenz_master_grp + '.copyScreenX',
                f=True,
            )
            cmds.connectAttr(
                screen_xy_master_grp + '.translateY',
                screenz_master_grp + '.copyScreenY',
                f=True,
            )
            fastbake_lib.bake_attributes(
                [main_grp],
                ['screenX', 'screenY'],
                start_frame,
                end_frame,
                smart_bake=False,
            )
            fastbake_lib.bake_attributes(
                [screenz_master_grp],
                ['copyScreenX', 'copyScreenY'],
                start_frame,
                end_frame,
                smart_bake=False,
            )
            cmds.connectAttr(
                main_grp + '.screenX', screen_xy_master_grp + '.translateX', f=True
            )
            cmds.connectAttr(
                main_grp + '.screenY', screen_xy_master_grp + '.translateY', f=True
            )

            # Create condition node network
            screenx_condition_node = cmds.shadingNode(
                'condition', au=True, n=name + '_screenX_condition'
            )
            screeny_condition_node = cmds.shadingNode(
                'condition', au=True, n=name + '_screenY_condition'
            )
            cmds.connectAttr(
                main_grp + '.screenX', screenx_condition_node + '.firstTerm', f=True
            )
            cmds.connectAttr(
                screenz_master_grp + '.copyScreenX',
                screenx_condition_node + '.secondTerm',
                f=True,
            )
            cmds.connectAttr(
                main_grp + '.screenY', screeny_condition_node + '.firstTerm', f=True
            )
            cmds.connectAttr(
                screenz_master_grp + '.copyScreenY',
                screeny_condition_node + '.secondTerm',
                f=True,
            )
            attr_list = const.TRANSFORM_ATTR_LIST + ['visibility']
            for attr in attr_list:
                cmds.setAttr(screenz_master_grp + '.' + attr, lock=True)
            cmds.pointConstraint(screen_xy_master_grp, object)

            # Select the master control.
            cmds.select(main_grp, replace=True)
            self.refresh_rigsList()

    def check_name_exists(self, rigName, name, rigsList):
        valid_name_list = False
        same_name_used = False
        sel = cmds.ls(transforms=True, os=True) or []
        if len(sel) == 0:
            LOG.warn('Atleast one Transform node type object must be selected.')
            return valid_name_list, same_name_used
        if len(name) == 0:
            LOG.warn('Please type name first.')
            return valid_name_list, same_name_used
        names = name.split(',')
        if len(names) != len(sel):
            LOG.warn('Selection and name count not matching.')
            return valid_name_list, same_name_used
        valid_name_list = True
        for name_item in names:
            # Check if name already exists
            iterator = QtWidgets.QTreeWidgetItemIterator(rigsList)
            while iterator.value():
                item = iterator.value()
                item_name = item.text(0)
                item_name = item_name.replace(rigName, '')
                if item_name == name_item:
                    same_name_used = True
                iterator += 1
        if same_name_used is True:
            LOG.warn('Same name exists already please type different name.')
        return valid_name_list, same_name_used

    def create_screen_space_rig_clicked(self):
        name = self.nameLineEdit.text()
        rigsList = self.rigsList
        cam_tfm = self.get_vp_camera()
        if cam_tfm is None:
            LOG.warn('Please select a camera.')
            return
        sel = cmds.ls(transforms=True, os=True)
        check_name = self.check_name_exists(const.RIG_SUFFIX_NAME, name, rigsList)
        valid_name_list, same_name_used = check_name
        names = name.split(',')
        if valid_name_list is False or same_name_used is True:
            return
        assert len(names) == len(sel)
        node_screen_depths = []
        ctx = tools_utils.tool_context(
            use_undo_chunk=True,
            restore_current_frame=True,
            use_dg_evaluation_mode=True,
            disable_viewport=True,
            disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE,
        )
        with ctx:
            for sel_item, name_item in zip(sel, names):
                # Check if object has existing point constraint already
                has_constraints = transform_has_constraints(sel_item)
                if has_constraints is False:
                    depth_list = self.calc_distance(cam_tfm, sel_item, 0)
                    node_screen_depths.append((sel_item, name_item, depth_list))
                else:
                    LOG.warn('Selected object(s) already have constraints.')
                    return
            for sel_item, name_item, depth_list in node_screen_depths:
                self.create_rig(
                    cam_tfm, sel_item, depth_list, name_item, const.RIG_SUFFIX_NAME
                )
        return

    def create_freeze_rig_clicked(self):
        nameLineEdit = self.nameLineEdit.text()
        rigsList = self.rigsList
        cam_tfm = self.get_vp_camera()
        if cam_tfm is None:
            LOG.warn('Please select a camera.')
            return
        check_name = self.check_name_exists(
            const.FREEZE_RIG_SUFFIX_NAME, nameLineEdit, rigsList
        )
        valid_name_list, same_name_used = check_name

        if valid_name_list is not True or same_name_used is not False:
            LOG.warn('Invalid freeze rig name.')
            return
        do_camera_space = self.camera_space_action.isChecked()
        do_world_space = self.world_space_action.isChecked()
        use_anim_layer = self.animlayer_action.isChecked()
        # When making a freeze rig we always assume the full frame
        # range will be baked - NO smart bake.
        LOG.warn('Force full bake for Freeze Rig.')
        self.fullBakeRadioButton.setChecked(True)
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        sel = cmds.ls(orderedSelection=True, transforms=True) or []
        names = nameLineEdit.split(',')

        for sel_item, name_item in zip(sel, names):
            ctx = tools_utils.tool_context(
                use_undo_chunk=True,
                restore_current_frame=True,
                use_dg_evaluation_mode=True,
                disable_viewport=True,
                disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE,
            )
            with ctx:
                freeze_rig_name = name_item + const.FREEZE_RIG_SUFFIX_NAME
                animLayerName = name_item + const.FREEZE_RIG_ANIM_LAYER

                # Check if object has existing point constraint already.
                has_constraints = transform_has_constraints(sel_item)
                if has_constraints is True:
                    LOG.warn(
                        'Selected object(s) already have constraints: %r.', sel_item
                    )
                    continue

                # Get the selected item's depth, if we don't have
                # anything, we cannot continue.
                dlist = self.calc_distance(cam_tfm, sel_item, 0)
                if len(dlist) == 0:
                    continue
                if do_camera_space:
                    # Camera space bake
                    self.create_rig(
                        cam_tfm,
                        sel_item,
                        dlist,
                        name_item,
                        const.FREEZE_RIG_SUFFIX_NAME,
                    )
                    cmds.cutKey(
                        name_item + const.FREEZE_RIG_SUFFIX_NAME,
                        clear=True,
                        at=const.SCREEN_Z_DEPTH_ATTR_NAME,
                    )
                else:
                    # World space bake
                    # Create a static temp group
                    temp_grp = cmds.group(empty=True)
                    con = cmds.parentConstraint(
                        sel_item, temp_grp, maintainOffset=False
                    )
                    cmds.delete(con)
                    fastbake_lib.bake_attributes(
                        [temp_grp], [], start_frame, end_frame, smart_bake=False
                    )
                    self.create_rig(
                        cam_tfm,
                        sel_item,
                        dlist,
                        name_item,
                        const.FREEZE_RIG_SUFFIX_NAME,
                    )

                    # Calc full freeze list
                    dlist = self.calc_distance(cam_tfm, temp_grp, 0)
                    if use_anim_layer is False:
                        # Set keyframes on screenzdepth attribute,
                        # with no anim layer.
                        set_z_depth_keyframes(
                            freeze_rig_name, start_frame, end_frame, dlist
                        )
                    else:
                        # Make the anim layer, and add our freeze rig
                        # node to the layer.
                        cmds.select(freeze_rig_name, replace=True)
                        cmds.animLayer(animLayerName, addSelectedObjects=True)
                        cmds.select(clear=True)
                        set_z_depth_keyframes(
                            freeze_rig_name,
                            start_frame,
                            end_frame,
                            dlist,
                            anim_layer_name=animLayerName,
                        )

                    # Delete temp group
                    cmds.delete(temp_grp)
        return

    def bake_rig_clicked(self):
        bake_options = self.get_bake_options()
        selected_items = self.rigsList.selectedItems()
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        if len(selected_items) == 0:
            LOG.warn('Atleast one rig must be selected from UI.')
            return
        ctx = tools_utils.tool_context(
            use_undo_chunk=True,
            restore_current_frame=True,
            use_dg_evaluation_mode=True,
            disable_viewport=True,
            disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE,
        )
        with ctx:
            cmds.select(clear=True)
            for sel_item in selected_items:
                children = self.get_all_children(sel_item)
                for j in children:
                    rigName = j.text(0)
                    object = cmds.getAttr(
                        rigName + '.' + const.ATTRIBUTE_IDENTIFIER_NAME
                    )
                    if const.FREEZE_RIG_SUFFIX_NAME in rigName:
                        self.fullBakeRadioButton.setChecked(True)
                    if const.RIG_SUFFIX_NAME in rigName:
                        name = rigName.split(const.RIG_SUFFIX_NAME)[0]
                    if const.FREEZE_RIG_SUFFIX_NAME in rigName:
                        name = rigName.split(const.FREEZE_RIG_SUFFIX_NAME)[0]
                    if bake_options == 'full_bake':
                        fastbake_lib.bake_attributes(
                            [object], [], start_frame, end_frame, smart_bake=False
                        )
                    if bake_options == 'smart_bake':
                        nodes_list = cmds.listConnections(
                            name + const.SCREEN_Z_MASTER_NAME
                        )
                        for node in nodes_list:
                            if 'screenX_condition' in node:
                                x_node = node
                            if 'screenY_condition' in node:
                                y_node = node
                        cmds.select(object)
                        attrs = ['tx', 'ty', 'tz']
                        # First key on objects existing key frames
                        for frame in self.get_prebake_frames_list_from_node(object):
                            oma.MAnimControl.setCurrentTime(om.MTime(frame))
                            cmds.setKeyframe(attribute=attrs)
                        # Key screen z depth attribute frames
                        keys_list = cmds.keyframe(
                            rigName + '.' + const.SCREEN_Z_DEPTH_ATTR_NAME, query=True
                        )
                        if keys_list:
                            for frame in keys_list:
                                oma.MAnimControl.setCurrentTime(om.MTime(frame))
                                cmds.setKeyframe(attribute=attrs)
                        # Check condition result node and set keyframe
                        for i in range(start_frame, end_frame + 1):
                            oma.MAnimControl.setCurrentTime(om.MTime(i))
                            x_changed = cmds.getAttr(x_node + '.outColor')[0][0]
                            y_changed = cmds.getAttr(y_node + '.outColor')[0][0]
                            if x_changed or y_changed:
                                cmds.setKeyframe(attribute=attrs)
                        cmds.select(clear=True)
            self.delete_rig_clicked()
            self.refresh_rigsList()
        return

    def get_all_children(self, tree_widget_item):
        nodes = [tree_widget_item]
        for i in range(tree_widget_item.childCount()):
            nodes.extend(self.get_all_children(tree_widget_item.child(i)))
        return nodes

    def delete_rig_clicked(self):
        selected_items = self.rigsList.selectedItems()
        if len(selected_items) == 0:
            LOG.warn('Atleast one rig must be selected from UI.')
            return
        nodes_to_delete = []
        for sel_item in selected_items:
            children = self.get_all_children(sel_item)
            for j in children:
                rigName = j.text(0)
                if const.RIG_SUFFIX_NAME in rigName:
                    name = rigName.split(const.RIG_SUFFIX_NAME)[0]
                elif const.FREEZE_RIG_SUFFIX_NAME in rigName:
                    name = rigName.split(const.FREEZE_RIG_SUFFIX_NAME)[0]
                else:
                    LOG.warn('No valid rig name: %r', rigName)
                    continue
                nodes_to_delete.append(rigName)
                nodes_to_delete.append(name + const.SCREEN_Z_MASTER_NAME)
                nodes_to_delete.append(name + const.SCREEN_XY_MASTER_NAME)
                nodes_list = cmds.listConnections(name + const.SCREEN_Z_MASTER_NAME)
                for node in nodes_list:
                    if 'screenX_condition' in node:
                        nodes_to_delete.append(node)
                    if 'screenY_condition' in node:
                        nodes_to_delete.append(node)
                animLayer = rigName + 'Layer'
                if cmds.animLayer(animLayer, query=True, exists=True):
                    nodes_to_delete.append(animLayer)
        # Delete selected nodes
        nodes_to_delete = [n for n in nodes_to_delete if cmds.objExists(n)]
        cmds.delete(nodes_to_delete)
        self.refresh_rigsList()
        return

    def lock_unlock_attributes(self, tfm_node, lock=True):
        attr_list = const.TRANSFORM_ATTR_LIST
        for attr in attr_list:
            cmds.setAttr(tfm_node + '.' + attr, lock=lock)

    def match(self):
        selected_items = self.rigsList.selectedItems()
        if len(selected_items) < 2:
            LOG.warn('Atleast two rigs must be selected from UI.')
            return
        # Get parent
        selected_parent = selected_items[0]
        parent_main = selected_parent.text(0)
        parent_base_name = parent_main.split(const.RIG_SUFFIX_NAME)[0]
        parent = parent_base_name + const.SCREEN_Z_MASTER_NAME
        try:
            self.lock_unlock_attributes(parent, lock=False)
            selected_children = selected_items[1:]
            for selected_child in selected_children:
                child_main = selected_child.text(0)
                child_base_name = child_main.split(const.RIG_SUFFIX_NAME)[0]
                child = child_base_name + const.SCREEN_Z_MASTER_NAME
                self.lock_unlock_attributes(child, lock=False)
                attr_list = const.TRANSFORM_ATTR_LIST
                for attr in attr_list:
                    plug = child + '.' + attr
                    cmd = 'source channelBoxCommand; ' 'CBdeleteConnection "{}";'
                    mel.eval(cmd.format(plug))
                cmds.parent(child, parent)
                cmds.parent(child_main, parent_main)
                cmds.cutKey(child_main, cl=True, at=const.SCREEN_Z_DEPTH_ATTR_NAME)
                child_scale = cmds.getAttr(child + '.sx')
                cmds.setAttr(
                    child_main + '.' + const.SCREEN_Z_DEPTH_ATTR_NAME, child_scale
                )
                src = child_main + '.' + const.SCREEN_Z_DEPTH_ATTR_NAME
                cmds.connectAttr(src, child + '.scaleX', f=True)
                cmds.connectAttr(src, child + '.scaleY', f=True)
                cmds.connectAttr(src, child + '.scaleZ', f=True)
                self.lock_unlock_attributes(child, lock=True)
            self.lock_unlock_attributes(parent, lock=True)
        except RuntimeError:
            LOG.warn('Freeze rig can not be matched.')
        self.refresh_rigsList()
        return
