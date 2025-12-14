"""
Animated Button Component with hover, press, and ripple effects.
Implements IThemeable for full theme customization support.
"""

from typing import Dict, Any, List
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, Qt, QPoint, QTimer,
    pyqtProperty, QRect
)
from PyQt6.QtGui import QPainter, QColor, QBrush

from src.views.styles.themeable import IThemeable, get_component_registry
from src.views.styles.animation_engine import get_animation_engine
from src.views.styles.sound_manager import get_sound_manager
from src.views.styles.effects_engine import get_effects_engine


class AnimatedButton(QPushButton, IThemeable):
    """
    Premium animated button with scale, color transitions, and ripple effect.
    Fully themeable - supports colors, animations, effects, and sounds.
    """
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        
        # Animation properties
        self._scale = 1.0
        self._ripple_radius = 0
        self._ripple_opacity = 0
        self._ripple_center = QPoint()
        self._background_color = QColor("#2C2C2E")
        self._hover_color = QColor("#0A84FF")
        self._current_color = self._background_color
        
        # Theme configuration cache
        self._theme_config: Dict[str, Any] = {}
        self._glow_enabled = False
        self._glow_color = "#0A84FF"
        self._glow_intensity = 0.3
        self._play_sounds = True
        
        # Get engine references
        self._animation_engine = get_animation_engine()
        self._sound_manager = get_sound_manager()
        self._effects_engine = get_effects_engine()
        
        # Setup animations
        self._setup_animations()
        
        # Enable mouse tracking for smooth effects
        self.setMouseTracking(True)
        
        # Minimum size for good clickability
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Register with component registry
        get_component_registry().register(self)
    
    # === IThemeable Implementation ===
    
    @property
    def component_type(self) -> str:
        """Return component type identifier."""
        return "button"
    
    @property
    def theme_capabilities(self) -> List[str]:
        """Return list of supported theme capabilities."""
        return ['colors', 'animations', 'effects', 'sounds']
    
    def get_theme_metadata(self) -> Dict[str, Any]:
        """Return component metadata for theme customization."""
        return {
            "type": self.component_type,
            "id": self.objectName() or f"button_{id(self)}",
            "text": self.text(),
            "enabled": self.isEnabled(),
            "visible": self.isVisible(),
            "geometry": {
                "x": self.x(),
                "y": self.y(),
                "width": self.width(),
                "height": self.height()
            },
            "capabilities": self.theme_capabilities,
            "properties": {
                "background_color": self._background_color.name(),
                "hover_color": self._hover_color.name(),
                "glow_enabled": self._glow_enabled
            }
        }
    
    def apply_theme_config(self, config: Dict[str, Any]):
        """Apply theme configuration to this button."""
        self._theme_config = config
        
        # Apply animation settings
        anim_config = self._animation_engine.get_animation_config('button', 'hover')
        if 'scale' in anim_config:
            self._hover_scale = anim_config['scale']
        if 'duration' in anim_config:
            self._scale_anim.setDuration(anim_config['duration'])
        
        # Apply glow settings
        hover_config = anim_config
        self._glow_enabled = hover_config.get('glow', False)
        self._glow_color = hover_config.get('glowColor', '#0A84FF')
        self._glow_intensity = hover_config.get('glowIntensity', 0.3)
        
        # Apply ripple settings
        ripple_config = self._animation_engine.get_animation_config('button', 'ripple')
        if ripple_config.get('enabled', True):
            if 'duration' in ripple_config:
                self._ripple_anim.setDuration(ripple_config['duration'])
        
        # Apply component-specific settings from config
        if config:
            padding = config.get('padding', '10px 20px')
            border_radius = config.get('borderRadius', '8px')
            # Could apply more specific styling here
        
        self.update()
    
    def get_layout_info(self) -> Dict[str, Any]:
        """Return layout information."""
        return {
            "position": (self.x(), self.y()),
            "size": (self.width(), self.height()),
            "min_size": (self.minimumWidth(), self.minimumHeight())
        }
    
    def on_theme_changed(self, theme_name: str):
        """Called when theme changes."""
        self.update()
    
    # === Animation Setup ===
    
    def _setup_animations(self):
        """Initialize all button animations."""
        # Get animation config
        hover_config = self._animation_engine.get_animation_config('button', 'hover')
        press_config = self._animation_engine.get_animation_config('button', 'press')
        ripple_config = self._animation_engine.get_animation_config('button', 'ripple')
        
        # Store hover scale
        self._hover_scale = hover_config.get('scale', 1.03)
        self._press_scale = press_config.get('scale', 0.97)
        
        # Scale animation
        self._scale_anim = QPropertyAnimation(self, b"buttonScale")
        self._scale_anim.setDuration(hover_config.get('duration', 150))
        self._scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Ripple animation
        self._ripple_anim = QPropertyAnimation(self, b"rippleRadius")
        self._ripple_anim.setDuration(ripple_config.get('duration', 400))
        self._ripple_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._ripple_fade = QPropertyAnimation(self, b"rippleOpacity")
        self._ripple_fade.setDuration(ripple_config.get('duration', 400))
        self._ripple_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    # === Properties for animation ===
    
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
    
    # === Event Handlers ===
    
    def enterEvent(self, event):
        """Handle mouse enter with scale effect."""
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(self._hover_scale)
        self._scale_anim.start()
        
        # Play hover sound if enabled
        if self._play_sounds:
            self._sound_manager.play('hover')
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave - restore scale."""
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(1.0)
        self._scale_anim.start()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press with ripple effect."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Play click sound
            if self._play_sounds:
                self._sound_manager.play('click')
            
            # Start ripple from click position
            self._ripple_center = event.pos()
            
            # Calculate max radius (diagonal of button)
            max_radius = (self.width() ** 2 + self.height() ** 2) ** 0.5
            
            # Ripple expansion
            self._ripple_anim.stop()
            self._ripple_anim.setStartValue(0)
            self._ripple_anim.setEndValue(max_radius)
            
            # Ripple fade
            self._ripple_fade.stop()
            self._ripple_opacity = 0.3
            self._ripple_fade.setStartValue(0.3)
            self._ripple_fade.setEndValue(0)
            
            self._ripple_anim.start()
            self._ripple_fade.start()
            
            # Scale down slightly
            self._scale_anim.stop()
            self._scale_anim.setStartValue(self._scale)
            self._scale_anim.setEndValue(self._press_scale)
            self._scale_anim.start()
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release - restore scale."""
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(self._hover_scale if self.underMouse() else 1.0)
        self._scale_anim.start()
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event):
        """Custom paint with scale, ripple, and glow effects."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Apply scale transform
        center = self.rect().center()
        painter.translate(center)
        painter.scale(self._scale, self._scale)
        painter.translate(-center)
        
        # Draw glow effect if enabled and hovering
        if self._glow_enabled and self.underMouse():
            from PyQt6.QtCore import QRectF
            rect = QRectF(self.rect())
            self._effects_engine.draw_glow(
                painter, rect, 
                self._glow_color, 
                self._glow_intensity
            )
        
        # Draw the ripple effect
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
        
        # Call parent paint for actual button rendering
        super().paintEvent(event)
    
    def setColors(self, background: str, hover: str):
        """Set custom colors for the button."""
        self._background_color = QColor(background)
        self._hover_color = QColor(hover)
    
    def setSoundsEnabled(self, enabled: bool):
        """Enable or disable sound effects."""
        self._play_sounds = enabled


class PrimaryButton(AnimatedButton):
    """Primary action button with accent color."""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("primaryButton")
        self.setStyleSheet("""
            QPushButton#primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0A84FF, stop:1 #0066CC);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3399FF, stop:1 #0A84FF);
            }
            QPushButton#primaryButton:pressed {
                background: #0066CC;
            }
        """)


class SecondaryButton(AnimatedButton):
    """Secondary action button with outline style."""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("secondaryButton")
        self.setStyleSheet("""
            QPushButton#secondaryButton {
                background: transparent;
                color: #0A84FF;
                border: 2px solid #0A84FF;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#secondaryButton:hover {
                background: rgba(10, 132, 255, 0.1);
            }
            QPushButton#secondaryButton:pressed {
                background: rgba(10, 132, 255, 0.2);
            }
        """)


class DangerButton(AnimatedButton):
    """Danger/delete action button with red color."""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("dangerButton")
        self.setStyleSheet("""
            QPushButton#dangerButton {
                background: #FF3B30;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#dangerButton:hover {
                background: #FF5C54;
            }
            QPushButton#dangerButton:pressed {
                background: #D32F2F;
            }
        """)
