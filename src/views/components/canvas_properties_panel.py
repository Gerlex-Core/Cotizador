
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, 
    QPushButton, QColorDialog, QSlider, QGroupBox, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

class CanvasPropertiesPanel(QWidget):
    """
    Vertical side panel for editing properties of selected canvas items.
    Replaces the floating CanvasToolbar.
    """
    
    color_changed = pyqtSignal(QColor)
    stroke_color_changed = pyqtSignal(QColor)
    stroke_width_changed = pyqtSignal(float)
    scale_changed = pyqtSignal(float)
    rotation_changed = pyqtSignal(float)
    opacity_changed = pyqtSignal(float)
    lock_toggled = pyqtSignal(bool)
    delete_active = pyqtSignal()
    z_order_changed = pyqtSignal(str) # "front", "back", "up", "down"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setStyleSheet("""
            CanvasPropertiesPanel {
                background-color: #2D2D2D;
                border-left: 1px solid #3E3E3E;
            }
            QLabel { color: #E0E0E0; font-family: 'Segoe UI'; }
            QGroupBox { 
                border: 1px solid #3E3E3E; 
                border-radius: 4px; 
                margin-top: 1em; 
                padding-top: 10px;
                color: #AAAAAA;
                font-weight: bold;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
            QPushButton {
                background-color: #3E3E3E; border: none; border-radius: 4px; padding: 6px; color: white;
            }
            QPushButton:hover { background-color: #505050; }
            QSpinBox, QDoubleSpinBox {
                background-color: #1E1E1E; border: 1px solid #3E3E3E; border-radius: 3px; color: white; padding: 4px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("Propiedades")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0A84FF;")
        layout.addWidget(title)
        
        # 1. Appearance Section
        grp_style = QGroupBox("Apariencia")
        form_style = QFormLayout(grp_style)
        
        # Color (Fill)
        self.btn_color = QPushButton("Color de Relleno")
        self.btn_color.clicked.connect(self._choose_color)
        form_style.addRow("Relleno:", self.btn_color)
        
        # Stroke Color
        self.btn_stroke_color = QPushButton("Color de Borde")
        self.btn_stroke_color.clicked.connect(self._choose_stroke_color)
        form_style.addRow("Borde:", self.btn_stroke_color)
        
        # Stroke Width
        self.spin_stroke_width = QDoubleSpinBox()
        self.spin_stroke_width.setRange(0, 50)
        self.spin_stroke_width.setSingleStep(0.5)
        self.spin_stroke_width.setValue(1.0)
        self.spin_stroke_width.valueChanged.connect(self.stroke_width_changed.emit)
        form_style.addRow("Grosor:", self.spin_stroke_width)
        
        # Opacity
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(0, 100)
        self.slider_opacity.setValue(100)
        self.slider_opacity.valueChanged.connect(self._on_opacity_change)
        form_style.addRow("Opacidad:", self.slider_opacity)
        
        layout.addWidget(grp_style)
        
        # 2. Transform Section
        grp_trans = QGroupBox("Transformación")
        form_trans = QFormLayout(grp_trans)
        
        # Scale
        self.spin_scale = QDoubleSpinBox()
        self.spin_scale.setRange(0.1, 5.0)
        self.spin_scale.setSingleStep(0.1)
        self.spin_scale.setValue(1.0)
        self.spin_scale.valueChanged.connect(self.scale_changed.emit)
        form_trans.addRow("Escala:", self.spin_scale)
        
        # Rotation
        self.spin_rot = QDoubleSpinBox()
        self.spin_rot.setRange(-360, 360)
        self.spin_rot.setSuffix("°")
        self.spin_rot.valueChanged.connect(self.rotation_changed.emit)
        form_trans.addRow("Rotación:", self.spin_rot)
        
        layout.addWidget(grp_trans)
        
        # 3. Arrange Section
        grp_arrange = QGroupBox("Organización")
        vbox_arrange = QVBoxLayout(grp_arrange)
        
        hbox_order = QHBoxLayout()
        btn_front = QPushButton("Frente")
        btn_front.clicked.connect(lambda: self.z_order_changed.emit("front"))
        btn_back = QPushButton("Fondo")
        btn_back.clicked.connect(lambda: self.z_order_changed.emit("back"))
        hbox_order.addWidget(btn_front)
        hbox_order.addWidget(btn_back)
        vbox_arrange.addLayout(hbox_order)
        
        self.btn_lock = QPushButton("Bloquear Posición")
        self.btn_lock.setCheckable(True)
        self.btn_lock.toggled.connect(self.lock_toggled.emit)
        vbox_arrange.addWidget(self.btn_lock)
        
        self.btn_delete = QPushButton("Eliminar Objeto")
        self.btn_delete.setStyleSheet("background-color: #8B0000; color: white;")
        self.btn_delete.clicked.connect(self.delete_active.emit)
        vbox_arrange.addWidget(self.btn_delete)
        
        layout.addWidget(grp_arrange)
        
        # === TEXT MODE CONTROLS (Initially Hidden) ===
        grp_text = QGroupBox("Formato de Texto")
        form_text = QFormLayout(grp_text)
        
        # Font Size (simpler version for now)
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(8, 120)
        self.spin_font_size.setValue(12)
        form_text.addRow("Tamaño:", self.spin_font_size)
        
        # Text Formatting
        hbox_format = QHBoxLayout()
        self.btn_text_bold = QPushButton("B")
        self.btn_text_bold.setCheckable(True)
        self.btn_text_bold.setStyleSheet("font-weight: bold; max-width: 30px;")
        
        self.btn_text_italic = QPushButton("I")
        self.btn_text_italic.setCheckable(True)
        self.btn_text_italic.setStyleSheet("font-style: italic; max-width: 30px;")
        
        hbox_format.addWidget(self.btn_text_bold)
        hbox_format.addWidget(self.btn_text_italic)
        hbox_format.addStretch()
        form_text.addRow("Estilo:", hbox_format)
        
        # Text Color
        self.btn_text_color = QPushButton("Color de Texto")
        self.btn_text_color.clicked.connect(self._choose_text_color)
        form_text.addRow("Color:", self.btn_text_color)
        
        layout.addWidget(grp_text)
        grp_text.hide()  # Hidden by default
        
        layout.addStretch()
        
        # Current color state
        self._current_color = QColor("white")
        self._current_stroke = QColor("black")
        self._current_text_color = QColor("black")
        self._current_mode = "shape"  # "text" or "shape"
        
        # Store references to mode-specific widgets
        self._shape_widgets = [grp_style, grp_trans, grp_arrange]
        self._text_widgets = [grp_text]
    
    def set_mode(self, mode: str):
        """Switch panel mode between 'text' and 'shape'."""
        if mode == self._current_mode:
            return
        
        self._current_mode = mode
        
        # Show/hide appropriate controls
        if mode == "text":
            for widget in self._shape_widgets:
                widget.hide()
            for widget in self._text_widgets:
                widget.show()
        else:  # shape mode
            for widget in self._text_widgets:
                widget.hide()
            for widget in self._shape_widgets:
                widget.show()
        
        print(f"[PROPERTIES] Switched to {mode} mode")

    def set_values(self, color, opacity, scale, rotation, locked, mode="shape"):
        """Update panel with values from selected item."""
        self.set_mode(mode)
        
        # Update common properties
        self._current_color = QColor(color) if color else QColor("transparent")
        self.btn_color.setStyleSheet(f"background-color: {self._current_color.name()}; color: {'black' if self._current_color.lightness() > 128 else 'white'};")
        
        self.blockSignals(True)
        self.slider_opacity.setValue(int(opacity * 100))
        self.spin_scale.setValue(scale)
        self.spin_rot.setValue(rotation)
        self.btn_lock.setChecked(locked)
        self.btn_lock.setText("Desbloquear" if locked else "Bloquear Posición")
        self.blockSignals(False)

    def _choose_color(self):
        col = QColorDialog.getColor(self._current_color, self)
        if col.isValid():
            self._current_color = col
            self.color_changed.emit(col)
            self.btn_color.setStyleSheet(f"background-color: {col.name()};")

    def _choose_stroke_color(self):
        col = QColorDialog.getColor(self._current_stroke, self)
        if col.isValid():
            self._current_stroke = col
            self.stroke_color_changed.emit(col)
            self.btn_stroke_color.setStyleSheet(f"background-color: {col.name()};")

    def _choose_text_color(self):
        """Choose text color for text items."""
        col = QColorDialog.getColor(self._current_text_color, self)
        if col.isValid():
            self._current_text_color = col
            self.color_changed.emit(col)  # Use same signal for consistency
            self.btn_text_color.setStyleSheet(f"background-color: {col.name()};")
    
    def _on_opacity_change(self, val):
        self.opacity_changed.emit(val / 100.0)
