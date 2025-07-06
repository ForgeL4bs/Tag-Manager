# Editor tab UI
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QListWidgetItem,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from pathlib import Path
import os


class EditorTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_folder = None
        self.image_files = []
        self.current_image_path = None
        self.tags_map = {}  # filename -> set of tags
        self.unsaved_changes = False
        self.init_ui()

    def init_ui(self):
        self.image_preview = QLabel("No image selected")
        self.image_preview.setMaximumSize(256, 256)
        self.image_preview.setAlignment(Qt.AlignCenter)

        self.image_list = QListWidget()
        self.tag_list = QListWidget()

        self.load_button = QPushButton("Open Folder")
        self.save_button = QPushButton("Save Changes")
        self.add_tag_input = QLineEdit()
        self.add_tag_button = QPushButton("Add Tag")
        self.remove_tag_button = QPushButton("Remove Selected Tag")
        self.remove_global_button = QPushButton("Delete Tag From All")

        self.add_tag_all_input = QLineEdit()
        self.add_tag_all_input.setPlaceholderText("Tag to add to all captions")
        self.add_tag_all_button = QPushButton("Add Tag to All")
        self.add_tag_all_button.clicked.connect(self.add_tag_to_all_captions)

        layout = QVBoxLayout()
        # Column 1: Preview
        preview_col = QVBoxLayout()
        preview_col.addWidget(QLabel("Preview:"))
        preview_col.addWidget(self.image_preview, stretch=1)

        # Column 2: Images
        images_col = QVBoxLayout()
        images_col.addWidget(QLabel("Images:"))
        images_col.addWidget(self.image_list, stretch=1)

        # Column 3: Tags
        tags_col = QVBoxLayout()
        tags_col.addWidget(QLabel("Tags:"))
        tags_col.addWidget(self.tag_list, stretch=1)

        # Main row
        top_row = QHBoxLayout()
        top_row.addLayout(preview_col, stretch=1)
        top_row.addLayout(images_col)
        top_row.addLayout(tags_col)
        layout.addLayout(top_row)

        controls = QHBoxLayout()
        controls.addWidget(self.load_button)
        controls.addWidget(self.save_button)
        controls.addWidget(self.add_tag_input)
        controls.addWidget(self.add_tag_button)
        controls.addWidget(self.remove_tag_button)
        controls.addWidget(self.remove_global_button)
        controls.addWidget(self.add_tag_all_input)
        controls.addWidget(self.add_tag_all_button)
        layout.addLayout(controls)

        self.setLayout(layout)

        self.load_button.clicked.connect(self.select_folder)
        self.image_list.currentItemChanged.connect(self.load_selected_image)
        self.add_tag_button.clicked.connect(self.add_tag)
        self.remove_tag_button.clicked.connect(self.remove_tag)
        self.remove_global_button.clicked.connect(self.delete_tag_globally)
        self.save_button.clicked.connect(self.save_all_tags)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.image_folder = Path(folder)
            self.image_files = sorted(
                p
                for p in self.image_folder.iterdir()
                if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
            )
            self.tags_map = {}
            self.image_list.clear()
            for file in self.image_files:
                self.image_list.addItem(file.name)
                txt_path = file.with_suffix(".txt")
                if txt_path.exists():
                    with open(txt_path, "r", encoding="utf-8") as f:
                        tags = {
                            tag.strip() for tag in f.read().split(",") if tag.strip()
                        }
                        self.tags_map[file.name] = tags
                else:
                    self.tags_map[file.name] = set()

    def load_selected_image(self, current: QListWidgetItem):
        if not current:
            return
        filename = current.text()
        self.current_image_path = self.image_folder / filename
        pixmap = QPixmap(str(self.current_image_path))
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.image_preview.width(),
                self.image_preview.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.image_preview.setPixmap(scaled_pixmap)
        else:
            self.image_preview.setText("Cannot load image")
        self.update_tag_list(filename)

    def update_tag_list(self, filename):
        self.tag_list.clear()
        for tag in sorted(self.tags_map.get(filename, [])):
            self.tag_list.addItem(tag)

    def add_tag(self):
        tag = self.add_tag_input.text().strip()
        if not tag:
            return
        filename = self.current_image_path.name
        self.tags_map[filename].add(tag)
        self.update_tag_list(filename)
        self.add_tag_input.clear()
        self.unsaved_changes = True

    def add_tag_to_all_captions(self):
        tag = self.add_tag_all_input.text().strip()
        if not tag:
            QMessageBox.warning(self, "No Tag", "Please enter a tag to add.")
            return

        added_count = 0
        for image_file in self.image_files:
            tags = self.tags_map.get(image_file.name, set())
            if tag not in tags:
                tags.add(tag)
                self.tags_map[image_file.name] = tags
                added_count += 1
                self.unsaved_changes = True

        # Refresh tag list if current image is shown
        if self.current_image_path:
            self.update_tag_list(self.current_image_path.name)

        QMessageBox.information(self, "Done", f"Added tag '{tag}' to {added_count} images.")
        self.add_tag_all_input.clear()

    def remove_tag(self):
        selected_items = self.tag_list.selectedItems()
        if not selected_items:
            return
        filename = self.current_image_path.name
        for item in selected_items:
            self.tags_map[filename].discard(item.text())
            self.unsaved_changes = True
        self.update_tag_list(filename)

    def delete_tag_globally(self):
        selected_items = self.tag_list.selectedItems()
        if not selected_items:
            return
        tag_to_remove = selected_items[0].text()
        for filename in self.tags_map:
            self.tags_map[filename].discard(tag_to_remove)
            self.unsaved_changes = True
        self.update_tag_list(self.current_image_path.name)

    def save_all_tags(self):
        for file in self.image_files:
            tags = self.tags_map.get(file.name, set())
            txt_path = file.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(", ".join(sorted(tags)))
        self.unsaved_changes = False
        QMessageBox.information(self, "Success", "All tags saved.")
