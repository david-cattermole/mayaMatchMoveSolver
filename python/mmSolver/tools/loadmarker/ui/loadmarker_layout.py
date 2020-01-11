# Copyright (C) 2018 David Cattermole.
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
import pprint

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uimodels as uimodels
import mmSolver.utils.config as config_utils
import mmSolver.tools.loadmarker.constant as const
import mmSolver.tools.loadmarker.ui.ui_loadmarker_layout as ui_loadmarker_layout
import mmSolver.tools.loadmarker.lib.utils as lib

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

        self.distortionMode_model = QtCore.QStringListModel()
        self.distortionMode_comboBox.setModel(self.distortionMode_model)

        self.createConnections()
        self.populateUi()

    def createConnections(self):
        """Set up callback connections"""
        self.loadMode_comboBox.currentIndexChanged[str].connect(
            lambda x: self.updateLoadMode())
        self.camera_comboBox.currentIndexChanged[str].connect(
            lambda x: self.markerGroupUpdateClicked())
        self.camera_comboBox.currentIndexChanged[str].connect(
            lambda x: self.updateOverscanValues())

        self.cameraUpdate_pushButton.clicked.connect(self.cameraUpdateClicked)
        self.markerGroupUpdate_pushButton.clicked.connect(self.markerGroupUpdateClicked)
        self.filepath_pushButton.clicked.connect(self.filePathBrowseClicked)
        self.filepath_lineEdit.editingFinished.connect(self.updateFilePathWidget)
        self.overscan_checkBox.toggled.connect(self.setOverscanEnabled)
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

        value = get_config_value(
            config,
            'data/load_bundle_position',
            const.LOAD_BUNDLE_POS_DEFAULT_VALUE)
        self.loadBndPositions_checkBox.setChecked(value)

        value = get_config_value(
            config,
            'data/use_overscan',
            const.USE_OVERSCAN_DEFAULT_VALUE)
        self.overscan_checkBox.setChecked(value)

        # Get the file path from the clipboard.
        try:
            clippy = QtGui.QClipboard()
            text = str(clippy.text()).strip()
            if lib.is_valid_file_path(text):
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
            active_camera
        )
        active_camera = self.getCameraData()
        mkr_grp_nodes = lib.get_marker_groups(active_camera)
        active_mkr_grp = None
        self.updateMarkerGroupList(
            self.markerGroup_comboBox,
            self.markerGroup_model,
            active_mkr_grp,
            mkr_grp_nodes
        )

        value = get_config_value(
            config,
            "data/load_mode",
            const.LOAD_MODE_DEFAULT_VALUE
        )
        self.populateLoadModeModel(self.loadMode_model)
        index = self.loadMode_model.stringList().index(value)
        self.loadMode_comboBox.setCurrentIndex(index)

        value = get_config_value(
            config,
            "data/distortion_mode",
            const.DISTORTION_MODE_DEFAULT_VALUE
        )
        self.populateDistortionModeModel(self.distortionMode_model)
        index = self.distortionMode_model.stringList().index(value)
        self.distortionMode_comboBox.setCurrentIndex(index)
        return

    def updateFileInfo(self):
        file_path = self.getFilePath()
        if not file_path:
            return
        file_info = lib.get_file_info(file_path)
        self.setFileInfo(file_info)
        return

    def updateFileInfoText(self):
        file_path = self.getFilePath()
        info_widget = self.fileInfo_plainTextEdit
        valid = lib.is_valid_file_path(file_path)
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
        info = lib.get_file_info_strings(file_path)

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
        return

    def updateOverscanValues(self):
        x = 100.0
        y = 100.0
        file_info = self.getFileInfo()
        camera = self.getCameraData()
        if file_info is not None and camera is not None:
            fovs = file_info.camera_field_of_view
            x, y = lib.calculate_overscan_ratio(camera, fovs)
            x *= 100.0
            y *= 100.0
        self.overscanX_doubleSpinBox.setValue(x)
        self.overscanY_doubleSpinBox.setValue(y)
        return

    def updateOverscanEnabledState(self):
        value = False
        file_info = self.getFileInfo()
        if file_info is not None:
            value = bool(file_info.camera_field_of_view)
        self.overscan_checkBox.setEnabled(value)
        self.overscanX_label.setEnabled(value)
        self.overscanX_doubleSpinBox.setEnabled(value)
        self.overscanY_label.setEnabled(value)
        self.overscanY_doubleSpinBox.setEnabled(value)
        return

    def updateDistortionModeEnabledState(self):
        value = False
        file_info = self.getFileInfo()
        if file_info is not None:
            value = (file_info.marker_distorted
                     and file_info.marker_undistorted)
        self.distortionMode_label.setEnabled(value)
        self.distortionMode_comboBox.setEnabled(value)
        return

    def updateLoadBundlePosEnabledState(self):
        value = False
        file_info = self.getFileInfo()
        if file_info is not None:
            value = file_info.bundle_positions
        self.loadBndPositions_checkBox.setEnabled(value)
        return

    def updateImageResEnabledState(self):
        value = False
        file_path = self.getFilePath()
        fmt = lib.get_file_path_format(file_path)
        if fmt is None:
            value = False
        else:
            for func_name, _ in fmt.args:
                value = func_name == 'image_width'
                break
        self.imageRes_label.setEnabled(value)
        self.imageResWidth_label.setEnabled(value)
        self.imageResWidth_spinBox.setEnabled(value)
        self.imageResHeight_label.setEnabled(value)
        self.imageResHeight_spinBox.setEnabled(value)
        return

    def updateCameraList(self, comboBox, model, all_camera_nodes, selected_cameras, active_camera):
        self.populateCameraModel(model, all_camera_nodes)
        index = self.getDefaultCameraIndex(self.camera_model,
                                           selected_cameras,
                                           active_camera)
        comboBox.setCurrentIndex(index)
        return

    def updateMarkerGroupList(self, comboBox, model, active_mkr_grp, mkr_grp_nodes):
        self.populateMarkerGroupModel(model, active_mkr_grp, mkr_grp_nodes)
        index = self.getDefaultMarkerGroupIndex(self.markerGroup_model, active_mkr_grp, mkr_grp_nodes)
        comboBox.setCurrentIndex(index)
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
        :type selected_cameras: list of mmSolver.api.Camera

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

    def cameraUpdateClicked(self):
        all_camera_nodes = lib.get_cameras()
        selected_cameras = lib.get_selected_cameras()
        active_camera = lib.get_active_viewport_camera()
        self.updateCameraList(
            self.camera_comboBox,
            self.camera_model,
            all_camera_nodes,
            selected_cameras,
            active_camera
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

    def filePathBrowseClicked(self):
        title = "Select Marker File..."
        file_filter = lib.get_file_filter()
        start_dir = lib.get_start_directory(self.getFilePath())
        result = QtWidgets.QFileDialog.getOpenFileName(
            self,
            title,
            start_dir,
            file_filter
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

    def setOverscanEnabled(self, value):
        assert isinstance(value, bool)
        self.overscanX_label.setEnabled(value)
        self.overscanX_doubleSpinBox.setEnabled(value)
        self.overscanY_label.setEnabled(value)
        self.overscanY_doubleSpinBox.setEnabled(value)
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

    def getLoadModeText(self):
        text = self.loadMode_comboBox.currentText()
        return text

    def getDistortionModeText(self):
        text = self.distortionMode_comboBox.currentText()
        return text

    def getOverscanValues(self):
        x = 1.0
        y = 1.0
        use_overscan = self.overscan_checkBox.isChecked()
        if use_overscan is True:
            x = self.overscanX_doubleSpinBox.value() * 0.01
            y = self.overscanY_doubleSpinBox.value() * 0.01
        return use_overscan, x, y

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
