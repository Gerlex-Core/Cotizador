"""
Cover Page Dialog - Editor for quotation cover page.
Allows customization of the cover page with project name, description,
logo display options, and professional styling.
Features: Visual grid for style selection and live preview panel.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QLineEdit, QTextEdit, QCheckBox, QComboBox, QPushButton,
    QGroupBox, QFrame, QColorDialog, QSpinBox, QScrollArea,
    QSplitter, QWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient, QPainterPath

from .styles.theme_manager import ThemeManager
from ..logic.config.config_manager import ConfigManager


class CoverPreviewWidget(QFrame):
    """Live preview widget that shows how the cover page will look."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 350)
        self.setMaximumWidth(320)
        self._data = {}
        self._style = "Clásico Centrado"
        self._accent_color = "#0A84FF"
        self._company_name = "Mi Empresa"
        self._client_name = "Cliente"
        self._project_date = "12/12/2024"
        
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 8px;
            }
        """)
    
    def update_preview(self, data: dict, style: str, accent_color: str,
                       company: str = "", client: str = "", date: str = ""):
        """Update preview with current settings."""
        self._data = data
        self._style = style
        self._accent_color = accent_color
        self._company_name = company or "Mi Empresa"
        self._client_name = client or "Cliente"
        self._project_date = date or "12/12/2024"
        self.update()
    
    def paintEvent(self, event):
        """Draw the cover page preview."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor("white"))
        
        # Use the shared engine
        from src.export.cover_styles import CoverPageRenderer
        renderer = CoverPageRenderer()
        
        # Prepare context data
        cover_data = self._data.copy()
        cover_data["layout_style"] = self._style
        cover_data["accent_color"] = self._accent_color
        
        logo_path = "" # TODO: Pass logo path from settings/config
        # Ideally, main window passes full company data. 
        # For now, we simulate basic data if missing
        
        renderer.draw_cover_qt(
            painter, 
            self.width(), 
            self.height(),
            self._company_name,
            {"logo": "media/logo.png"}, # Placeholder, need real data flow
            {"name": self._client_name},
            self._project_date,
            cover_data
        )
        
        painter.end()


    def _draw_minimalist(self, p: QPainter, w: int, h: int, m: int, accent: QColor):
        p.setPen(QPen(accent, 2))
        p.drawLine(w//2 - 20, h - 40, w//2 + 20, h - 40)
        
        p.setFont(QFont("Arial", 12, QFont.Weight.Light))
        p.setPen(QPen(QColor("#1a1a1a")))
        title = self._data.get("project_name", "PROYECTO")
        p.drawText(m, h//2 - 30, w - 2*m, 20, Qt.AlignmentFlag.AlignCenter, title[:25])
        
        p.setFont(QFont("Arial", 8))
        p.setPen(QPen(QColor("#888888")))
        p.drawText(m, h//2, w - 2*m, 10, Qt.AlignmentFlag.AlignCenter, "SUBTITULO")
        
        # Logo placeholder
        if self._data.get("show_logo", True):
            p.setPen(QPen(QColor("#dddddd")))
            p.drawRect(w//2 - 15, h//2 - 60, 30, 20)

    def _draw_corporate(self, p: QPainter, w: int, h: int, m: int, accent: QColor):
        p.fillRect(0, 0, w, 40, accent)
        
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("white")))
        path = QPainterPath()
        path.moveTo(0, 40)
        path.cubicTo(w*0.3, 40, w*0.7, 60, w, 40)
        path.lineTo(w, 45)
        path.lineTo(0, 45)
        p.drawPath(path)
        
        p.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        p.setPen(QPen(QColor("white")))
        p.drawText(10, 25, self._company_name[:15])
        
        p.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        p.setPen(QPen(QColor("#1a1a1a")))
        p.drawText(20, h//2 - 20, self._data.get("project_name", "PROYECTO")[:15])
        
        p.setPen(QPen(accent, 2))
        p.drawLine(20, h//2, 60, h//2)

    def _draw_sidebar(self, p: QPainter, w: int, h: int, m: int, accent: QColor):
        p.fillRect(0, 0, w//3, h, accent)
        
        p.setPen(QPen(QColor("white")))
        p.setFont(QFont("Arial", 6, QFont.Weight.Bold))
        p.drawText(5, h - 30, "PREPARADO POR")
        p.setFont(QFont("Arial", 5))
        p.drawText(5, h - 20, self._company_name[:12])
        
        p.setPen(QPen(QColor("#1a1a1a")))
        p.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title = self._data.get("project_name", "PROYECTO")
        # Word wrap basic simulation
        p.drawText(w//3 + 10, h//3, w - w//3 - 15, 60, Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, title[:20])

    def _draw_futuristic(self, p: QPainter, w: int, h: int, m: int, accent: QColor):
        p.fillRect(0, 0, w, h, QColor("#1a1a1a"))
        
        p.setPen(QPen(accent, 1))
        p.setOpacity(0.3)
        for i in range(0, w, 20): p.drawLine(i, 0, i, h)
        p.setOpacity(1.0)
        
        # Circuit
        p.setPen(QPen(accent, 1))
        p.drawLine(10, h-10, 50, h-10)
        p.drawLine(50, h-10, 70, h-30)
        p.drawEllipse(70, h-30, 2, 2)
        
        p.setPen(QPen(QColor("white")))
        p.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        p.drawText(0, h//2, w, 20, Qt.AlignmentFlag.AlignCenter, self._data.get("project_name", "SYSTEM")[:20].upper())

    def _draw_architectural(self, p: QPainter, w: int, h: int, m: int, accent: QColor):
        p.fillRect(0, 0, w, h, QColor("#E0E0E0"))
        p.setPen(QPen(QColor("white")))
        p.setOpacity(0.5)
        for i in range(0, w, 15): p.drawLine(i, 0, i, h)
        for i in range(0, h, 15): p.drawLine(0, i, w, i)
        p.setOpacity(1.0)
        
        # Info Box bottom right
        box_w, box_h = 80, 40
        p.setPen(QPen(QColor("#1a1a1a"), 1))
        p.setBrush(QBrush(QColor("white")))
        p.drawRect(w - box_w - 5, 10, box_w, box_h)
        
        p.setFont(QFont("Arial", 5))
        p.drawText(w - box_w, 20, "PROYECTO:")
        p.drawText(w - box_w, 30, self._data.get("project_name", "COT")[:10])
        
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(w//2 - 20, h//2 - 20, 40, 40)

    def _draw_editorial(self, p: QPainter, w: int, h: int, m: int, accent: QColor):
        p.fillRect(0, 0, w, h, QColor("#FAFAFA"))
        
        p.setPen(QPen(QColor("#f0f0f0")))
        p.setFont(QFont("Arial", 60, QFont.Weight.Bold))
        p.drawText(w - 60, h - 20, "24")
        
        p.setPen(QPen(QColor("#1a1a1a")))
        p.setFont(QFont("Times New Roman", 20, QFont.Weight.Bold))
        p.drawText(10, h//2 - 20, self._data.get("project_name", "Title")[:10])
        
        p.setPen(QPen(accent, 4))
        p.drawLine(10, h//2, 40, h//2)
        
        p.setFont(QFont("Arial", 6, QFont.Weight.Bold))
        p.setPen(QPen(accent))
        p.drawText(10, h - 20, "EMPRESA")

    def _draw_organic(self, p: QPainter, w: int, h: int, m: int, accent: QColor):
        p.setPen(Qt.PenStyle.NoPen)
        c = QColor(accent)
        c.setAlpha(50)
        p.setBrush(QBrush(c))
        p.drawEllipse(-40, h-80, 120, 120)
        p.drawEllipse(w-40, -40, 100, 100)
        
        p.setPen(QPen(QColor("#1a1a1a")))
        p.setFont(QFont("Georgia", 12))
        p.drawText(0, h//2, w, 20, Qt.AlignmentFlag.AlignCenter, self._data.get("project_name", "Proyecto")[:20])

    def _draw_industrial(self, p: QPainter, w: int, h: int, m: int, accent: QColor):
        # Yellow black theme
        p.setPen(QPen(QColor("#1a1a1a"), 3))
        p.drawRect(5, 5, w-10, h-10)
        
        # Stripes
        p.save()
        p.setClipRect(10, h-30, w-20, 20)
        for i in range(0, w, 10):
            p.drawLine(i, h, i+10, h-30)
        p.restore()
        
        p.setBrush(QBrush(QColor("#1a1a1a")))
        p.drawRect(20, h//2 - 15, w-40, 30)
        
        p.setPen(QPen(QColor("white")))
        p.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        p.drawText(0, h//2 - 10, w, 20, Qt.AlignmentFlag.AlignCenter, self._data.get("project_name", "COT")[:15].upper())

    def _draw_luxury(self, p: QPainter, w: int, h: int, m: int, accent: QColor):
        p.fillRect(0, 0, w, h, QColor("#1f1f1f"))
        gold = QColor("#C9A962")
        p.setPen(QPen(gold, 2))
        p.drawRect(10, 10, w-20, h-20)
        p.setPen(QPen(gold, 1))
        p.drawRect(14, 14, w-28, h-28)
        
        p.setFont(QFont("Times New Roman", 10, QFont.Weight.Bold))
        p.drawText(0, h//2, w, 20, Qt.AlignmentFlag.AlignCenter, "PROPUESTA")

    def _draw_abstract(self, p: QPainter, w: int, h: int, m: int, accent: QColor):
        c = QColor(accent)
        c.setAlpha(60)
        p.setBrush(QBrush(c))
        p.setPen(Qt.PenStyle.NoPen)
        
        path = QPainterPath()
        path.moveTo(0, h)
        path.lineTo(w, h)
        path.lineTo(0, h//2)
        p.drawPath(path)
        
        p.setPen(QPen(QColor("#1a1a1a")))
        p.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        p.drawText(w - 80, h//3, self._data.get("project_name", "COT")[:10])
        
        p.fillRect(w-40, h//3 + 5, 30, 4, accent)


class StyleCard(QFrame):
    """Clickable card showing a style preview."""
    
    clicked = pyqtSignal(str)
    
    def __init__(self, style_name: str, description: str, parent=None):
        super().__init__(parent)
        self.style_name = style_name
        self._selected = False
        
        self.setFixedSize(140, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Mini preview icon
        self.preview = QFrame()
        self.preview.setFixedSize(124, 55)
        self.preview.setStyleSheet("background: white; border-radius: 4px;")
        layout.addWidget(self.preview)
        
        # Style name
        name_label = QLabel(style_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("font-size: 10px; font-weight: bold; color: white;")
        layout.addWidget(name_label)
        
        self._update_style()
    
    def set_selected(self, selected: bool):
        self._selected = selected
        self._update_style()
    
    def _update_style(self):
        if self._selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(10, 132, 255, 0.4);
                    border: 2px solid #0A84FF;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
            """)
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.style_name)
        super().mousePressEvent(event)


class CoverPageDialog(QDialog):
    """
    Dialog for editing the cover page of a quotation.
    Features a visual grid for style selection and live preview panel.
    """
    
    saved = pyqtSignal(dict)
    
    def __init__(self, parent=None, data: dict = None, company_name: str = "", 
                 client_name: str = "", project_date: str = ""):
        super().__init__(parent)
        
        # Load styles from Engine
        from src.export.cover_styles import CoverPageRenderer
        self.renderer = CoverPageRenderer()
        self.STYLES = self.renderer.get_available_styles()
        
        # Fallback if no JSONs yet
        if not self.STYLES:
            self.STYLES = [("Default", "Estilo por defecto")]

        self.data = data or {}
        self.company_name = company_name
        self.client_name = client_name
        self.project_date = project_date
        self._accent_color = "#0A84FF"
        self._selected_style = "Clásico Centrado"
        self._style_cards = {}
        
        self.setWindowTitle("Editor de Carátula")
        self.setMinimumSize(950, 700)
        self.setModal(True)
        
        # Apply theme
        config = ConfigManager()
        ThemeManager.apply_theme(self, config.tema)
        
        # Update preview timer
        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._update_preview)
        self._preview_timer.start(100)
        
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        """Create the dialog UI with splitter layout and visual style grid."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Configuración de Carátula")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0A84FF;")
        main_layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Seleccione un estilo y configure las opciones. El preview se actualiza en tiempo real."
        )
        desc.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 12px;")
        main_layout.addWidget(desc)
        
        # === Main Splitter: Options | Preview ===
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: rgba(255,255,255,0.1);
                width: 3px;
            }
        """)
        
        # LEFT SIDE: Scroll area with options
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(12)
        
        # === STYLE GRID ===
        style_group = QGroupBox("Seleccionar Estilo de Carátula")
        style_group.setStyleSheet(self._group_style())
        style_grid_layout = QGridLayout(style_group)
        style_grid_layout.setSpacing(10)
        
        # Create style cards in a 4x2 grid
        for i, (style_name, style_desc) in enumerate(self.STYLES):
            card = StyleCard(style_name, style_desc)
            card.clicked.connect(self._on_style_selected)
            self._style_cards[style_name] = card
            row = i // 4
            col = i % 4
            style_grid_layout.addWidget(card, row, col)
        
        # Select default style
        if "Clásico Centrado" in self._style_cards:
            self._style_cards["Clásico Centrado"].set_selected(True)
        elif self._style_cards:
            # Select first available
            first_key = list(self._style_cards.keys())[0]
            self._style_cards[first_key].set_selected(True)
            self._selected_style = first_key
        
        scroll_layout.addWidget(style_group)
        
        # === Project Information ===
        project_group = QGroupBox("Información del Proyecto")
        project_group.setStyleSheet(self._group_style())
        project_layout = QGridLayout(project_group)
        project_layout.setSpacing(8)
        
        project_layout.addWidget(QLabel("Nombre:"), 0, 0)
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Ej: Sistema de Gestión")
        self.project_name_input.setMinimumHeight(35)
        self._style_input(self.project_name_input)
        self.project_name_input.textChanged.connect(self._schedule_preview_update)
        project_layout.addWidget(self.project_name_input, 0, 1)
        
        project_layout.addWidget(QLabel("Subtítulo:"), 1, 0)
        self.subtitle_input = QLineEdit()
        self.subtitle_input.setPlaceholderText("Ej: Propuesta Comercial 2024")
        self.subtitle_input.setMinimumHeight(35)
        self._style_input(self.subtitle_input)
        self.subtitle_input.textChanged.connect(self._schedule_preview_update)
        project_layout.addWidget(self.subtitle_input, 1, 1)
        
        project_layout.addWidget(QLabel("Descripción:"), 2, 0, Qt.AlignmentFlag.AlignTop)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Breve descripción...")
        self.description_input.setMaximumHeight(60)
        self._style_textedit(self.description_input)
        self.description_input.textChanged.connect(self._schedule_preview_update)
        project_layout.addWidget(self.description_input, 2, 1)
        
        project_layout.addWidget(QLabel("Referencia:"), 3, 0)
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Ej: REF-2024-001")
        self.reference_input.setMinimumHeight(35)
        self._style_input(self.reference_input)
        project_layout.addWidget(self.reference_input, 3, 1)
        
        scroll_layout.addWidget(project_group)
        
        # === Display Options ===
        display_group = QGroupBox("Opciones de Visualización")
        display_group.setStyleSheet(self._group_style())
        display_layout = QGridLayout(display_group)
        display_layout.setSpacing(8)
        
        self.show_logo_check = QCheckBox("Logo")
        self.show_logo_check.setChecked(True)
        self.show_logo_check.stateChanged.connect(self._schedule_preview_update)
        display_layout.addWidget(self.show_logo_check, 0, 0)
        
        self.show_company_check = QCheckBox("Empresa")
        self.show_company_check.setChecked(True)
        self.show_company_check.stateChanged.connect(self._schedule_preview_update)
        display_layout.addWidget(self.show_company_check, 0, 1)
        
        self.show_client_check = QCheckBox("Cliente")
        self.show_client_check.setChecked(True)
        self.show_client_check.stateChanged.connect(self._schedule_preview_update)
        display_layout.addWidget(self.show_client_check, 0, 2)
        
        self.show_date_check = QCheckBox("Fecha")
        self.show_date_check.setChecked(True)
        self.show_date_check.stateChanged.connect(self._schedule_preview_update)
        display_layout.addWidget(self.show_date_check, 1, 0)
        
        self.show_reference_check = QCheckBox("Referencia")
        self.show_reference_check.setChecked(True)
        display_layout.addWidget(self.show_reference_check, 1, 1)
        
        self.show_border_check = QCheckBox("Borde")
        self.show_border_check.setChecked(True)
        self.show_border_check.stateChanged.connect(self._schedule_preview_update)
        display_layout.addWidget(self.show_border_check, 1, 2)
        
        scroll_layout.addWidget(display_group)
        
        # === Style Options ===
        options_group = QGroupBox("Personalización")
        options_group.setStyleSheet(self._group_style())
        options_layout = QGridLayout(options_group)
        options_layout.setSpacing(8)
        
        # Hidden combo to maintain compatibility (synced with grid)
        self.layout_combo = QComboBox()
        self.layout_combo.addItems([s[0] for s in self.STYLES])
        self.layout_combo.hide()  # Hidden, controlled by grid
        
        # Accent color
        options_layout.addWidget(QLabel("Color de Acento:"), 0, 0)
        self.color_btn = QPushButton("Seleccionar")
        self.color_btn.setMinimumHeight(35)
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._accent_color};
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(self._accent_color)};
            }}
        """)
        self.color_btn.clicked.connect(self._select_color)
        options_layout.addWidget(self.color_btn, 0, 1)
        
        # Logo size
        options_layout.addWidget(QLabel("Tamaño Logo:"), 1, 0)
        self.logo_size = QSpinBox()
        self.logo_size.setRange(50, 200)
        self.logo_size.setValue(120)
        self.logo_size.setSuffix(" px")
        self.logo_size.setMinimumHeight(35)
        options_layout.addWidget(self.logo_size, 1, 1)
        
        # Footer text
        options_layout.addWidget(QLabel("Texto Pie:"), 2, 0)
        self.footer_text = QLineEdit()
        self.footer_text.setPlaceholderText("Ej: Confidencial")
        self.footer_text.setMinimumHeight(35)
        self._style_input(self.footer_text)
        options_layout.addWidget(self.footer_text, 2, 1)
        
        scroll_layout.addWidget(options_group)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        left_layout.addWidget(scroll)
        
        # RIGHT SIDE: Preview panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        preview_title = QLabel("Vista Previa")
        preview_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #0A84FF;")
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(preview_title)
        
        # Preview widget
        self.preview_widget = CoverPreviewWidget()
        right_layout.addWidget(self.preview_widget, 1)
        
        # Style description below preview
        self.style_desc = QLabel("")
        self.style_desc.setStyleSheet("""
            QLabel {
                color: rgba(255,255,255,0.6);
                font-size: 11px;
                font-style: italic;
                padding: 8px;
                background-color: rgba(0,0,0,0.2);
                border-radius: 6px;
            }
        """)
        self.style_desc.setWordWrap(True)
        self.style_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.style_desc)
        self._update_style_description("Clásico Centrado")
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 350])
        
        main_layout.addWidget(splitter, 1)
        
        # === Buttons ===
        btn_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumHeight(45)
        btn_cancel.setMinimumWidth(120)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_layout.addStretch()
        
        btn_save = QPushButton("Guardar Carátula")
        btn_save.setMinimumHeight(45)
        btn_save.setMinimumWidth(160)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0A84FF;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0070E0;
            }
        """)
        btn_save.clicked.connect(self._save)
        btn_layout.addWidget(btn_save)
        
        main_layout.addLayout(btn_layout)
    
    def _on_style_selected(self, style_name: str):
        """Handle style card selection."""
        # Deselect all cards
        for name, card in self._style_cards.items():
            card.set_selected(name == style_name)
        
        self._selected_style = style_name
        self.layout_combo.setCurrentText(style_name)
        self._update_style_description(style_name)
        self._update_preview()
    
    def _update_style_description(self, style_name: str):
        """Update the style description text."""
        descriptions = {
            "Clásico Centrado": "Logo centrado, texto alineado al centro, borde decorativo simple. Ideal para propuestas formales.",
            "Moderno Lateral": "Logo en esquina, texto alineado a la izquierda con línea de acento vertical. Aspecto contemporáneo.",
            "Minimalista": "Diseño limpio con mucho espacio en blanco. Solo muestra elementos esenciales.",
            "Corporativo": "Secciones bien definidas con fondos alternados. Profesional y estructurado.",
            "Elegante Degradado": "Fondo con degradado sutil en encabezado y pie. Tipografía premium.",
            "Ejecutivo": "Líneas dobles decorativas, aspecto muy formal. Ideal para propuestas VIP.",
            "Creativo": "Formas geométricas decorativas, diseño dinámico con acentos de color.",
            "Premium": "Borde elegante dorado/plateado, sello de calidad visual."
        }
        self.style_desc.setText(descriptions.get(style_name, ""))
    
    def _schedule_preview_update(self):
        """Schedule a preview update (debounced)."""
        self._preview_timer.start(150)
    
    def _update_preview(self):
        """Update the live preview widget."""
        data = {
            "project_name": self.project_name_input.text(),
            "subtitle": self.subtitle_input.text(),
            "description": self.description_input.toHtml(),
            "show_logo": self.show_logo_check.isChecked(),
            "show_company": self.show_company_check.isChecked(),
            "show_client": self.show_client_check.isChecked(),
            "show_date": self.show_date_check.isChecked(),
            "show_reference": self.show_reference_check.isChecked(),
            "show_border": self.show_border_check.isChecked(),
        }
        self.preview_widget.update_preview(
            data, 
            self._selected_style, 
            self._accent_color,
            self.company_name,
            self.client_name,
            self.project_date
        )
    
    def _group_style(self) -> str:
        """Get group box style."""
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: rgba(0,0,0,0.2);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: rgba(255,255,255,0.8);
            }
        """
    
    def _style_input(self, widget: QLineEdit):
        """Apply style to line edit."""
        widget.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                padding: 8px 12px;
                color: white;
            }
            QLineEdit:focus {
                border-color: #0A84FF;
            }
        """)
    
    def _style_textedit(self, widget: QTextEdit):
        """Apply style to text edit."""
        widget.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                padding: 8px 12px;
                color: white;
            }
            QTextEdit:focus {
                border-color: #0A84FF;
            }
        """)
    
    def _lighten_color(self, hex_color: str) -> str:
        """Lighten a hex color."""
        color = QColor(hex_color)
        h, s, l, a = color.getHslF()
        l = min(1.0, l + 0.1)
        color.setHslF(h, s, l, a)
        return color.name()
    
    def _select_color(self):
        """Open color picker."""
        color = QColorDialog.getColor(QColor(self._accent_color), self)
        if color.isValid():
            self._accent_color = color.name()
            self.color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self._accent_color};
                    border: none;
                    border-radius: 6px;
                    color: white;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self._lighten_color(self._accent_color)};
                }}
            """)
            self._update_preview()
    
    def _update_style_preview(self, style_name: str):
        """Update the style description based on selected style."""
        descriptions = {
            "Minimalista": "Diseño limpio con mucho espacio en blanco. Solo muestra los elementos esenciales con tipografía elegante.",
            "Corporativo": "Secciones bien definidas con fondos alternados. Profesional y estructurado, ideal para empresas tradicionales.",
            "Elegante Degradado": "Fondo con degradado sutil en encabezado y pie. Tipografía premium que transmite sofisticación.",
            "Ejecutivo": "Líneas dobles decorativas, aspecto muy formal y serio. Ideal para propuestas de alto nivel o legales.",
            "Creativo": "Formas geométricas decorativas en las esquinas, diseño dinámico con acentos de color vibrantes.",
            "Premium": "Borde elegante dorado/plateado, inspirado en invitaciones de alta gama. Transmite exclusividad.",
            "Futurista Digital": "Estilo tecnológico con líneas de circuito y fuentes modernas. Ideal para software y tecnología.",
            "Olas Abstractas": "Diseño orgánico con curvas suaves y fluidas. Transmite movimiento y creatividad.",
            "Mosaico Geométrico": "Patrón de polígonos entrelazados con transparencias. Moderno y artístico.",
            "Editorial Moderno": "Enfoque en tipografía grande y layout asimétrico. Estilo revista de diseño."
        }
        self.style_desc.setText(descriptions.get(style_name, ""))
    
    def _load_data(self):
        """Load existing data into the form."""
        if not self.data:
            return
        
        self.project_name_input.setText(self.data.get("project_name", ""))
        self.subtitle_input.setText(self.data.get("subtitle", ""))
        self.description_input.setHtml(self.data.get("description", ""))
        self.reference_input.setText(self.data.get("reference", ""))
        
        self.show_logo_check.setChecked(self.data.get("show_logo", True))
        self.show_company_check.setChecked(self.data.get("show_company", True))
        self.show_client_check.setChecked(self.data.get("show_client", True))
        self.show_date_check.setChecked(self.data.get("show_date", True))
        self.show_reference_check.setChecked(self.data.get("show_reference", True))
        self.show_border_check.setChecked(self.data.get("show_border", True))
        
        # Load layout style and update card selection
        layout_style = self.data.get("layout_style", "Clásico Centrado")
        self._selected_style = layout_style
        layout_idx = self.layout_combo.findText(layout_style)
        if layout_idx >= 0:
            self.layout_combo.setCurrentIndex(layout_idx)
        
        # Update style cards selection
        for name, card in self._style_cards.items():
            card.set_selected(name == layout_style)
        self._update_style_description(layout_style)
        
        if self.data.get("accent_color"):
            self._accent_color = self.data["accent_color"]
            self.color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self._accent_color};
                    border: none;
                    border-radius: 6px;
                    color: white;
                    font-weight: bold;
                }}
            """)
        
        self.logo_size.setValue(self.data.get("logo_size", 120))
        self.footer_text.setText(self.data.get("footer_text", ""))
        
        # Trigger preview update
        self._schedule_preview_update()
    
    def _save(self):
        """Save the cover page data."""
        data = {
            "enabled": True,
            "project_name": self.project_name_input.text(),
            "subtitle": self.subtitle_input.text(),
            "description": self.description_input.toHtml(),
            "reference": self.reference_input.text(),
            "show_logo": self.show_logo_check.isChecked(),
            "show_company": self.show_company_check.isChecked(),
            "show_client": self.show_client_check.isChecked(),
            "show_date": self.show_date_check.isChecked(),
            "show_reference": self.show_reference_check.isChecked(),
            "show_border": self.show_border_check.isChecked(),
            "layout_style": self.layout_combo.currentText(),
            "accent_color": self._accent_color,
            "logo_size": self.logo_size.value(),
            "footer_text": self.footer_text.text()
        }
        
        self.saved.emit(data)
        self.accept()
    
    def get_data(self) -> dict:
        """Get the current cover page data."""
        return {
            "enabled": True,
            "project_name": self.project_name_input.text(),
            "subtitle": self.subtitle_input.text(),
            "description": self.description_input.toHtml(),
            "reference": self.reference_input.text(),
            "show_logo": self.show_logo_check.isChecked(),
            "show_company": self.show_company_check.isChecked(),
            "show_client": self.show_client_check.isChecked(),
            "show_date": self.show_date_check.isChecked(),
            "show_reference": self.show_reference_check.isChecked(),
            "show_border": self.show_border_check.isChecked(),
            "layout_style": self.layout_combo.currentText(),
            "accent_color": self._accent_color,
            "logo_size": self.logo_size.value(),
            "footer_text": self.footer_text.text()
        }
