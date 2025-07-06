# Tagging tab UI
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QComboBox,
    QTextEdit,
    QSlider,
    QFormLayout,
    QProgressBar,
    QCheckBox,
    QApplication,
    QLineEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from pathlib import Path
from PIL import Image
from tagger.model_runner import ONNXTagger
from tagger.selected_tags_loader import SelectedTagsLoader
import config_manager


class TaggingTab(QWidget):
    def __init__(self, model_paths: dict[str, Path], parent=None):
        super().__init__(parent)

        self.model_paths = model_paths
        self.tagger = None
        self.image_path = None
        self.label_list = []
        self.config = config_manager.ConfigManager()
        self.general_threshold = self.config.get("general_threshold", 0.35)
        self.character_threshold = self.config.get("character_threshold", 0.85)

        self.init_ui()

    def init_ui(self):
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(self.model_paths.keys())

        self.load_button = QPushButton("Load Image")
        self.tag_button = QPushButton("Tag Image")
        self.save_button = QPushButton("Save Tags")

        self.image_label = QLabel("No image loaded")
        self.image_label.setFixedSize(256, 256)
        self.image_label.setScaledContents(True)

        self.tag_output = QTextEdit()
        self.tag_output.setReadOnly(True)

        self.bulk_input = QLineEdit()
        self.bulk_input.setPlaceholderText("Select folder for bulk tagging...")
        self.bulk_browse = QPushButton("Browse")
        self.bulk_browse.clicked.connect(self.browse_bulk_folder)
        self.bulk_run = QPushButton("Run Bulk Tagging")
        self.bulk_run.clicked.connect(self.run_bulk_tagging)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate by default
        self.progress_bar.setVisible(False)

        self.mcut_checkbox = QCheckBox("Use MCut Thresholding")

        self.general_slider = QSlider(Qt.Horizontal)
        self.general_slider.setMinimum(0)
        self.general_slider.setMaximum(100)
        self.general_slider.setValue(int(self.general_threshold * 100))
        self.general_slider.setTickInterval(1)
        self.general_slider.valueChanged.connect(self.update_thresholds)

        self.character_slider = QSlider(Qt.Horizontal)
        self.character_slider.setMinimum(0)
        self.character_slider.setMaximum(100)
        self.character_slider.setValue(int(self.character_threshold * 100))
        self.character_slider.setTickInterval(1)
        self.character_slider.valueChanged.connect(self.update_thresholds)

        self.general_label = QLabel(f"General Threshold: {self.general_threshold:.2f}")
        self.character_label = QLabel(
            f"Character Threshold: {self.character_threshold:.2f}"
        )

        threshold_layout = QFormLayout()
        threshold_layout.addRow(self.general_label, self.general_slider)
        threshold_layout.addRow(self.character_label, self.character_slider)

        bulk_layout = QHBoxLayout()
        bulk_layout.addWidget(self.bulk_input)
        bulk_layout.addWidget(self.bulk_browse)
        bulk_layout.addWidget(self.bulk_run)

        layout = QVBoxLayout()
        top_row = QHBoxLayout()
        top_row.addWidget(self.model_dropdown)
        top_row.addWidget(self.load_button)
        top_row.addWidget(self.tag_button)
        top_row.addWidget(self.save_button)

        layout.addLayout(top_row)
        layout.addLayout(threshold_layout)
        layout.addWidget(self.image_label)
        layout.addWidget(QLabel("Tags:"))
        layout.addWidget(self.tag_output)
        layout.addWidget(self.mcut_checkbox)
        layout.addWidget(self.progress_bar)
        layout.addLayout(bulk_layout)
        self.setLayout(layout)

        self.load_button.clicked.connect(self.load_image)
        self.tag_button.clicked.connect(self.run_tagging)
        self.save_button.clicked.connect(self.save_tags)
        self.model_dropdown.currentTextChanged.connect(self.update_model)

        self.update_model(self.model_dropdown.currentText())

    def update_thresholds(self):
        self.general_threshold = self.general_slider.value() / 100
        self.character_threshold = self.character_slider.value() / 100
        self.general_label.setText(f"General Threshold: {self.general_threshold:.2f}")
        self.character_label.setText(
            f"Character Threshold: {self.character_threshold:.2f}"
        )
        if self.tagger:
            self.tagger.set_thresholds(self.general_threshold, self.character_threshold)

    def update_model(self, selected_model: str):
        model_path = self.model_paths[selected_model]
        csv_path = model_path.parent / "selected_tags.csv"
        loader = SelectedTagsLoader(csv_path)
        tag_names, rating_indexes, general_indexes, character_indexes = (
            loader.load_tags()
        )
        self.tagger = ONNXTagger(
            model_path,
            tag_names,
            rating_indexes,
            general_indexes,
            character_indexes,
            general_threshold=self.general_threshold,
            character_threshold=self.character_threshold,
        )

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(
                pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

    def run_tagging(self):
        if not self.image_path or not self.tagger:
            return
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)
        QApplication.processEvents()
        image = Image.open(self.image_path)
        general_mcut = self.mcut_checkbox.isChecked()
        character_mcut = self.mcut_checkbox.isChecked()
        sorted_general, rating, sorted_character, general_res = self.tagger.predict(
            image, general_mcut=general_mcut, character_mcut=character_mcut
        )
        # Combine general and character tags for output (like SmilingWolf)
        tags = sorted_general + sorted_character
        self.tag_output.setText(", ".join(tags))
        self.progress_bar.setVisible(False)

    def browse_bulk_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.bulk_input.setText(folder)

    def run_bulk_tagging(self):
        from bulk.bulk_processor import bulk_tag_images

        input_dir = Path(self.bulk_input.text())
        output_dir = input_dir  # Save .txt files in the same folder
        if not input_dir.exists():
            self.tag_output.setText("Invalid folder path.")
            return
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)
        QApplication.processEvents()
        results = bulk_tag_images(self.tagger, input_dir)
        self.progress_bar.setVisible(False)
        success = sum(1 for r in results if r[1])
        fail = len(results) - success
        self.tag_output.setText(
            f"Bulk tagging complete.\nSuccess: {success}, Failed: {fail}"
        )

    def save_tags(self):
        if not self.image_path:
            return
        tag_path = Path(self.image_path).with_suffix(".txt")
        with open(tag_path, "w", encoding="utf-8") as f:
            f.write(self.tag_output.toPlainText())
