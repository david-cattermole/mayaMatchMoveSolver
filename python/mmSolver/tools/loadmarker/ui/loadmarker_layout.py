"""
The main component of the user interface for the loadmarker window.
"""

import os
import sys
import time
from functools import partial

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets


import mmSolver.logger
import mmSolver.ui.uimodels as uimodels
import mmSolver.tools.loadmarker.constant as const
import mmSolver.tools.loadmarker.ui.ui_loadmarker_layout as ui_loadmarker_layout
import mmSolver.tools.loadmarker.formatmanager as formatmanager
import mmSolver.tools.loadmarker.tool as tool


LOG = mmSolver.logger.get_logger()


class LoadMarkerLayout(QtWidgets.QWidget, ui_loadmarker_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(LoadMarkerLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Get the file path from the clipboard.
        clippy = QtGui.QClipboard()
        text = str(clippy.text()).strip()
        if tool.is_valid_file_path(text):
            self.filepath_lineEdit.setText(text)

        # Camera combo box.
        # self.camera_model = QtCore.QStringListModel()
        self.camera_model = uimodels.StringDataListModel()
        self.camera_comboBox.setModel(self.camera_model)

        # Camera update.
        self.cameraUpdate_pushButton.clicked.connect(self.cameraUpdateClicked)

        # File path browse.
        self.filepath_pushButton.clicked.connect(self.filePathBrowseClicked)

        # Populate the UI with data
        self.populateUi()

    def populateUi(self):
        # Camera list
        selected_cameras = tool.get_selected_cameras()
        self.updateCameraList(
            self.camera_comboBox,
            self.camera_model,
            selected_cameras
        )
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
        camera_nodes = tool.get_cameras()
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

    def getFileFilter(self):
        """
        Construct a string to be given to QFileDialog as a file filter.

        :return: String of file filters, separated by ';;' characters.
        :rtype: str
        """
        file_fmt_names = []
        file_exts = []
        fmt_mgr = formatmanager.get_format_manager()
        fmts = fmt_mgr.get_formats()
        for fmt in fmts:
            file_fmt_names.append(fmt.name)
            file_exts += fmt.file_exts
        file_fmt_names = sorted(file_fmt_names)
        file_exts = sorted(file_exts)

        extensions_str = ''
        for file_ext in file_exts:
            extensions_str += '*' + file_ext + ' '

        file_filter = 'Marker Files (%s);;' % extensions_str
        for name in file_fmt_names:
            name = name + ';;'
            file_filter += name
        file_filter += 'All Files (*.*);;'
        return file_filter

    def getStartDirectory(self, file_path):
        """
        Get a start directory for a file browser window.

        :param file_path: An input
        :return:
        """
        if isinstance(file_path, (str, unicode)) is False:
            msg = 'file_path must be a string.'
            raise TypeError(msg)
        start_dir = os.getcwd()
        file_path = str(file_path).strip()
        if len(file_path) > 0:
            head, tail = os.path.split(file_path)
            if os.path.isdir(head) is True:
                start_dir = head
        return start_dir

    def cameraUpdateClicked(self):
        selected_cameras = tool.get_selected_cameras()
        self.updateCameraList(
            self.camera_comboBox,
            self.camera_model,
            selected_cameras
        )
        return

    def filePathBrowseClicked(self):
        title = "Select Marker File..."
        file_filter = self.getFileFilter()
        start_dir = self.getStartDirectory(self.getFilePath())

        result = QtWidgets.QFileDialog.getOpenFileName(
            self,
            title,
            start_dir,
            file_filter
        )
        if result is not None:
            file_path = result[0]
            self.filepath_lineEdit.setText(file_path)
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
        LOG.debug('self.camera_model.data(): %r', data)
        return data
