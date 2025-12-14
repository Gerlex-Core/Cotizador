from PyQt6.QtWidgets import QFrame, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class Card(QFrame):
    """
    A generic card container with modern styling, border radius, and hover effects.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Base styling
        self.setStyleSheet("""
            Card {
                background-color: rgba(30, 30, 30, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
            Card:hover {
                background-color: rgba(40, 40, 40, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        
        # Layout - using _content_layout to avoid shadowing QWidget.layout()
        self._content_layout = QVBoxLayout(self)
        self._content_layout.setContentsMargins(16, 16, 16, 16)
        self._content_layout.setSpacing(8)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
    def addWidget(self, widget):
        self._content_layout.addWidget(widget)
        
    def addLayout(self, layout):
        self._content_layout.addLayout(layout)
        
    def addStretch(self, stretch=0):
        self._content_layout.addStretch(stretch)
