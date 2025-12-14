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
from ...styles.theme_manager import ThemeManager

class CompanyListCard(Card):
    """
    Card to display a company in the list.
    Supports selected state with accent color highlighting.
    """
    clicked = pyqtSignal(str) # Emits company name
    edit_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)

    def __init__(self, name: str, nit: str, logo_path: str, parent=None):
        super().__init__(parent)
        self.company_name = name
        self._is_selected = False
        
        # Store base and selected styles
        self._base_style = """
            CompanyListCard {
                background-color: rgba(30, 30, 30, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
            CompanyListCard:hover {
                background-color: rgba(40, 40, 40, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """
        
        # Override padding
        self._content_layout.setContentsMargins(12, 12, 12, 12)
        
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
        
        self.addLayout(h_layout)
        
        # Make the cursor a hand pointer
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def setSelected(self, selected: bool):
        """Set the selected state of the card with accent color highlighting."""
        self._is_selected = selected
        
        if selected:
            # Get accent color from current theme
            accent_color = ThemeManager.get_accent_color()
            
            # Create selected style with accent color
            selected_style = f"""
                CompanyListCard {{
                    background-color: rgba({self._hex_to_rgb(accent_color)}, 0.15);
                    border: 2px solid {accent_color};
                    border-radius: 12px;
                }}
                CompanyListCard:hover {{
                    background-color: rgba({self._hex_to_rgb(accent_color)}, 0.25);
                    border: 2px solid {accent_color};
                }}
            """
            self.setStyleSheet(selected_style)
        else:
            self.setStyleSheet(self._base_style)
    
    def isSelected(self) -> bool:
        """Check if the card is currently selected."""
        return self._is_selected
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB comma-separated string."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"{r}, {g}, {b}"
        except (ValueError, IndexError):
            return "10, 132, 255"  # Default accent color RGB

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
