"""
The main component of the user interface for the smooth keyframes
window.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.smoothkeyframes.ui.ui_smoothkeys_layout as ui_smoothkeys_layout
import mmSolver.tools.smoothkeyframes.constant as const
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.constant as utils_const


LOG = mmSolver.logger.get_logger()


class SmoothKeysLayout(QtWidgets.QWidget, ui_smoothkeys_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(SmoothKeysLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Function
        modes = [
            str(utils_const.SMOOTH_TYPE_AVERAGE).title(),
            str(utils_const.SMOOTH_TYPE_GAUSSIAN).title(),
            str(utils_const.SMOOTH_TYPE_FOURIER).title(),
        ]
        self.function_comboBox.addItems(modes)
        self.function_comboBox.currentIndexChanged.connect(
            self.modeIndexChanged
        )

        # Width
        self.width_horizontalSlider.valueChanged.connect(
            self.widthValueChanged
        )
        self.width_spinBox.valueChanged.connect(
            self.widthSpinBoxValueChanged
        )

        # Populate the UI with data
        self.populateUi()

    def modeIndexChanged(self, index):
        name = const.CONFIG_MODE_KEY
        value = utils_const.SMOOTH_TYPES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def widthValueChanged(self, value):
        self.width_spinBox.setValue(value)
        name = const.CONFIG_WIDTH_KEY
        value = float(value)
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def widthSpinBoxValueChanged(self, value):
        self.width_horizontalSlider.setValue(value)
        name = const.CONFIG_WIDTH_KEY
        value = float(value)
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def reset_options(self):
        name = const.CONFIG_MODE_KEY
        value = const.DEFAULT_MODE
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_WIDTH_KEY
        value = const.DEFAULT_WIDTH
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        self.populateUi()
        return

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        name = const.CONFIG_MODE_KEY
        value = configmaya.get_scene_option(
            name,
            default=const.DEFAULT_MODE)
        value = str(value).title()
        LOG.debug('key=%r value=%r', name, value)
        self.function_comboBox.setCurrentText(value)

        name = const.CONFIG_WIDTH_KEY
        value = configmaya.get_scene_option(
            name,
            default=const.DEFAULT_WIDTH)
        LOG.debug('key=%r value=%r', name, value)
        self.width_horizontalSlider.setValue(value)
        self.width_spinBox.setValue(value)
        return
