"""
Themed Button Components - Buttons with full theme support, animations, and effects.
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, Qt, QPoint, pyqtProperty, QTimer
)
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient

from src.views.styles.theme_base import ThemeConfig


class ThemedButton(QPushButton):
    """
    Premium themed button with:
    - Theme-aware colors and styling
    - Ripple effect on click
    - Scale animation on hover/press
    - Glow effect when theme supports it
    """
    
    def __init__(self, text: str = "", parent=None, theme_config: ThemeConfig = None):
        super().__init__(text, parent)
        
        self._theme = theme_config
        self._scale = 1.0
        self._ripple_radius = 0
        self._ripple_opacity = 0.0
        self._ripple_center = QPoint()
        self._glow_opacity = 0.0
        
        self._setup_animations()
        self.setMouseTracking(True)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if theme_config:
            self.apply_theme(theme_config)
    
    def _setup_animations(self):
        """Initialize animations."""
        duration = 200 if not self._theme else self._theme.animation_duration
        
        self._scale_anim = QPropertyAnimation(self, b"buttonScale")
        self._scale_anim.setDuration(duration)
        self._scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._ripple_anim = QPropertyAnimation(self, b"rippleRadius")
        self._ripple_anim.setDuration(400)
        self._ripple_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._ripple_fade = QPropertyAnimation(self, b"rippleOpacity")
        self._ripple_fade.setDuration(400)
        self._ripple_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._glow_anim = QPropertyAnimation(self, b"glowOpacity")
        self._glow_anim.setDuration(250)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    # Animation properties
    @pyqtProperty(float)
    def buttonScale(self):
        return self._scale
    
    @buttonScale.setter
    def buttonScale(self, value):
        self._scale = value
        self.update()
    
    @pyqtProperty(float)
    def rippleRadius(self):
        return self._ripple_radius
    
    @rippleRadius.setter
    def rippleRadius(self, value):
        self._ripple_radius = value
        self.update()
    
    @pyqtProperty(float)
    def rippleOpacity(self):
        return self._ripple_opacity
    
    @rippleOpacity.setter
    def rippleOpacity(self, value):
        self._ripple_opacity = value
        self.update()
    
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
        
        bg = config.get('button_bg', '#2C2C2E')
        text_color = config.get('button_text', '#FFFFFF')
        border = config.get('border', '#3A3A3C')
        accent = config.get('accent', '#0A84FF')
        radius = config.get('button_radius', '8px')
        padding = config.get('button_padding', '10px 20px')
        font_weight = config.get('button_weight', '600')
        
        # Handle transparent backgrounds
        if config.has_transparency:
            bg = config.get('button_bg', 'rgba(44, 44, 46, 0.7)')
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {text_color};
                border: 1px solid {border};
                border-radius: {radius};
                padding: {padding};
                font-weight: {font_weight};
            }}
            QPushButton:hover {{
                background: {accent};
                border-color: {accent};
            }}
            QPushButton:pressed {{
                background: {config.get('accent_dark', '#0064D2')};
            }}
            QPushButton:disabled {{
                background: {config.get('disabled_bg', '#1C1C1E')};
                color: {config.get('disabled_text', '#48484A')};
                border-color: {config.get('disabled_border', '#2C2C2E')};
            }}
        """)
    
    def enterEvent(self, event):
        """Mouse enter - scale up and show glow."""
        hover_scale = self._theme.get('hover_scale', 1.02) if self._theme else 1.02
        
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(hover_scale)
        self._scale_anim.start()
        
        if self._theme and self._theme.has_glow:
            self._glow_anim.stop()
            self._glow_anim.setStartValue(self._glow_opacity)
            self._glow_anim.setEndValue(self._theme.get('glow_intensity', 0.3))
            self._glow_anim.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Mouse leave - scale down and hide glow."""
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(1.0)
        self._scale_anim.start()
        
        if self._theme and self._theme.has_glow:
            self._glow_anim.stop()
            self._glow_anim.setStartValue(self._glow_opacity)
            self._glow_anim.setEndValue(0.0)
            self._glow_anim.start()
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Mouse press - ripple and scale down."""
        if event.button() == Qt.MouseButton.LeftButton:
            press_scale = self._theme.get('press_scale', 0.98) if self._theme else 0.98
            
            self._ripple_center = event.pos()
            max_radius = (self.width() ** 2 + self.height() ** 2) ** 0.5
            
            self._ripple_anim.stop()
            self._ripple_anim.setStartValue(0)
            self._ripple_anim.setEndValue(max_radius)
            
            self._ripple_fade.stop()
            self._ripple_opacity = 0.3
            self._ripple_fade.setStartValue(0.3)
            self._ripple_fade.setEndValue(0)
            
            self._ripple_anim.start()
            self._ripple_fade.start()
            
            self._scale_anim.stop()
            self._scale_anim.setStartValue(self._scale)
            self._scale_anim.setEndValue(press_scale)
            self._scale_anim.start()
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Mouse release - restore scale."""
        hover_scale = self._theme.get('hover_scale', 1.02) if self._theme else 1.02
        
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(hover_scale if self.underMouse() else 1.0)
        self._scale_anim.start()
        
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event):
        """Custom paint with effects."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Scale transform
        center = self.rect().center()
        painter.translate(center)
        painter.scale(self._scale, self._scale)
        painter.translate(-center)
        
        # Draw glow effect
        if self._glow_opacity > 0 and self._theme and self._theme.has_glow:
            glow_color = self._theme.get_qcolor('glow_color')
            glow_color.setAlphaF(self._glow_opacity * 0.5)
            
            for i in range(3):
                glow_rect = self.rect().adjusted(-i*3, -i*3, i*3, i*3)
                glow_color.setAlphaF(self._glow_opacity * (0.3 - i*0.1))
                painter.setPen(QPen(glow_color, 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                radius = int(self._theme.get('corner_radius', 8))
                painter.drawRoundedRect(glow_rect, radius + i, radius + i)
        
        # Draw ripple
        if self._ripple_radius > 0 and self._ripple_opacity > 0:
            ripple_color = QColor(255, 255, 255, int(255 * self._ripple_opacity))
            painter.setBrush(QBrush(ripple_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                self._ripple_center,
                int(self._ripple_radius),
                int(self._ripple_radius)
            )
        
        painter.end()
        super().paintEvent(event)


class PrimaryThemedButton(ThemedButton):
    """Primary action button with accent gradient."""
    
    def apply_theme(self, config: ThemeConfig):
        self._theme = config
        
        accent = config.get('accent', '#0A84FF')
        accent_dark = config.get('accent_dark', '#0064D2')
        text_color = config.get('button_hover_text', '#FFFFFF')
        radius = config.get('button_radius', '8px')
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {accent}, stop:1 {accent_dark});
                color: {text_color};
                border: none;
                border-radius: {radius};
                padding: 12px 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {accent}, stop:0.5 {accent}, stop:1 {accent_dark});
            }}
            QPushButton:pressed {{
                background: {accent_dark};
            }}
        """)


class SecondaryThemedButton(ThemedButton):
    """Secondary outline button."""
    
    def apply_theme(self, config: ThemeConfig):
        self._theme = config
        
        accent = config.get('accent', '#0A84FF')
        radius = config.get('button_radius', '8px')
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {accent};
                border: 2px solid {accent};
                border-radius: {radius};
                padding: 12px 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(10, 132, 255, 0.15);
            }}
            QPushButton:pressed {{
                background: rgba(10, 132, 255, 0.25);
            }}
        """)


class DangerThemedButton(ThemedButton):
    """Danger/delete button with red styling."""
    
    def apply_theme(self, config: ThemeConfig):
        self._theme = config
        
        radius = config.get('button_radius', '8px')
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: #FF3B30;
                color: white;
                border: none;
                border-radius: {radius};
                padding: 12px 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #FF5C54;
            }}
            QPushButton:pressed {{
                background: #D32F2F;
            }}
        """)


class GlassButton(ThemedButton):
    """Glass-style button with transparency for glassmorphism themes."""
    
    def apply_theme(self, config: ThemeConfig):
        self._theme = config
        
        text_color = config.get('text_primary', '#FFFFFF')
        accent = config.get('accent', '#0A84FF')
        glow = config.get('accent_glow', 'rgba(10, 132, 255, 0.4)')
        radius = config.get('corner_radius', 12)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.08);
                color: {text_color};
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: {radius}px;
                padding: 12px 24px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.15);
                border-color: {accent};
                box-shadow: 0 0 20px {glow};
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.1);
            }}
        """)
