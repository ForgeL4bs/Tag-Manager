# Main menu UI hook
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QApplication, QMenuBar, QAction, QFileDialog
)
import sys
from ui.tagging_tab import TaggingTab
from ui.editor_tab import EditorTab
from ui.settings_dialog import SettingsDialog
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Waifu Diffusion Tagger")
        self.resize(1000, 600)

        self.model_paths = {
            "wd-vit-tagger-v3": Path("models/wd-vit-tagger-v3.onnx"),
            "wd-vit-large-tagger-v3": Path("models/wd-vit-large-tagger-v3.onnx")
        }

        self.tabs = QTabWidget()
        self.tagging_tab = TaggingTab(self.model_paths)
        self.editor_tab = EditorTab()

        self.tabs.addTab(self.tagging_tab, "Tagging")
        self.tabs.addTab(self.editor_tab, "Editor")
        self.setCentralWidget(self.tabs)

        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Settings")

        open_settings_action = QAction("Preferences", self)
        open_settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(open_settings_action)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
