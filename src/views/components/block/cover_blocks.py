"""
Cover Page Blocks - Draggable blocks for cover page customization.
These blocks allow drag-and-drop reordering of cover page elements.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QLineEdit, QTextEdit, QCheckBox, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class CoverBlock(QFrame):
    """Base class for cover page blocks with move and delete controls."""
    
    removed = pyqtSignal(object)
    moved_up = pyqtSignal(object)
    moved_down = pyqtSignal(object)
    content_changed = pyqtSignal()
    
    BLOCK_TYPE = "base"
    BLOCK_TITLE = "Elemento"
    BLOCK_ICON = "📄"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._order = 0
        self._setup_base_ui()
    
    def _setup_base_ui(self):
        """Setup base UI with header and controls."""
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("""
            CoverBlock, CoverTitleBlock, CoverSubtitleBlock, CoverDescriptionBlock,
            CoverReferenceBlock, CoverLogoBlock, CoverCompanyBlock, CoverClientBlock,
            CoverDateBlock, CoverFooterBlock {
                background-color: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                margin: 2px 0;
            }
            CoverBlock:hover, CoverTitleBlock:hover, CoverSubtitleBlock:hover, 
            CoverDescriptionBlock:hover, CoverReferenceBlock:hover, CoverLogoBlock:hover,
            CoverCompanyBlock:hover, CoverClientBlock:hover, CoverDateBlock:hover,
            CoverFooterBlock:hover {
                border-color: #0A84FF;
                background-color: rgba(10, 132, 255, 0.08);
            }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 6, 10, 10)
        self.main_layout.setSpacing(6)
        
        # Header with icon, title, and controls
        header = QHBoxLayout()
        header.setSpacing(6)
        
        # Drag handle / Order indicator
        self.order_label = QLabel(f"{self.BLOCK_ICON}")
        self.order_label.setStyleSheet("""
            background-color: rgba(10, 132, 255, 0.2);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        """)
        self.order_label.setCursor(Qt.CursorShape.OpenHandCursor)
        header.addWidget(self.order_label)
        
        # Block type label
        self.type_label = QLabel(self.BLOCK_TITLE)
        self.type_label.setStyleSheet("font-weight: bold; color: rgba(255,255,255,0.8); font-size: 11px;")
        header.addWidget(self.type_label)
        
        header.addStretch()
        
        # Control buttons
        btn_style = """
            QPushButton {
                background-color: rgba(255,255,255,0.1);
                border: none;
                border-radius: 4px;
                color: white;
                padding: 2px 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.2);
            }
        """
        
        btn_up = QPushButton("▲")
        btn_up.setFixedSize(24, 24)
        btn_up.setStyleSheet(btn_style)
        btn_up.setToolTip("Mover arriba")
        btn_up.clicked.connect(lambda _: self.moved_up.emit(self))
        header.addWidget(btn_up)
        
        btn_down = QPushButton("▼")
        btn_down.setFixedSize(24, 24)
        btn_down.setStyleSheet(btn_style)
        btn_down.setToolTip("Mover abajo")
        btn_down.clicked.connect(lambda _: self.moved_down.emit(self))
        header.addWidget(btn_down)
        
        btn_delete = QPushButton("✕")
        btn_delete.setFixedSize(24, 24)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 69, 58, 0.3);
                border: none;
                border-radius: 4px;
                color: white;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 69, 58, 0.6);
            }
        """)
        btn_delete.setToolTip("Eliminar")
        btn_delete.clicked.connect(lambda _: self.removed.emit(self))
        header.addWidget(btn_delete)
        
        self.main_layout.addLayout(header)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)
        self.main_layout.addWidget(self.content_widget)
    
    def set_order(self, order: int):
        """Set the display order number."""
        self._order = order
    
    def get_order(self) -> int:
        """Get the current order."""
        return self._order
    
    def get_data(self) -> dict:
        """Get block data for saving. Override in subclasses."""
        return {"type": self.BLOCK_TYPE, "order": self._order}
    
    def load_data(self, data: dict):
        """Load block data. Override in subclasses."""
        self._order = data.get("order", 0)


class CoverTitleBlock(CoverBlock):
    """Block for the main cover title."""
    
    BLOCK_TYPE = "title"
    BLOCK_TITLE = "Título Principal"
    BLOCK_ICON = "📝"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_content()
    
    def _setup_content(self):
        """Setup title input."""
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Nombre del proyecto...")
        self.title_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border-color: #0A84FF;
            }
        """)
        self.title_input.textChanged.connect(lambda _: self.content_changed.emit())
        self.content_layout.addWidget(self.title_input)
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["text"] = self.title_input.text()
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        self.title_input.setText(data.get("text", ""))


class CoverSubtitleBlock(CoverBlock):
    """Block for the cover subtitle."""
    
    BLOCK_TYPE = "subtitle"
    BLOCK_TITLE = "Subtítulo"
    BLOCK_ICON = "📋"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_content()
    
    def _setup_content(self):
        """Setup subtitle input."""
        self.subtitle_input = QLineEdit()
        self.subtitle_input.setPlaceholderText("Ej: Propuesta Comercial 2024")
        self.subtitle_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #0A84FF;
            }
        """)
        self.subtitle_input.textChanged.connect(lambda _: self.content_changed.emit())
        self.content_layout.addWidget(self.subtitle_input)
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["text"] = self.subtitle_input.text()
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        self.subtitle_input.setText(data.get("text", ""))


class CoverDescriptionBlock(CoverBlock):
    """Block for cover description/text."""
    
    BLOCK_TYPE = "description"
    BLOCK_TITLE = "Descripción"
    BLOCK_ICON = "📄"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_content()
    
    def _setup_content(self):
        """Setup description editor."""
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Breve descripción del proyecto...")
        self.description_input.setMaximumHeight(80)
        self.description_input.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 11px;
            }
            QTextEdit:focus {
                border-color: #0A84FF;
            }
        """)
        self.description_input.textChanged.connect(lambda: self.content_changed.emit())
        self.content_layout.addWidget(self.description_input)
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["text"] = self.description_input.toPlainText()
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        self.description_input.setHtml(data.get("text", ""))


class CoverReferenceBlock(CoverBlock):
    """Block for project reference."""
    
    BLOCK_TYPE = "reference"
    BLOCK_TITLE = "Referencia"
    BLOCK_ICON = "🔖"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_content()
    
    def _setup_content(self):
        """Setup reference input."""
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Ej: REF-2024-001")
        self.reference_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #0A84FF;
            }
        """)
        self.reference_input.textChanged.connect(lambda _: self.content_changed.emit())
        self.content_layout.addWidget(self.reference_input)
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["text"] = self.reference_input.text()
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        self.reference_input.setText(data.get("text", ""))


class CoverLogoBlock(CoverBlock):
    """Block for logo settings."""
    
    BLOCK_TYPE = "logo"
    BLOCK_TITLE = "Logo"
    BLOCK_ICON = "🖼️"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._company_name = ""
        self._setup_content()
    
    def _setup_content(self):
        """Setup logo options with company name display."""
        # Company name display (read-only, synced from quotation)
        company_row = QHBoxLayout()
        company_row.addWidget(QLabel("Empresa:"))
        self.company_label = QLabel("(Sin seleccionar)")
        self.company_label.setStyleSheet("""
            QLabel {
                color: #0A84FF;
                font-weight: bold;
                padding: 4px 8px;
                background-color: rgba(10, 132, 255, 0.1);
                border-radius: 4px;
            }
        """)
        company_row.addWidget(self.company_label)
        company_row.addStretch()
        self.content_layout.addLayout(company_row)
        
        # Logo options
        options_layout = QHBoxLayout()
        
        self.show_logo_check = QCheckBox("Mostrar Logo")
        self.show_logo_check.setChecked(True)
        self.show_logo_check.setStyleSheet("color: white;")
        self.show_logo_check.stateChanged.connect(lambda _: self.content_changed.emit())
        options_layout.addWidget(self.show_logo_check)
        
        options_layout.addWidget(QLabel("Tamaño:"))
        self.logo_size = QSpinBox()
        self.logo_size.setRange(50, 200)
        self.logo_size.setValue(120)
        self.logo_size.setSuffix(" px")
        self.logo_size.setStyleSheet("""
            QSpinBox {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                padding: 4px;
                color: white;
            }
        """)
        self.logo_size.valueChanged.connect(lambda _: self.content_changed.emit())
        options_layout.addWidget(self.logo_size)
        
        options_layout.addStretch()
        self.content_layout.addLayout(options_layout)
    
    def set_project_data(self, company_name: str = ""):
        """Set project data to display (called from dialog)."""
        self._company_name = company_name
        self.company_label.setText(company_name if company_name else "(Sin seleccionar)")
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["show_logo"] = self.show_logo_check.isChecked()
        data["logo_size"] = self.logo_size.value()
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        self.show_logo_check.setChecked(data.get("show_logo", True))
        self.logo_size.setValue(data.get("logo_size", 120))


class CoverCompanyBlock(CoverBlock):
    """Block for company name display (read-only from quotation)."""
    
    BLOCK_TYPE = "company"
    BLOCK_TITLE = "Empresa"
    BLOCK_ICON = "🏢"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._company_name = ""
        self._setup_content()
    
    def _setup_content(self):
        """Setup company display."""
        row = QHBoxLayout()
        
        # Value display
        self.value_label = QLabel("(Sin seleccionar)")
        self.value_label.setStyleSheet("""
            QLabel {
                color: #0A84FF;
                font-weight: bold;
                font-size: 13px;
                padding: 6px 12px;
                background-color: rgba(10, 132, 255, 0.15);
                border-radius: 6px;
            }
        """)
        row.addWidget(self.value_label)
        row.addStretch()
        
        # Note
        note = QLabel("📌 Se toma de la cotización")
        note.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 9px;")
        row.addWidget(note)
        
        self.content_layout.addLayout(row)
    
    def set_project_data(self, company_name: str = "", **kwargs):
        """Set project data to display."""
        self._company_name = company_name
        self.value_label.setText(company_name if company_name else "(Sin seleccionar)")
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["visible"] = True
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)


class CoverClientBlock(CoverBlock):
    """Block for client name display (read-only from quotation)."""
    
    BLOCK_TYPE = "client"
    BLOCK_TITLE = "Cliente"
    BLOCK_ICON = "👤"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._client_name = ""
        self._setup_content()
    
    def _setup_content(self):
        """Setup client display."""
        row = QHBoxLayout()
        
        label = QLabel("Preparado para:")
        label.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 10px;")
        row.addWidget(label)
        
        # Value display
        self.value_label = QLabel("(Sin cliente)")
        self.value_label.setStyleSheet("""
            QLabel {
                color: #30D158;
                font-weight: bold;
                font-size: 13px;
                padding: 6px 12px;
                background-color: rgba(48, 209, 88, 0.15);
                border-radius: 6px;
            }
        """)
        row.addWidget(self.value_label)
        row.addStretch()
        
        # Note
        note = QLabel("� Se toma de la cotización")
        note.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 9px;")
        row.addWidget(note)
        
        self.content_layout.addLayout(row)
    
    def set_project_data(self, client_name: str = "", **kwargs):
        """Set project data to display."""
        self._client_name = client_name
        self.value_label.setText(client_name if client_name else "(Sin cliente)")
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["visible"] = True
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)


class CoverDateBlock(CoverBlock):
    """Block for date display (read-only from quotation)."""
    
    BLOCK_TYPE = "date"
    BLOCK_TITLE = "Fecha"
    BLOCK_ICON = "📅"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_date = ""
        self._setup_content()
    
    def _setup_content(self):
        """Setup date display."""
        row = QHBoxLayout()
        
        # Value display
        self.value_label = QLabel("--/--/----")
        self.value_label.setStyleSheet("""
            QLabel {
                color: #FF9F0A;
                font-weight: bold;
                font-size: 12px;
                padding: 6px 12px;
                background-color: rgba(255, 159, 10, 0.15);
                border-radius: 6px;
            }
        """)
        row.addWidget(self.value_label)
        row.addStretch()
        
        # Note
        note = QLabel("📌 Se toma de la cotización")
        note.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 9px;")
        row.addWidget(note)
        
        self.content_layout.addLayout(row)
    
    def set_project_data(self, project_date: str = "", **kwargs):
        """Set project data to display."""
        self._project_date = project_date
        self.value_label.setText(project_date if project_date else "--/--/----")
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["visible"] = True
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)


class CoverFooterBlock(CoverBlock):
    """Block for footer text."""
    
    BLOCK_TYPE = "footer"
    BLOCK_TITLE = "Pie de Página"
    BLOCK_ICON = "📎"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_content()
    
    def _setup_content(self):
        """Setup footer input."""
        row = QHBoxLayout()
        
        self.footer_input = QLineEdit()
        self.footer_input.setPlaceholderText("Ej: Confidencial")
        self.footer_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #0A84FF;
            }
        """)
        self.footer_input.textChanged.connect(lambda _: self.content_changed.emit())
        row.addWidget(self.footer_input)
        
        self.show_border_check = QCheckBox("Mostrar Borde")
        self.show_border_check.setChecked(True)
        self.show_border_check.setStyleSheet("color: white; font-size: 11px;")
        self.show_border_check.stateChanged.connect(lambda _: self.content_changed.emit())
        row.addWidget(self.show_border_check)
        
        self.content_layout.addLayout(row)
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["text"] = self.footer_input.text()
        data["show_border"] = self.show_border_check.isChecked()
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        self.footer_input.setText(data.get("text", ""))
        self.show_border_check.setChecked(data.get("show_border", True))


# Block type registry
COVER_BLOCK_TYPES = {
    "title": CoverTitleBlock,
    "subtitle": CoverSubtitleBlock,
    "description": CoverDescriptionBlock,
    "reference": CoverReferenceBlock,
    "logo": CoverLogoBlock,
    "company": CoverCompanyBlock,
    "client": CoverClientBlock,
    "date": CoverDateBlock,
    "footer": CoverFooterBlock,
}

# Block menu items for add menu
COVER_BLOCK_MENU = [
    ("logo", "🖼️ Logo"),
    ("company", "🏢 Empresa"),
    ("client", "👤 Cliente"),
    ("date", "📅 Fecha"),
    ("title", "📝 Título Principal"),
    ("subtitle", "📋 Subtítulo"),
    ("description", "📄 Descripción"),
    ("reference", "🔖 Referencia"),
    ("footer", "📎 Pie de Página"),
]
