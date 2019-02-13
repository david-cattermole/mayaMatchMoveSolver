"""
The main component of the user interface for the channel sensitivity
window.
"""

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets


import mmSolver.logger
import mmSolver.tools.channelsensitivity.ui.ui_channelsensitivity_layout\
    as ui_channelsensitivity_layout
import mmSolver.tools.channelsensitivity.lib as lib


LOG = mmSolver.logger.get_logger()


class ChannelSensitivityLayout(QtWidgets.QWidget, ui_channelsensitivity_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(ChannelSensitivityLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Connect Buttons
        self.up_pushButton.clicked.connect(
            self.upValueClicked
        )
        self.down_pushButton.clicked.connect(
            self.downValueClicked
        )
        self.default_pushButton.clicked.connect(
            self.defaultValueClicked
        )

        # Populate the UI with data
        self.populateUi()

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        # Query the channel box sensitivity (using a "lib." function).
        value = lib.get_channel_sensitivity()
        # Set the text of the label.
        self.setSensitivityText(str(value))
        return

    def upValueClicked(self):
        # Make increase the channel box sensitivity
        value = lib.get_channel_sensitivity()
        if value >= 10.0:
            return
        sensitivity = 10
        lib.set_value(sensitivity)
        value = lib.get_channel_sensitivity()
        # ... and update the UI.
        self.setSensitivityText(str(value))

    def downValueClicked(self):
        # Make decrease the channel box sensitivity
        value = lib.get_channel_sensitivity()
        if value <= 0.001:
            return
        sensitivity = 0.1
        lib.set_value(sensitivity)
        value = lib.get_channel_sensitivity()
        # ... and update the UI.
        self.setSensitivityText(str(value))

    def defaultValueClicked(self):
        # Make the channel box sensitivity default value.
        lib.set_default_value()
        value = lib.get_channel_sensitivity()
        
        # ... and update the UI.
        self.setSensitivityText(str(value))
    
    def setSensitivityText(self, value):
        # Set the 'self.sensitivity_label' using the sensitivity value.
        self.sensitivity_label.setText(value)
        return
