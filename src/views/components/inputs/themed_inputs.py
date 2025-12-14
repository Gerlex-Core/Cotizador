"""
Themed Input Components - TextBox, ComboBox, SpinBox with full theme support.
"""

from PyQt6.QtWidgets import QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPen

from src.views.styles.theme_base import ThemeConfig


class ThemedTextBox(QLineEdit):
    """
    Themed text input with:
    - Theme-aware styling
    - Focus glow animation
    - Transparent background support
    """
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent)
        
        self._theme = theme_config
        self._glow_opacity = 0.0
        
        self._setup_animations()
        self.setMinimumHeight(40)
        
        if theme_config:
            self.apply_theme(theme_config)
    
    def _setup_animations(self):
        duration = 200 if not self._theme else self._theme.animation_duration
        
        self._glow_anim = QPropertyAnimation(self, b"glowOpacity")
        self._glow_anim.setDuration(duration)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    @pyqtProperty(float)
    def glowOpacity(self):
        return self._glow_opacity
    
    @glowOpacity.setter
    def glowOpacity(self, value):
        self._glow_opacity = value
        self.update()
    
    def apply_theme(self, config: ThemeConfig):
        """Apply theme configuration."""
        self._theme = config
        
        bg = config.get('input_bg', '#2C2C2E')
        text_color = config.get('text_primary', '#FFFFFF')
        border = config.get('border', '#3A3A3C')
        accent = config.get('accent', '#0A84FF')
        radius = config.get('corner_radius', 8)
        
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg};
                color: {text_color};
                border: 2px solid {border};
                border-radius: {radius}px;
                padding: 8px 12px;
                selection-background-color: {accent};
            }}
            QLineEdit:focus {{
                border-color: {accent};
            }}
            QLineEdit:disabled {{
                background-color: {config.get('disabled_bg', '#1C1C1E')};
                color: {config.get('disabled_text', '#48484A')};
            }}
        """)
    
    def focusInEvent(self, event):
        if self._theme and self._theme.has_glow:
            self._glow_anim.stop()
            self._glow_anim.setStartValue(self._glow_opacity)
            self._glow_anim.setEndValue(self._theme.get('glow_intensity', 0.3))
            self._glow_anim.start()
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        if self._theme and self._theme.has_glow:
            self._glow_anim.stop()
            self._glow_anim.setStartValue(self._glow_opacity)
            self._glow_anim.setEndValue(0.0)
            self._glow_anim.start()
        super().focusOutEvent(event)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self._glow_opacity > 0 and self._theme and self._theme.has_glow:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            glow_color = self._theme.get_qcolor('glow_color')
            
            for i in range(3):
                glow_rect = self.rect().adjusted(-i*2, -i*2, i*2, i*2)
                glow_color.setAlphaF(self._glow_opacity * (0.3 - i*0.1))
                painter.setPen(QPen(glow_color, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                radius = int(self._theme.get('corner_radius', 8))
                painter.drawRoundedRect(glow_rect, radius + i, radius + i)
            
            painter.end()


class ThemedComboBox(QComboBox):
    """
    Themed combo box with:
    - Theme-aware styling
    - Dropdown animation
    - Glow effects
    """
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent)
        
        self._theme = theme_config
        self.setMinimumHeight(40)
        
        if theme_config:
            self.apply_theme(theme_config)
    
    def apply_theme(self, config: ThemeConfig):
        """Apply theme configuration."""
        self._theme = config
        
        bg = config.get('input_bg', '#2C2C2E')
        text_color = config.get('text_primary', '#FFFFFF')
        border = config.get('border', '#3A3A3C')
        accent = config.get('accent', '#0A84FF')
        menu_bg = config.get('menu_bg', '#2C2C2E')
        radius = config.get('corner_radius', 8)
        
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {bg};
                color: {text_color};
                border: 2px solid {border};
                border-radius: {radius}px;
                padding: 8px 12px;
                min-height: 36px;
            }}
            QComboBox:hover {{
                border-color: {accent};
            }}
            QComboBox:focus {{
                border-color: {accent};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid {text_color};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {menu_bg};
                color: {text_color};
                border: 1px solid {border};
                selection-background-color: {accent};
                outline: none;
            }}
        """)


class ThemedSpinBox(QSpinBox):
    """Themed spin box with animations."""
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent)
        
        self._theme = theme_config
        self.setMinimumHeight(40)
        
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
        
        self.setStyleSheet(f"""
            QSpinBox {{
                background-color: {bg};
                color: {text_color};
                border: 2px solid {border};
                border-radius: {radius}px;
                padding: 8px 12px;
            }}
            QSpinBox:focus {{
                border-color: {accent};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                border: none;
                background-color: rgba(255, 255, 255, 0.05);
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {accent};
            }}
        """)


class ThemedDoubleSpinBox(QDoubleSpinBox):
    """Themed double spin box."""
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent)
        
        self._theme = theme_config
        self.setMinimumHeight(40)
        
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
        
        self.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {bg};
                color: {text_color};
                border: 2px solid {border};
                border-radius: {radius}px;
                padding: 8px 12px;
            }}
            QDoubleSpinBox:focus {{
                border-color: {accent};
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                width: 20px;
                border: none;
                background-color: rgba(255, 255, 255, 0.05);
            }}
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {accent};
            }}
        """)


class ThemedCheckBox(QCheckBox):
    """
    Themed checkbox with:
    - Theme-aware styling
    - Check animation
    - Glow effects
    """
    
    def __init__(self, text: str = "", parent=None, theme_config: ThemeConfig = None):
        super().__init__(text, parent)
        
        self._theme = theme_config
        
        if theme_config:
            self.apply_theme(theme_config)
    
    def apply_theme(self, config: ThemeConfig):
        """Apply theme configuration."""
        self._theme = config
        
        text_color = config.get('text_primary', '#FFFFFF')
        border = config.get('border', '#3A3A3C')
        accent = config.get('accent', '#0A84FF')
        bg = config.get('input_bg', '#2C2C2E')
        
        self.setStyleSheet(f"""
            QCheckBox {{
                color: {text_color};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {border};
                border-radius: 4px;
                background-color: {bg};
            }}
            QCheckBox::indicator:hover {{
                border-color: {accent};
            }}
            QCheckBox::indicator:checked {{
                background-color: {accent};
                border-color: {accent};
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: {config.get('accent_dark', '#0064D2')};
            }}
        """)
