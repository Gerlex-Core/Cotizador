
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSpinBox, QDoubleSpinBox, 
    QLabel, QColorDialog, QToolButton, QDial
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QColor, QAction

class CanvasToolbar(QWidget):
    """Floating toolbar for editing canvas items."""
    
    color_changed = pyqtSignal(QColor)
    scale_changed = pyqtSignal(float)
    rotation_changed = pyqtSignal(float)
    lock_toggled = pyqtSignal(bool)
    delete_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget#Toolbar {
                background-color: #2D2D2D;
                border-radius: 8px;
                border: 1px solid #3E3E3E;
            }
            QLabel { color: #CCCCCC; font-size: 10px; }
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 4px;
            }
            QToolButton:hover { background-color: #3E3E3E; }
            QDoubleSpinBox, QSpinBox {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #3E3E3E;
                border-radius: 4px;
            }
        """)
        self.setObjectName("Toolbar")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Color
        self.color_btn = QToolButton()
        self.color_btn.setText("🎨")
        self.color_btn.setToolTip("Cambiar Color")
        self.color_btn.clicked.connect(self._choose_color)
        layout.addWidget(self.color_btn)
        
        # Scale
        layout.addWidget(QLabel("Escala:"))
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 5.0)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.setValue(1.0)
        self.scale_spin.setToolTip("Escala")
        self.scale_spin.valueChanged.connect(self.scale_changed.emit)
        layout.addWidget(self.scale_spin)
        
        # Rotation
        layout.addWidget(QLabel("Rot:"))
        self.rot_spin = QDoubleSpinBox()
        self.rot_spin.setRange(-360, 360)
        self.rot_spin.setSingleStep(5)
        self.rot_spin.setToolTip("Rotación")
        self.rot_spin.valueChanged.connect(self.rotation_changed.emit)
        layout.addWidget(self.rot_spin)
        
        # Lock
        self.lock_btn = QToolButton()
        self.lock_btn.setText("🔓")
        self.lock_btn.setCheckable(True)
        self.lock_btn.setToolTip("Bloquear Posición")
        self.lock_btn.toggled.connect(self._toggle_lock)
        layout.addWidget(self.lock_btn)
        
        # Delete
        self.del_btn = QToolButton()
        self.del_btn.setText("🗑️")
        self.del_btn.setToolTip("Eliminar")
        self.del_btn.setStyleSheet("color: #FF5555;")
        self.del_btn.clicked.connect(self.delete_requested.emit)
        layout.addWidget(self.del_btn)
        
        # Current Item Ref
        self.current_item = None

    def set_item(self, item):
        """Update toolbar to match item state."""
        self.current_item = item
        if not item:
            self.hide()
            return
            
        self.blockSignals(True)
        self.scale_spin.setValue(item.scale())
        self.rot_spin.setValue(item.rotation())
        
        is_locked = getattr(item, "is_locked", False)
        self.lock_btn.setChecked(is_locked)
        self.lock_btn.setText("🔒" if is_locked else "🔓")
        
        # Determine if color is relevant
        # Access brush/pen color?
        pass # TODO: Helper to extract color
        
        self.blockSignals(False)
        self.show()
        self.adjustSize()

    def _choose_color(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.color_changed.emit(col)

    def _toggle_lock(self, checked):
        self.lock_btn.setText("🔒" if checked else "🔓")
        self.lock_toggled.emit(checked)
