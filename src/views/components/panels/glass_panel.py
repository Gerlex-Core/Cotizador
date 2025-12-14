"""
Glass Panel Component with glassmorphism effect.
Optimized for Windows to avoid QPainter conflicts.
Implements IThemeable for full theme customization.
"""

from typing import Dict, Any, List
from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient, QPainterPath

from src.views.styles.themeable import IThemeable, get_component_registry
from src.views.styles.effects_engine import get_effects_engine


class GlassPanel(QFrame, IThemeable):
    """
    A panel widget with enhanced glassmorphism effect:
    - Semi-transparent gradient background
    - Subtle glowing border
    - Inner highlight for depth
    - Full theme support via IThemeable
    """
    
    def __init__(self, parent=None, blur_radius: int = 10, 
                 background_opacity: float = 0.12, border_opacity: float = 0.25):
        super().__init__(parent)
        
        self._blur_radius = blur_radius
        self._background_opacity = background_opacity
        self._border_opacity = border_opacity
        self._background_color = QColor(255, 255, 255)
        self._border_color = QColor(255, 255, 255)
        self._corner_radius = 16
        self._glow_color = QColor(10, 132, 255)  # Accent color for glow
        self._glow_enabled = True
        
        # Theme config cache
        self._theme_config: Dict[str, Any] = {}
        
        # Effects engine reference
        self._effects_engine = get_effects_engine()
        
        # Enable custom painting
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Default styling with padding
        self.setMinimumHeight(60)
        self.setContentsMargins(16, 16, 16, 16)
        
        # Register with component registry
        get_component_registry().register(self)
    
    # === IThemeable Implementation ===
    
    @property
    def component_type(self) -> str:
        return "panel"
    
    @property
    def theme_capabilities(self) -> List[str]:
        return ['colors', 'effects', 'animations']
    
    def get_theme_metadata(self) -> Dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.objectName() or f"panel_{id(self)}",
            "visible": self.isVisible(),
            "geometry": {
                "x": self.x(),
                "y": self.y(),
                "width": self.width(),
                "height": self.height()
            },
            "capabilities": self.theme_capabilities,
            "properties": {
                "corner_radius": self._corner_radius,
                "glow_enabled": self._glow_enabled,
                "background_opacity": self._background_opacity,
                "glow_color": self._glow_color.name()
            }
        }
    
    def apply_theme_config(self, config: Dict[str, Any]):
        self._theme_config = config
        
        if config:
            # Apply corner radius
            if 'borderRadius' in config:
                self._corner_radius = config['borderRadius']
            
            # Apply padding
            if 'padding' in config:
                p = config['padding']
                self.setContentsMargins(p, p, p, p)
            
            # Apply background opacity
            if 'backgroundOpacity' in config:
                self._background_opacity = config['backgroundOpacity']
        
        self.update()
    
    def on_theme_changed(self, theme_name: str):
        self.update()
    
    # === Paint Event ===
    
    def paintEvent(self, event):
        """Custom paint for enhanced glassmorphism effect."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get rect with margin for glow effect
        margin = 2
        rect = self.rect().adjusted(margin, margin, -margin, -margin)
        
        # Create rounded rect path
        path = QPainterPath()
        path.addRoundedRect(float(rect.x()), float(rect.y()), 
                           float(rect.width()), float(rect.height()),
                           self._corner_radius, self._corner_radius)
        
        # Draw outer glow simulation (multiple layers)
        if self._glow_enabled:
            for i in range(3):
                glow_rect = rect.adjusted(-i*2, -i*2, i*2, i*2)
                glow_color = QColor(self._glow_color)
                glow_color.setAlpha(int(15 - i * 5))
                
                glow_path = QPainterPath()
                glow_path.addRoundedRect(float(glow_rect.x()), float(glow_rect.y()),
                                        float(glow_rect.width()), float(glow_rect.height()),
                                        self._corner_radius + i, self._corner_radius + i)
                
                painter.setPen(QPen(glow_color, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawPath(glow_path)
        
        # Main background gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        
        # Top highlight
        top_color = QColor(self._background_color)
        top_color.setAlphaF(self._background_opacity * 1.5)
        gradient.setColorAt(0, top_color)
        
        # Middle
        mid_color = QColor(self._background_color)
        mid_color.setAlphaF(self._background_opacity)
        gradient.setColorAt(0.5, mid_color)
        
        # Bottom - slightly darker
        bottom_color = QColor(self._background_color)
        bottom_color.setAlphaF(self._background_opacity * 0.7)
        gradient.setColorAt(1, bottom_color)
        
        painter.setBrush(QBrush(gradient))
        
        # Border with gradient for depth
        border_color = QColor(self._border_color)
        border_color.setAlphaF(self._border_opacity)
        painter.setPen(QPen(border_color, 1.5))
        
        # Draw the main panel
        painter.drawPath(path)
        
        # Inner highlight line at top
        highlight_color = QColor(255, 255, 255, 30)
        painter.setPen(QPen(highlight_color, 1))
        
        inner_rect = rect.adjusted(4, 4, -4, 0)
        painter.drawLine(inner_rect.left() + self._corner_radius, inner_rect.top(),
                        inner_rect.right() - self._corner_radius, inner_rect.top())
        
        painter.end()
        
        super().paintEvent(event)
    
    # === Setters ===
    
    def setBackgroundColor(self, color: QColor):
        """Set the base background color."""
        self._background_color = color
        self.update()
    
    def setBorderColor(self, color: QColor):
        """Set the border color."""
        self._border_color = color
        self.update()
    
    def setGlowColor(self, color: QColor):
        """Set the glow accent color."""
        self._glow_color = color
        self.update()
    
    def setGlowEnabled(self, enabled: bool):
        """Enable or disable glow effect."""
        self._glow_enabled = enabled
        self.update()
    
    def setBackgroundOpacity(self, opacity: float):
        """Set background opacity (0.0 - 1.0)."""
        self._background_opacity = max(0.0, min(1.0, opacity))
        self.update()
    
    def setBorderOpacity(self, opacity: float):
        """Set border opacity (0.0 - 1.0)."""
        self._border_opacity = max(0.0, min(1.0, opacity))
        self.update()
    
    def setCornerRadius(self, radius: int):
        """Set the corner radius."""
        self._corner_radius = radius
        self.update()


class DarkGlassPanel(GlassPanel):
    """Glass panel with dark theme colors."""
    
    def __init__(self, parent=None):
        super().__init__(parent, blur_radius=15, 
                        background_opacity=0.18, border_opacity=0.12)
        self._background_color = QColor(0, 0, 0)
        self._border_color = QColor(255, 255, 255)
        self._glow_color = QColor(10, 132, 255)


class AccentGlassPanel(GlassPanel):
    """Glass panel with accent color tint."""
    
    def __init__(self, parent=None, accent_color: QColor = None):
        super().__init__(parent, blur_radius=12,
                        background_opacity=0.15, border_opacity=0.35)
        
        if accent_color is None:
            accent_color = QColor(10, 132, 255)  # Default blue accent
        
        self._background_color = accent_color
        self._border_color = accent_color
        self._glow_color = accent_color


class CardPanel(GlassPanel):
    """Card-style panel for content containers."""
    
    def __init__(self, parent=None):
        super().__init__(parent, blur_radius=8,
                        background_opacity=0.08, border_opacity=0.1)
        
        self._corner_radius = 12
        self._background_color = QColor(255, 255, 255)
        self._border_color = QColor(255, 255, 255)
        self._glow_enabled = False  # No glow for cards
        self.setContentsMargins(12, 12, 12, 12)


class InfoPanel(GlassPanel):
    """Info panel with subtle accent for displaying information."""
    
    def __init__(self, parent=None):
        super().__init__(parent, blur_radius=6,
                        background_opacity=0.06, border_opacity=0.15)
        
        self._corner_radius = 10
        self._background_color = QColor(10, 132, 255)
        self._border_color = QColor(10, 132, 255)
        self._glow_color = QColor(10, 132, 255)
        self.setContentsMargins(12, 8, 12, 8)
