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

        # Width
        self.width_horizontalSlider.valueChanged.connect(
            self.widthValueChanged
        )
        self.width_spinBox.valueChanged.connect(
            self.widthSpinBoxValueChanged
        )

        # Blend Width 
        self.blendWidth_horizontalSlider.valueChanged.connect(
            self.blendWidthValueChanged
        )
        self.blendWidth_spinBox.valueChanged.connect(
            self.blendWidthSpinBoxValueChanged
        )

        # Populate the UI with data
        self.populateUi()

    def widthValueChanged(self, value):
        self.width_spinBox.setValue(value)

    def widthSpinBoxValueChanged(self, value):
        self.width_horizontalSlider.setValue(value)

    def blendWidthValueChanged(self, value):
        self.blendWidth_spinBox.setValue(value)

    def blendWidthSpinBoxValueChanged(self, value):
        self.blendWidth_horizontalSlider.setValue(value)

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        mode = str(const.DEFAULT_MODE).title()
        width = const.DEFAULT_WIDTH
        blendWidth = const.DEFAULT_BLEND_WIDTH
        self.function_comboBox.setCurrentText(mode)
        self.width_horizontalSlider.setValue(width)
        self.width_spinBox.setValue(width)
        self.blendWidth_horizontalSlider.setValue(blendWidth)
        self.blendWidth_spinBox.setValue(blendWidth)
        return
