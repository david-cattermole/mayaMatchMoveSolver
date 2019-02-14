"""
The main component of the user interface for the channel sensitivity
window.
"""

import Qt.QtWidgets as QtWidgets


import mmSolver.logger
import mmSolver.tools.channelsen.ui.ui_channelsen_layout\
    as ui_channelsen_layout
import mmSolver.tools.channelsen.lib as lib


LOG = mmSolver.logger.get_logger()


class ChannelSenLayout(QtWidgets.QWidget, ui_channelsen_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(ChannelSenLayout, self).__init__(*args, **kwargs)
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
        value = lib.get_value()
        # Set the text of the label.
        self.setSensitivityText(str(value))
        return

    def upValueClicked(self):
        # Make increase the channel box sensitivity
        sensitivity = 10
        lib.set_value(sensitivity)
        value = lib.get_value()
        # ... and update the UI.
        self.setSensitivityText(str(value))

    def downValueClicked(self):
        # Make decrease the channel box sensitivity
        sensitivity = 0.1
        lib.set_value(sensitivity)
        value = lib.get_value()
        # ... and update the UI.
        self.setSensitivityText(str(value))

    def defaultValueClicked(self):
        # Make the channel box sensitivity default value.
        lib.set_default_value()
        value = lib.get_value()
        # ... and update the UI.
        self.setSensitivityText(str(value))
    
    def setSensitivityText(self, value):
        # Set the 'self.sensitivity_label' using the sensitivity value.
        self.sensitivity_label.setText(value)
        return
