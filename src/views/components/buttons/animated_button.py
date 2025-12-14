"""
Animated Button Component with hover, press, and ripple effects.
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, Qt, QPoint, QTimer,
    pyqtProperty, QRect
)
from PyQt6.QtGui import QPainter, QColor, QBrush


class AnimatedButton(QPushButton):
    """
    Premium animated button with scale, color transitions, and ripple effect.
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
        
        # Setup animations
        self._setup_animations()
        
        # Enable mouse tracking for smooth effects
        self.setMouseTracking(True)
        
        # Minimum size for good clickability
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _setup_animations(self):
        """Initialize all button animations."""
        # Scale animation
        self._scale_anim = QPropertyAnimation(self, b"buttonScale")
        self._scale_anim.setDuration(150)
        self._scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Ripple animation
        self._ripple_anim = QPropertyAnimation(self, b"rippleRadius")
        self._ripple_anim.setDuration(400)
        self._ripple_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._ripple_fade = QPropertyAnimation(self, b"rippleOpacity")
        self._ripple_fade.setDuration(400)
        self._ripple_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    # Custom properties for animation
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
    
    def enterEvent(self, event):
        """Handle mouse enter with scale effect."""
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(1.03)
        self._scale_anim.start()
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
            self._scale_anim.setEndValue(0.97)
            self._scale_anim.start()
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release - restore scale."""
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._scale)
        self._scale_anim.setEndValue(1.03 if self.underMouse() else 1.0)
        self._scale_anim.start()
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event):
        """Custom paint with scale and ripple."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Apply scale transform
        center = self.rect().center()
        painter.translate(center)
        painter.scale(self._scale, self._scale)
        painter.translate(-center)
        
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
