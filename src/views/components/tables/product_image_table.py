"""
Product Image Table - Table widget for managing product images.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QFileDialog, QHeaderView, QAbstractItemView
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize


class ImageCellWidget(QWidget):
    """Widget for displaying/editing image in table cell."""
    
    image_changed = pyqtSignal(int, str)  # row, path
    
    def __init__(self, row: int, image_path: str = "", parent=None):
        super().__init__(parent)
        self.row = row
        self.image_path = image_path
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Thumbnail
        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(50, 50)
        self.thumbnail.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 4px;
            }
        """)
        self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_thumbnail()
        layout.addWidget(self.thumbnail)
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(2)
        
        btn_add = QPushButton("📷")
        btn_add.setFixedSize(28, 28)
        btn_add.setToolTip("Agregar/Cambiar imagen")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: rgba(10, 132, 255, 0.3);
                border: 1px solid #0A84FF;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(10, 132, 255, 0.5);
            }
        """)
        btn_add.clicked.connect(self._add_image)
        btn_layout.addWidget(btn_add)
        
        btn_remove = QPushButton("✕")
        btn_remove.setFixedSize(28, 28)
        btn_remove.setToolTip("Quitar imagen")
        btn_remove.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 69, 58, 0.3);
                border: 1px solid rgba(255, 69, 58, 0.5);
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 69, 58, 0.5);
            }
        """)
        btn_remove.clicked.connect(self._remove_image)
        btn_layout.addWidget(btn_remove)
        
        layout.addLayout(btn_layout)
    
    def _update_thumbnail(self):
        """Update the thumbnail display."""
        if self.image_path and os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            scaled = pixmap.scaled(
                46, 46,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.thumbnail.setPixmap(scaled)
        else:
            self.thumbnail.setText("📷")
            self.thumbnail.setStyleSheet("""
                QLabel {
                    background-color: rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.2);
                    border-radius: 4px;
                    color: rgba(255,255,255,0.4);
                    font-size: 18px;
                }
            """)
    
    def _add_image(self):
        """Open dialog to add image (Local or Internet)."""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Agregar Imagen")
        msg.setText("¿Cómo desea cargar la imagen?")
        msg.setIcon(QMessageBox.Icon.Question)
        
        btn_local = msg.addButton("📁 Desde Archivo PC", QMessageBox.ButtonRole.AcceptRole)
        btn_internet = msg.addButton("🌐 Buscar en Internet", QMessageBox.ButtonRole.ActionRole)
        btn_cancel = msg.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == btn_local:
            # Local File
            path, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar Imagen", "",
                "Imágenes (*.png *.jpg *.jpeg *.gif *.bmp *.webp)"
            )
            if path:
                self.image_path = path
                self._update_thumbnail()
                self.image_changed.emit(self.row, path)
                
        elif msg.clickedButton() == btn_internet:
            # Internet Search
            # Lazy import to avoid circular dependency issues
            try:
                from src.views.components.dialogs.image_search_dialog import ImageSearchDialog
                dlg = ImageSearchDialog(self)
                if dlg.exec():
                    path = dlg.selected_image_path
                    if path:
                        self.image_path = path
                        self._update_thumbnail()
                        self.image_changed.emit(self.row, path)
            except ImportError:
                 QMessageBox.warning(self, "Error", "No se pudo cargar el módulo de búsqueda.")
            except Exception as e:
                 QMessageBox.warning(self, "Error", f"Ocurrió un error: {e}")
    
    def _remove_image(self):
        """Remove the current image."""
        self.image_path = ""
        self._update_thumbnail()
        self.image_changed.emit(self.row, "")
    
    def set_image(self, path: str):
        """Set image path programmatically."""
        self.image_path = path
        self._update_thumbnail()


class ProductImageTable(QWidget):
    """
    Table widget for managing product images.
    Shows products with their images for the quotation.
    """
    
    images_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._product_images = {}  # row -> image_path
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("📦 Imágenes de Productos")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(header)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Producto", "Descripción", "Imagen"])
        
        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                gridline-color: rgba(255,255,255,0.1);
            }
            QTableWidget::item {
                padding: 8px;
                color: white;
            }
            QTableWidget::item:selected {
                background-color: rgba(10, 132, 255, 0.3);
            }
            QHeaderView::section {
                background-color: rgba(255,255,255,0.1);
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Column sizes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(2, 100)
        
        self.table.verticalHeader().setDefaultSectionSize(60)
        self.table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.table)
    
    def load_products(self, products: list):
        """
        Load products into the table.
        
        Args:
            products: List of product dicts with 'description', 'image_path', etc.
        """
        self.table.setRowCount(0)
        self._product_images.clear()
        
        for i, product in enumerate(products):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Product number
            num_item = QTableWidgetItem(f"#{i+1}")
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, num_item)
            
            # Description
            desc = product.get("description", "Sin descripción")
            desc_item = QTableWidgetItem(desc[:50] + "..." if len(desc) > 50 else desc)
            self.table.setItem(row, 1, desc_item)
            
            # Image widget
            image_path = product.get("image_path", "")
            image_widget = ImageCellWidget(row, image_path)
            image_widget.image_changed.connect(self._on_image_changed)
            self.table.setCellWidget(row, 2, image_widget)
            
            if image_path:
                self._product_images[row] = image_path
    
    def _on_image_changed(self, row: int, path: str):
        """Handle image change for a product."""
        if path:
            self._product_images[row] = path
        elif row in self._product_images:
            del self._product_images[row]
        self.images_changed.emit()
    
    def get_product_images(self) -> dict:
        """Get dict of row -> image_path for all products with images."""
        return self._product_images.copy()
    
    def get_image_for_product(self, index: int) -> str:
        """Get image path for a specific product index."""
        return self._product_images.get(index, "")
