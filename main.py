# Entry point
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QApplication,
    QMessageBox,
)
import sys
from ui.tagging_tab import TaggingTab
from ui.editor_tab import EditorTab
from ui.settings_tab import SettingsTab
from pathlib import Path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Waifu Diffusion Tagger")
        self.resize(1000, 600)

        self.model_paths = {
            "wd-vit-tagger-v3": Path("models/wd-vit-tagger-v3.onnx"),
            "wd-vit-large-tagger-v3": Path("models/wd-vit-large-tagger-v3.onnx"),
        }

        self.tabs = QTabWidget()
        self.tagging_tab = TaggingTab(self.model_paths)
        self.editor_tab = EditorTab()
        self.settings_tab = SettingsTab()

        self.tabs.addTab(self.tagging_tab, "Tagging")
        self.tabs.addTab(self.editor_tab, "Editor")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.setCentralWidget(self.tabs)

    def closeEvent(self, event):
        if self.editor_tab.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes in the Editor tab. Do you want to save before exiting?",
                QMessageBox.Save | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            if reply == QMessageBox.Save:
                self.editor_tab.save_all_tags()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
