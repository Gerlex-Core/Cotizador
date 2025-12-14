from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QFont, QPalette

class ToastNotification(QWidget):
    """
    Animated toast notification that slides down from top.
    Supports rich text and custom styling.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # UI Setup
        self._setup_ui()
        
        # Animation
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Timer to auto-hide
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_toast)
        
        self.hide()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Container for style
        self.container = QWidget()
        self.container.setObjectName("toastContainer")
        self.container.setStyleSheet("""
            QWidget#toastContainer {
                background-color: rgba(20, 20, 20, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                border-left: 5px solid #FFC107; /* Warning Yellow Default */
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #FFC107;") # Yellow
        container_layout.addWidget(self.title_label)
        
        # Message (Rich Text)
        self.msg_label = QLabel()
        self.msg_label.setFont(QFont("Segoe UI", 10))
        self.msg_label.setStyleSheet("color: white;")
        self.msg_label.setWordWrap(True)
        self.msg_label.setTextFormat(Qt.TextFormat.RichText)
        container_layout.addWidget(self.msg_label)
        
        layout.addWidget(self.container)

    def show_toast(self, title, message, parent_widget, duration=4000, type="warning"):
        """
        Show notification sliding from top center of parent.
        Type can be: warning (yellow), error (red), success (green)
        """
        if not parent_widget:
            return
            
        # Update Content
        self.title_label.setText(title)
        self.msg_label.setText(message)
        
        # Update Style based on type
        color = "#FFC107" # Warning
        if type == "error": color = "#FF5252"
        elif type == "success": color = "#4CAF50"
        
        self.title_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.container.setStyleSheet(f"""
            QWidget#toastContainer {{
                background-color: rgba(20, 20, 20, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                border-left: 5px solid {color};
            }}
        """)
        
        # Resize to fit content
        self.adjustSize()
        self.resize(self.width(), self.height())
        
        # Position
        parent_rect = parent_widget.geometry()
        x = (parent_rect.width() - self.width()) // 2
        start_y = -self.height() - 20
        end_y = 20 # Margin from top
        
        self.move(x, start_y)
        self.show()
        self.raise_()
        
        # Animate In
        self.animation.setDuration(500)
        self.animation.setStartValue(QPoint(x, start_y))
        self.animation.setEndValue(QPoint(x, end_y))
        self.animation.start()
        
        # Start timer
        self.timer.start(duration)

    def hide_toast(self):
        """Animate out."""
        current_pos = self.pos()
        end_y = -self.height() - 20
        
        self.animation.setDuration(400)
        self.animation.setStartValue(current_pos)
        self.animation.setEndValue(QPoint(current_pos.x(), end_y))
        self.animation.finished.connect(self.close)
        self.animation.start()
