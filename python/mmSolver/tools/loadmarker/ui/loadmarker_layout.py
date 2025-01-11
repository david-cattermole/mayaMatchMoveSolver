# Copyright (C) 2018, 2019, 2020, 2025 David Cattermole.
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
The main component of the user interface for the loadmarker window.
"""

import os

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uimodels as uimodels
import mmSolver.utils.config as config_utils
import mmSolver.api as mmapi
import mmSolver.tools.loadmarker.constant as const
import mmSolver.tools.loadmarker.ui.ui_loadmarker_layout as ui_loadmarker_layout
import mmSolver.tools.loadmarker.lib.fieldofview as fieldofview
import mmSolver.utils.loadmarker.fileutils as fileutils
import mmSolver.tools.loadmarker.lib.utils as lib
import mmSolver.tools.loadmarker.lib.mayareadfile as mayareadfile
import mmSolver.tools.solver.lib.state as state_lib
import mmSolver.tools.solver.lib.collection as col_lib
import mmSolver.tools.userpreferences.constant as userprefs_const
import mmSolver.tools.userpreferences.lib as userprefs_lib


LOG = mmSolver.logger.get_logger()


def get_config():
    """Get the Load Marker config object or None."""
    file_name = const.CONFIG_FILE_NAME
    config_path = config_utils.get_home_dir_path(file_name)
    config = config_utils.Config(config_path)
    config.set_autoread(False)
    config.set_autowrite(False)
    if os.path.isfile(config.file_path):
        config.read()
    return config


def get_config_value(config, key, fallback):
    """Query the attribute from the user's home directory. If the user's
    option is saved, use that value instead.
    """
    value = fallback
    if config is not None:
        value = config.get_value(key, fallback)
    return value


def get_user_prefs_add_marker_to_collection():
    config = userprefs_lib.get_config()
    key = userprefs_const.REG_EVNT_ADD_NEW_MKR_TO_KEY
    value = userprefs_lib.get_value(config, key)
    return value != userprefs_const.REG_EVNT_ADD_NEW_MKR_TO_NONE_VALUE


def get_user_prefs_distortion_mode_default():
    config = userprefs_lib.get_config()
    key = userprefs_const.LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_KEY
    value = userprefs_lib.get_value(config, key)
    result = None
    if value == userprefs_const.LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_UNDISTORT_VALUE:
        result = userprefs_const.LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_UNDISTORT_LABEL
    elif value == userprefs_const.LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_DISTORT_VALUE:
        result = userprefs_const.LOAD_MARKER_UI_DISTORTION_MODE_DEFAULT_DISTORT_LABEL
    return result


def get_user_prefs_use_overscan_default():
    config = userprefs_lib.get_config()
    key = userprefs_const.LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_KEY
    value = userprefs_lib.get_value(config, key)
    return value == userprefs_const.LOAD_MARKER_UI_USE_OVERSCAN_DEFAULT_TRUE_VALUE


def get_user_prefs_load_bundle_positions_default():
    config = userprefs_lib.get_config()
    key = userprefs_const.LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_KEY
    value = userprefs_lib.get_value(config, key)
    return (
        value == userprefs_const.LOAD_MARKER_UI_LOAD_BUNDLE_POSITIONS_DEFAULT_TRUE_VALUE
    )


def get_user_prefs_rename_markers_default():
    config = userprefs_lib.get_config()
    key = userprefs_const.LOAD_MARKER_UI_RENAME_MARKERS_DEFAULT_KEY
    value = userprefs_lib.get_value(config, key)
    return value == userprefs_const.LOAD_MARKER_UI_RENAME_MARKERS_DEFAULT_TRUE_VALUE


class LoadMarkerLayout(QtWidgets.QWidget, ui_loadmarker_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(LoadMarkerLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.loadMode_model = QtCore.QStringListModel()
        self.loadMode_comboBox.setModel(self.loadMode_model)

        self.camera_model = uimodels.StringDataListModel()
        self.camera_comboBox.setModel(self.camera_model)

        self.markerGroup_model = uimodels.StringDataListModel()
        self.markerGroup_comboBox.setModel(self.markerGroup_model)

        self.collection_model = uimodels.StringDataListModel()
        self.collection_comboBox.setModel(self.collection_model)

        self.distortionMode_model = QtCore.QStringListModel()
        self.distortionMode_comboBox.setModel(self.distortionMode_model)

        self.createConnections()
        self.populateUi()

    def createConnections(self):
        """Set up callback connections"""
        self.loadMode_comboBox.currentIndexChanged.connect(
            lambda x: self.updateLoadMode()
        )
        self.camera_comboBox.currentIndexChanged.connect(
            lambda x: self.markerGroupUpdateClicked()
        )
        self.camera_comboBox.currentIndexChanged.connect(
            lambda x: self.updateOverscanValues()
        )
        self.markerGroup_comboBox.currentIndexChanged.connect(
            lambda x: self.updateOverscanValues()
        )
        self.collection_checkBox.clicked[bool].connect(
            lambda x: self.updateCollectionEnabledState()
        )

        self.cameraUpdate_pushButton.clicked.connect(self.cameraUpdateClicked)
        self.markerGroupUpdate_pushButton.clicked.connect(self.markerGroupUpdateClicked)
        self.collectionUpdate_pushButton.clicked.connect(self.collectionUpdateClicked)

        self.filepath_pushButton.clicked.connect(self.filePathBrowseClicked)
        self.filepath_lineEdit.editingFinished.connect(self.updateFilePathWidget)
        self.overscan_checkBox.toggled.connect(self.setOverscanEnabledState)
        self.overscan_checkBox.released.connect(self.updateOverscanValues)
        return

    def populateUi(self):
        config = get_config()
        self._file_info = None

        w, h = lib.get_default_image_resolution()
        self.imageRes_label.setEnabled(False)
        self.imageResWidth_label.setEnabled(False)
        self.imageResWidth_spinBox.setValue(w)
        self.imageResWidth_spinBox.setEnabled(False)
        self.imageResHeight_label.setEnabled(False)
        self.imageResHeight_spinBox.setValue(h)
        self.imageResHeight_spinBox.setEnabled(False)

        self.fileInfo_plainTextEdit.setReadOnly(True)

        default_value = get_user_prefs_rename_markers_default()
        value = get_config_value(config, 'data/rename_markers', default_value)
        self.renameMarkers_checkBox.setChecked(value)
        if value is True:
            # Empty string is intended to force the user to enter a valid name.
            fallback = ''
            new_name = get_config_value(config, 'data/rename_markers_name', fallback)
            self.renameMarkers_lineEdit.setText(new_name)

        default_value = get_user_prefs_load_bundle_positions_default()
        value = get_config_value(config, 'data/load_bundle_position', default_value)
        self.loadBndPositions_checkBox.setChecked(value)

        # Get the file path from the clipboard.
        try:
            clippy = QtGui.QClipboard()
            text = str(clippy.text()).strip()
            if fileutils.is_valid_file_path(text, mayareadfile.read):
                self.setFilePath(text)
        except Exception as e:
            msg = 'Could not get file path from clipboard.'
            LOG.warning(msg)
            LOG.info(str(e))

        all_camera_nodes = lib.get_cameras()
        selected_cameras = lib.get_selected_cameras()
        active_camera = lib.get_active_viewport_camera()
        self.updateCameraList(
            self.camera_comboBox,
            self.camera_model,
            all_camera_nodes,
            selected_cameras,
            active_camera,
        )
        active_camera = self.getCameraData()
        mkr_grp_nodes = lib.get_marker_groups(active_camera)
        active_mkr_grp = None
        self.updateMarkerGroupList(
            self.markerGroup_comboBox,
            self.markerGroup_model,
            active_mkr_grp,
            mkr_grp_nodes,
        )

        col_list = col_lib.get_collections()
        active_col = state_lib.get_active_collection()
        self.updateCollectionList(
            self.collection_comboBox, self.collection_model, active_col, col_list
        )
        # If the user's preferences say to add the marker to the
        # collection, then turn on the feature.
        auto_add_marker = get_user_prefs_add_marker_to_collection()
        self.collection_checkBox.setChecked(auto_add_marker)
        self.updateCollectionEnabledState()

        value = get_config_value(
            config, "data/load_mode", const.LOAD_MODE_DEFAULT_VALUE
        )
        self.populateLoadModeModel(self.loadMode_model)
        index = self.loadMode_model.stringList().index(value)
        self.loadMode_comboBox.setCurrentIndex(index)

        default_value = get_user_prefs_distortion_mode_default()
        value = get_config_value(config, "data/distortion_mode", default_value)
        self.populateDistortionModeModel(self.distortionMode_model)
        index = self.distortionMode_model.stringList().index(value)
        self.distortionMode_comboBox.setCurrentIndex(index)

        default_value = get_user_prefs_use_overscan_default()
        value = get_config_value(config, 'data/use_overscan', default_value)
        self.overscan_checkBox.setChecked(value)
        self.updateOverscanValues()

        default_value = get_user_prefs_load_bundle_positions_default()
        value = get_config_value(config, 'data/load_bundle_positions', default_value)
        self.overscan_checkBox.setChecked(value)
        self.updateOverscanValues()
        return

    def updateFileInfo(self):
        file_path = self.getFilePath()
        if not file_path:
            return
        file_info = fileutils.get_file_info(file_path, mayareadfile.read)
        self.setFileInfo(file_info)
        return

    def updateFileInfoText(self):
        file_path = self.getFilePath()
        info_widget = self.fileInfo_plainTextEdit
        valid = fileutils.is_valid_file_path(file_path, mayareadfile.read)
        if valid is False:
            text = 'File path is not valid:\n'
            text += repr(file_path)
            info_widget.setPlainText(text)
            return
        text = 'Frame Range: {start_frame}-{end_frame}\n'
        text += 'Number of Points: {num_points}\n'
        text += 'Point Names: {point_names}\n'
        text += '\n'
        text += 'Format: {fmt_name}\n'
        text += 'Distorted Data: {lens_dist}\n'
        text += 'Undistorted Data: {lens_undist}\n'
        text += 'Bundle Positions: {positions}\n'
        text += 'With Camera FOV: {has_camera_fov}\n'
        info = fileutils.get_file_info_strings(file_path, mayareadfile.read)

        # Change point names into single string.
        point_names = info.get('point_names', '')
        point_names = point_names.strip()
        point_names = '\n- ' + point_names.replace(' ', '\n- ')
        info['point_names'] = point_names

        text = text.format(**info)
        info_widget.setPlainText(text)
        return

    def updateLoadMode(self):
        text = self.getLoadModeText()
        value = None
        if text == const.LOAD_MODE_NEW_VALUE:
            value = True
        elif text == const.LOAD_MODE_REPLACE_VALUE:
            value = False
        else:
            assert False

        self.camera_label.setEnabled(value)
        self.camera_comboBox.setEnabled(value)
        self.cameraUpdate_pushButton.setEnabled(value)
        self.markerGroup_label.setEnabled(value)
        self.markerGroup_comboBox.setEnabled(value)
        self.markerGroupUpdate_pushButton.setEnabled(value)
        self.updateCollectionEnabledState()
        self.updateOverscanValues()
        return

    def updateOverscanValues(self):
        label_x = ''
        label_y = ''
        data_source = ''

        use_overscan = self.getUseOverscanValue()
        load_mode_text = self.getLoadModeText()
        if use_overscan is False:
            if load_mode_text == const.LOAD_MODE_NEW_VALUE:
                data_source = 'from default values'
                label_x = 'Width: %.2f' % 100.0
                label_y = 'Height: %.2f' % 100.0
                label_x += '%'
                label_y += '%'
                label_y += ' (%s)' % data_source
            self.overscanX_label.setText(label_x)
            self.overscanY_label.setText(label_y)
            return

        file_info = self.getFileInfo()
        camera = self.getCameraData()
        has_file_data = (
            file_info is not None
            and camera is not None
            and isinstance(file_info.camera_field_of_view, list)
        )
        if load_mode_text == const.LOAD_MODE_NEW_VALUE:
            if has_file_data is True:
                data_source = 'from file'

                # Purposefully do not allow Marker Group to influence the
                # value shown to the user.
                mkr_grp = None
                file_fovs = file_info.camera_field_of_view
                x, y = fieldofview.calculate_overscan_ratio(camera, mkr_grp, file_fovs)
                # NOTE: Inverse the overscan value, because the user will
                # be more comfortable with numbers above 100%.
                x = 1.0 / x
                y = 1.0 / y
                x *= 100.0
                y *= 100.0
            else:
                data_source = 'from default values'
                x = 100.0
                y = 100.0
            label_x = 'Width: %.2f' % x
            label_y = 'Height: %.2f' % y
            label_x += '%'
            label_y += '%'
        elif load_mode_text == const.LOAD_MODE_REPLACE_VALUE:
            label_x = 'Width: ?'
            label_y = 'Height: ?'
            data_source = 'from selected Marker'

        label_y += ' (%s)' % data_source
        self.overscanX_label.setText(label_x)
        self.overscanY_label.setText(label_y)
        return

    def updateOverscanEnabledState(self):
        value = False
        file_info = self.getFileInfo()
        if file_info is not None:
            value = bool(file_info.camera_field_of_view)
        self.overscan_checkBox.setEnabled(value)
        self.setOverscanEnabledState(value)
        return

    def updateDistortionModeEnabledState(self):
        value = False
        file_info = self.getFileInfo()
        if file_info is not None:
            value = file_info.marker_distorted and file_info.marker_undistorted
        self.distortionMode_label.setEnabled(value)
        self.distortionMode_comboBox.setEnabled(value)
        return

    def updateCollectionEnabledState(self):
        value = self.collection_checkBox.isChecked()
        self.collection_comboBox.setEnabled(value)
        self.collectionUpdate_pushButton.setEnabled(value)
        return

    def updateLoadBundlePosEnabledState(self):
        value = False
        file_info = self.getFileInfo()
        if file_info is not None:
            value = file_info.bundle_positions
        self.loadBndPositions_checkBox.setEnabled(value)
        return

    def updateImageResEnabledState(self):
        enabled = False
        file_path = self.getFilePath()
        fmt = fileutils.get_file_path_format(file_path, mayareadfile.read)
        if fmt is None:
            enabled = False
        else:
            for arg in fmt.args:
                enabled = arg == 'image_width'
                break
        self.imageRes_label.setEnabled(enabled)
        self.imageResWidth_label.setEnabled(enabled)
        self.imageResWidth_spinBox.setEnabled(enabled)
        self.imageResHeight_label.setEnabled(enabled)
        self.imageResHeight_spinBox.setEnabled(enabled)
        return

    def updateCameraList(
        self, comboBox, model, all_camera_nodes, selected_cameras, active_camera
    ):
        self.populateCameraModel(model, all_camera_nodes)
        index = self.getDefaultCameraIndex(model, selected_cameras, active_camera)
        comboBox.setCurrentIndex(index)
        return

    def updateMarkerGroupList(self, comboBox, model, active_mkr_grp, mkr_grp_nodes):
        self.populateMarkerGroupModel(model, active_mkr_grp, mkr_grp_nodes)
        index = self.getDefaultMarkerGroupIndex(model, active_mkr_grp, mkr_grp_nodes)
        comboBox.setCurrentIndex(index)
        self.updateOverscanValues()
        return

    def updateCollectionList(self, comboBox, model, active_col, col_list):
        self.populateCollectionModel(model, active_col, col_list)
        index = self.getDefaultCollectionIndex(model, active_col, col_list)
        comboBox.setCurrentIndex(index)
        self.updateCollectionEnabledState()
        return

    def populateLoadModeModel(self, model):
        """
        Add entries of cameras in the scene into the given camera model.

        :param model: The Qt model to add cameras to.
        :type model: QtCore.QStringListModel

        :return:
        """
        values = [
            const.LOAD_MODE_NEW_VALUE,
            const.LOAD_MODE_REPLACE_VALUE,
        ]
        model.setStringList(values)
        return

    def populateCameraModel(self, model, camera_nodes):
        """
        Add entries of cameras in the scene into the given camera model.

        :param model: The Qt model to add cameras to.
        :type model: QtCore.QStringListModel

        :return:
        """
        string_data_list = [(const.NEW_CAMERA_VALUE, None)]
        for camera_node in camera_nodes:
            if camera_node.is_valid() is False:
                LOG.warning('Camera node is not valid: %r', camera_node)
                continue
            node = camera_node.get_shape_node()
            string_data_list.append((node, camera_node))
        model.setStringDataList(string_data_list)
        return

    def populateMarkerGroupModel(self, model, active_mkr_grp, mkr_grp_nodes):
        """
        Add entries of cameras in the scene into the given camera model.

        :param model: The Qt model to add cameras to.
        :type model: uimodels.StringDataListModel

        :return:
        """
        string_data_list = [(const.NEW_MARKER_GROUP_VALUE, None)]
        for mkr_grp_node in mkr_grp_nodes:
            if mkr_grp_node.is_valid() is False:
                LOG.warning('Marker Group node is not valid: %r', mkr_grp_node)
                continue
            node = mkr_grp_node.get_node()
            string_data_list.append((node, mkr_grp_node))
        model.setStringDataList(string_data_list)
        return

    def populateCollectionModel(self, model, active_col, col_list):
        """
        Add Collections in the scene into the given Collection model.

        :param model: The Qt model to add Collections to.
        :type model: uimodels.StringDataListModel

        :return:
        """
        string_data_list = [
            (const.NEW_COLLECTION_VALUE, None),
        ]
        for col_node in col_list:
            node = col_node.get_node()
            string_data_list.append((node, col_node))
        model.setStringDataList(string_data_list)
        return

    def populateDistortionModeModel(self, model):
        """
        Add entries of cameras in the scene into the given camera model.

        :param model: The Qt model to add cameras to.
        :type model: QtCore.QStringListModel

        :return:
        """
        values = [
            const.UNDISTORTION_MODE_VALUE,
            const.DISTORTION_MODE_VALUE,
        ]
        model.setStringList(values)
        return

    def getDefaultCameraIndex(self, model, selected_cameras, active_camera):
        """
        Chooses the index in model based on the currently selected
        cameras.

        :param model: The Camera model.
        :type model: uimodels.StringDataListModel

        :param selected_cameras: List of cameras that are selected.
        :type selected_cameras: [mmSolver.api.Camera, ..]

        :param active_camera: The active camera.
        :type active_camera: mmSolver.api.Camera

        :return: index number as default item in camera list.
        :rtyle: int
        """
        assert isinstance(selected_cameras, (list, tuple))
        if len(selected_cameras) == 0 and active_camera is None:
            return 0

        selected_cameras = list(selected_cameras)
        if active_camera is not None:
            selected_cameras.insert(0, active_camera)

        string_data_list = model.stringDataList()
        for cam in selected_cameras:
            if not isinstance(cam, mmapi.Camera):
                continue
            if cam is None:
                continue
            nodes = [
                cam.get_transform_node(),
                cam.get_shape_node(),
            ]
            for i, (string, _) in enumerate(string_data_list):
                for node in nodes:
                    find = string.find(node)
                    if find != -1:
                        return i
        return 0

    def getDefaultMarkerGroupIndex(self, model, active_mkr_grp, mkr_grp_nodes):
        """
        Chooses the index in model for Marker Group

        :param model: The MarkerGroup model.
        :type model: uimodels.StringDataListModel

        :param mkr_grp_nodes: List of MarkerGroups under active camera.
        :type mkr_grp_nodes: list of mmSolver.api.MarkerGroup

        :return: index number as default item in MarkerGroup list.
        :rtyle: int
        """
        idx = 0
        if len(mkr_grp_nodes) > 0:
            idx = 1
        return idx

    def getDefaultCollectionIndex(self, model, active_col, col_list):
        """
        Chooses the index in model for Marker Group

        :param model: The MarkerGroup model.
        :type model: uimodels.StringDataListModel

        :param col_list: List of Collections in the scene.
        :type col_list: [mmSolver.api.Collection, ..]

        :return: index number as default item in MarkerGroup list.
        :rtyle: int
        """
        idx = 0  # Create a new Collection
        if active_col and len(col_list) > 0:
            # Use the active Collection
            active_col_node = active_col.get_node()
            string_data_list = model.stringDataList()
            for i, (string, _) in enumerate(string_data_list):
                if string == active_col_node:
                    return i
        return idx

    def cameraUpdateClicked(self):
        all_camera_nodes = lib.get_cameras()
        selected_cameras = lib.get_selected_cameras()
        active_camera = lib.get_active_viewport_camera()
        self.updateCameraList(
            self.camera_comboBox,
            self.camera_model,
            all_camera_nodes,
            selected_cameras,
            active_camera,
        )
        return

    def markerGroupUpdateClicked(self):
        active_camera = self.getCameraData()
        mkr_grp_nodes = lib.get_marker_groups(active_camera)
        active_mkr_grp = None
        self.updateMarkerGroupList(
            self.markerGroup_comboBox,
            self.markerGroup_model,
            active_mkr_grp,
            mkr_grp_nodes,
        )
        return

    def collectionUpdateClicked(self):
        col_list = col_lib.get_collections()
        active_col = state_lib.get_active_collection()
        self.updateCollectionList(
            self.collection_comboBox,
            self.collection_model,
            active_col,
            col_list,
        )
        return

    def filePathBrowseClicked(self):
        title = "Select Marker File..."
        file_filter = fileutils.get_file_filter()
        start_dir = lib.get_start_directory(self.getFilePath())
        result = QtWidgets.QFileDialog.getOpenFileName(
            self, title, start_dir, file_filter
        )
        if result is not None:
            file_path = result[0]
            self.setFilePath(file_path)
        return

    def updateFilePathWidget(self):
        self.updateFileInfo()
        self.updateFileInfoText()
        self.updateImageResEnabledState()
        self.updateDistortionModeEnabledState()
        self.updateOverscanValues()
        self.updateOverscanEnabledState()
        self.updateLoadBundlePosEnabledState()
        return

    def setOverscanEnabledState(self, value):
        assert isinstance(value, bool)
        self.overscanX_label.setEnabled(value)
        self.overscanY_label.setEnabled(value)
        return

    def setFilePath(self, value):
        self.filepath_lineEdit.setText(value)
        self.updateFilePathWidget()
        return

    def getFilePath(self):
        value = self.filepath_lineEdit.text()
        return str(value).strip()

    def setFileInfo(self, value):
        self._file_info = value
        return

    def getFileInfo(self):
        return self._file_info

    def getCameraFieldOfViewValue(self):
        file_info = self.getFileInfo()
        if file_info is None:
            return None
        return file_info.camera_field_of_view

    def getLoadModeText(self):
        text = self.loadMode_comboBox.currentText()
        return text

    def getRenameMarkers(self):
        value = self.renameMarkers_checkBox.isChecked()
        enabled = self.renameMarkers_checkBox.isEnabled()
        return value and enabled

    def getRenameMarkersName(self):
        enabled = self.renameMarkers_lineEdit.isEnabled()
        if enabled is False:
            return ''
        value = self.renameMarkers_lineEdit.text()
        return value

    def getDistortionModeText(self):
        text = self.distortionMode_comboBox.currentText()
        return text

    def getUseOverscanValue(self):
        use_overscan = self.overscan_checkBox.isChecked()
        enabled = self.overscan_checkBox.isEnabled()
        return use_overscan and enabled

    def getCameraText(self):
        text = self.camera_comboBox.currentText()
        return text

    def getCameraData(self):
        index = self.camera_comboBox.currentIndex()
        model_index = self.camera_model.index(index)
        data = self.camera_model.data(model_index, role=QtCore.Qt.UserRole)
        return data

    def getMarkerGroupText(self):
        text = self.markerGroup_comboBox.currentText()
        return text

    def getMarkerGroupData(self):
        index = self.markerGroup_comboBox.currentIndex()
        model_index = self.markerGroup_model.index(index)
        data = self.markerGroup_model.data(model_index, role=QtCore.Qt.UserRole)
        return data

    def getAddToCollectionValue(self):
        value = False
        enabled = self.collection_checkBox.isEnabled()
        if not enabled:
            return value
        value = self.collection_checkBox.isChecked()
        return value

    def getCollectionText(self):
        text = self.collection_comboBox.currentText()
        return text

    def getCollectionData(self):
        index = self.collection_comboBox.currentIndex()
        model_index = self.collection_model.index(index)
        data = self.collection_model.data(model_index, role=QtCore.Qt.UserRole)
        return data

    def getLoadBundlePositions(self):
        value = False
        enabled = self.loadBndPositions_checkBox.isEnabled()
        if not enabled:
            return value
        value = self.loadBndPositions_checkBox.isChecked()
        return value

    def getImageResolution(self):
        width = self.imageResWidth_spinBox.value()
        height = self.imageResHeight_spinBox.value()
        return width, height
