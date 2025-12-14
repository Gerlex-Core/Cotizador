"""
Themed Widget Components - ProgressBar, Image, and other widgets.
"""

from PyQt6.QtWidgets import QProgressBar, QLabel, QFrame
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QPainterPath, QBrush, QPixmap

from src.views.styles.theme_base import ThemeConfig


class ThemedProgressBar(QProgressBar):
    """
    Themed progress bar with:
    - Animated fill
    - Glow effect
    - Gradient fill
    """
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent)
        
        self._theme = theme_config
        self._glow_opacity = 0.0
        
        self.setTextVisible(True)
        self.setMinimumHeight(24)
        
        if theme_config:
            self.apply_theme(theme_config)
    
    def apply_theme(self, config: ThemeConfig):
        """Apply theme configuration."""
        self._theme = config
        
        bg = config.get('input_bg', '#2C2C2E')
        text_color = config.get('text_primary', '#FFFFFF')
        accent = config.get('accent', '#0A84FF')
        accent_dark = config.get('accent_dark', '#0064D2')
        radius = config.get('corner_radius', 8)
        
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: {bg};
                color: {text_color};
                border: 1px solid {config.get('border', '#3A3A3C')};
                border-radius: {radius}px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {accent_dark}, stop:0.5 {accent}, stop:1 {accent_dark});
                border-radius: {radius - 1}px;
            }}
        """)


class ThemedImage(QLabel):
    """
    Themed image display with:
    - Frame effects
    - Shadow
    - Rounded corners
    """
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent)
        
        self._theme = theme_config
        self._corner_radius = 8
        self._show_shadow = True
        self._pixmap = None
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(100, 100)
        
        if theme_config:
            self.apply_theme(theme_config)
    
    def apply_theme(self, config: ThemeConfig):
        """Apply theme configuration."""
        self._theme = config
        self._corner_radius = config.get('corner_radius', 8)
        self.update()
    
    def setImage(self, path: str):
        """Set image from file path."""
        self._pixmap = QPixmap(path)
        self.update()
    
    def setPixmap(self, pixmap: QPixmap):
        """Override setPixmap to store internally."""
        self._pixmap = pixmap
        self.update()
    
    def paintEvent(self, event):
        """Custom paint with effects."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self._pixmap or self._pixmap.isNull():
            super().paintEvent(event)
            return
        
        rect = self.rect().adjusted(4, 4, -4, -4)
        
        # Draw shadow
        if self._show_shadow and self._theme:
            shadow_rect = rect.adjusted(3, 3, 3, 3)
            shadow_color = self._theme.get_qcolor('card_shadow')
            shadow_color.setAlphaF(0.3)
            
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(float(shadow_rect.x()), float(shadow_rect.y()),
                                      float(shadow_rect.width()), float(shadow_rect.height()),
                                      self._corner_radius, self._corner_radius)
            painter.setBrush(QBrush(shadow_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(shadow_path)
        
        # Clip to rounded rect
        path = QPainterPath()
        path.addRoundedRect(float(rect.x()), float(rect.y()),
                           float(rect.width()), float(rect.height()),
                           self._corner_radius, self._corner_radius)
        painter.setClipPath(path)
        
        # Scale and draw image
        scaled = self._pixmap.scaled(rect.size(), 
                                     Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)
        x = rect.x() + (rect.width() - scaled.width()) // 2
        y = rect.y() + (rect.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        
        # Draw border
        painter.setClipping(False)
        if self._theme:
            border_color = self._theme.get_qcolor('border')
            painter.setPen(QPen(border_color, 1.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
        
        painter.end()


class ThemedSeparator(QFrame):
    """Themed horizontal separator line."""
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent)
        
        self._theme = theme_config
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(2)
        
        if theme_config:
            self.apply_theme(theme_config)
    
    def apply_theme(self, config: ThemeConfig):
        """Apply theme configuration."""
        self._theme = config
        
        border = config.get('border', 'rgba(255, 255, 255, 0.1)')
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {border};
                border: none;
            }}
        """)


class ThemedTextEdit(QFrame):
    """
    Themed multi-line text edit with theming support.
    Wraps QTextEdit for consistent styling.
    """
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        from PyQt6.QtWidgets import QTextEdit, QVBoxLayout
        super().__init__(parent)
        
        self._theme = theme_config
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._text_edit = QTextEdit()
        layout.addWidget(self._text_edit)
        
        if theme_config:
            self.apply_theme(theme_config)
    
    def apply_theme(self, config: ThemeConfig):
        """Apply theme configuration."""
        self._theme = config
        
        bg = config.get('input_bg', '#2C2C2E')
        text_color = config.get('text_primary', '#FFFFFF')
        border = config.get('border', '#3A3A3C')
        accent = config.get('accent', '#0A84FF')
        radius = config.get('corner_radius', 8)
        
        self._text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg};
                color: {text_color};
                border: 2px solid {border};
                border-radius: {radius}px;
                padding: 10px;
                selection-background-color: {accent};
            }}
            QTextEdit:focus {{
                border-color: {accent};
            }}
        """)
    
    def toPlainText(self) -> str:
        return self._text_edit.toPlainText()
    
    def setPlainText(self, text: str):
        self._text_edit.setPlainText(text)
    
    def setPlaceholderText(self, text: str):
        self._text_edit.setPlaceholderText(text)
    
    def clear(self):
        self._text_edit.clear()
