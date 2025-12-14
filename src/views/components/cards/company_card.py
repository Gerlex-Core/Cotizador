from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

# Import Card base
from .card import Card
# Import LogoWidget & Buttons
from ..widgets.logo_widget import LogoWidget
from ..buttons.animated_button import AnimatedButton, DangerButton
from ...styles.icon_manager import IconManager

class CompanyListCard(Card):
    """
    Card to display a company in the list.
    """
    clicked = pyqtSignal(str) # Emits company name
    edit_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)

    def __init__(self, name: str, nit: str, logo_path: str, parent=None):
        super().__init__(parent)
        self.company_name = name
        
        # Override padding
        self.layout.setContentsMargins(12, 12, 12, 12)
        
        # Horizontal layout for the card content
        h_layout = QHBoxLayout()
        h_layout.setSpacing(16)
        
        # Logo
        self.logo = LogoWidget(max_width=60, max_height=40)
        if logo_path:
            self.logo.setLogo(logo_path, animate=False)
        else:
            self.logo.setPlaceholderText(name[:2].upper())
        h_layout.addWidget(self.logo)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        info_layout.addWidget(name_label)
        
        if nit:
            nit_label = QLabel(f"NIT: {nit}")
            nit_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.6);")
            info_layout.addWidget(nit_label)
            
        h_layout.addLayout(info_layout, 1) # 1 stretch factor to push buttons right
        
        # Buttons (only visible on hover or always?)
        # Let's add them but maybe they are handled by the main view via selection. 
        # But having them on the card is nice.
        
        # Actually, standard list behavior usually selects. 
        # Adding buttons directly might interfere with selection if not careful.
        # But let's add them for "edit" and "delete" quick access
        
        btns_layout = QVBoxLayout() # Vertical or Horizontal? Horizontal usually better.
        # But let's keep it simple.
        
        # For now, let's just make the whole card clickable.
        # We can accept clicks via mousePressEvent
        
        self.addLayout(h_layout)
        
        # Make the cursor a hand pointer
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.company_name)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.edit_clicked.emit(self.company_name)
        super().mouseDoubleClickEvent(event)


class ImageSelectionCard(Card):
    """
    Card for selecting an image (Logo or Signature) with preview.
    """
    imageChanged = pyqtSignal(str) # Emits new path

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.image_path = ""
        
        # Header
        header = QLabel(title)
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: rgba(255,255,255,0.9);")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addWidget(header)
        
        # Image Preview
        self.preview = LogoWidget(max_width=200, max_height=120)
        self.addWidget(self.preview)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_select = AnimatedButton("Seleccionar")
        self.btn_select.setIcon(IconManager.get_instance().get_icon("imageCompany", 16))
        self.btn_select.clicked.connect(self._select_image)
        btn_layout.addWidget(self.btn_select)
        
        self.btn_clear = AnimatedButton("")
        self.btn_clear.setIcon(IconManager.get_instance().get_icon("cancel", 16))
        self.btn_clear.setToolTip("Eliminar imagen")
        self.btn_clear.setMaximumWidth(40)
        self.btn_clear.clicked.connect(self.clear)
        btn_layout.addWidget(self.btn_clear)
        
        self.addLayout(btn_layout)

    def setImage(self, path: str):
        self.image_path = path
        self.preview.setLogo(path)
        
    def clear(self):
        self.image_path = ""
        self.preview.clear()
        self.imageChanged.emit("")
        
    def _select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.setImage(file_path)
            self.imageChanged.emit(file_path)

    def getPath(self):
        return self.image_path
