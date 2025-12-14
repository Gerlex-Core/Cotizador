"""
Main Window - Primary interface for the Cotizador application.
Redesigned with tabs for better organization.
"""

import os
import json
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QTableWidgetItem, QGroupBox,
    QSpinBox, QDoubleSpinBox, QFrame, QTabWidget, QScrollArea,
    QSizePolicy, QCheckBox, QApplication
)
from PyQt6.QtGui import QAction, QFont, QIcon, QKeySequence
from PyQt6.QtCore import Qt, QSize

from .components.buttons.animated_button import AnimatedButton, PrimaryButton, DangerButton
from .components.tables.animated_table import QuotationTable
from .components.panels.glass_panel import GlassPanel
from .components.canvas.drop_canvas import DropCanvas
from .terms_window import TermsWindow
from .products_window import ProductsWindow
from .history_window import HistoryWindow
from .components.notification.toast_notification import ToastNotification
from .components.editor.rich_text_editor import RichTextEditor
from .styles.theme_manager import ThemeManager
from .styles.icon_manager import IconManager

from ..logic.config.config_manager import get_config
from ..logic.company.company_logic import get_company_logic
from ..logic.json.unit_converter import get_unit_converter
from ..logic.file.cotz_manager import get_cotz_manager
from ..logic.history.history_manager import HistoryManager
from ..export.pdf_generator import generar_pdf

# Path to payments JSON
PAGOS_FILE = os.path.join("media", "data", "pay", "pagos.json")


def _load_pagos_config():
    """Load payment options from JSON file."""
    default = {
        "tipos_pago": ["Efectivo", "Tarjeta", "Transferencia", "Otro"],
        "formas_pago": ["50% anticipo, 50% contra entrega", "100% anticipo", "Crédito 30 días"]
    }
    if os.path.exists(PAGOS_FILE):
        try:
            with open(PAGOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return default


class MainWindow(QMainWindow):
    """
    Main window for the Cotizador Pro application.
    Uses tabs for better organization of content.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.config = get_config()
        self.company_logic = get_company_logic()
        self.unit_converter = get_unit_converter()
        self.cotz_manager = get_cotz_manager()
        
        # Observations data storage
        self._observations_data = {}
        # Cover page data storage
        self._cover_page_data = {}
        # Enhanced terms data storage
        self._terms_data = {}
        # Products data storage (now managed via ProductsWindow)
        self._products_data = {}
        self.icon_manager = IconManager.get_instance()
        
        # Setup paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.icons_dir = os.path.join(self.base_dir, "media", "icons")
        
        # Initialize History Manager
        self.history_manager = HistoryManager()
        
        # Window setup
        self.setWindowTitle("Cotizador Pro - Sin Título")
        self.setGeometry(50, 50, 1200, 800)
        self.setMinimumSize(1000, 650)
        
        # Set app icon
        self.setWindowIcon(QIcon(os.path.join(self.icons_dir, "pdf.png")))
        
        # Apply theme
        ThemeManager.apply_theme(self, self.config.tema)
        font_size = max(8, self.config.tamaño_fuente) # Ensure valid font size
        self.setFont(QFont(self.config.fuente, font_size))
        
        # Update Icon Manager Color based on theme
        icon_color = "#1D1D1F" if "Claro" in self.config.tema else "#FFFFFF"
        self.icon_manager.set_theme_color(icon_color)
        
        # Create UI
        self._create_menu()
        self._create_ui()
        
        # Load companies
        self._load_companies()
        
        # Generate initial quotation number
        self._generate_quotation_number()
    
    def _get_icon(self, name: str, size: int = 20) -> QIcon:
        """Helper to get dynamic icon."""
        return self.icon_manager.get_icon(name, size)
    
    def _create_icon_label(self, icon_name: str, text: str, icon_size: int = 18) -> QWidget:
        """Create a widget with icon and text label for section headers."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(self.icon_manager.get_pixmap(icon_name, icon_size))
        layout.addWidget(icon_label)
        
        # Text
        text_label = QLabel(text)
        text_label.setStyleSheet(f"font-size: {icon_size}px; font-weight: bold;")
        layout.addWidget(text_label)
        
        layout.addStretch()
        return widget
    
    def _on_shipping_toggled(self, state):
        """Enable/disable shipping inputs based on checkbox."""
        enabled = state == Qt.CheckState.Checked.value
        self.shipping_input.setEnabled(enabled)
        self.shipping_type_combo.setEnabled(enabled)
        self._calculate_total()
    
    def _create_menu(self):
        """Create the menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        menu_file = menu_bar.addMenu("Archivo")
        
        action_new = QAction(self._get_icon("add"), "Nuevo", self)
        action_new.setShortcut(QKeySequence("Ctrl+N"))
        action_new.triggered.connect(self._new_quotation)
        menu_file.addAction(action_new)
        
        action_open = QAction(self._get_icon("openFolder"), "Abrir...", self)
        action_open.setShortcut(QKeySequence("Ctrl+O"))
        action_open.triggered.connect(self._open_quotation)
        menu_file.addAction(action_open)
        
        action_save = QAction(self._get_icon("save"), "Guardar", self)
        action_save.setShortcut(QKeySequence("Ctrl+S"))
        action_save.triggered.connect(self._save_file)
        menu_file.addAction(action_save)
        
        menu_file.addSeparator()
        
        action_export = QAction(self._get_icon("pdf"), "Exportar PDF...", self)
        action_export.setShortcut(QKeySequence("Ctrl+P"))
        action_export.triggered.connect(self._export_pdf)
        menu_file.addAction(action_export)
        
        menu_file.addSeparator()
        
        action_save_as = QAction(self.icon_manager.get_icon("saveAs", 16), "Guardar Como...", self)
        action_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        action_save_as.triggered.connect(self._save_file_as)
        menu_file.addAction(action_save_as)
        
        # Recent Files Submenu
        self.menu_recent = menu_file.addMenu(self.icon_manager.get_icon("time", 16), "Recientes")
        self.menu_recent.aboutToShow.connect(self._update_recent_menu)
        
        action_history = QAction(self.icon_manager.get_icon("history", 16), "Historial de Archivos", self)
        action_history.setShortcut(QKeySequence("Ctrl+H"))
        action_history.triggered.connect(self._open_history_window)
        menu_file.addAction(action_history)
        
        # Options menu
        menu_options = menu_bar.addMenu("Opciones")
        
        action_config = QAction(self._get_icon("settings"), "Configuración", self)
        action_config.triggered.connect(self._open_config)
        menu_options.addAction(action_config)
        
        # Company menu
        menu_company = menu_bar.addMenu("Empresa")
        
        action_company = QAction(self._get_icon("company"), "Gestionar Empresas", self)
        action_company.triggered.connect(self._open_company_manager)
        menu_company.addAction(action_company)
    
    def _create_ui(self):
        """Create the main UI with tabs."""
        from .company_view import CompanyManagerView
        from .config_view import ConfigManagerView
        self._CompanyManagerView = CompanyManagerView
        self._ConfigManagerView = ConfigManagerView
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # === HEADER: Basic Info (Compact) ===
        header_widget = QWidget()
        header_layout = QGridLayout(header_widget)
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        # Row 0: Title, Document Type and Number
        title = QLabel("Cotizador Pro")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title, 0, 0)
        
        # Document type selector
        header_layout.addWidget(QLabel("Tipo:"), 0, 1)
        self.document_type_combo = QComboBox()
        self.document_type_combo.addItems(["Cotizacion", "Recibo"])
        self.document_type_combo.setMinimumHeight(35)
        self.document_type_combo.setMinimumWidth(120)
        self.document_type_combo.currentTextChanged.connect(self._on_document_type_changed)
        header_layout.addWidget(self.document_type_combo, 0, 2)
        
        header_layout.addWidget(QLabel("Numero:"), 0, 4)
        self.quotation_number_input = QLineEdit()
        self.quotation_number_input.setMaximumWidth(160)
        self.quotation_number_input.setMinimumHeight(35)
        header_layout.addWidget(self.quotation_number_input, 0, 5)
        
        # Row 1: Company, Date, Validity
        header_layout.addWidget(QLabel("Empresa:"), 1, 0)
        self.company_combo = QComboBox()
        self.company_combo.setMinimumHeight(35)
        self.company_combo.setMinimumWidth(200)
        self.company_combo.currentTextChanged.connect(self._on_company_changed)
        header_layout.addWidget(self.company_combo, 1, 1)
        
        header_layout.addWidget(QLabel("Fecha:"), 1, 2)
        self.date_input = QLineEdit(datetime.today().strftime("%d/%m/%Y"))
        self.date_input.setMaximumWidth(100)
        self.date_input.setMinimumHeight(35)
        header_layout.addWidget(self.date_input, 1, 3)
        
        header_layout.addWidget(QLabel("Validez:"), 1, 4)
        self.validez_input = QSpinBox()
        self.validez_input.setRange(1, 365)
        self.validez_input.setValue(15)
        self.validez_input.setSuffix(" días")
        self.validez_input.setMinimumHeight(35)
        self.validez_input.setMaximumWidth(100)
        self.validez_input.valueChanged.connect(self._on_header_validez_changed)
        header_layout.addWidget(self.validez_input, 1, 5)
        
        # Row 2: Client Info (compact)
        header_layout.addWidget(QLabel("Cliente:"), 2, 0)
        self.client_name_input = QLineEdit()
        self.client_name_input.setPlaceholderText("Nombre del cliente")
        self.client_name_input.setMinimumHeight(35)
        header_layout.addWidget(self.client_name_input, 2, 1)
        
        header_layout.addWidget(QLabel("Contacto:"), 2, 2)
        self.client_contact_input = QLineEdit()
        self.client_contact_input.setPlaceholderText("Teléfono/Email")
        self.client_contact_input.setMinimumHeight(35)
        header_layout.addWidget(self.client_contact_input, 2, 3)
        
        header_layout.addWidget(QLabel("Dirección:"), 2, 4)
        self.client_address_input = QLineEdit()
        self.client_address_input.setPlaceholderText("Dirección")
        self.client_address_input.setMinimumHeight(35)
        header_layout.addWidget(self.client_address_input, 2, 5)
        
        # Company info label
        self.company_info_label = QLabel("")
        self.company_info_label.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px;")
        header_layout.addWidget(self.company_info_label, 3, 0, 1, 6)
        
        main_layout.addWidget(header_widget)
        
        # === TAB WIDGET ===
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                background-color: rgba(0,0,0,0.2);
            }
            QTabBar::tab {
                background-color: rgba(255,255,255,0.05);
                color: white;
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: rgba(10, 132, 255, 0.4);
                border-bottom: 2px solid #0A84FF;
            }
            QTabBar::tab:hover {
                background-color: rgba(255,255,255,0.1);
            }
        """)
        
        # TAB 1: Details (with Products card)
        self._create_details_tab()
        
        # TAB 2: Finance
        self._create_finance_tab()
        
        main_layout.addWidget(self.tabs, 1)
        
        # === FOOTER: Actions ===
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 8, 0, 0)
        
        # Total display
        self.total_display = QLabel("Total: 0.00")
        self.total_display.setStyleSheet("font-size: 18px; font-weight: bold; color: #0A84FF;")
        footer_layout.addWidget(self.total_display)
        
        footer_layout.addStretch()
        
        btn_save = AnimatedButton("Guardar")
        btn_save.setIcon(self.icon_manager.get_icon("save", 20))
        btn_save.setMinimumWidth(140)
        btn_save.setMinimumHeight(40)
        btn_save.clicked.connect(self._save_file)
        footer_layout.addWidget(btn_save)
        
        btn_export = PrimaryButton("Generar PDF")
        btn_export.setIcon(self.icon_manager.get_icon("pdf", 20))
        btn_export.setMinimumWidth(160)
        btn_export.setMinimumHeight(40)
        btn_export.clicked.connect(self._export_pdf)
        footer_layout.addWidget(btn_export)
        
        main_layout.addWidget(footer)
    
    def _create_products_tab(self):
        """Create the products tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        products_label = self._create_icon_label("box", "Lista de Productos", 18)
        toolbar.addWidget(products_label)
        toolbar.addStretch()
        
        btn_add = AnimatedButton("Agregar")
        btn_add.setIcon(self.icon_manager.get_icon("addItem", 18))
        btn_add.clicked.connect(lambda: self._add_product())
        toolbar.addWidget(btn_add)
        
        btn_dup = AnimatedButton("Duplicar")
        btn_dup.setIcon(self.icon_manager.get_icon("copy", 18))
        btn_dup.clicked.connect(self._duplicate_product)
        toolbar.addWidget(btn_dup)
        
        btn_del = DangerButton("Eliminar")
        btn_del.setIcon(self.icon_manager.get_icon("deleteTrash", 18))
        btn_del.clicked.connect(self._remove_product)
        toolbar.addWidget(btn_del)
        
        btn_clear = AnimatedButton("Limpiar")
        btn_clear.setIcon(self.icon_manager.get_icon("clear", 18))
        btn_clear.clicked.connect(self._clear_table)
        toolbar.addWidget(btn_clear)
        
        layout.addLayout(toolbar)
        
        # Table
        self.table = QuotationTable()
        self.table.itemChanged.connect(self._calculate_amount)
        layout.addWidget(self.table, 1)  # Give table stretch priority
        
        # === Shipping Section (Visible in Quote) ===
        shipping_frame = QFrame()
        shipping_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 132, 255, 0.1);
                border: 1px solid rgba(10, 132, 255, 0.3);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        shipping_layout = QHBoxLayout(shipping_frame)
        shipping_layout.setSpacing(12)
        
        # Shipping icon and checkbox
        shipping_icon = QLabel()
        shipping_icon.setPixmap(self.icon_manager.get_pixmap("delivery", 24))
        shipping_layout.addWidget(shipping_icon)
        
        self.enable_shipping_check = QCheckBox("Envío")
        self.enable_shipping_check.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.enable_shipping_check.stateChanged.connect(self._on_shipping_toggled)
        shipping_layout.addWidget(self.enable_shipping_check)
        
        # Shipping amount (no prefix - just the number)
        self.shipping_input = QDoubleSpinBox()
        self.shipping_input.setRange(0, 99999)
        self.shipping_input.setDecimals(2)
        self.shipping_input.setValue(0)
        self.shipping_input.setMinimumHeight(35)
        self.shipping_input.setMinimumWidth(120)
        self.shipping_input.setEnabled(False)
        self.shipping_input.valueChanged.connect(self._calculate_total)
        shipping_layout.addWidget(self.shipping_input)
        
        # Shipping type
        self.shipping_type_combo = QComboBox()
        self.shipping_type_combo.addItems([
            "Envío Local",
            "Delivery",
            "Encomienda",
            "Express/Urgente",
            "Pickup (Retiro)",
            "Courier Nacional",
            "Courier Internacional",
            "Flete",
            "Transporte Especializado"
        ])
        self.shipping_type_combo.setMinimumHeight(35)
        self.shipping_type_combo.setEnabled(False)
        shipping_layout.addWidget(self.shipping_type_combo)
        
        # Shipping display
        self.shipping_display = QLabel("+ 0.00")
        self.shipping_display.setStyleSheet("color: #0A84FF; font-weight: bold; font-size: 14px;")
        shipping_layout.addWidget(self.shipping_display)
        
        shipping_layout.addStretch()
        
        layout.addWidget(shipping_frame)
        
        # Add tab with icon
        self.tabs.addTab(tab, self.icon_manager.get_icon("box", 20), "Productos")
    
        # Connect table signals
        if hasattr(self, 'table') and isinstance(self.table, QuotationTable):
            self.table.resolution_warning.connect(self._show_toast_warning)

        # Initialize Toast
        self.toast = ToastNotification(self)

    def _show_toast_warning(self, title, message):
        """Show warning toast from table."""
        self.toast.show_toast(title, message, self, duration=6000, type="warning")

    def _create_details_tab(self):
        """Create the details/observations tab with cover page option."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Unified card style
        card_style = """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 30, 35, 0.95), stop:1 rgba(25, 25, 30, 0.9));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """
        
        # === 1. COVER PAGE ===
        cover_frame = QFrame()
        cover_frame.setStyleSheet(card_style)
        cover_layout = QVBoxLayout(cover_frame)
        cover_layout.setContentsMargins(20, 16, 20, 16)
        cover_layout.setSpacing(12)
        
        cover_header = QHBoxLayout()
        cover_header.setSpacing(12)
        cover_icon = QLabel()
        cover_icon.setFixedSize(44, 44)
        cover_icon.setStyleSheet("background: rgba(10, 132, 255, 0.3); border: 2px solid #0A84FF; border-radius: 12px;")
        cover_icon.setPixmap(self.icon_manager.get_pixmap("pdf", 24))
        cover_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover_header.addWidget(cover_icon)
        
        cover_text = QVBoxLayout()
        cover_text.setSpacing(2)
        cover_title = QLabel("Carátula del Documento")
        cover_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        cover_text.addWidget(cover_title)
        cover_desc = QLabel("Portada profesional para tu cotización")
        cover_desc.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.5);")
        cover_text.addWidget(cover_desc)
        cover_header.addLayout(cover_text)
        cover_header.addStretch()
        
        self.cover_page_check = QCheckBox("Incluir")
        self.cover_page_check.setStyleSheet("QCheckBox { font-size: 13px; color: #0A84FF; font-weight: bold; } QCheckBox::indicator { width: 20px; height: 20px; border-radius: 4px; border: 2px solid #0A84FF; } QCheckBox::indicator:checked { background: #0A84FF; }")
        cover_header.addWidget(self.cover_page_check)
        cover_layout.addLayout(cover_header)
        
        self.edit_cover_btn = QPushButton("  Editar Carátula")
        self.edit_cover_btn.setIcon(self.icon_manager.get_icon("noteAdd", 18))
        self.edit_cover_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_cover_btn.setStyleSheet("QPushButton { background: rgba(10, 132, 255, 0.4); border: 1px solid #0A84FF; border-radius: 10px; color: white; padding: 12px 24px; font-weight: bold; font-size: 13px; } QPushButton:hover { background: rgba(10, 132, 255, 0.6); }")
        self.edit_cover_btn.clicked.connect(self._open_cover_page_editor)
        cover_layout.addWidget(self.edit_cover_btn)
        content_layout.addWidget(cover_frame)
        
        # === 1.5 PRODUCTS ===
        products_frame = QFrame()
        products_frame.setStyleSheet(card_style)
        products_layout = QVBoxLayout(products_frame)
        products_layout.setContentsMargins(20, 16, 20, 16)
        products_layout.setSpacing(12)
        
        products_header = QHBoxLayout()
        products_header.setSpacing(12)
        products_icon = QLabel()
        products_icon.setFixedSize(44, 44)
        products_icon.setStyleSheet("background: rgba(94, 92, 230, 0.3); border: 2px solid #5E5CE6; border-radius: 12px;")
        products_icon.setPixmap(self.icon_manager.get_pixmap("box", 24))
        products_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        products_header.addWidget(products_icon)
        
        products_text = QVBoxLayout()
        products_text.setSpacing(2)
        products_title = QLabel("Producto")
        products_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        products_text.addWidget(products_title)
        products_desc = QLabel("Elige los productos de la cotización + envío si aplica")
        products_desc.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.5);")
        products_text.addWidget(products_desc)
        products_header.addLayout(products_text)
        products_header.addStretch()
        
        self.include_products_check = QCheckBox("Incluir")
        self.include_products_check.setChecked(True)
        self.include_products_check.setStyleSheet("QCheckBox { font-size: 13px; color: #5E5CE6; font-weight: bold; } QCheckBox::indicator { width: 20px; height: 20px; border-radius: 4px; border: 2px solid #5E5CE6; } QCheckBox::indicator:checked { background: #5E5CE6; }")
        products_header.addWidget(self.include_products_check)
        products_layout.addLayout(products_header)
        
        # Products summary
        self.products_summary = QLabel("Sin productos agregados")
        self.products_summary.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.6); padding: 8px 0;")
        self.products_summary.setWordWrap(True)
        products_layout.addWidget(self.products_summary)
        
        btn_products = QPushButton("  Gestionar Productos y Envío")
        btn_products.setIcon(self.icon_manager.get_icon("box", 18))
        btn_products.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_products.setStyleSheet("QPushButton { background: rgba(94, 92, 230, 0.4); border: 1px solid #5E5CE6; border-radius: 10px; color: white; padding: 12px 24px; font-weight: bold; font-size: 13px; } QPushButton:hover { background: rgba(94, 92, 230, 0.6); }")
        btn_products.clicked.connect(self._open_products_window)
        products_layout.addWidget(btn_products)
        content_layout.addWidget(products_frame)
        
        # === 2. OBSERVATIONS ===
        obs_frame = QFrame()
        obs_frame.setStyleSheet(card_style)
        obs_layout = QVBoxLayout(obs_frame)
        obs_layout.setContentsMargins(20, 16, 20, 16)
        obs_layout.setSpacing(12)
        
        obs_header = QHBoxLayout()
        obs_header.setSpacing(12)
        obs_icon = QLabel()
        obs_icon.setFixedSize(44, 44)
        obs_icon.setStyleSheet("background: rgba(52, 199, 89, 0.3); border: 2px solid #34C759; border-radius: 12px;")
        obs_icon.setPixmap(self.icon_manager.get_pixmap("termsAndCondition", 24))
        obs_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        obs_header.addWidget(obs_icon)
        
        obs_text = QVBoxLayout()
        obs_text.setSpacing(2)
        obs_title = QLabel("Observaciones y Notas")
        obs_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        obs_text.addWidget(obs_title)
        self.observations_summary = QLabel("Sin observaciones añadidas")
        self.observations_summary.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.5);")
        self.observations_summary.setWordWrap(True)
        obs_text.addWidget(self.observations_summary)
        obs_header.addLayout(obs_text)
        obs_header.addStretch()
        
        self.include_details_check = QCheckBox("Incluir")
        self.include_details_check.setChecked(False)
        self.include_details_check.setStyleSheet("QCheckBox { font-size: 13px; color: #34C759; font-weight: bold; } QCheckBox::indicator { width: 20px; height: 20px; border-radius: 4px; border: 2px solid #34C759; } QCheckBox::indicator:checked { background: #34C759; }")
        obs_header.addWidget(self.include_details_check)
        obs_layout.addLayout(obs_header)
        
        btn_open = QPushButton("  Abrir Ventana de Observaciones")
        btn_open.setIcon(self.icon_manager.get_icon("noteAdd", 18))
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.setStyleSheet("QPushButton { background: rgba(52, 199, 89, 0.4); border: 1px solid #34C759; border-radius: 10px; color: white; padding: 12px 24px; font-weight: bold; font-size: 13px; } QPushButton:hover { background: rgba(52, 199, 89, 0.6); }")
        btn_open.clicked.connect(self._open_observations_window)
        obs_layout.addWidget(btn_open)
        content_layout.addWidget(obs_frame)
        
        # === 3. TERMS & CONDITIONS ===
        terms_frame = QFrame()
        terms_frame.setStyleSheet(card_style)
        terms_layout = QVBoxLayout(terms_frame)
        terms_layout.setContentsMargins(20, 16, 20, 16)
        terms_layout.setSpacing(12)
        
        terms_header = QHBoxLayout()
        terms_header.setSpacing(12)
        terms_icon = QLabel()
        terms_icon.setFixedSize(44, 44)
        terms_icon.setStyleSheet("background: rgba(255, 149, 0, 0.3); border: 2px solid #FF9500; border-radius: 12px;")
        terms_icon.setPixmap(self.icon_manager.get_pixmap("maintenance", 24))
        terms_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        terms_header.addWidget(terms_icon)
        
        terms_text = QVBoxLayout()
        terms_text.setSpacing(2)
        terms_title = QLabel("Términos, Condiciones y Garantía")
        terms_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        terms_text.addWidget(terms_title)
        terms_desc = QLabel("Validez, entrega, garantía y formas de pago")
        terms_desc.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.5);")
        terms_text.addWidget(terms_desc)
        terms_header.addLayout(terms_text)
        terms_header.addStretch()
        terms_layout.addLayout(terms_header)
        
        btn_terms = QPushButton("  Gestionar Términos y Condiciones")
        btn_terms.setIcon(self.icon_manager.get_icon("termsAndCondition", 18))
        btn_terms.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_terms.setStyleSheet("QPushButton { background: rgba(255, 149, 0, 0.4); border: 1px solid #FF9500; border-radius: 10px; color: white; padding: 12px 24px; font-weight: bold; font-size: 13px; } QPushButton:hover { background: rgba(255, 149, 0, 0.6); }")
        btn_terms.clicked.connect(self._open_terms_window)
        terms_layout.addWidget(btn_terms)
        
        # Validez row - syncs with _terms_data
        validez_row = QHBoxLayout()
        validez_lbl = QLabel("Validez de oferta:")
        validez_lbl.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.7);")
        validez_row.addWidget(validez_lbl)
        self.validez_dias_spin = QSpinBox()
        self.validez_dias_spin.setRange(1, 365)
        self.validez_dias_spin.setValue(self._terms_data.get('validez_dias', 15))
        self.validez_dias_spin.setSuffix(" días")
        self.validez_dias_spin.setStyleSheet("QSpinBox { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; padding: 6px 12px; color: white; min-width: 100px; }")
        self.validez_dias_spin.valueChanged.connect(self._on_validez_changed)
        validez_row.addWidget(self.validez_dias_spin)
        validez_row.addStretch()
        terms_layout.addLayout(validez_row)
        content_layout.addWidget(terms_frame)
        
        # === 4. SIGNATURE ===
        sig_frame = QFrame()
        sig_frame.setStyleSheet(card_style)
        sig_layout = QVBoxLayout(sig_frame)
        sig_layout.setContentsMargins(20, 16, 20, 16)
        sig_layout.setSpacing(12)
        
        sig_header = QHBoxLayout()
        sig_header.setSpacing(12)
        sig_icon = QLabel()
        sig_icon.setFixedSize(44, 44)
        sig_icon.setStyleSheet("background: rgba(175, 82, 222, 0.3); border: 2px solid #AF52DE; border-radius: 12px;")
        sig_icon.setPixmap(self.icon_manager.get_pixmap("user", 24))
        sig_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sig_header.addWidget(sig_icon)
        
        sig_text = QVBoxLayout()
        sig_text.setSpacing(2)
        sig_title = QLabel("Firma del Documento")
        sig_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        sig_text.addWidget(sig_title)
        sig_desc = QLabel("Incluye tu firma profesional en la cotización")
        sig_desc.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.5);")
        sig_text.addWidget(sig_desc)
        sig_header.addLayout(sig_text)
        sig_header.addStretch()
        
        self.include_signature_check = QCheckBox("Incluir Firma")
        self.include_signature_check.setStyleSheet("QCheckBox { font-size: 13px; color: #AF52DE; font-weight: bold; } QCheckBox::indicator { width: 20px; height: 20px; border-radius: 4px; border: 2px solid #AF52DE; } QCheckBox::indicator:checked { background: #AF52DE; }")
        self.include_signature_check.setChecked(False)
        sig_header.addWidget(self.include_signature_check)
        sig_layout.addLayout(sig_header)
        content_layout.addWidget(sig_frame)
        
        # Hidden fields
        self.installation_terms = QTextEdit()
        self.installation_terms.hide()
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.canvas = DropCanvas()
        self.canvas.hide()
        
        # Hidden table for backward compatibility (products now managed via ProductsWindow)
        self.table = QuotationTable()
        self.table.hide()
        
        # Toast for warnings
        self.toast = ToastNotification(self)
        
        self.tabs.addTab(tab, self.icon_manager.get_icon("note", 20), "Detalles")
    
    def _create_finance_tab(self):
        """Create the finance tab - Simplified."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create scroll area for finance content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        content_layout = QGridLayout(content)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        row = 0
        
        # === Calculations Section ===
        calc_header = QHBoxLayout()
        calc_icon = QLabel()
        calc_icon.setPixmap(self.icon_manager.get_pixmap("money", 22))
        calc_header.addWidget(calc_icon)
        calc_title = QLabel("Cálculos y Totales")
        calc_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        calc_header.addWidget(calc_title)
        calc_header.addStretch()
        calc_widget = QWidget()
        calc_widget.setLayout(calc_header)
        content_layout.addWidget(calc_widget, row, 0, 1, 4)
        row += 1
        
        # Subtotal
        content_layout.addWidget(QLabel("Subtotal:"), row, 0)
        self.subtotal_label = QLabel("0.00")
        self.subtotal_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        content_layout.addWidget(self.subtotal_label, row, 1)
        row += 1
        
        # Discount with checkbox
        self.apply_discount_check = QCheckBox("Aplicar Descuento:")
        self.apply_discount_check.setChecked(False)
        self.apply_discount_check.stateChanged.connect(self._calculate_total)
        content_layout.addWidget(self.apply_discount_check, row, 0)
        
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setValue(0)
        self.discount_input.setSuffix(" %")
        self.discount_input.setMinimumHeight(35)
        self.discount_input.setMaximumWidth(120)
        self.discount_input.valueChanged.connect(self._calculate_total)
        content_layout.addWidget(self.discount_input, row, 1)
        
        self.discount_amount_label = QLabel("- 0.00")
        self.discount_amount_label.setStyleSheet("color: #FF453A;")
        content_layout.addWidget(self.discount_amount_label, row, 2)
        row += 1
        
        # IVA with checkbox
        self.apply_iva_check = QCheckBox("Aplicar IVA:")
        self.apply_iva_check.setChecked(True)
        self.apply_iva_check.stateChanged.connect(self._calculate_total)
        content_layout.addWidget(self.apply_iva_check, row, 0)
        
        self.iva_input = QDoubleSpinBox()
        self.iva_input.setRange(0, 50)
        self.iva_input.setValue(13)
        self.iva_input.setSuffix(" %")
        self.iva_input.setMinimumHeight(35)
        self.iva_input.setMaximumWidth(120)
        self.iva_input.valueChanged.connect(self._calculate_total)
        content_layout.addWidget(self.iva_input, row, 1)
        
        self.iva_amount_label = QLabel("+ 0.00")
        self.iva_amount_label.setStyleSheet("color: #34C759;")
        content_layout.addWidget(self.iva_amount_label, row, 2)
        row += 1
        
        # Shipping Reference
        shipping_ref = QLabel("Envío:")
        content_layout.addWidget(shipping_ref, row, 0)
        self.shipping_label = QLabel("Ver en tab Productos")
        self.shipping_label.setStyleSheet("color: #0A84FF; font-style: italic;")
        content_layout.addWidget(self.shipping_label, row, 1, 1, 2)
        row += 1
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(255,255,255,0.2);")
        content_layout.addWidget(sep, row, 0, 1, 4)
        row += 1
        
        # Total
        total_label = QLabel("TOTAL:")
        total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        content_layout.addWidget(total_label, row, 0)
        
        self.total_label = QLabel(f"0.00 {self.config.moneda}")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #0A84FF;")
        content_layout.addWidget(self.total_label, row, 1, 1, 3)
        row += 1
        
        # === Bank Details Section ===
        sep4 = QFrame()
        sep4.setFrameShape(QFrame.Shape.HLine)
        sep4.setStyleSheet("background-color: rgba(255,255,255,0.1);")
        content_layout.addWidget(sep4, row, 0, 1, 4)
        row += 1
        
        bank_header = QHBoxLayout()
        bank_icon_lbl = QLabel()
        bank_icon_lbl.setPixmap(self.icon_manager.get_pixmap("bank", 20))
        bank_header.addWidget(bank_icon_lbl)
        bank_title = QLabel("Datos Bancarios")
        bank_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        bank_header.addWidget(bank_title)
        bank_header.addStretch()
        
        # Checkbox to include bank details in PDF
        self.include_bank_details_check = QCheckBox("Incluir en PDF")
        self.include_bank_details_check.setChecked(False)
        self.include_bank_details_check.setStyleSheet("font-size: 12px; color: #34C759;")
        bank_header.addWidget(self.include_bank_details_check)
        
        bank_widget = QWidget()
        bank_widget.setLayout(bank_header)
        content_layout.addWidget(bank_widget, row, 0, 1, 4)
        row += 1
        
        content_layout.addWidget(QLabel("Banco/Cuenta:"), row, 0, Qt.AlignmentFlag.AlignTop)
        self.bank_details = QTextEdit()
        self.bank_details.setPlaceholderText(
            "Información bancaria para pagos:\n"
            "Banco: \n"
            "Cuenta: \n"
            "Titular: \n"
            "CLABE/IBAN: "
        )
        self.bank_details.setMaximumHeight(80)
        self.bank_details.setMinimumHeight(60)
        content_layout.addWidget(self.bank_details, row, 1, 1, 3)
        row += 1
        
        # === Internal Notes Section ===
        sep5 = QFrame()
        sep5.setFrameShape(QFrame.Shape.HLine)
        sep5.setStyleSheet("background-color: rgba(255,255,255,0.1);")
        content_layout.addWidget(sep5, row, 0, 1, 4)
        row += 1
        
        internal_header = QHBoxLayout()
        internal_icon = QLabel()
        internal_icon.setPixmap(self.icon_manager.get_pixmap("highPriority", 18))
        internal_header.addWidget(internal_icon)
        internal_title = QLabel("Notas Internas")
        internal_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FF9500;")
        internal_header.addWidget(internal_title)
        internal_header.addStretch()
        internal_widget = QWidget()
        internal_widget.setLayout(internal_header)
        content_layout.addWidget(internal_widget, row, 0, 1, 4)
        row += 1
        
        self.internal_notes = QTextEdit()
        self.internal_notes.setPlaceholderText(
            "Notas internas para uso del vendedor (no aparecen en la cotización)..."
        )
        self.internal_notes.setMaximumHeight(60)
        content_layout.addWidget(self.internal_notes, row, 0, 1, 4)
        row += 1
        
        # Reference/PO Number (Moved here from Finance)
        content_layout.addWidget(QLabel("Referencia/PO:"), row, 0)
        self.reference_number = QLineEdit()
        self.reference_number.setPlaceholderText("Número de referencia o PO del cliente")
        self.reference_number.setMinimumHeight(35)
        content_layout.addWidget(self.reference_number, row, 1, 1, 3)
        row += 1
        
        # Stretch at end
        content_layout.setRowStretch(row, 1)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, self.icon_manager.get_icon("money", 20), "Finanzas")
    
    def _generate_quotation_number(self):
        """Generate automatic quotation/receipt number based on document type."""
        today = datetime.today()
        doc_type = self.document_type_combo.currentText() if hasattr(self, 'document_type_combo') else "Cotizacion"
        prefix = "COT" if doc_type == "Cotizacion" else "REC"
        number = f"{prefix}-{today.strftime('%Y%m%d')}-{today.strftime('%H%M')}"
        self.quotation_number_input.setText(number)
    
    def _on_document_type_changed(self, doc_type: str):
        """Handle document type change."""
        self._generate_quotation_number()
        if doc_type == "Cotizacion":
            self.setWindowTitle("Cotizador Pro - Cotizacion")
        else:
            self.setWindowTitle("Cotizador Pro - Recibo")
    
    def _on_validez_changed(self, value: int):
        """Sync validez_dias from details tab to header and _terms_data."""
        self._terms_data["validez_dias"] = value
        # Sync to header spinbox without triggering infinite loop
        if hasattr(self, 'validez_input'):
            self.validez_input.blockSignals(True)
            self.validez_input.setValue(value)
            self.validez_input.blockSignals(False)
    
    def _on_header_validez_changed(self, value: int):
        """Sync validez_dias from header to details tab and _terms_data."""
        self._terms_data["validez_dias"] = value
        # Sync to details tab spinbox without triggering infinite loop
        if hasattr(self, 'validez_dias_spin'):
            self.validez_dias_spin.blockSignals(True)
            self.validez_dias_spin.setValue(value)
            self.validez_dias_spin.blockSignals(False)
    
    def _load_companies(self):
        """Load companies into combo box."""
        current = self.company_combo.currentText()
        self.company_combo.blockSignals(True)
        self.company_combo.clear()
        self.company_combo.addItem("Seleccionar Empresa")
        for name in self.company_logic.get_company_names():
            self.company_combo.addItem(name)
        index = self.company_combo.findText(current)
        if index >= 0: 
            self.company_combo.setCurrentIndex(index)
        self.company_combo.blockSignals(False)
    
    def _on_company_changed(self, name: str):
        """Handle company selection change."""
        if name == "Seleccionar Empresa":
            self.company_info_label.setText("")
            return
        company = self.company_logic.get_company(name)
        if company:
            info_parts = []
            if company.nit:
                info_parts.append(f"NIT: {company.nit}")
            if company.telefono:
                info_parts.append(f"📞 {company.telefono}")
            if company.correo:
                info_parts.append(f"✉️ {company.correo}")
            self.company_info_label.setText(" | ".join(info_parts))
    
    def _add_product(self, details: dict = None):
        """Add a new product row."""
        row = self.table.insertAnimatedRow()
        
        # Create unit combo box
        unit_combo = QComboBox()
        unit_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
                min-height: 28px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: white;
                selection-background-color: #0A84FF;
            }
        """)
        
        # Populate units
        units_grouped = self.unit_converter.get_all_units_grouped()
        for category, units in units_grouped.items():
            if units:
                unit_combo.addItem(f"── {category.upper()} ──")
                idx = unit_combo.count() - 1
                unit_combo.model().item(idx).setEnabled(False)
                for unit in units:
                    unit_combo.addItem(f"  {unit}")
        
        self.table.setCellWidget(row, 2, unit_combo)
        
        if details and isinstance(details, dict):
            self.table.setItem(row, 0, QTableWidgetItem(details.get("description", "")))
            self.table.setItem(row, 1, QTableWidgetItem(str(details.get("quantity", ""))))
            
            unit_text = f"  {details.get('unit', '')}"
            unit_idx = unit_combo.findText(unit_text)
            if unit_idx >= 0: 
                unit_combo.setCurrentIndex(unit_idx)
            
            self.table.setItem(row, 3, QTableWidgetItem(str(details.get("price", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(str(details.get("amount", ""))))
        
            # Handle image path
            if details.get("image_path"):
                item = self.table.item(row, 0)
                img_path = details["image_path"]
                item.setData(Qt.ItemDataRole.UserRole, img_path)
                item.setIcon(self.icon_manager.get_icon("image", 16))
                item.setToolTip(f"Imagen adjunta: {img_path}")
    
    def _duplicate_product(self):
        """Duplicate the selected product row."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Seleccione un producto para duplicar.")
            return
        
        desc = self.table.item(row, 0)
        qty = self.table.item(row, 1)
        unit_widget = self.table.cellWidget(row, 2)
        price = self.table.item(row, 3)
        
        # Get image path if exists
        image_path = desc.data(Qt.ItemDataRole.UserRole) if desc else None
        
        details = {
            "description": desc.text() if desc else "",
            "quantity": qty.text() if qty else "",
            "unit": unit_widget.currentText().strip() if unit_widget else "",
            "price": price.text() if price else "",
            "image_path": image_path
        }
        
        self._add_product(details)
        self._calculate_total()
    
    def _remove_product(self):
        """Remove selected product."""
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeAnimatedRow(row)
            self._calculate_total()
    
    def _clear_table(self):
        """Clear all products."""
        if self.table.rowCount() == 0:
            return
        reply = QMessageBox.question(
            self, "Confirmar",
            "¿Eliminar todos los productos?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.table.setRowCount(0)
            self._calculate_total()
    
    def _calculate_amount(self, item: QTableWidgetItem):
        """Calculate amount for a row."""
        if item.column() not in [1, 3]: 
            return
        
        row = item.row()
        try:
            qty_item = self.table.item(row, 1)
            price_item = self.table.item(row, 3)
            quantity = float(qty_item.text()) if qty_item and qty_item.text() else 0
            price = float(price_item.text()) if price_item and price_item.text() else 0
            amount = quantity * price
            
            self.table.blockSignals(True)
            self.table.setItem(row, 4, QTableWidgetItem(f"{amount:.2f}"))
            self.table.blockSignals(False)
        except ValueError: 
            pass
        
        self._calculate_total()
    
    def _calculate_total(self):
        """Calculate all totals respecting checkboxes."""
        subtotal = 0.0
        for row in range(self.table.rowCount()):
            amount_item = self.table.item(row, 4)
            if amount_item and amount_item.text():
                try: 
                    subtotal += float(amount_item.text())
                except ValueError: 
                    pass
        
        self.subtotal_label.setText(f"{subtotal:.2f} {self.config.moneda}")
        
        # Discount - only apply if checkbox is checked
        discount_amount = 0.0
        if hasattr(self, 'apply_discount_check') and self.apply_discount_check.isChecked():
            discount_percent = self.discount_input.value()
            discount_amount = subtotal * (discount_percent / 100)
        self.discount_amount_label.setText(f"- {discount_amount:.2f}")
        after_discount = subtotal - discount_amount
        
        # IVA - only apply if checkbox is checked
        iva_amount = 0.0
        if hasattr(self, 'apply_iva_check') and self.apply_iva_check.isChecked():
            iva_percent = self.iva_input.value()
            iva_amount = after_discount * (iva_percent / 100)
        self.iva_amount_label.setText(f"+ {iva_amount:.2f}")
        
        # Shipping - get from _products_data (widgets are in ProductsWindow)
        shipping_amount = 0.0
        shipping_data = self._products_data.get('shipping', {})
        if shipping_data.get('enabled', False):
            shipping_amount = shipping_data.get('amount', 0)
        
        # Update shipping display in Products tab
        if hasattr(self, 'shipping_display'):
            self.shipping_display.setText(f"+ {shipping_amount:.2f}")
        
        # Update shipping label in Finance tab  
        if hasattr(self, 'shipping_label'):
            if shipping_amount > 0:
                self.shipping_label.setText(f"+ {shipping_amount:.2f}")
            else:
                self.shipping_label.setText("No habilitado")
        
        total = after_discount + iva_amount + shipping_amount
        self.total_label.setText(f"{total:.2f} {self.config.moneda}")
        self.total_display.setText(f"Total: {total:.2f} {self.config.moneda}")
    
    # === FILE OPERATIONS ===
    
    def _get_quotation_data(self) -> dict:
        """Collect current data from UI."""
        subtotal = float(self.subtotal_label.text().split()[0]) if self.subtotal_label.text() else 0
        total = float(self.total_label.text().split()[0]) if self.total_label.text() else 0
        
        products = []
        for p in self.table.getProducts():
            products.append({
                "description": p[0],
                "quantity": p[1],
                "unit": p[2].strip() if p[2] else "",
                "price": p[3],
                "amount": p[4],
                "image_path": p[5] if len(p) > 5 else ""
            })
        
        return {
            "document_type": self.document_type_combo.currentText() if hasattr(self, 'document_type_combo') else "Cotizacion",
            "quotation_number": self.quotation_number_input.text(),
            "company_name": self.company_combo.currentText(),
            "date": self.date_input.text(),
            "validity": self.validez_input.value(),
            "client": {
                "name": self.client_name_input.text(),
                "contact": self.client_contact_input.text(),
                "address": self.client_address_input.text()
            },
            "products": products,
            "subtotal": subtotal,
            "apply_discount": self.apply_discount_check.isChecked() if hasattr(self, 'apply_discount_check') else False,
            "discount_percent": self.discount_input.value(),
            "apply_iva": self.apply_iva_check.isChecked() if hasattr(self, 'apply_iva_check') else True,
            "iva_percent": self.iva_input.value(),
            "shipping": self.shipping_input.value() if hasattr(self, 'shipping_input') else 0,
            "shipping_type": self.shipping_type_combo.currentText() if hasattr(self, 'shipping_type_combo') else "Sin envío",
            "total": total,
            "currency": self.config.moneda,
            "notes": self.internal_notes.toHtml() if hasattr(self, 'internal_notes') else "",
            "canvas_data": self.canvas.get_all_data(),
            
            # Terms Data (Now managed via TermsWindow / _terms_data)
            "payment_type": self._terms_data.get("payment_type", "Efectivo"),
            "payment_method": self._terms_data.get("payment_method", "Contado"),
            "delivery_time": str(self._terms_data.get("estimated_days", 7)), # Legacy compat
            "estimated_days": self._terms_data.get("estimated_days", 7),
            "reference_number": self.reference_number.text() if hasattr(self, 'reference_number') else "",
            "validez_dias": self._terms_data.get("validez_dias", 15),
            
            "warranty": self._terms_data.get("warranty_duration", ""),
            "warranty_covers": self._terms_data.get("warranty_terms", ""), # Mapping legacy to new text
            "warranty_excludes": "", # Deprecated/Merged
            "bank_details": self.bank_details.toHtml() if hasattr(self, 'bank_details') else "",
            "internal_notes": self.internal_notes.toHtml() if hasattr(self, 'internal_notes') else "",
            "installation_terms": self.installation_terms.toHtml() if hasattr(self, 'installation_terms') else "",
            "cover_page_enabled": self.cover_page_check.isChecked() if hasattr(self, 'cover_page_check') else False,
            "cover_page_data": self._cover_page_data,
            "terms_data": self._terms_data,
            "prepared_by": self.prepared_by_input.text() if hasattr(self, 'prepared_by_input') else "",
            "signature_source": self.signature_source.currentText() if hasattr(self, 'signature_source') else "Sin Firma",
            
            # Products data with shipping state (stored in _products_data)
            "products_data": self._products_data,
            
            # Persistent UI Flags
            "ui_FLAGS": {
                "apply_iva": self.apply_iva_check.isChecked() if hasattr(self, 'apply_iva_check') else True,
                "apply_discount": self.apply_discount_check.isChecked() if hasattr(self, 'apply_discount_check') else False,
                "enable_shipping": self.enable_shipping_check.isChecked() if hasattr(self, 'enable_shipping_check') else False,
                "include_bank_details": self.include_bank_details_check.isChecked() if hasattr(self, 'include_bank_details_check') else False,
                "cover_page_enabled": self.cover_page_check.isChecked() if hasattr(self, 'cover_page_check') else False,
                "include_signature": self.include_signature_check.isChecked() if hasattr(self, 'include_signature_check') else False,
                "include_details": self.include_details_check.isChecked() if hasattr(self, 'include_details_check') else True
            }
        }

    def _load_quotation_data(self, data: dict):
        """Load quotation data into UI."""
        if "quotation_number" in data:
            self.quotation_number_input.setText(data["quotation_number"])
        
        if "company_name" in data:
            idx = self.company_combo.findText(data["company_name"])
            if idx >= 0: 
                self.company_combo.setCurrentIndex(idx)
        
        if "date" in data: 
            self.date_input.setText(data["date"])
        if "validity" in data: 
            self._terms_data["validez_dias"] = int(data["validity"])
        
        client = data.get("client", {})
        self.client_name_input.setText(client.get("name", ""))
        self.client_contact_input.setText(client.get("contact", ""))
        self.client_address_input.setText(client.get("address", ""))
        
        if "discount_percent" in data:
            self.discount_input.setValue(float(data["discount_percent"]))
        if "apply_discount" in data and hasattr(self, 'apply_discount_check'):
            self.apply_discount_check.setChecked(data["apply_discount"])

        if "iva_percent" in data:
            self.iva_input.setValue(float(data["iva_percent"]))
        if "apply_iva" in data and hasattr(self, 'apply_iva_check'):
            self.apply_iva_check.setChecked(data["apply_iva"])
            
        if "shipping" in data and hasattr(self, 'shipping_input'):
            self.shipping_input.setValue(float(data["shipping"]))
        
        # Shipping type
        if "shipping_type" in data and hasattr(self, 'shipping_type_combo'):
            idx = self.shipping_type_combo.findText(data["shipping_type"])
            if idx >= 0:
                self.shipping_type_combo.setCurrentIndex(idx)
        
        if "notes" in data and hasattr(self, 'internal_notes'):
            self.internal_notes.setHtml(data["notes"])
        
        if "canvas_data" in data:
            self.canvas.load_data(data["canvas_data"])
        
        # Parse legacy terms data into _terms_data
        if "payment_method" in data:
            self._terms_data["payment_method"] = data["payment_method"]
        
        if "delivery_time" in data:
            self._terms_data["delivery_time"] = data["delivery_time"]
            
        if "estimated_days" in data:
            self._terms_data["estimated_days"] = int(data["estimated_days"])
            
        if "reference_number" in data and hasattr(self, 'reference_number'):
            self.reference_number.setText(data["reference_number"])
        
        # Warranty fields
        if "warranty" in data:
            self._terms_data["warranty_duration"] = data["warranty"]
            
        # Legacy warranty text merge if needed, or just let TermsWindow handle defaults
        
        # Bank details and notes
        if "bank_details" in data and hasattr(self, 'bank_details'):
            self.bank_details.setHtml(data["bank_details"])
        if "internal_notes" in data and hasattr(self, 'internal_notes'):
            self.internal_notes.setHtml(data["internal_notes"])
        if "installation_terms" in data:
             self._terms_data["installation_terms"] = data["installation_terms"]
        
        # Cover page
        if "cover_page_enabled" in data and hasattr(self, 'cover_page_check'):
            self.cover_page_check.setChecked(data["cover_page_enabled"])
        if "cover_page_data" in data:
            self._cover_page_data = data["cover_page_data"]
        
        # Terms data (New format overwrites legacy if present)
        if "terms_data" in data:
            self._terms_data.update(data["terms_data"])
        
        # Sync validez_dias spinbox with loaded data
        validez_value = self._terms_data.get("validez_dias", 15)
        if hasattr(self, 'validez_dias_spin'):
            self.validez_dias_spin.blockSignals(True)
            self.validez_dias_spin.setValue(validez_value)
            self.validez_dias_spin.blockSignals(False)
        if hasattr(self, 'validez_input'):
            self.validez_input.blockSignals(True)
            self.validez_input.setValue(validez_value)
            self.validez_input.blockSignals(False)
        
        # Signature fields
        if "prepared_by" in data and hasattr(self, 'prepared_by_input'):
            self.prepared_by_input.setText(data["prepared_by"])
        
        if "signature_source" in data and hasattr(self, 'signature_source'):
            idx = self.signature_source.findText(data["signature_source"])
            if idx >= 0:
                self.signature_source.setCurrentIndex(idx)
        
        # Load Persistent Flags
        # Fallback to direct keys for legacy support, then try new container
        flags = data.get("ui_FLAGS", {})
        
        # IVA
        if hasattr(self, 'apply_iva_check'):
            state = flags.get("apply_iva", data.get("apply_iva", True))
            self.apply_iva_check.setChecked(state)
            
        # Discount
        if hasattr(self, 'apply_discount_check'):
            state = flags.get("apply_discount", data.get("apply_discount", False))
            self.apply_discount_check.setChecked(state)
            
        # Shipping
        if hasattr(self, 'enable_shipping_check'):
            # Legacy might implicitly rely on value > 0, but explicit check is better
            state = flags.get("enable_shipping", data.get("shipping", 0) > 0)
            self.enable_shipping_check.setChecked(state)
            
        # Bank Details
        if hasattr(self, 'include_bank_details_check'):
            state = flags.get("include_bank_details", False)
            self.include_bank_details_check.setChecked(state)
            
        # Cover Page
        if hasattr(self, 'cover_page_check'):
            state = flags.get("cover_page_enabled", data.get("cover_page_enabled", False))
            self.cover_page_check.setChecked(state)
            
        # Signature
        if hasattr(self, 'include_signature_check'):
            state = flags.get("include_signature", False)
            self.include_signature_check.setChecked(state)
            
        # Details
        if hasattr(self, 'include_details_check'):
            state = flags.get("include_details", data.get("include_details", False))
            self.include_details_check.setChecked(state)
        
        # Load products_data (includes shipping state - widgets are in ProductsWindow)
        if "products_data" in data:
            self._products_data = data["products_data"]
        
        self.table.setRowCount(0)
        for prod in data.get("products", []):
            self._add_product(prod)
        
        self._calculate_total()

    def _new_quotation(self):
        """Reset UI for new quotation."""
        self.company_combo.setCurrentIndex(0)
        self.table.setRowCount(0)
        self.date_input.setText(datetime.today().strftime("%d/%m/%Y"))
        self.validez_input.setValue(15)
        self.client_name_input.clear()
        self.client_contact_input.clear()
        self.client_address_input.clear()
        self.discount_input.setValue(0)
        self.iva_input.setValue(13)
        if hasattr(self, 'internal_notes'):
            self.internal_notes.clear()
        self.canvas._clear_all_silent()
        
        # Reset data structures
        self._terms_data = {}
        self._cover_page_data = {}
        self._observations_data = {}
        
        # Note: payment_method, delivery_time, warranty are now managed in self._terms_data
        # and edited via TermsWindow. Defaults will be loaded when TermsWindow opens.
        
        # Clear new fields
        if hasattr(self, 'shipping_input'):
            self.shipping_input.setValue(0)
        if hasattr(self, 'shipping_type_combo'):
            self.shipping_type_combo.setCurrentIndex(0)
        if hasattr(self, 'estimated_days'):
            self.estimated_days.setValue(7)
        if hasattr(self, 'reference_number'):
            self.reference_number.clear()
        if hasattr(self, 'warranty_covers'):
            self.warranty_covers.clear()
        if hasattr(self, 'warranty_excludes'):
            self.warranty_excludes.clear()
        if hasattr(self, 'bank_details'):
            self.bank_details.clear()
        if hasattr(self, 'internal_notes'):
            self.internal_notes.clear()
        if hasattr(self, 'installation_terms'):
            self.installation_terms.clear()
        if hasattr(self, 'cover_page_check'):
            self.cover_page_check.setChecked(False)
        
        self._observations_data = {}  # Clear observations
        self._cover_page_data = {}  # Clear cover page
        self._terms_data = {}        # Enhanced terms data
        
        # Reset signature fields
        if hasattr(self, 'prepared_by_input'):
            self.prepared_by_input.setText(self.config.prepared_by)
        if hasattr(self, 'signature_source'):
            self.signature_source.setCurrentIndex(0)  # Default to "Firma de la Empresa" or whatever is first
        
        self._update_observations_summary()
        self._calculate_total()
        self.cotz_manager.current_file = None
        self._generate_quotation_number()
        self.setWindowTitle("Cotizador Pro - Sin Título")

    def _save_file(self):
        """Save current file, or Save As if new."""
        if self.cotz_manager.current_file:
            data = self._get_quotation_data()
            data["observations"] = self._observations_data
            if self.cotz_manager.save_quotation(self.cotz_manager.current_file, data):
                self._add_to_history(self.cotz_manager.current_file, data)
                QMessageBox.information(self, "Guardado", "Cotización guardada exitosamente.")
                self.setWindowTitle(f"Cotizador Pro - {os.path.basename(self.cotz_manager.current_file)}")
        else:
            self._save_file_as()

    def _save_file_as(self):
        """Save As with smart naming."""
        data = self._get_quotation_data()
        data["observations"] = self._observations_data
        
        # Smart Naming: Type-Date-Client/Project
        doc_type = "COT" if "Cotizaci" in self.document_type_combo.currentText() else "REC"
        date_str = datetime.now().strftime("%Y%m%d")
        client_name = self.client_name_input.text().strip()
        if not client_name: client_name = "Cliente"
        # Sanitize filename
        safe_client = "".join([c for c in client_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        suggested_name = f"{doc_type}-{date_str}-{safe_client}.cotz"
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Cotización Como", 
            suggested_name,
            "Cotización (*.cotz)"
        )
        
        if path:
            if self.cotz_manager.save_quotation(path, data):
                self._add_to_history(path, data)
                QMessageBox.information(self, "Guardado", f"Archivo guardado en:\n{path}")
                self.setWindowTitle(f"Cotizador Pro - {os.path.basename(path)}")

    def _add_to_history(self, path, data):
        """Add file to history and recent list."""
        self.history_manager.add_to_recent(path)
        
        # Metadata for advanced history
        meta = {
            "client": data.get("client", {}).get("name", ""),
            "total": data.get("total", "0"),
            "doc_type": self.document_type_combo.currentText(),
            "items_count": len(data.get("products", []))
        }
        self.history_manager.add_to_history(path, meta)

    def _update_recent_menu(self):
        """Update recent files menu."""
        self.menu_recent.clear()
        recent_files = self.history_manager.get_recent()
        
        if not recent_files:
            action = self.menu_recent.addAction("No hay archivos recientes")
            action.setEnabled(False)
            return
            
        for path in recent_files:
            if os.path.exists(path):
                filename = os.path.basename(path)
                action = self.menu_recent.addAction(filename)
                action.setData(path)
                action.triggered.connect(lambda checked, p=path: self._open_recent_file(p))
    
    def _open_recent_file(self, path):
        """Open a file from recent menu."""
        if os.path.exists(path):
            data = self.cotz_manager.load_quotation(path)
            if data:
                self._load_quotation_data(data)
                self._observations_data = data.get("observations", {})
                
                # Check legacy terms if not in terms_data
                if "terms_data" in data:
                    self._terms_data = data["terms_data"]
                
                self._update_observations_summary()
                self._add_to_history(path, data) # Move to top
                
                self.setWindowTitle(f"Cotizador Pro - {os.path.basename(path)}")
        else:
             QMessageBox.warning(self, "Error", "El archivo ya no existe.")

    def _open_history_window(self):
        """Open local history window."""
        dialog = HistoryWindow(self.history_manager, self)
        dialog.file_selected.connect(self._open_recent_file)
        dialog.exec()

    def _open_quotation(self):
        """Open a .cotz file (supports both ZIP and legacy JSON)."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Cotización", "", "Cotización (*.cotz)"
        )
        
        if path:
            data = self.cotz_manager.load_quotation(path)
            if data:
                self._load_quotation_data(data)
                # Load observations data
                self._observations_data = data.get("observations", {})
                
                if "terms_data" in data: self._terms_data = data["terms_data"]
                
                self._update_observations_summary()
                
                self._add_to_history(path, data)
                
                self.setWindowTitle(f"Cotizador Pro - {os.path.basename(path)}")

    def _export_pdf(self):
        """Export quotation as PDF."""
        # Helper to clean html for PDF (force black text)
        from .components.editor.rich_text_editor import RichTextEditor
        def clean(html):
            return RichTextEditor.sanitize_for_pdf(html) if html else ""
            
        company = self.company_combo.currentText()
        if company == "Seleccionar Empresa":
            QMessageBox.warning(self, "Error", "Seleccione una empresa.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar PDF", 
            f"{self.quotation_number_input.text()}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            company_data = self.company_logic.get_company_dict(company)
            products = [[p[0], p[1], p[2].strip(), p[3], p[4]] for p in self.table.getProducts()]
            data = self._get_quotation_data()
            
            # Prepare client data
            cliente = {
                "name": self.client_name_input.text(),
                "contact": self.client_contact_input.text(),
                "address": self.client_address_input.text()
            }
            
            # Prepare cover page data
            cover_page_data = None
            if hasattr(self, 'cover_page_check') and self.cover_page_check.isChecked():
                cover_page_data = self._cover_page_data.copy() if self._cover_page_data else {}
                cover_page_data["enabled"] = True
            
            # Prepare warranty data from _terms_data (managed by TermsWindow)
            # Use raw data but sanitize it for PDF
            warranty_data = {
                "duration": self._terms_data.get("warranty_duration", ""),
                
                # New 5 sections logic
                "garantia": clean(self._terms_data.get("warranty_garantia", "") or self._terms_data.get("warranty_terms", "")),
                "covers": clean(self._terms_data.get("warranty_covers", "")),
                "excludes": clean(self._terms_data.get("warranty_excludes", "")),
                "warning": clean(self._terms_data.get("warranty_warning", "")),
                "verification": clean(self._terms_data.get("warranty_verification", ""))
            }
            
            # Prepare signature data
            prepared_by = ""
            signature_image = None
            include_signature = self.include_signature_check.isChecked() if hasattr(self, 'include_signature_check') else False
            
            if include_signature:
                # Use User Profile from Config
                prepared_by = self.config.prepared_by
                if self.config.signature_path and os.path.exists(self.config.signature_path):
                     signature_image = self.config.signature_path
                else:
                    # Fallback to Company Signature if no user signature?
                    # Or just leave mostly blank. User said "tenemos perfil".
                    # Let's try company if user is missing, for backward compat.
                    try:
                        comp_sig = self.company_logic.get_signature_absolute_path(company)
                        if comp_sig and os.path.exists(comp_sig):
                            if not signature_image: signature_image = comp_sig
                    except: pass

            try:
                generar_pdf(
                    file_path=file_path,
                    empresa=company,
                    datos_empresa=company_data,
                    productos=products,
                    total=data["total"],
                    moneda=self.config.moneda,
                    fecha=self.date_input.text(),
                    validez_dias=int(self._terms_data.get('validez_dias', 15)),
                    cliente=cliente,
                    observaciones_data=self._observations_data,
                    numero_cotizacion=self.quotation_number_input.text(),
                    document_type=self.document_type_combo.currentText() if hasattr(self, 'document_type_combo') else "Cotizacion",
                    shipping=self._products_data.get('shipping', {}).get('amount', 0) if self._products_data.get('shipping', {}).get('enabled', False) else 0,
                    cover_page_data=cover_page_data,
                    warranty_data=warranty_data,
                    estimated_days=int(self._terms_data.get('estimated_days', 7)),
                    shipping_type=self._products_data.get('shipping', {}).get('type', 'Sin envío') if self._products_data.get('shipping', {}).get('enabled', False) else "Sin envío",
                    payment_method=str(self._terms_data.get('payment_method', '')),
                    bank_details=clean(self.bank_details.toHtml()) if (hasattr(self, 'bank_details') and hasattr(self, 'include_bank_details_check') and self.include_bank_details_check.isChecked()) else "",
                    installation_terms=clean(self._terms_data.get('installation_terms', '')),
                    payment_type=str(self._terms_data.get('payment_type', '')),
                    apply_iva=self.apply_iva_check.isChecked() if hasattr(self, 'apply_iva_check') else True,
                    include_details=self.include_details_check.isChecked() if hasattr(self, 'include_details_check') else True,
                    # Sanitize terms_data in place or copy? Copy safest
                    terms_data={k: clean(v) if isinstance(v, str) and k.endswith('_terms') else v for k, v in self._terms_data.items()},
                    prepared_by=prepared_by,
                    signature_image=signature_image,
                    mostrar_firma=include_signature  # Only show signature if checkbox enabled
                )
                QMessageBox.information(self, "Exito", "PDF generado correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def _open_terms_window(self):
        """Open the Terms & Conditions management window."""
        self.terms_window = TermsWindow(self._terms_data, self)
        self.terms_window.terms_saved.connect(self._update_terms_data)
        self.terms_window.show()
    
    def _update_terms_data(self, data: dict):
        """Update terms data from the window."""
        self._terms_data = data
        QMessageBox.information(self, "Términos Actualizados", "Los términos y condiciones se han actualizado correctamente.")

    def _open_config(self):
        """Open configuration window."""
        self.config_window = self._ConfigManagerView(self)
        self.config_window.config_updated.connect(self._apply_config_changes)
        self.config_window.show()
    
    def _apply_config_changes(self):
        """Apply configuration changes."""
        self.config = get_config()
        ThemeManager.apply_theme(self, self.config.tema)
        font_size = max(8, self.config.tamaño_fuente)  # Ensure valid font size
        self.setFont(QFont(self.config.fuente, font_size))
        icon_color = "#1D1D1F" if "Claro" in self.config.tema else "#FFFFFF"
        self.icon_manager.set_theme_color(icon_color)
        self._calculate_total()
    
    def _open_company_manager(self):
        """Open company manager window."""
        self.company_window = self._CompanyManagerView(self)
        self.company_window.company_updated.connect(self._load_companies)
        self.company_window.show()
    
    def _open_cover_page_editor(self):
        """Open the cover page editor dialog."""
        from .cover_page_dialog import CoverPageDialog
        
        dialog = CoverPageDialog(
            self, 
            data=self._cover_page_data,
            company_name=self.company_combo.currentText(),
            client_name=self.client_name_input.text(),
            project_date=self.date_input.text()
        )
        dialog.saved.connect(self._on_cover_page_saved)
        dialog.exec()
    
    def _on_cover_page_saved(self, data: dict):
        """Handle cover page data saved from dialog."""
        self._cover_page_data = data
        # Auto-check the cover page checkbox when data is saved
        if hasattr(self, 'cover_page_check') and data.get("enabled", False):
            self.cover_page_check.setChecked(True)
        self.cotz_manager.mark_modified()
    
    def _open_products_window(self):
        """Open the products management window."""
        # Prepare products data from table and stored shipping state
        products = []
        for p in self.table.getProducts():
            products.append({
                'descripcion': p[0],
                'cantidad': p[1],
                'unidad': p[2].strip() if p[2] else '',
                'precio_unitario': p[3],
                'importe': p[4],
                'imagen': p[5] if len(p) > 5 else ''
            })
        
        # Get shipping from stored _products_data (shipping widgets are in ProductsWindow, not here)
        stored_shipping = self._products_data.get('shipping', {})
        shipping = {
            'enabled': stored_shipping.get('enabled', False),
            'amount': stored_shipping.get('amount', 0),
            'type': stored_shipping.get('type', 'Envío Local')
        }
        
        products_data = {
            'products': products if products else self._products_data.get('products', []),
            'shipping': shipping
        }
        
        # Create and show window
        self.products_window = ProductsWindow(
            products_data=products_data,
            parent=None
        )
        self.products_window.products_saved.connect(self._on_products_saved)
        self.products_window.show()
    
    def _on_products_saved(self, data: dict):
        """Handle products data saved from window."""
        self._products_data = data
        
        # Update hidden table with products for compatibility
        self.table.setRowCount(0)
        for prod in data.get('products', []):
            self.table.addProduct(
                description=prod.get('descripcion', ''),
                quantity=str(prod.get('cantidad', '')),
                unit=prod.get('unidad', ''),
                price=str(prod.get('precio_unitario', '')),
                amount=str(prod.get('importe', '')),
                image_path=prod.get('imagen', '')
            )
        
        # Shipping state is already stored in _products_data, no widgets to update here
        # (shipping widgets only exist in ProductsWindow)
        
        # Update products summary
        self._update_products_summary()
        
        # Recalculate totals
        self._calculate_total()
        
        # Mark as modified
        self.cotz_manager.mark_modified()
    
    def _update_products_summary(self):
        """Update the products summary display in details tab."""
        if not hasattr(self, 'products_summary'):
            return
        
        products = self._products_data.get('products', [])
        count = len(products)
        
        if count == 0:
            self.products_summary.setText("Sin productos agregados")
            return
        
        total = self._products_data.get('total', 0)
        shipping = self._products_data.get('shipping', {})
        
        summary_parts = [f"{count} producto{'s' if count != 1 else ''}"]
        summary_parts.append(f"Total: {total:.2f} {self.config.moneda}")
        
        if shipping.get('enabled', False):
            summary_parts.append(f"Envío: +{shipping.get('amount', 0):.2f}")
        
        self.products_summary.setText(" • ".join(summary_parts))
    
    def _open_observations_window(self):
        """Open the observations window."""
        from .observations_window import ObservationsWindow
        
        # Get current products for the observations window
        products = []
        for p in self.table.getProducts():
            products.append({
                "description": p[0],
                "quantity": p[1],
                "unit": p[2].strip() if p[2] else "",
                "price": p[3],
                "amount": p[4],
                "image_path": self._observations_data.get("products", [{}])[len(products)].get("image_path", "") if len(products) < len(self._observations_data.get("products", [])) else ""
            })
        
        # Update observations data with current products
        obs_data = self._observations_data.copy()
        obs_data["products"] = products
        
        # Create and show window
        self.observations_window = ObservationsWindow(
            products=products,
            observations_data=obs_data,
            parent=None
        )
        self.observations_window.data_saved.connect(self._on_observations_saved)
        self.observations_window.exec()
    
    def _on_observations_saved(self, data: dict):
        """Handle observations data saved from window."""
        self._observations_data = data
        
        # Helper to normalize path separators
        def normalize_path(p):
            return os.path.normpath(str(p)) if p else ""
        
        # Update product images in main table if they were changed in observations
        if "products" in data:
            current_products = self.table.getProducts() # [(desc, qty, unit, price, amount, image_path?), ...]
            
            # Map description -> image_path from observations data
            image_map = {
                p.get("description"): normalize_path(p.get("image_path")) 
                for p in data["products"] 
                if p.get("description")
            }
            
            # Iterate main table and update
            for row in range(self.table.rowCount()):
                desc_item = self.table.item(row, 0)
                if not desc_item: continue
                
                desc = desc_item.text()
                if desc in image_map:
                    new_path = image_map[desc]
                    # Update table item data
                    desc_item.setData(Qt.ItemDataRole.UserRole, new_path)
                    
                    # Update icon visual
                    if new_path and os.path.exists(new_path):
                         desc_item.setIcon(self.icon_manager.get_icon("image", 16))
                         desc_item.setToolTip(f"Imagen adjunta: {new_path}")
                    else:
                        desc_item.setIcon(QIcon())
                        desc_item.setToolTip("")
                        
        self._update_observations_summary()
        self.cotz_manager.mark_modified()
    
    def _update_observations_summary(self):
        """Update the observations summary display."""
        obs_text = self._observations_data.get("text", "")
        gallery = self._observations_data.get("gallery", [])
        products = self._observations_data.get("products", [])
        
        # Count items
        has_text = bool(obs_text.strip())
        image_count = len([g for g in gallery if g.get("type") == "image"])
        product_images = len([p for p in products if p.get("image_path")])
        
        # Create summary
        summary_parts = []
        if has_text:
            # Show first 100 chars of text
            preview = obs_text[:100] + "..." if len(obs_text) > 100 else obs_text
            summary_parts.append(f"📝 {preview}")
        if image_count > 0:
            summary_parts.append(f"🖼️ {image_count} imagen(es) en galería")
        if product_images > 0:
            summary_parts.append(f"📦 {product_images} producto(s) con imagen")
        
        if summary_parts:
            self.observations_summary.setText("\n".join(summary_parts))
            self.observations_summary.setStyleSheet("color: rgba(255,255,255,0.8); padding: 10px;")
            if hasattr(self, 'internal_notes'):
                self.internal_notes.setHtml(obs_text)
        else:
            self.observations_summary.setText("Sin observaciones añadidas")
            self.observations_summary.setStyleSheet("color: rgba(255,255,255,0.5); padding: 10px;")
            if hasattr(self, 'internal_notes'):
                self.internal_notes.clear()

