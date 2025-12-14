"""
Drag & Drop Canvas Component for adding text and images to quotations.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QFileDialog, QFrame, QSizePolicy, QTextEdit,
    QGridLayout, QMessageBox
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QSize


class ImageBlock(QFrame):
    """A draggable/deletable image block for the canvas."""
    
    removed = pyqtSignal(object)
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        
        self.setFrameShape(QFrame.Shape.Box)
        self.setStyleSheet("""
            ImageBlock {
                background-color: rgba(255,255,255,0.05);
                border: 2px dashed rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 8px;
            }
            ImageBlock:hover {
                border-color: #0A84FF;
                background-color: rgba(10, 132, 255, 0.1);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(150, 100)
        self.image_label.setMaximumSize(300, 200)
        self._load_image(image_path)
        layout.addWidget(self.image_label)
        
        # Caption
        self.caption = QTextEdit()
        self.caption.setPlaceholderText("Escriba una descripción...")
        self.caption.setMaximumHeight(60)
        self.caption.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.caption)
        
        # Delete button
        btn_delete = QPushButton("❌ Eliminar")
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 69, 58, 0.3);
                border: 1px solid rgba(255, 69, 58, 0.5);
                border-radius: 4px;
                color: white;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 69, 58, 0.6);
            }
        """)
        btn_delete.clicked.connect(self._on_delete)
        layout.addWidget(btn_delete)
    
    def _load_image(self, path: str):
        """Load and display the image."""
        if os.path.exists(path):
            pixmap = QPixmap(path)
            scaled = pixmap.scaled(
                280, 180, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
    
    def _on_delete(self):
        """Handle delete button click."""
        self.removed.emit(self)
    
    def get_data(self) -> dict:
        """Get the image block data."""
        return {
            "path": self.image_path,
            "caption": self.caption.toHtml()
        }
    
    def set_caption(self, text: str):
        """Set the caption text."""
        self.caption.setHtml(text)


class TextBlock(QFrame):
    """A text block for notes and descriptions."""
    
    removed = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFrameShape(QFrame.Shape.Box)
        self.setStyleSheet("""
            TextBlock {
                background-color: rgba(255,255,255,0.05);
                border: 2px dashed rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 8px;
            }
            TextBlock:hover {
                border-color: #34C759;
                background-color: rgba(52, 199, 89, 0.1);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Header
        header = QLabel("📝 Nota de Texto")
        header.setStyleSheet("font-weight: bold; color: #34C759;")
        layout.addWidget(header)
        
        # Text area
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Escriba su nota aquí...")
        self.text_edit.setMinimumHeight(80)
        self.text_edit.setMaximumHeight(150)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                color: white;
            }
        """)
        layout.addWidget(self.text_edit)
        
        # Delete button
        btn_delete = QPushButton("❌ Eliminar")
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 69, 58, 0.3);
                border: 1px solid rgba(255, 69, 58, 0.5);
                border-radius: 4px;
                color: white;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 69, 58, 0.6);
            }
        """)
        btn_delete.clicked.connect(self._on_delete)
        layout.addWidget(btn_delete)
    
    def _on_delete(self):
        """Handle delete button click."""
        self.removed.emit(self)
    
    def get_data(self) -> dict:
        """Get the text block data."""
        return {
            "type": "text",
            "content": self.text_edit.toHtml()
        }
    
    def set_text(self, text: str):
        """Set the text content."""
        self.text_edit.setHtml(text)


class DropCanvas(QScrollArea):
    """
    A canvas widget that accepts drag & drop for images and text.
    Displays blocks in a grid layout.
    """
    
    content_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.blocks = []
        
        # Setup scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Main container
        self.container = QWidget()
        self.setWidget(self.container)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setSpacing(16)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        btn_add_image = QPushButton("🖼️ Agregar Imagen")
        btn_add_image.setStyleSheet("""
            QPushButton {
                background-color: rgba(10, 132, 255, 0.3);
                border: 1px solid #0A84FF;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(10, 132, 255, 0.5);
            }
        """)
        btn_add_image.clicked.connect(self._add_image_dialog)
        toolbar.addWidget(btn_add_image)
        
        btn_add_text = QPushButton("📝 Agregar Nota")
        btn_add_text.setStyleSheet("""
            QPushButton {
                background-color: rgba(52, 199, 89, 0.3);
                border: 1px solid #34C759;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(52, 199, 89, 0.5);
            }
        """)
        btn_add_text.clicked.connect(self._add_text_block)
        toolbar.addWidget(btn_add_text)
        
        toolbar.addStretch()
        
        btn_clear = QPushButton("🗑️ Limpiar Todo")
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 69, 58, 0.3);
                border: 1px solid rgba(255, 69, 58, 0.5);
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 69, 58, 0.5);
            }
        """)
        btn_clear.clicked.connect(self._clear_all)
        toolbar.addWidget(btn_clear)
        
        self.main_layout.addLayout(toolbar)
        
        # Grid container for blocks
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.grid_widget)
        
        # Add stretch at the end
        self.main_layout.addStretch()
        
        # Enable drag & drop
        self.setAcceptDrops(True)
        
        # Styling
        self.setStyleSheet("""
            DropCanvas {
                background-color: rgba(0, 0, 0, 0.2);
                border: 2px dashed rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag events with URLs (files)."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle dropped files."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                self._add_image_block(file_path)
        event.acceptProposedAction()
    
    def _add_image_dialog(self):
        """Open file dialog to add image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "",
            "Imágenes (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if file_path:
            self._add_image_block(file_path)
    
    def _add_image_block(self, image_path: str):
        """Add an image block to the canvas."""
        block = ImageBlock(image_path)
        block.removed.connect(self._remove_block)
        self.blocks.append(block)
        self._reorganize_grid()
        self.content_changed.emit()
    
    def _add_text_block(self):
        """Add a text block to the canvas."""
        block = TextBlock()
        block.removed.connect(self._remove_block)
        self.blocks.append(block)
        self._reorganize_grid()
        self.content_changed.emit()
    
    def _remove_block(self, block):
        """Remove a block from the canvas."""
        if block in self.blocks:
            self.blocks.remove(block)
            block.deleteLater()
            self._reorganize_grid()
            self.content_changed.emit()
    
    def _reorganize_grid(self):
        """Reorganize blocks in the grid (2 columns)."""
        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Add blocks to grid
        for i, block in enumerate(self.blocks):
            row = i // 2
            col = i % 2
            self.grid_layout.addWidget(block, row, col)
    
    def _clear_all(self):
        """Clear all blocks."""
        if not self.blocks:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar",
            "¿Está seguro de eliminar todos los elementos?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for block in self.blocks[:]:
                block.deleteLater()
            self.blocks.clear()
            self._reorganize_grid()
            self.content_changed.emit()
    
    def get_all_data(self) -> list:
        """Get data from all blocks."""
        data = []
        for block in self.blocks:
            if isinstance(block, ImageBlock):
                d = block.get_data()
                d["type"] = "image"
                data.append(d)
            elif isinstance(block, TextBlock):
                data.append(block.get_data())
        return data
    
    def load_data(self, data: list):
        """Load blocks from saved data."""
        self._clear_all_silent()
        
        for item in data:
            if item.get("type") == "image":
                if os.path.exists(item.get("path", "")):
                    block = ImageBlock(item["path"])
                    block.set_caption(item.get("caption", ""))
                    block.removed.connect(self._remove_block)
                    self.blocks.append(block)
            elif item.get("type") == "text":
                block = TextBlock()
                block.set_text(item.get("content", ""))
                block.removed.connect(self._remove_block)
                self.blocks.append(block)
        
        self._reorganize_grid()
    
    def _clear_all_silent(self):
        """Clear all blocks without confirmation."""
        for block in self.blocks[:]:
            block.deleteLater()
        self.blocks.clear()
