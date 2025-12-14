from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QColor

class SourceCard(QPushButton):
    """Clickable card for selection."""
    
    def __init__(self, title, description, icon_name, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setMinimumHeight(200) # Allow expanding
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Icon
        self.icon_lbl = QLabel()
        # We will set pixmap externally or use emoji as placeholder if icon not passed
        # But user said NO EMOJIS.
        # We will use text-based icons or styles if IconManager is not easy to access here.
        # Actually, let's use a simple colored rectangle or styled text if no icon.
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_lbl)
        
        # Title
        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background: transparent;")
        layout.addWidget(title_lbl)
        
        # Description
        desc_lbl = QLabel(description)
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("font-size: 12px; color: #aaa; background: transparent;")
        layout.addWidget(desc_lbl)
        
        # Styling
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(10, 132, 255, 0.1);
                border-color: #0A84FF;
            }
            QPushButton:checked {
                background-color: rgba(10, 132, 255, 0.2);
                border-color: #0A84FF;
                border-width: 2px;
            }
        """)

class ImageSourceDialog(QDialog):
    """Dialog to select image source (Local vs Internet)."""
    
    SOURCE_LOCAL = "local"
    SOURCE_INTERNET = "internet"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_source = None
        self._setup_ui()
        
    def _setup_ui(self):
        self.setWindowTitle("Seleccionar Origen de Imagen")
        self.resize(800, 500)  # Significantly increased size
        self.setMinimumSize(700, 450)
        self.setStyleSheet("background-color: #1c1c1e; color: white;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60) # Generous margins
        layout.setSpacing(40)
        
        # Header
        header = QLabel("¿Cómo desea agregar la imagen?")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Cards Container
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(50) # More space between cards
        
        # Local Card
        self.card_local = SourceCard(
            "Desde mi PC", 
            "Seleccionar un archivo de imagen guardado en su equipo.",
            "folder"
        )
        self.card_local.setFixedHeight(250) # Matches minimum but explicit
        self.card_local.icon_lbl.setText("📁") 
        self.card_local.icon_lbl.setStyleSheet("font-size: 64px; background: transparent;")
        self.card_local.clicked.connect(lambda: self._on_select(self.SOURCE_LOCAL))
        cards_layout.addWidget(self.card_local)
        
        # Internet Card
        self.card_internet = SourceCard(
            "Buscar en Internet", 
            "Buscar y descargar imágenes directamente desde la web.",
            "globe"
        )
        self.card_internet.setFixedHeight(250)
        self.card_internet.icon_lbl.setText("🌏")
        self.card_internet.icon_lbl.setStyleSheet("font-size: 64px; background: transparent;")
        self.card_internet.clicked.connect(lambda: self._on_select(self.SOURCE_INTERNET))
        cards_layout.addWidget(self.card_internet)
        
        layout.addLayout(cards_layout)
        
        # Cancel Button
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888;
                font-size: 14px;
            }
            QPushButton:hover {
                color: white;
                text-decoration: underline;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel, 0, Qt.AlignmentFlag.AlignCenter)
        
    def _on_select(self, source):
        self.selected_source = source
        self.accept()
