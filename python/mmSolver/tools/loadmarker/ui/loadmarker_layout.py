"""
The main component of the user interface for the loadmarker window.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets


import mmSolver.logger
import mmSolver.ui.uimodels as uimodels
import mmSolver.tools.loadmarker.constant as const
import mmSolver.tools.loadmarker.ui.ui_loadmarker_layout as ui_loadmarker_layout
import mmSolver.tools.loadmarker.lib as lib


LOG = mmSolver.logger.get_logger()


class LoadMarkerLayout(QtWidgets.QWidget, ui_loadmarker_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(LoadMarkerLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # 'File Info' should be read-only.
        self.fileInfo_plainTextEdit.setReadOnly(True)

        # Camera combo box.
        self.camera_model = uimodels.StringDataListModel()
        self.camera_comboBox.setModel(self.camera_model)

        # Camera update.
        self.cameraUpdate_pushButton.clicked.connect(
            self.cameraUpdateClicked
        )

        # Set default image resolution values
        w, h = lib.get_default_image_resolution()
        self.imageResWidth_spinBox.setValue(w)
        self.imageResWidth_spinBox.setEnabled(False)
        self.imageResWidth_spinBox.setMaximum(99999)
        self.imageResHeight_spinBox.setValue(h)
        self.imageResHeight_spinBox.setEnabled(False)
        self.imageResHeight_spinBox.setMaximum(99999)

        # File path browse.
        self.filepath_pushButton.clicked.connect(
            self.filePathBrowseClicked
        )

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

        # Update the 'Image Resolution' enable state when the file
        # patch changes.
        self.filepath_lineEdit.editingFinished.connect(
            self.updateImageResEnabledState
        )

        # Update the 'File Info' when the file patch changes
        self.filepath_lineEdit.editingFinished.connect(
            self.updateFileInfoText
        )

        # Populate the UI with data
        self.populateUi()

    def populateUi(self):
        # Camera list
        selected_cameras = lib.get_selected_cameras()
        self.updateCameraList(
            self.camera_comboBox,
            self.camera_model,
            selected_cameras
        )
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
        text = 'Format: {fmt_name}\n'
        text += 'Frame Range: {start_frame}-{end_frame}\n'
        text += 'Number of Points: {num_points}\n'
        text += 'Point Names: {point_names}\n'
        info = lib.get_file_info(file_path)
        text = text.format(**info)
        info_widget.setPlainText(text)
        return

    def updateImageResEnabledState(self):
        value = False
        file_path = self.getFilePath()
        fmt = lib.get_file_path_format(file_path)
        if fmt is None:
            value = False
        else:
            for func_name, arg in fmt.args:
                value = func_name == 'image_width'
                break
        self.imageResWidth_spinBox.setEnabled(value)
        self.imageResHeight_spinBox.setEnabled(value)
        return

    def updateCameraList(self, comboBox, model, selected_cameras):
        self.populateCameraModel(model)
        index = self.getDefaultCameraIndex(self.camera_model, selected_cameras)
        comboBox.setCurrentIndex(index)
        return

    def populateCameraModel(self, model):
        """
        Add entries of cameras in the scene into the given camera model.

        :param model: The Qt model to add cameras to.
        :type model: QtCore.QStringListModel

        :return:
        """
        camera_nodes = lib.get_cameras()
        string_data_list = [(const.NEW_CAMERA_VALUE, None)]
        for camera_node in camera_nodes:
            if camera_node.is_valid() is False:
                LOG.warning('Camera node is not valid: %r', camera_node)
                continue
            node = camera_node.get_shape_node()
            string_data_list.append((node, camera_node))
        model.setStringDataList(string_data_list)
        return

    def getDefaultCameraIndex(self, model, selected_cameras):
        """
        Chooses the index in model based on the currently selected
        cameras.

        :param model: The Camera model.
        :type model: QtCore.QStringListModel

        :param selected_cameras: List of cameras that are selected.
        :type selected_cameras: list of mmSolver.api.Camera

        :return: index number as default item in camera list.
        :rtyle: int
        """
        string_data_list = model.stringDataList()
        if len(selected_cameras) == 0:
            return 0

        for cam in selected_cameras:
            if cam is None:
                continue
            nodes = [
                cam.get_transform_node(),
                cam.get_shape_node(),
            ]
            for i, (string, data) in enumerate(string_data_list):
                for node in nodes:
                    find = string.find(node)
                    if find != -1:
                        return i
        return 0

    def cameraUpdateClicked(self):
        selected_cameras = lib.get_selected_cameras()
        self.updateCameraList(
            self.camera_comboBox,
            self.camera_model,
            selected_cameras
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

    def setFilePath(self, value):
        self.filepath_lineEdit.setText(value)
        self.updateFileInfoText()
        self.updateImageResEnabledState()
        return

    def getFilePath(self):
        value = self.filepath_lineEdit.text()
        return str(value).strip()

    def getCameraText(self):
        text = self.camera_comboBox.currentText()
        return text

    def getCameraData(self):
        index = self.camera_comboBox.currentIndex()
        model_index = self.camera_model.index(index)
        data = self.camera_model.data(model_index, role=QtCore.Qt.UserRole)
        return data

    def getImageResolution(self):
        width = self.imageResWidth_spinBox.value()
        height = self.imageResHeight_spinBox.value()
        return width, height
