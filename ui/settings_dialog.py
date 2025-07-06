# Settings dialog
from PySide6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QCheckBox, QPushButton
)
import config_manager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.config = config_manager.ConfigManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setSingleStep(0.01)
        self.threshold_spin.setValue(self.config.get("threshold"))

        self.include_rating = QCheckBox("Include Rating Tags")
        self.include_rating.setChecked(self.config.get("include_rating"))

        self.character_first = QCheckBox("Prioritize Character Tags")
        self.character_first.setChecked(self.config.get("character_first"))

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)

        layout.addWidget(QLabel("Confidence Threshold:"))
        layout.addWidget(self.threshold_spin)
        layout.addWidget(self.include_rating)
        layout.addWidget(self.character_first)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save_settings(self):
        self.config.set("threshold", self.threshold_spin.value())
        self.config.set("include_rating", self.include_rating.isChecked())
        self.config.set("character_first", self.character_first.isChecked())
        self.accept()

