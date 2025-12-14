"""
Effects Engine - Visual effects manager for themed components.
Handles blur, bloom, glow, shadows, gradients, and transparency effects.
"""

from typing import Dict, Any, Optional, Tuple
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QColor, QPainter, QLinearGradient, QRadialGradient,
    QBrush, QPen, QPainterPath
)
from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect, QGraphicsBlurEffect


class EffectsEngine:
    """
    Manages visual effects for themed components.
    Provides methods for applying blur, glow, shadows, and other effects.
    """
    
    _instance = None
    
    def __init__(self):
        self._blur_enabled = True
        self._glow_enabled = True
        self._shadow_enabled = True
        self._transparency_enabled = True
        
        # Default effect configurations
        self._default_blur_radius = 12
        self._default_glow_color = "#0A84FF"
        self._default_glow_intensity = 0.4
        self._default_shadow_config = {
            'blur_radius': 15,
            'offset_x': 0,
            'offset_y': 4,
            'color': 'rgba(0, 0, 0, 0.4)'
        }
    
    @classmethod
    def get_instance(cls) -> 'EffectsEngine':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = EffectsEngine()
        return cls._instance
    
    def configure(self, config: Dict[str, Any]):
        """
        Configure effects from theme settings.
        
        Args:
            config: Effects configuration from theme JSON
        """
        self._blur_enabled = config.get('blur', {}).get('enabled', True)
        self._default_blur_radius = config.get('blur', {}).get('radius', 12)
        
        self._glow_enabled = config.get('glow', {}).get('enabled', True)
        self._default_glow_color = config.get('glow', {}).get('color', '#0A84FF')
        self._default_glow_intensity = config.get('glow', {}).get('intensity', 0.4)
        
        self._transparency_enabled = config.get('transparency', 0) > 0
        self._shadow_enabled = True  # Always available
    
    # === Blur Effects ===
    
    def apply_blur(
        self,
        widget: QWidget,
        radius: float = None,
        enabled: bool = True
    ) -> Optional[QGraphicsBlurEffect]:
        """
        Apply blur effect to widget.
        
        Args:
            widget: Target widget
            radius: Blur radius (uses default if None)
            enabled: Whether to apply or remove effect
        
        Returns:
            The blur effect if applied, None otherwise
        """
        if not enabled or not self._blur_enabled:
            widget.setGraphicsEffect(None)
            return None
        
        effect = QGraphicsBlurEffect(widget)
        effect.setBlurRadius(radius or self._default_blur_radius)
        effect.setBlurHints(QGraphicsBlurEffect.BlurHint.AnimationHint)
        widget.setGraphicsEffect(effect)
        return effect
    
    # === Shadow Effects ===
    
    def apply_shadow(
        self,
        widget: QWidget,
        config: Dict[str, Any] = None
    ) -> Optional[QGraphicsDropShadowEffect]:
        """
        Apply drop shadow effect to widget.
        
        Args:
            widget: Target widget
            config: Shadow configuration (uses defaults if None)
        
        Returns:
            The shadow effect if applied
        """
        if not self._shadow_enabled:
            return None
        
        cfg = config or self._default_shadow_config
        
        effect = QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(cfg.get('blur_radius', 15))
        effect.setXOffset(cfg.get('offset_x', 0))
        effect.setYOffset(cfg.get('offset_y', 4))
        effect.setColor(self._parse_color(cfg.get('color', 'rgba(0,0,0,0.4)')))
        
        widget.setGraphicsEffect(effect)
        return effect
    
    def create_shadow_config(
        self,
        blur_radius: int = 15,
        offset_x: int = 0,
        offset_y: int = 4,
        color: str = 'rgba(0, 0, 0, 0.4)'
    ) -> Dict[str, Any]:
        """Create a shadow configuration dict."""
        return {
            'blur_radius': blur_radius,
            'offset_x': offset_x,
            'offset_y': offset_y,
            'color': color
        }
    
    # === Glow Effects ===
    
    def draw_glow(
        self,
        painter: QPainter,
        rect: QRectF,
        color: str = None,
        intensity: float = None,
        radius: int = 3
    ):
        """
        Draw glow effect around a rectangle.
        
        Args:
            painter: QPainter to draw with
            rect: Rectangle to draw glow around
            color: Glow color (hex or rgba)
            intensity: Glow opacity (0.0-1.0)
            radius: Number of glow layers
        """
        if not self._glow_enabled:
            return
        
        glow_color = self._parse_color(color or self._default_glow_color)
        glow_intensity = intensity or self._default_glow_intensity
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for i in range(radius):
            glow_rect = rect.adjusted(-i*2, -i*2, i*2, i*2)
            alpha = glow_intensity * (1.0 - i/radius) * 0.5
            
            glow_color.setAlphaF(max(0, alpha))
            
            path = QPainterPath()
            path.addRoundedRect(glow_rect, 8 + i, 8 + i)
            
            painter.setPen(QPen(glow_color, 1.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
    
    # === Gradient Creation ===
    
    def create_linear_gradient(
        self,
        colors: list,
        direction: str = 'vertical',
        rect: QRectF = None
    ) -> QLinearGradient:
        """
        Create a linear gradient.
        
        Args:
            colors: List of color stops, either strings or (position, color) tuples
            direction: 'vertical', 'horizontal', or 'diagonal'
            rect: Rectangle for gradient bounds (for directional calculation)
        
        Returns:
            QLinearGradient object
        """
        width = rect.width() if rect else 100
        height = rect.height() if rect else 100
        
        if direction == 'vertical':
            gradient = QLinearGradient(0, 0, 0, height)
        elif direction == 'horizontal':
            gradient = QLinearGradient(0, 0, width, 0)
        else:  # diagonal
            gradient = QLinearGradient(0, 0, width, height)
        
        # Add color stops
        for i, item in enumerate(colors):
            if isinstance(item, tuple):
                position, color = item
            else:
                position = i / max(1, len(colors) - 1)
                color = item
            
            gradient.setColorAt(position, self._parse_color(color))
        
        return gradient
    
    def create_radial_gradient(
        self,
        center_color: str,
        edge_color: str,
        center: Tuple[float, float] = (0.5, 0.5),
        radius: float = 100
    ) -> QRadialGradient:
        """
        Create a radial gradient.
        
        Args:
            center_color: Color at center
            edge_color: Color at edge
            center: Center point as (x, y) fractions
            radius: Gradient radius
        
        Returns:
            QRadialGradient object
        """
        gradient = QRadialGradient(center[0] * radius * 2, center[1] * radius * 2, radius)
        gradient.setColorAt(0, self._parse_color(center_color))
        gradient.setColorAt(1, self._parse_color(edge_color))
        return gradient
    
    # === Glass/Transparency Effects ===
    
    def draw_glass_background(
        self,
        painter: QPainter,
        rect: QRectF,
        corner_radius: int = 12,
        opacity: float = 0.08
    ):
        """
        Draw a glassmorphism-style background.
        
        Args:
            painter: QPainter to draw with
            rect: Rectangle to fill
            corner_radius: Corner radius
            opacity: Base opacity
        """
        if not self._transparency_enabled:
            return
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(255, 255, 255, int(255 * opacity * 1.5)))
        gradient.setColorAt(0.1, QColor(255, 255, 255, int(255 * opacity)))
        gradient.setColorAt(0.5, QColor(255, 255, 255, int(255 * opacity * 0.7)))
        gradient.setColorAt(1.0, QColor(0, 0, 0, int(255 * opacity * 0.5)))
        
        path = QPainterPath()
        path.addRoundedRect(rect, corner_radius, corner_radius)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 255, 255, int(255 * opacity * 2)), 1))
        painter.drawPath(path)
        
        # Top reflection
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(
            int(rect.left() + corner_radius),
            int(rect.top() + 1),
            int(rect.right() - corner_radius),
            int(rect.top() + 1)
        )
    
    # === Bloom Effect ===
    
    def draw_bloom(
        self,
        painter: QPainter,
        rect: QRectF,
        color: str,
        intensity: float = 0.3
    ):
        """
        Draw a bloom lighting effect.
        
        Args:
            painter: QPainter to draw with
            rect: Rectangle for bloom center
            color: Bloom color
            intensity: Bloom intensity
        """
        bloom_color = self._parse_color(color)
        
        # Create radial gradient for bloom
        center_x = rect.center().x()
        center_y = rect.center().y()
        radius = max(rect.width(), rect.height())
        
        gradient = QRadialGradient(center_x, center_y, radius)
        
        bloom_color.setAlphaF(intensity * 0.6)
        gradient.setColorAt(0, bloom_color)
        
        bloom_color.setAlphaF(intensity * 0.3)
        gradient.setColorAt(0.5, bloom_color)
        
        bloom_color.setAlphaF(0)
        gradient.setColorAt(1, bloom_color)
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        
        painter.drawEllipse(rect.adjusted(-radius*0.3, -radius*0.3, radius*0.3, radius*0.3))
    
    # === Helper Methods ===
    
    def _parse_color(self, color_str: str) -> QColor:
        """Parse a color string to QColor."""
        if not color_str:
            return QColor(255, 255, 255)
        
        if color_str.startswith('rgba('):
            # Parse rgba(r, g, b, a)
            parts = color_str.replace('rgba(', '').replace(')', '').split(',')
            r = int(parts[0].strip())
            g = int(parts[1].strip())
            b = int(parts[2].strip())
            a = float(parts[3].strip())
            color = QColor(r, g, b)
            color.setAlphaF(a)
            return color
        elif color_str.startswith('rgb('):
            # Parse rgb(r, g, b)
            parts = color_str.replace('rgb(', '').replace(')', '').split(',')
            r = int(parts[0].strip())
            g = int(parts[1].strip())
            b = int(parts[2].strip())
            return QColor(r, g, b)
        else:
            # Hex color
            return QColor(color_str)
    
    def get_contrasting_text_color(self, background: str) -> str:
        """Get appropriate text color based on background luminance."""
        color = self._parse_color(background)
        
        # Calculate luminance
        luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
        
        return '#FFFFFF' if luminance < 0.5 else '#1D1D1F'
    
    # === New Advanced Effects ===
    
    def apply_transparency(
        self,
        widget: QWidget,
        opacity: float = 0.95,
        enabled: bool = True
    ):
        """
        Apply transparency effect to widget.
        
        Args:
            widget: Target widget
            opacity: Opacity level (0.0-1.0)
            enabled: Whether to apply or remove effect
        """
        if not enabled or not self._transparency_enabled:
            widget.setWindowOpacity(1.0)
            return
        
        widget.setWindowOpacity(max(0.0, min(1.0, opacity)))
    
    def draw_frosted_glass(
        self,
        painter: QPainter,
        rect: QRectF,
        base_color: str = '#1C1C1E',
        blur_intensity: float = 0.3,
        corner_radius: int = 12
    ):
        """
        Draw a frosted glass effect (simulated without actual blur).
        
        Args:
            painter: QPainter to draw with
            rect: Rectangle to fill
            base_color: Base color of the glass
            blur_intensity: How much the background shows through
            corner_radius: Corner radius
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        base = self._parse_color(base_color)
        base.setAlphaF(1.0 - blur_intensity)
        
        path = QPainterPath()
        path.addRoundedRect(rect, corner_radius, corner_radius)
        
        # Draw the frosted background
        painter.setBrush(QBrush(base))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Add subtle gradient overlay for depth
        gradient = QLinearGradient(0, rect.top(), 0, rect.bottom())
        gradient.setColorAt(0, QColor(255, 255, 255, int(255 * 0.1)))
        gradient.setColorAt(0.5, QColor(255, 255, 255, int(255 * 0.02)))
        gradient.setColorAt(1, QColor(0, 0, 0, int(255 * 0.05)))
        
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)
        
        # Add edge highlight
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawPath(path)
    
    def draw_light_effect(
        self,
        painter: QPainter,
        rect: QRectF,
        light_color: str = '#FFFFFF',
        direction: str = 'top',
        intensity: float = 0.3
    ):
        """
        Draw a directional light effect.
        
        Args:
            painter: QPainter to draw with
            rect: Rectangle for the light
            light_color: Color of the light
            direction: Direction of light ('top', 'left', 'right', 'bottom', 'center')
            intensity: Light intensity (0.0-1.0)
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = self._parse_color(light_color)
        
        if direction == 'center':
            # Radial light from center
            gradient = QRadialGradient(
                rect.center().x(), rect.center().y(),
                max(rect.width(), rect.height()) / 2
            )
            color.setAlphaF(intensity * 0.5)
            gradient.setColorAt(0, color)
            color.setAlphaF(0)
            gradient.setColorAt(1, color)
        else:
            # Directional light
            if direction == 'top':
                gradient = QLinearGradient(0, rect.top(), 0, rect.bottom())
            elif direction == 'bottom':
                gradient = QLinearGradient(0, rect.bottom(), 0, rect.top())
            elif direction == 'left':
                gradient = QLinearGradient(rect.left(), 0, rect.right(), 0)
            else:  # right
                gradient = QLinearGradient(rect.right(), 0, rect.left(), 0)
            
            color.setAlphaF(intensity * 0.6)
            gradient.setColorAt(0, color)
            color.setAlphaF(intensity * 0.2)
            gradient.setColorAt(0.3, color)
            color.setAlphaF(0)
            gradient.setColorAt(1, color)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)
    
    def draw_vector_shape(
        self,
        painter: QPainter,
        shape: str,
        rect: QRectF,
        fill_color: str = None,
        stroke_color: str = None,
        stroke_width: float = 1.0
    ):
        """
        Draw a vector shape.
        
        Args:
            painter: QPainter to draw with
            shape: Shape type ('circle', 'triangle', 'diamond', 'hexagon', 'star')
            rect: Bounding rectangle
            fill_color: Fill color (None for no fill)
            stroke_color: Stroke color (None for no stroke)
            stroke_width: Width of stroke
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if fill_color:
            painter.setBrush(QBrush(self._parse_color(fill_color)))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        
        if stroke_color:
            painter.setPen(QPen(self._parse_color(stroke_color), stroke_width))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
        
        path = QPainterPath()
        cx, cy = rect.center().x(), rect.center().y()
        w, h = rect.width(), rect.height()
        
        if shape == 'circle':
            path.addEllipse(rect)
        elif shape == 'triangle':
            path.moveTo(cx, rect.top())
            path.lineTo(rect.right(), rect.bottom())
            path.lineTo(rect.left(), rect.bottom())
            path.closeSubpath()
        elif shape == 'diamond':
            path.moveTo(cx, rect.top())
            path.lineTo(rect.right(), cy)
            path.lineTo(cx, rect.bottom())
            path.lineTo(rect.left(), cy)
            path.closeSubpath()
        elif shape == 'hexagon':
            import math
            for i in range(6):
                angle = math.pi / 3 * i - math.pi / 2
                x = cx + (w / 2) * math.cos(angle)
                y = cy + (h / 2) * math.sin(angle)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
        elif shape == 'star':
            import math
            outer_r = min(w, h) / 2
            inner_r = outer_r * 0.4
            for i in range(10):
                angle = math.pi / 5 * i - math.pi / 2
                r = outer_r if i % 2 == 0 else inner_r
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
        else:
            # Default rectangle
            path.addRoundedRect(rect, 4, 4)
        
        painter.drawPath(path)
    
    def draw_neon_glow(
        self,
        painter: QPainter,
        rect: QRectF,
        color: str = '#00FFFF',
        intensity: float = 0.8,
        layers: int = 5
    ):
        """
        Draw a neon glow effect (multiple layered glows for neon look).
        
        Args:
            painter: QPainter to draw with
            rect: Rectangle to draw glow around
            color: Neon color
            intensity: Glow intensity
            layers: Number of glow layers
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        glow_color = self._parse_color(color)
        
        # Draw outer glows
        for i in range(layers, 0, -1):
            expansion = i * 3
            glow_rect = rect.adjusted(-expansion, -expansion, expansion, expansion)
            
            alpha = (intensity * (1.0 - (i / layers)) * 0.4)
            glow_color.setAlphaF(max(0, min(1, alpha)))
            
            path = QPainterPath()
            path.addRoundedRect(glow_rect, 8 + i * 2, 8 + i * 2)
            
            painter.setPen(QPen(glow_color, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
        
        # Draw core glow
        glow_color.setAlphaF(intensity)
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        painter.setPen(QPen(glow_color, 1.5))
        painter.drawPath(path)
    
    def create_transition_effect(
        self,
        effect_type: str = 'fade',
        from_state: Dict[str, Any] = None,
        to_state: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a transition effect configuration.
        
        Args:
            effect_type: Type of transition ('fade', 'slide', 'scale', 'blur')
            from_state: Starting state configuration
            to_state: Ending state configuration
        
        Returns:
            Transition configuration dict
        """
        return {
            'type': effect_type,
            'from': from_state or {},
            'to': to_state or {},
            'duration': 300,
            'easing': 'OutCubic'
        }
    
    def get_effect_config(self) -> Dict[str, Any]:
        """Get current effect configuration."""
        return {
            'blur_enabled': self._blur_enabled,
            'blur_radius': self._default_blur_radius,
            'glow_enabled': self._glow_enabled,
            'glow_color': self._default_glow_color,
            'glow_intensity': self._default_glow_intensity,
            'shadow_enabled': self._shadow_enabled,
            'transparency_enabled': self._transparency_enabled
        }


# Global instance
def get_effects_engine() -> EffectsEngine:
    """Get the global effects engine instance."""
    return EffectsEngine.get_instance()
