from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton, QMessageBox
import config_manager

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = config_manager.ConfigManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.include_rating = QCheckBox("Include Rating Tags")
        self.include_rating.setChecked(self.config.get("include_rating", False))

        self.exclude_character = QCheckBox("Exclude Character Tags")
        self.exclude_character.setChecked(self.config.get("exclude_character", False))

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)

        layout.addWidget(self.include_rating)
        layout.addWidget(self.exclude_character)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_settings(self):
        self.config.set("include_rating", self.include_rating.isChecked())
        self.config.set("exclude_character", self.exclude_character.isChecked())
        QMessageBox.information(self, "Settings", "Settings saved!")