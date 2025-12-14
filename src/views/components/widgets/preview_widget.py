"""
Preview Widget - Universal PDF preview component with multi-page support.
Supports: single page, multi-page pagination, fullscreen view, and callbacks.
"""

import os
import tempfile
from typing import List, Callable, Optional, Union
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QDialog, QSizePolicy, QFrame, QSpinBox
)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from src.views.styles.theme_manager import ThemeManager
from src.views.styles.icon_manager import IconManager
from src.logic.config.config_manager import ConfigManager


class PreviewThumbnail(QFrame):
    """
    Preview thumbnail that shows the current page of the PDF.
    Click to open fullscreen view.
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFrameShape(QFrame.Shape.Box)
        self.setStyleSheet("""
            PreviewThumbnail {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(10, 132, 255, 0.3);
                border-radius: 8px;
            }
            PreviewThumbnail:hover {
                border-color: #0A84FF;
                background-color: rgba(10, 132, 255, 0.1);
            }
        """)
        
        self.setMinimumSize(200, 280)
        self.setMaximumSize(350, 500)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Preview image
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(180, 240)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 4px;
            }
        """)
        self._set_placeholder()
        layout.addWidget(self.preview_label, 1)
        
        # Click hint
        hint = QLabel("Click para pantalla completa")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 10px;")
        layout.addWidget(hint)
    
    def _set_placeholder(self):
        """Set placeholder content."""
        pixmap = QPixmap(180, 240)
        pixmap.fill(QColor(255, 255, 255))
        
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        
        # Draw placeholder lines
        for y in range(20, 240, 20):
            painter.drawLine(10, y, 170, y)
        
        painter.setFont(QFont("Arial", 12))
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Vista Previa\nPDF")
        painter.end()
        
        self.preview_label.setPixmap(pixmap)
    
    def set_preview(self, pixmap: QPixmap, max_width: int = 280, max_height: int = 400):
        """Set the preview image with customizable size."""
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(
                max_width, max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
    
    def mousePressEvent(self, event):
        """Handle click to open fullscreen."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class FullscreenPreviewDialog(QDialog):
    """
    Fullscreen dialog for viewing PDF preview with multi-page support.
    """
    
    def __init__(self, pages: List[QPixmap] = None, parent=None):
        super().__init__(parent)
        
        self._pages = pages or []
        self._current_page = 0
        
        self.setWindowTitle("Vista Previa del PDF")
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )
        
        self.setMinimumSize(600, 800)
        self.resize(850, 1050)
        
        # Apply theme
        config = ConfigManager()
        ThemeManager.apply_theme(self, config.tema)
        
        self.icon_manager = IconManager.get_instance()
        
        self._setup_ui()
        
        if self._pages:
            self._update_display()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        title = QLabel("Vista Previa del PDF")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        toolbar.addWidget(title)
        
        toolbar.addStretch()
        
        # Page navigation
        self.page_label = QLabel("Página 1 de 1")
        self.page_label.setStyleSheet("color: white; font-size: 12px;")
        toolbar.addWidget(self.page_label)
        
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setFixedSize(36, 36)
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background-color: rgba(10, 132, 255, 0.3);
                border: 1px solid #0A84FF;
                border-radius: 6px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(10, 132, 255, 0.5); }
            QPushButton:disabled { opacity: 0.5; }
        """)
        self.btn_prev.clicked.connect(self._prev_page)
        toolbar.addWidget(self.btn_prev)
        
        self.btn_next = QPushButton("▶")
        self.btn_next.setFixedSize(36, 36)
        self.btn_next.setStyleSheet("""
            QPushButton {
                background-color: rgba(10, 132, 255, 0.3);
                border: 1px solid #0A84FF;
                border-radius: 6px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(10, 132, 255, 0.5); }
            QPushButton:disabled { opacity: 0.5; }
        """)
        self.btn_next.clicked.connect(self._next_page)
        toolbar.addWidget(self.btn_next)
        
        toolbar.addSpacing(20)
        
        btn_close = QPushButton("Cerrar")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 69, 58, 0.3);
                border: 1px solid rgba(255, 69, 58, 0.5);
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(255, 69, 58, 0.6); }
        """)
        btn_close.clicked.connect(self.close)
        toolbar.addWidget(btn_close)
        
        layout.addLayout(toolbar)
        
        # Scroll area for preview
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #333;
                border: none;
                border-radius: 8px;
            }
        """)
        
        # Preview container
        self.preview_container = QWidget()
        self.preview_container.setStyleSheet("background-color: #333;")
        container_layout = QVBoxLayout(self.preview_container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: white; padding: 10px;")
        container_layout.addWidget(self.preview_label)
        
        scroll.setWidget(self.preview_container)
        layout.addWidget(scroll)
    
    def _update_display(self):
        """Update the displayed page and navigation."""
        if not self._pages:
            return
        
        total = len(self._pages)
        self.page_label.setText(f"Página {self._current_page + 1} de {total}")
        
        self.btn_prev.setEnabled(self._current_page > 0)
        self.btn_next.setEnabled(self._current_page < total - 1)
        
        # Display current page
        pixmap = self._pages[self._current_page]
        if pixmap and not pixmap.isNull():
            max_size = QSize(self.width() - 60, self.height() - 100)
            scaled = pixmap.scaled(
                max_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
    
    def _prev_page(self):
        """Go to previous page."""
        if self._current_page > 0:
            self._current_page -= 1
            self._update_display()
    
    def _next_page(self):
        """Go to next page."""
        if self._current_page < len(self._pages) - 1:
            self._current_page += 1
            self._update_display()
    
    def set_pages(self, pages: List[QPixmap]):
        """Set the preview pages."""
        self._pages = pages or []
        self._current_page = 0
        self._update_display()
    
    def set_preview(self, pixmap: QPixmap):
        """Set single page preview (backwards compatible)."""
        self.set_pages([pixmap] if pixmap else [])


class PreviewWidget(QWidget):
    """
    Universal preview widget with multi-page pagination support.
    
    Features:
    - Single or multi-page preview
    - Thumbnail view with pagination controls
    - Fullscreen dialog with page navigation
    - Callback-based generation (single pixmap or list)
    
    Usage:
        preview = PreviewWidget()
        preview.set_generate_callback(my_generate_function)
        # or directly:
        preview.set_preview(pixmap)  # Single page
        preview.set_pages([page1, page2, page3])  # Multi-page
    """
    
    def __init__(self, parent=None, show_header: bool = True, 
                 show_generate_button: bool = True):
        super().__init__(parent)
        
        self._pages: List[QPixmap] = []
        self._current_page = 0
        self._generate_callback: Optional[Callable] = None
        
        self.icon_manager = IconManager.get_instance()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Header (optional)
        if show_header:
            header = QLabel("Vista Previa")
            header.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(header)
        
        # Thumbnail
        self.thumbnail = PreviewThumbnail()
        self.thumbnail.clicked.connect(self._open_fullscreen)
        layout.addWidget(self.thumbnail, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Page navigation (hidden when single page)
        self.nav_widget = QWidget()
        nav_layout = QHBoxLayout(self.nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(8)
        
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setFixedSize(32, 32)
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background-color: rgba(10, 132, 255, 0.3);
                border: 1px solid #0A84FF;
                border-radius: 6px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(10, 132, 255, 0.5); }
            QPushButton:disabled { background-color: rgba(100,100,100,0.2); border-color: #555; }
        """)
        self.btn_prev.clicked.connect(self._prev_page)
        nav_layout.addWidget(self.btn_prev)
        
        self.page_label = QLabel("1 / 1")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("color: white; font-size: 12px; min-width: 60px;")
        nav_layout.addWidget(self.page_label)
        
        self.btn_next = QPushButton("▶")
        self.btn_next.setFixedSize(32, 32)
        self.btn_next.setStyleSheet("""
            QPushButton {
                background-color: rgba(10, 132, 255, 0.3);
                border: 1px solid #0A84FF;
                border-radius: 6px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(10, 132, 255, 0.5); }
            QPushButton:disabled { background-color: rgba(100,100,100,0.2); border-color: #555; }
        """)
        self.btn_next.clicked.connect(self._next_page)
        nav_layout.addWidget(self.btn_next)
        
        layout.addWidget(self.nav_widget, 0, Qt.AlignmentFlag.AlignCenter)
        self.nav_widget.hide()  # Hidden by default, shown when multi-page
        
        # Generate button (optional)
        if show_generate_button:
            btn_generate = QPushButton("Actualizar Vista Previa")
            btn_generate.setStyleSheet("""
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
            btn_generate.clicked.connect(self._on_generate_clicked)
            layout.addWidget(btn_generate)
        
        layout.addStretch()
    
    def set_generate_callback(self, callback: Callable):
        """
        Set callback function that generates preview.
        
        Callback can return:
        - QPixmap: Single page
        - List[QPixmap]: Multiple pages
        """
        self._generate_callback = callback
    
    def _on_generate_clicked(self):
        """Handle generate button click."""
        if self._generate_callback:
            result = self._generate_callback()
            if isinstance(result, list):
                self.set_pages(result)
            elif result:
                self.set_preview(result)
    
    def set_preview(self, pixmap: QPixmap):
        """Set single page preview (backwards compatible)."""
        self.set_pages([pixmap] if pixmap and not pixmap.isNull() else [])
    
    def set_pages(self, pages: List[QPixmap]):
        """Set multiple pages for preview."""
        self._pages = [p for p in pages if p and not p.isNull()]
        self._current_page = 0
        self._update_display()
    
    def _update_display(self):
        """Update thumbnail and navigation."""
        if not self._pages:
            self.nav_widget.hide()
            return
        
        total = len(self._pages)
        
        # Show/hide navigation based on page count
        if total > 1:
            self.nav_widget.show()
            self.page_label.setText(f"{self._current_page + 1} / {total}")
            self.btn_prev.setEnabled(self._current_page > 0)
            self.btn_next.setEnabled(self._current_page < total - 1)
        else:
            self.nav_widget.hide()
        
        # Update thumbnail
        self.thumbnail.set_preview(self._pages[self._current_page])
    
    def _prev_page(self):
        """Go to previous page."""
        if self._current_page > 0:
            self._current_page -= 1
            self._update_display()
    
    def _next_page(self):
        """Go to next page."""
        if self._current_page < len(self._pages) - 1:
            self._current_page += 1
            self._update_display()
    
    def _open_fullscreen(self):
        """Open fullscreen preview dialog."""
        if self._pages:
            dialog = FullscreenPreviewDialog(self._pages, self)
            dialog._current_page = self._current_page
            dialog._update_display()
            dialog.exec()
        elif self._generate_callback:
            # Try to generate first
            result = self._generate_callback()
            if isinstance(result, list):
                self.set_pages(result)
            elif result:
                self.set_preview(result)
            
            if self._pages:
                dialog = FullscreenPreviewDialog(self._pages, self)
                dialog.exec()
    
    def get_current_page(self) -> int:
        """Get current page index."""
        return self._current_page
    
    def get_total_pages(self) -> int:
        """Get total number of pages."""
        return len(self._pages)
