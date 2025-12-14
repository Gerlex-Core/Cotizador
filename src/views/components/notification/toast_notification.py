"""
Toast Notification Component with slide animations.
Implements IThemeable for full theme customization.
"""

from typing import Dict, Any, List
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QFont, QPalette

from src.views.styles.themeable import IThemeable, get_component_registry
from src.views.styles.animation_engine import get_animation_engine
from src.views.styles.sound_manager import get_sound_manager


class ToastNotification(QWidget, IThemeable):
    """
    Animated toast notification that slides down from top.
    Supports rich text, custom styling, and full theme support.
    """
    
    # Toast types and their default colors
    TOAST_COLORS = {
        'warning': '#FFC107',
        'error': '#FF5252',
        'success': '#4CAF50',
        'info': '#2196F3'
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Theme config
        self._theme_config: Dict[str, Any] = {}
        self._play_sounds = True
        
        # Engine references
        self._animation_engine = get_animation_engine()
        self._sound_manager = get_sound_manager()
        
        # UI Setup
        self._setup_ui()
        
        # Get animation config
        show_config = self._animation_engine.get_animation_config('toast', 'show')
        hide_config = self._animation_engine.get_animation_config('toast', 'hide')
        
        # Animation
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self.animation.setDuration(show_config.get('duration', 300))
        
        self._hide_duration = hide_config.get('duration', 200)
        
        # Timer to auto-hide
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_toast)
        
        self.hide()
        
        # Register with component registry
        get_component_registry().register(self)
    
    # === IThemeable Implementation ===
    
    @property
    def component_type(self) -> str:
        return "toast"
    
    @property
    def theme_capabilities(self) -> List[str]:
        return ['colors', 'animations', 'sounds']
    
    def get_theme_metadata(self) -> Dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.objectName() or f"toast_{id(self)}",
            "visible": self.isVisible(),
            "capabilities": self.theme_capabilities
        }
    
    def apply_theme_config(self, config: Dict[str, Any]):
        self._theme_config = config
        
        # Update animation durations from new config
        show_config = self._animation_engine.get_animation_config('toast', 'show')
        hide_config = self._animation_engine.get_animation_config('toast', 'hide')
        
        self.animation.setDuration(show_config.get('duration', 300))
        self._hide_duration = hide_config.get('duration', 200)
    
    def on_theme_changed(self, theme_name: str):
        pass  # Toast styles are set per-show
    
    # === UI Setup ===

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Container for style
        self.container = QWidget()
        self.container.setObjectName("toastContainer")
        self._apply_container_style('#FFC107')  # Default warning style
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #FFC107;")
        container_layout.addWidget(self.title_label)
        
        # Message (Rich Text)
        self.msg_label = QLabel()
        self.msg_label.setFont(QFont("Segoe UI", 10))
        self.msg_label.setStyleSheet("color: white;")
        self.msg_label.setWordWrap(True)
        self.msg_label.setTextFormat(Qt.TextFormat.RichText)
        container_layout.addWidget(self.msg_label)
        
        layout.addWidget(self.container)
    
    def _apply_container_style(self, color: str):
        """Apply container style with given accent color."""
        self.container.setStyleSheet(f"""
            QWidget#toastContainer {{
                background-color: rgba(20, 20, 20, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                border-left: 5px solid {color};
            }}
        """)

    def show_toast(self, title, message, parent_widget, duration=4000, type="warning"):
        """
        Show notification sliding from top center of parent.
        Type can be: warning (yellow), error (red), success (green), info (blue)
        """
        if not parent_widget:
            return
        
        # Play sound
        if self._play_sounds:
            sound_name = 'notification' if type == 'info' else type
            self._sound_manager.play(sound_name)
        
        # Update Content
        self.title_label.setText(title)
        self.msg_label.setText(message)
        
        # Get color for type
        color = self.TOAST_COLORS.get(type, '#FFC107')
        
        # Update Style based on type
        self.title_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self._apply_container_style(color)
        
        # Resize to fit content
        self.adjustSize()
        self.resize(self.width(), self.height())
        
        # Position
        parent_rect = parent_widget.geometry()
        x = (parent_rect.width() - self.width()) // 2
        start_y = -self.height() - 20
        end_y = 20  # Margin from top
        
        self.move(x, start_y)
        self.show()
        self.raise_()
        
        # Animate In
        self.animation.setStartValue(QPoint(x, start_y))
        self.animation.setEndValue(QPoint(x, end_y))
        self.animation.start()
        
        # Start timer
        self.timer.start(duration)

    def hide_toast(self):
        """Animate out."""
        current_pos = self.pos()
        end_y = -self.height() - 20
        
        self.animation.setDuration(self._hide_duration)
        self.animation.setStartValue(current_pos)
        self.animation.setEndValue(QPoint(current_pos.x(), end_y))
        self.animation.finished.connect(self.close)
        self.animation.start()
    
    def setSoundsEnabled(self, enabled: bool):
        """Enable or disable sound effects."""
        self._play_sounds = enabled
