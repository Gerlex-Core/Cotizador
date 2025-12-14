"""
Observations Window - Separate window for managing quotation observations.
Uses reorderable blocks system for professional APA-style formatting.
Auto-saves on close.
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QTextEdit, QPushButton, QTabWidget, QScrollArea,
    QFileDialog, QFrame, QSplitter, QMessageBox, QSizePolicy
)
from PyQt6.QtGui import (
    QPixmap, QFont, QIcon, QColor, QBrush, QPainter, QPen, 
    QTextDocument, QTextOption, QImage
)
from PyQt6.QtCore import QRect
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import json
from typing import List

from .components.widgets.preview_widget import PreviewWidget
from .components.block.reorderable_blocks import BlockContainer, ProductMatrixBlock
from .components.notification.toast_notification import ToastNotification
from .styles.theme_manager import ThemeManager
from ..logic.config.config_manager import ConfigManager


class ObservationsWindow(QDialog):
    """
    Separate window for managing quotation observations.
    Features:
    - Reorderable blocks system (titles, notes, product matrix, images, separators)
    - Product images table
    - PDF preview with fullscreen
    - Auto-save on close
    - Professional APA-style formatting (no emojis)
    """
    
    data_saved = pyqtSignal(dict)  # Emitted when data is saved
    
    def __init__(self, products: list = None, observations_data: dict = None, parent=None):
        super().__init__(parent)
        
        self._products = products or []
        self._observations_data = observations_data or {}
        self._is_modified = False
        self._last_modification = None
        self._preview_callback = None
        self.title_styles = self._load_title_styles()
        
        # Auto-update preview timer
        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._refresh_preview)
        
        self._setup_window()
        try:
            self._create_ui()
            self._load_data()
        except Exception as e:
            import traceback
            error_msg = f"Error al inicializar la ventana:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Error de Inicialización", error_msg)
        
        self._setup_auto_save()
        
    def _load_title_styles(self):
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logic", "config", "title_styles.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("styles", [])
        except: pass
        return []
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Observaciones y Detalles")
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )
        self.setMinimumSize(950, 700)
        self.resize(1150, 850)
        
        # Apply theme
        config = ConfigManager()
        ThemeManager.apply_theme(self, config.tema)
    
    def _create_ui(self):
        """Create the main UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
            QSplitter::handle:hover {
                background-color: rgba(10, 132, 255, 0.3);
            }
        """)
        
        # Left panel: Observations blocks
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Preview
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([750, 350])
        
        main_layout.addWidget(splitter, 1)
        
        # Footer with buttons
        footer = self._create_footer()
        main_layout.addWidget(footer)
    
    def _create_header(self) -> QWidget:
        """Create header section."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 10)
        
        title = QLabel("Observaciones y Detalles de la Cotizacion")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Help button
        btn_help = QPushButton("?")
        btn_help.setFixedSize(28, 28)
        btn_help.setStyleSheet("""
            QPushButton {
                background-color: rgba(10, 132, 255, 0.3);
                border: 1px solid #0A84FF;
                border-radius: 14px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(10, 132, 255, 0.5);
            }
        """)
        btn_help.setToolTip("Ayuda: Use los botones para agregar bloques. Use las flechas para reordenarlos.")
        layout.addWidget(btn_help)
        
        # Status indicator
        self.status_label = QLabel("Sin cambios")
        self.status_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 12px;
            padding: 4px 8px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        """)
        layout.addWidget(self.status_label)
        
        return header
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with tabs."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                background-color: rgba(0,0,0,0.2);
            }
            QTabBar::tab {
                background-color: rgba(255,255,255,0.05);
                color: white;
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: rgba(10, 132, 255, 0.4);
                border-bottom: 2px solid #0A84FF;
            }
            QTabBar::tab:hover {
                background-color: rgba(255,255,255,0.1);
            }
        """)
        
        # Tab 1: Reorderable blocks
        self.tabs.addTab(self._create_blocks_tab(), "Bloques de Contenido")
        
        layout.addWidget(self.tabs)
        
        return panel
    
    def _create_blocks_tab(self) -> QWidget:
        """Create reorderable blocks tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Info label
        info = QLabel(
            "Agregue y organice bloques de contenido. Use las flechas para reordenar. "
            "El orden aqui determina el orden en el PDF."
        )
        info.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 11px; padding: 5px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Block container
        self.block_container = BlockContainer()
        self.block_container.set_products(self._products)
        self.block_container.content_changed.connect(self._mark_modified)
        self.block_container.image_warning.connect(self._show_image_warning)
        layout.addWidget(self.block_container, 1)
        
        # Initialize toast notification for image warnings
        self.toast = ToastNotification(self)
        
        return tab
    

    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with preview."""
        panel = QWidget()
        panel.setMinimumWidth(280)
        # panel.setMaximumWidth(450) # Allow preview to expand
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 0, 0, 0)
        
        # Preview widget
        self.preview_widget = PreviewWidget()
        self.preview_widget.set_generate_callback(self._generate_preview)
        layout.addWidget(self.preview_widget)
        
        return panel
    
    def _create_footer(self) -> QWidget:
        """Create footer with buttons."""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Info about auto-save
        auto_save_info = QLabel("Los cambios se guardan automaticamente al cerrar")
        auto_save_info.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px;")
        layout.addWidget(auto_save_info)
        
        layout.addStretch()
        
        # Cancel button
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                color: white;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        btn_cancel.clicked.connect(self._on_cancel)
        layout.addWidget(btn_cancel)
        
        # Save button
        btn_save = QPushButton("Guardar y Cerrar")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: rgba(52, 199, 89, 0.3);
                border: 1px solid #34C759;
                border-radius: 6px;
                color: white;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(52, 199, 89, 0.5);
            }
        """)
        btn_save.clicked.connect(self._save_and_close)
        layout.addWidget(btn_save)
        
        return footer
    
    def _setup_auto_save(self):
        """Setup auto-save detection."""
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setInterval(500)  # Check every 500ms
        self._auto_save_timer.timeout.connect(self._check_auto_save)
    
    def _mark_modified(self):
        """Mark as modified."""
        self._is_modified = True
        self._last_modification = datetime.now()
        self.status_label.setText("Cambios sin guardar")
        self.status_label.setStyleSheet("""
            color: #FF9F0A;
            font-size: 12px;
            padding: 4px 8px;
            background-color: rgba(255, 159, 10, 0.2);
            border-radius: 4px;
        """)
        self._preview_timer.start(800) # Trigger preview update

    def _refresh_preview(self):
        """Trigger preview widget update."""
        if hasattr(self, 'preview_widget'):
            self.preview_widget._on_generate_clicked()
    
    def _check_auto_save(self):
        """Check if we should trigger auto-save (not used currently)."""
        pass
    
    def _show_image_warning(self, title: str, message: str):
        """Show image resolution warning toast."""
        if hasattr(self, 'toast'):
            self.toast.show_toast(title, message, self, duration=6000, type="warning")
    
    def _load_data(self):
        """Load existing data into UI."""
        # Load blocks data
        if "blocks" in self._observations_data:
            self.block_container.load_data(self._observations_data["blocks"])
        # Legacy: load from old format
        elif "text" in self._observations_data or "gallery" in self._observations_data:
            # Convert old format to new blocks
            self._convert_legacy_data()
        
        # Check if we need to auto-add a Matrix block
        # If we have products but no blocks (or no matrix block), add one for convenience
        has_matrix = any(b.get("type", "") == "product_matrix" for b in self.block_container.get_all_data())
        
        if self._products and not has_matrix:
            # Create a default matrix block with current products
            matrix = ProductMatrixBlock(self._products)
            self.block_container._add_block(matrix)

        # Reset modified state after loading
        self._is_modified = False
        self.status_label.setText("Sin cambios")
        self.status_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 12px;
            padding: 4px 8px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        """)
    
    def _convert_legacy_data(self):
        """Convert legacy observations format to new blocks format."""
        blocks_data = []
        
        # Convert text to note block
        if self._observations_data.get("text", "").strip():
            blocks_data.append({
                "type": "note",
                "order": 1,
                "content": self._observations_data["text"]
            })
        
        # Convert gallery items
        for item in self._observations_data.get("gallery", []):
            if item.get("type") == "image":
                blocks_data.append({
                    "type": "image",
                    "order": len(blocks_data) + 1,
                    "path": item.get("path", ""),
                    "caption": item.get("caption", "")
                })
            elif item.get("type") == "text":
                blocks_data.append({
                    "type": "note",
                    "order": len(blocks_data) + 1,
                    "content": item.get("content", "")
                })
        
        if blocks_data:
            self.block_container.load_data(blocks_data)
    
    def _collect_data(self) -> dict:
        """Collect all data from UI."""
        # Get blocks data
        blocks_data = self.block_container.get_all_data()
        
        # Find images in Matrix blocks to update main product list
        updated_products = []
        image_map = {} # desc -> image_path
        
        # First pass: collect images from all matrix blocks
        for block_data in blocks_data:
             if block_data.get("type") == "product_matrix":
                 for prod in block_data.get("products", []):
                     if prod.get("image_path"):
                         image_map[prod.get("description")] = prod.get("image_path")

        # Second pass: update product list
        for product in self._products:
            p = product.copy()
            # If we found an image for this product in the matrix, update it
            if p.get("description") in image_map:
                p["image_path"] = image_map[p.get("description")]
            updated_products.append(p)
        
        return {
            "blocks": blocks_data,
            "products": updated_products
        }
    
    def _generate_preview(self) -> List[QPixmap]:
        """Generate multi-page preview using the actual PDF generator and PyMuPDF."""
        pages = []
        
        try:
            data = self._collect_data()
            blocks = data.get("blocks", [])
            
            if not blocks:
                # Return empty placeholder page
                pix = QPixmap(500, 700)
                pix.fill(QColor(255, 255, 255))
                p = QPainter(pix)
                p.setFont(QFont("Arial", 14))
                p.setPen(QColor(150, 150, 150))
                p.drawText(QRect(0, 0, 500, 700), Qt.AlignmentFlag.AlignCenter, "Sin contenido")
                p.end()
                return [pix]
            
            # Use PDF Generator to create PDF in memory
            from ..export.pdf_generator import PDFGenerator
            
            generator = PDFGenerator()
            pdf_bytes = generator.generate_preview_pdf(blocks, "")
            
            # Use PyMuPDF (fitz) to render PDF to images
            try:
                import fitz  # PyMuPDF
            except ImportError:
                # Fallback if fitz not installed - show error message
                pix = QPixmap(500, 700)
                pix.fill(QColor(255, 255, 255))
                p = QPainter(pix)
                p.setFont(QFont("Arial", 12))
                p.setPen(QColor(255, 0, 0))
                p.drawText(QRect(20, 20, 460, 660), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, 
                          "PyMuPDF no está instalado.\nEjecuta: pip install PyMuPDF")
                p.end()
                return [pix]
            
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Render at 2x for better quality, then scale down
                zoom = 2.0
                mat = fitz.Matrix(zoom, zoom)
                pix_fitz = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to QImage then QPixmap
                img_data = pix_fitz.samples
                qimg = QImage(img_data, pix_fitz.width, pix_fitz.height,
                             pix_fitz.stride, QImage.Format.Format_RGB888)
                
                # Scale to preview size
                qpix = QPixmap.fromImage(qimg)
                scaled = qpix.scaled(500, 700, Qt.AspectRatioMode.KeepAspectRatio, 
                                     Qt.TransformationMode.SmoothTransformation)
                pages.append(scaled)
            
            doc.close()
            
        except Exception as e:
            print(f"Error preview: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error page
            pix = QPixmap(500, 700)
            pix.fill(QColor(255, 255, 255))
            p = QPainter(pix)
            p.setFont(QFont("Arial", 10))
            p.setPen(QColor(255, 0, 0))
            p.drawText(QRect(20, 20, 460, 660), Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, 
                      f"Error generando preview:\n{str(e)}")
            p.end()
            return [pix]
            

        return pages if pages else [QPixmap(500, 700)]
    
    def set_preview_callback(self, callback):
        """Set callback for generating preview."""
        self._generate_preview_callback = callback
    
    def _save_and_close(self):
        """Save data and close."""
        data = self._collect_data()
        self.data_saved.emit(data)
        self._is_modified = False
        self.accept()
    
    def set_preview_callback(self, callback):
        """Set callback for generating preview."""

        self._generate_preview_callback = callback
    
    def _save_and_close(self):
        """Save data and close."""
        data = self._collect_data()
        self.data_saved.emit(data)
        self._is_modified = False
        self.accept()
    
    def _on_cancel(self):
        """Handle cancel button."""
        if self._is_modified:
            reply = QMessageBox.question(
                self, "Cambios sin guardar",
                "Hay cambios sin guardar. Desea guardarlos antes de cerrar?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self._save_and_close()
            elif reply == QMessageBox.StandardButton.Discard:
                self.reject()
            # Cancel just returns
        else:
            self.reject()
    
    def closeEvent(self, event):
        """Handle window close - auto-save."""
        if self._is_modified:
            # Auto-save on close
            data = self._collect_data()
            self.data_saved.emit(data)
        event.accept()
    
    def set_products(self, products: list):
        """Update products list."""
        self._products = products
        self.block_container.set_products(products)
    
    def get_observations_data(self) -> dict:
        """Get the current observations data."""
        return self._collect_data()
