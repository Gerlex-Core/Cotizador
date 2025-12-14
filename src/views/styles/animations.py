"""
Animation utilities and constants for the Cotizador application.
Provides reusable animation factories and timing configurations.
"""

from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QSequentialAnimationGroup, QAbstractAnimation
)
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect


# Animation duration constants (milliseconds)
DURATIONS = {
    'instant': 50,
    'fast': 150,
    'normal': 250,
    'slow': 400,
    'very_slow': 600
}

# Easing curve presets
EASINGS = {
    'smooth': QEasingCurve.Type.InOutCubic,
    'bounce': QEasingCurve.Type.OutBounce,
    'elastic': QEasingCurve.Type.OutElastic,
    'overshoot': QEasingCurve.Type.OutBack,
    'linear': QEasingCurve.Type.Linear,
    'ease_out': QEasingCurve.Type.OutCubic,
    'ease_in': QEasingCurve.Type.InCubic
}


class AnimationFactory:
    """Factory class for creating reusable animations."""
    
    @staticmethod
    def fade_in(widget: QWidget, duration: int = DURATIONS['normal'], 
                easing: QEasingCurve.Type = EASINGS['smooth']) -> QPropertyAnimation:
        """Create a fade-in animation for a widget."""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(easing)
        
        return animation
    
    @staticmethod
    def fade_out(widget: QWidget, duration: int = DURATIONS['normal'],
                 easing: QEasingCurve.Type = EASINGS['smooth']) -> QPropertyAnimation:
        """Create a fade-out animation for a widget."""
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(easing)
        
        return animation
    
    @staticmethod
    def scale(widget: QWidget, start_scale: float = 1.0, end_scale: float = 1.05,
              duration: int = DURATIONS['fast'],
              easing: QEasingCurve.Type = EASINGS['smooth']) -> QPropertyAnimation:
        """Create a scale animation using geometry."""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        
        original_geometry = widget.geometry()
        
        # Calculate scaled geometries
        center_x = original_geometry.center().x()
        center_y = original_geometry.center().y()
        
        start_width = int(original_geometry.width() * start_scale)
        start_height = int(original_geometry.height() * start_scale)
        end_width = int(original_geometry.width() * end_scale)
        end_height = int(original_geometry.height() * end_scale)
        
        animation.setEasingCurve(easing)
        
        return animation
    
    @staticmethod
    def slide_in(widget: QWidget, direction: str = 'left',
                 duration: int = DURATIONS['normal'],
                 easing: QEasingCurve.Type = EASINGS['ease_out']) -> QPropertyAnimation:
        """Create a slide-in animation from a direction."""
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        
        end_pos = widget.pos()
        
        if direction == 'left':
            start_pos = end_pos - widget.rect().topRight()
        elif direction == 'right':
            start_pos = end_pos + widget.rect().topRight()
        elif direction == 'top':
            start_pos = end_pos - widget.rect().bottomLeft()
        else:  # bottom
            start_pos = end_pos + widget.rect().bottomLeft()
        
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        
        return animation
    
    @staticmethod
    def color_transition_stylesheet(widget: QWidget, property_name: str,
                                    start_color: str, end_color: str,
                                    duration: int = DURATIONS['normal']) -> QPropertyAnimation:
        """
        Creates animation data for color transitions.
        Note: StyleSheet animations require manual interpolation.
        This returns animation timing data for use with QTimer.
        """
        animation = QPropertyAnimation(widget, b"styleSheet")
        animation.setDuration(duration)
        # Actual color interpolation would need custom implementation
        return animation
    
    @staticmethod
    def create_group(animations: list, parallel: bool = True) -> QAbstractAnimation:
        """Create a grouped animation (parallel or sequential)."""
        if parallel:
            group = QParallelAnimationGroup()
        else:
            group = QSequentialAnimationGroup()
        
        for anim in animations:
            group.addAnimation(anim)
        
        return group


class HoverAnimationMixin:
    """Mixin class to add hover animations to widgets."""
    
    _hover_animation: QPropertyAnimation = None
    _normal_style: str = ""
    _hover_style: str = ""
    
    def setup_hover_animation(self, normal_style: str, hover_style: str):
        """Setup the hover animation with normal and hover styles."""
        self._normal_style = normal_style
        self._hover_style = hover_style
    
    def enterEvent(self, event):
        """Handle mouse enter."""
        if hasattr(self, '_hover_style') and self._hover_style:
            self.setStyleSheet(self._hover_style)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        if hasattr(self, '_normal_style') and self._normal_style:
            self.setStyleSheet(self._normal_style)
        super().leaveEvent(event)


class PressAnimationMixin:
    """Mixin class to add press animations to widgets."""
    
    _press_scale: float = 0.95
    _original_geometry = None
    
    def mousePressEvent(self, event):
        """Handle mouse press with scale effect."""
        self._original_geometry = self.geometry()
        
        # Scale down
        center = self.geometry().center()
        new_width = int(self.width() * self._press_scale)
        new_height = int(self.height() * self._press_scale)
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release - restore original size."""
        if self._original_geometry:
            self.setGeometry(self._original_geometry)
        
        super().mouseReleaseEvent(event)
