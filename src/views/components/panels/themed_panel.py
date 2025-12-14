"""
Themed Panel Components - Panels with glassmorphism, transparency, and depth effects.
"""

from PyQt6.QtWidgets import QFrame, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QPainterPath, QBrush

from src.views.styles.theme_base import ThemeConfig


class ThemedPanel(QFrame):
    """
    Base themed panel with:
    - Theme-aware background and border
    - Transparency support
    - Glow effects
    - Gradient backgrounds
    """
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent)
        
        self._theme = theme_config
        self._corner_radius = 12
        self._glow_enabled = True
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setContentsMargins(16, 16, 16, 16)
        self.setMinimumHeight(60)
        
        if theme_config:
            self.apply_theme(theme_config)
    
    def apply_theme(self, config: ThemeConfig):
        """Apply theme configuration."""
        self._theme = config
        self._corner_radius = config.get('corner_radius', 12)
        self._glow_enabled = config.get('glow_enabled', False)
        self.update()
    
    def paintEvent(self, event):
        """Custom paint for themed panel."""
        if not self._theme:
            super().paintEvent(event)
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        margin = 3 if self._glow_enabled else 1
        rect = self.rect().adjusted(margin, margin, -margin, -margin)
        
        # Create rounded rect path
        path = QPainterPath()
        path.addRoundedRect(float(rect.x()), float(rect.y()),
                           float(rect.width()), float(rect.height()),
                           self._corner_radius, self._corner_radius)
        
        # Draw glow
        if self._glow_enabled and self._theme.has_glow:
            glow_color = self._theme.get_qcolor('panel_glow')
            for i in range(3):
                glow_rect = rect.adjusted(-i*2, -i*2, i*2, i*2)
                alpha = 0.15 - i * 0.05
                glow_color.setAlphaF(max(0, alpha))
                
                glow_path = QPainterPath()
                glow_path.addRoundedRect(float(glow_rect.x()), float(glow_rect.y()),
                                        float(glow_rect.width()), float(glow_rect.height()),
                                        self._corner_radius + i, self._corner_radius + i)
                
                painter.setPen(QPen(glow_color, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawPath(glow_path)
        
        # Background gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        
        panel_bg = self._theme.get_qcolor('panel_bg')
        
        # Top lighter
        top_color = QColor(panel_bg)
        top_color.setAlphaF(min(1.0, panel_bg.alphaF() * 1.3))
        gradient.setColorAt(0, top_color)
        
        # Middle
        gradient.setColorAt(0.5, panel_bg)
        
        # Bottom darker
        bottom_color = QColor(panel_bg)
        bottom_color.setAlphaF(max(0, panel_bg.alphaF() * 0.8))
        gradient.setColorAt(1, bottom_color)
        
        painter.setBrush(QBrush(gradient))
        
        # Border
        border_color = self._theme.get_qcolor('panel_border')
        painter.setPen(QPen(border_color, 1.5))
        
        painter.drawPath(path)
        
        # Inner highlight
        if self._theme.has_transparency:
            highlight = QColor(255, 255, 255, 20)
            painter.setPen(QPen(highlight, 1))
            inner_rect = rect.adjusted(4, 4, -4, 0)
            painter.drawLine(inner_rect.left() + self._corner_radius, inner_rect.top(),
                           inner_rect.right() - self._corner_radius, inner_rect.top())
        
        painter.end()
        super().paintEvent(event)


class GlassPanel(ThemedPanel):
    """
    Premium glass panel with enhanced glassmorphism effect.
    """
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent, theme_config)
        self._glow_enabled = True
    
    def paintEvent(self, event):
        """Enhanced glass effect paint."""
        if not self._theme:
            super().paintEvent(event)
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        path = QPainterPath()
        path.addRoundedRect(float(rect.x()), float(rect.y()),
                           float(rect.width()), float(rect.height()),
                           self._corner_radius, self._corner_radius)
        
        # Outer glow
        if self._theme.has_glow:
            glow_color = self._theme.get_qcolor('accent_glow')
            for i in range(4):
                glow_rect = rect.adjusted(-i*2, -i*2, i*2, i*2)
                glow_color.setAlphaF(0.12 - i * 0.03)
                
                glow_path = QPainterPath()
                glow_path.addRoundedRect(float(glow_rect.x()), float(glow_rect.y()),
                                        float(glow_rect.width()), float(glow_rect.height()),
                                        self._corner_radius + i, self._corner_radius + i)
                
                painter.setPen(QPen(glow_color, 1.5))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawPath(glow_path)
        
        # Glass gradient background
        gradient = QLinearGradient(0, 0, 0, rect.height())
        
        # Top highlight
        gradient.setColorAt(0, QColor(255, 255, 255, 25))
        gradient.setColorAt(0.1, QColor(255, 255, 255, 15))
        gradient.setColorAt(0.4, QColor(255, 255, 255, 8))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 20))
        
        painter.setBrush(QBrush(gradient))
        
        # Border
        accent = self._theme.get_qcolor('accent')
        accent.setAlphaF(0.35)
        painter.setPen(QPen(accent, 1.5))
        
        painter.drawPath(path)
        
        # Top reflection line
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(rect.left() + self._corner_radius + 2, rect.top() + 1,
                        rect.right() - self._corner_radius - 2, rect.top() + 1)
        
        painter.end()


class CardPanel(ThemedPanel):
    """
    Card-style panel for content containers.
    """
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent, theme_config)
        self._glow_enabled = False
        self.setContentsMargins(16, 16, 16, 16)
    
    def paintEvent(self, event):
        """Card paint with shadow effect."""
        if not self._theme:
            super().paintEvent(event)
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Shadow offset
        shadow_offset = 3
        rect = self.rect().adjusted(2, 2, -2 - shadow_offset, -2 - shadow_offset)
        
        # Draw shadow
        shadow_rect = rect.adjusted(shadow_offset, shadow_offset, shadow_offset, shadow_offset)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(float(shadow_rect.x()), float(shadow_rect.y()),
                                   float(shadow_rect.width()), float(shadow_rect.height()),
                                   self._corner_radius, self._corner_radius)
        
        shadow_color = self._theme.get_qcolor('card_shadow')
        shadow_color.setAlphaF(0.25)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(shadow_path)
        
        # Main card
        path = QPainterPath()
        path.addRoundedRect(float(rect.x()), float(rect.y()),
                           float(rect.width()), float(rect.height()),
                           self._corner_radius, self._corner_radius)
        
        card_bg = self._theme.get_qcolor('card_bg')
        painter.setBrush(QBrush(card_bg))
        
        border_color = self._theme.get_qcolor('card_border')
        painter.setPen(QPen(border_color, 1))
        
        painter.drawPath(path)
        
        painter.end()


class AccentPanel(ThemedPanel):
    """
    Panel with accent color tint.
    """
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent, theme_config)
    
    def paintEvent(self, event):
        """Accent tinted panel."""
        if not self._theme:
            super().paintEvent(event)
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        path = QPainterPath()
        path.addRoundedRect(float(rect.x()), float(rect.y()),
                           float(rect.width()), float(rect.height()),
                           self._corner_radius, self._corner_radius)
        
        # Accent background
        accent = self._theme.get_qcolor('accent')
        accent.setAlphaF(0.12)
        painter.setBrush(QBrush(accent))
        
        # Accent border
        border = self._theme.get_qcolor('accent')
        border.setAlphaF(0.35)
        painter.setPen(QPen(border, 1.5))
        
        painter.drawPath(path)
        
        painter.end()
