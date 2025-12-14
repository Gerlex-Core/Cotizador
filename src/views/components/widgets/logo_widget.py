"""
Logo Widget Component for displaying company logos with animation support.
"""

import os
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize
)
from PyQt6.QtGui import QPixmap, QPainter, QColor


class LogoWidget(QLabel):
    """
    Widget for displaying company logos with fade animation on change,
    automatic scaling, and fallback placeholder.
    """
    
    def __init__(self, parent=None, max_width: int = 150, max_height: int = 80):
        super().__init__(parent)
        
        self._max_width = max_width
        self._max_height = max_height
        self._logo_path = ""
        self._opacity = 1.0
        self._placeholder_text = "LOGO"
        
        # Setup appearance
        self.setFixedSize(max_width, max_height)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        
        # Animation
        self._fade_anim = QPropertyAnimation(self, b"logoOpacity")
        self._fade_anim.setDuration(200)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # Show placeholder initially
        self._show_placeholder()
    
    @pyqtProperty(float)
    def logoOpacity(self):
        return self._opacity
    
    @logoOpacity.setter
    def logoOpacity(self, value):
        self._opacity = value
        self.update()
    
    def setLogo(self, path: str, animate: bool = True):
        """
        Set the logo from a file path with optional fade animation.
        """
        if not path or not os.path.exists(path):
            self._show_placeholder()
            return
        
        self._logo_path = path
        
        if animate and self._opacity > 0:
            # Fade out, change, fade in
            self._fade_anim.stop()
            self._fade_anim.setStartValue(1.0)
            self._fade_anim.setEndValue(0.0)
            self._fade_anim.finished.connect(self._load_and_fade_in)
            self._fade_anim.start()
        else:
            self._load_logo()
    
    def _load_and_fade_in(self):
        """Load the logo and fade back in."""
        self._fade_anim.finished.disconnect()
        self._load_logo()
        
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.start()
    
    def _load_logo(self):
        """Load and display the logo image."""
        if not self._logo_path or not os.path.exists(self._logo_path):
            self._show_placeholder()
            return
        
        pixmap = QPixmap(self._logo_path)
        if pixmap.isNull():
            self._show_placeholder()
            return
        
        # Scale while maintaining aspect ratio
        scaled = pixmap.scaled(
            self._max_width, self._max_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.setPixmap(scaled)
    
    def _show_placeholder(self):
        """Show a placeholder when no logo is available."""
        self.clear()
        self._logo_path = ""
    
    def paintEvent(self, event):
        """Custom paint with opacity support."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Apply opacity
        if self._opacity < 1.0:
            painter.setOpacity(self._opacity)
            
        # Draw Pixmap if available
        if self.pixmap() and not self.pixmap().isNull():
            # Calculate centered position
            pixmap = self.pixmap()
            
            # Helper to center image
            x = (self.width() - pixmap.width()) // 2
            y = (self.height() - pixmap.height()) // 2
            
            painter.drawPixmap(x, y, pixmap)
            
        else:
            # Draw placeholder
            painter.setOpacity(self._opacity * 0.3)
            
            # Placeholder box
            painter.setPen(QColor(128, 128, 128))
            painter.drawRoundedRect(
                2, 2, self.width() - 4, self.height() - 4, 8, 8
            )
            
            # Placeholder text
            painter.setOpacity(self._opacity * 0.5)
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._placeholder_text)
            
        painter.end()
    
    def getLogoPath(self) -> str:
        """Get the current logo file path."""
        return self._logo_path
    
    def setMaxSize(self, width: int, height: int):
        """Set the maximum size for the logo."""
        self._max_width = width
        self._max_height = height
        self.setFixedSize(width, height)
        
        # Reload logo if present
        if self._logo_path:
            self._load_logo()
    
    def setPlaceholderText(self, text: str):
        """Set the placeholder text when no logo is loaded."""
        self._placeholder_text = text
        self.update()


class CompanyHeader(QWidget):
    """
    Widget combining logo with company info for headers.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Logo
        self.logo = LogoWidget(self, max_width=120, max_height=60)
        layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Company name
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
            }
        """)
        layout.addWidget(self.name_label)
        
        # Slogan
        self.slogan_label = QLabel()
        self.slogan_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slogan_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-style: italic;
                color: #8E8E93;
            }
        """)
        layout.addWidget(self.slogan_label)
    
    def setCompany(self, name: str, slogan: str = "", logo_path: str = ""):
        """Set the company information."""
        self.name_label.setText(name)
        self.slogan_label.setText(slogan)
        self.slogan_label.setVisible(bool(slogan))
        
        if logo_path:
            self.logo.setLogo(logo_path)
