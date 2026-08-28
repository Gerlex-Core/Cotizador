
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QToolButton, 
    QLabel, QComboBox, QSpinBox, QFontComboBox, QFrame, QButtonGroup,
    QSizePolicy, QColorDialog, QPushButton, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QColor, QAction, QFont, QPixmap
import os

class RibbonGroup(QFrame):
    """A group of buttons within a ribbon tab."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(2)
        
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(4)
        self.layout.addLayout(self.content_layout)
        
        # Divider / Label
        # self.label = QLabel(title)
        # self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.label.setStyleSheet("color: #888888; font-size: 9px;")
        # self.layout.addWidget(self.label)
        
        # Vertical Separator css
        self.setStyleSheet("""
            RibbonGroup {
                border-right: 1px solid #3E3E3E;
            }
        """)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

class RibbonButton(QToolButton):
    """Large or small ribbon button."""
    def __init__(self, text, icon_name=None, large=False, parent=None):
        super().__init__(parent)
        self.setText(text)
        if icon_name:
            # Try to find icon in media/icons
            icon_path = os.path.join(os.getcwd(), "media", "icons", icon_name)
            if os.path.exists(icon_path):
                self.setIcon(QIcon(icon_path))
            else:
                self.setIcon(QIcon.fromTheme("help")) # scaling fallback
        
        if large:
            self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            self.setIconSize(QSize(32, 32))
            self.setFixedSize(60, 60)
            self.setStyleSheet("""
                QToolButton { border: none; border-radius: 4px; padding: 4px; color: #E0E0E0; }
                QToolButton:hover { background-color: #3E3E3E; }
                QToolButton:pressed { background-color: #505050; }
            """)
        else:
            self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            self.setIconSize(QSize(16, 16))
            self.setStyleSheet("""
                QToolButton { border: none; border-radius: 3px; padding: 2px; color: #E0E0E0; }
                QToolButton:hover { background-color: #3E3E3E; }
            """)

class OfficeRibbon(QTabWidget):
    """The main Ribbon interface."""
    
    # Signals
    action_paste = pyqtSignal()
    action_undo = pyqtSignal()
    action_redo = pyqtSignal()
    
    tool_changed = pyqtSignal(str) # "select", "hand"
    
    font_family_changed = pyqtSignal(QFont)
    font_size_changed = pyqtSignal(int)
    text_bold_toggled = pyqtSignal(bool)
    text_italic_toggled = pyqtSignal(bool)
    text_color_changed = pyqtSignal(QColor)
    
    insert_shape = pyqtSignal(str) # "rect", "circle", "line", "text"
    insert_image = pyqtSignal()
    insert_dynamic_text = pyqtSignal(str)  # "company_name", "client_name", "project_date"
    
    theme_changed = pyqtSignal(str)
    accent_color_clicked = pyqtSignal()
    edit_data_requested = pyqtSignal()
    toggle_panel = pyqtSignal(bool)
    save_requested = pyqtSignal()  # Save button signal
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize icon manager
        from src.views.styles.icon_manager import IconManager
        self.icon_manager = IconManager()
        
        self.setFixedHeight(120)
        self.setStyleSheet("""
            QTabWidget::pane { border: none; background-color: #2D2D2D; }
            QTabWidget::tab-bar { left: 10px; }
            QTabBar::tab {
                background: transparent;
                color: #BBBBBB;
                padding: 6px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2D2D2D;
                color: white;
                border-bottom: 2px solid #0A84FF;
            }
            QTabBar::tab:hover { color: white; }
            QWidget { font-family: 'Segoe UI', sans-serif; }
        """)
        
        self.addTab(self._create_home_tab(), "Inicio")
        self.addTab(self._create_insert_tab(), "Insertar")
        self.addTab(self._create_design_tab(), "Diseño")

    def _create_home_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # --- GUARDAR (Archivo) ---
        grp_file = RibbonGroup("Archivo")
        btn_save = RibbonButton("GUARDAR", "save.png", large=True)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0A84FF;
                color: white;
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0066CC;
            }
        """)
        btn_save.clicked.connect(self.save_requested.emit)
        grp_file.add_widget(btn_save)
        layout.addWidget(grp_file)
        
        # --- Clipboard ---
        grp_clip = RibbonGroup("Portapapeles")
        btn_paste = RibbonButton("Pegar", "copyPaste.png", large=True) 
        btn_paste.clicked.connect(self.action_paste.emit)
        grp_clip.add_widget(btn_paste)
        layout.addWidget(grp_clip)
        
        # --- Tools ---
        grp_tools = RibbonGroup("Herramientas")
        self.btn_select = RibbonButton("Selector", "preview.png")
        self.btn_select.setCheckable(True)
        self.btn_select.setChecked(True)
        self.btn_select.clicked.connect(lambda: self._set_tool("select"))
        
        self.btn_hand = RibbonButton("Mano", "highPriority.png") 
        self.btn_hand.setCheckable(True)
        self.btn_hand.clicked.connect(lambda: self._set_tool("hand"))
        
        # Tools layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn_select)
        vbox.addWidget(self.btn_hand)
        grp_tools.content_layout.addLayout(vbox)
        layout.addWidget(grp_tools)

        # --- View ---
        grp_view = RibbonGroup("Ver")
        self.btn_panel = RibbonButton("Panel\nPropiedades", "menu.png", large=True) # Icon placeholder
        self.btn_panel.setCheckable(True)
        self.btn_panel.setChecked(True)
        self.btn_panel.toggled.connect(self.toggle_panel.emit)
        grp_view.add_widget(self.btn_panel)
        layout.addWidget(grp_view)
        
        # --- Text ---
        grp_font = RibbonGroup("Fuente")
        
        # Font Family & Size
        hbox_top = QHBoxLayout()
        self.font_combo = QFontComboBox()
        self.font_combo.setFixedWidth(120)
        self.font_combo.currentFontChanged.connect(self.font_family_changed.emit)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(12)
        self.size_spin.valueChanged.connect(self.font_size_changed.emit)
        
        hbox_top.addWidget(self.font_combo)
        hbox_top.addWidget(self.size_spin)
        
        # Styles
        hbox_bot = QHBoxLayout()
        self.btn_bold = QToolButton()
        self.btn_bold.setText("B")
        self.btn_bold.setToolTip("Negrita (Bold)")
        self.btn_bold.setFont(QFont("Arial", 10, weight=QFont.Weight.Bold))
        self.btn_bold.setCheckable(True)
        self.btn_bold.toggled.connect(self.text_bold_toggled.emit)
        
        self.btn_italic = QToolButton()
        self.btn_italic.setText("I")
        self.btn_italic.setToolTip("Cursiva (Italic)")
        self.btn_italic.setFont(QFont("Arial", 10, italic=True))
        self.btn_italic.setCheckable(True)
        self.btn_italic.toggled.connect(self.text_italic_toggled.emit)
        
        self.btn_color = QToolButton()
        self.btn_color.setText("A")
        self.btn_color.setToolTip("Color de Texto")
        self.btn_color.setStyleSheet("color: red; font-weight: bold;")
        self.btn_color.clicked.connect(self._choose_color)
        
        hbox_bot.addWidget(self.btn_bold)
        hbox_bot.addWidget(self.btn_italic)
        hbox_bot.addWidget(self.btn_color)
        
        # Vertical stack for font group
        vbox_font = QVBoxLayout()
        vbox_font.addLayout(hbox_top)
        vbox_font.addLayout(hbox_bot)
        grp_font.content_layout.addLayout(vbox_font)
        layout.addWidget(grp_font)
        
        # --- Data ---
        grp_data = RibbonGroup("Datos")
        btn_data = RibbonButton("Editar\nDatos", "note.png", large=True)
        btn_data.clicked.connect(self.edit_data_requested.emit)
        grp_data.add_widget(btn_data)
        layout.addWidget(grp_data)
        
        layout.addStretch()
        return widget

    def _create_insert_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # --- ELEMENTOS DINÁMICOS ---
        grp_dynamic = RibbonGroup("Elementos Dinámicos")
        
        btn_company = RibbonButton("Nombre\nEmpresa", "company.png")
        btn_company.setToolTip("Insertar nombre de la empresa")
        btn_company.clicked.connect(lambda: self.insert_dynamic_text.emit("company_name"))
        
        btn_client = RibbonButton("Nombre\nCliente", "client.png")
        btn_client.setToolTip("Insertar nombre del cliente")
        btn_client.clicked.connect(lambda: self.insert_dynamic_text.emit("client_name"))
        
        btn_date = RibbonButton("Fecha", "calendar.png")
        btn_date.setToolTip("Insertar fecha del proyecto")
        btn_date.clicked.connect(lambda: self.insert_dynamic_text.emit("project_date"))
        
        btn_logo = RibbonButton("Logo\nEmpresa", "image.png", large=True)
        btn_logo.setToolTip("Insertar logo de la empresa")
        btn_logo.clicked.connect(lambda: self.insert_image.emit())
        
        grp_dynamic.add_widget(btn_company)
        grp_dynamic.add_widget(btn_client)
        grp_dynamic.add_widget(btn_date)
        grp_dynamic.add_widget(btn_logo)
        layout.addWidget(grp_dynamic)
        
        # --- FORMAS (Consolidated Shapes) ---
        grp_shapes = RibbonGroup("Formas")
        
        # Create dropdown button for shapes
        btn_shapes = QPushButton("Insertar Forma ")
        btn_shapes.setIcon(self.icon_manager.get_icon("formas/rectanguloRedondeado.png", 20))
        btn_shapes.setIconSize(QSize(20, 20))
        btn_shapes.setStyleSheet("""
            QPushButton {
                background-color: #3E3E3E;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                color: white;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover { background-color: #505050; }
            QPushButton::menu-indicator { width: 0px; }
        """)
        btn_shapes.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_shapes.clicked.connect(self._show_shapes_menu)
        
        grp_shapes.add_widget(btn_shapes)
        layout.addWidget(grp_shapes)

        # --- Drawing / Advanced ---
        grp_draw = RibbonGroup("Dibujo")
        
        btn_line = RibbonButton("Línea", "formas/linea.png")
        btn_line.clicked.connect(lambda: self.insert_shape.emit("line"))
        
        btn_star = RibbonButton("Estrella", "star.png")
        btn_star.clicked.connect(lambda: self.insert_shape.emit("star"))

        btn_poly_tool = RibbonButton("Polígono\nLibre", "vectorCurve.png", large=True)
        btn_poly_tool.clicked.connect(lambda: self.insert_shape.emit("polygon"))
        
        grp_draw.add_widget(btn_line)
        grp_draw.add_widget(btn_star)
        grp_draw.add_widget(btn_poly_tool)
        layout.addWidget(grp_draw)
        
        # --- Text ---
        grp_text = RibbonGroup("Texto")
        btn_textbox = RibbonButton("Cuadro de\nTexto", "noteAdd.png", large=True)
        btn_textbox.clicked.connect(lambda: self.insert_shape.emit("text"))
        grp_text.add_widget(btn_textbox)
        layout.addWidget(grp_text)
        
        # --- Media ---
        grp_media = RibbonGroup("Multimedia")
        btn_img = RibbonButton("Imagen", "image.png", large=True)
        btn_img.clicked.connect(self.insert_image.emit)
        grp_media.add_widget(btn_img)
        layout.addWidget(grp_media)
        
        layout.addStretch()
        return widget

    def _create_design_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        grp_theme = RibbonGroup("Temas")
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(200)
        # Populate later
        self.theme_combo.currentTextChanged.connect(self.theme_changed.emit)
        grp_theme.add_widget(QLabel("Tema:"))
        grp_theme.add_widget(self.theme_combo)
        layout.addWidget(grp_theme)
        
        grp_color = RibbonGroup("Color")
        self.btn_accent = RibbonButton("Color de\nAcento", "theme.png", large=True)
        self.btn_accent.clicked.connect(self.accent_color_clicked.emit)
        grp_color.add_widget(self.btn_accent)
        layout.addWidget(grp_color)
        
        layout.addStretch()
        return widget

    def _set_tool(self, tool):
        self.btn_select.setChecked(tool == "select")
        self.btn_hand.setChecked(tool == "hand")
        self.tool_changed.emit(tool)

    def _choose_color(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.text_color_changed.emit(col)
            # Update icon color hint
            self.btn_color.setStyleSheet(f"color: {col.name()}; font-weight: bold;")
    
    def _show_shapes_menu(self):
        """Show organized dropdown menu for all shapes."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
                border-radius: 4px;
                padding: 8px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 32px 8px 24px;
                color: white;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #0A84FF;
            }
            QMenu::icon {
                padding-left: 8px;
            }
        """)
        
        # Define all shapes with their metadata
        shapes = [
            ("rect", "Rectángulo", "box.png"),
            ("rounded_rect", "Rectángulo Redondeado", "formas/rectanguloRedondeado.png"),
            ("circle", "Círculo", "formas/circuloSilueta.png"),
            ("triangle", "Triángulo", "formas/trianguloSilueta.png"),
            ("pentagon", "Pentágono", "formas/pentagono.png"),
            ("hexagon", "Hexágono", "formas/hexagonoSilueta.png"),
            ("octagon", "Octágono", "formas/ocyagono.png"),
            ("line", "Línea", "formas/linea.png"),
            ("star", "Estrella", "star.png"),
        ]
        
        for shape_id, shape_name, icon_path in shapes:
            action = menu.addAction(self.icon_manager.get_icon(icon_path, 18), shape_name)
            action.triggered.connect(lambda checked, s=shape_id: self.insert_shape.emit(s))
        
        # Show menu below button
        button = self.sender()
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
