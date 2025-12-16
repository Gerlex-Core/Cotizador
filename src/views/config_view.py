"""
Configuration Manager View - UI for application settings.
Expanded layout with scroll area for better visibility.
"""

import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QMessageBox, QSpinBox, QDoubleSpinBox, QFrame,
    QScrollArea, QTextEdit, QTabWidget
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import pyqtSignal, Qt

from .components.buttons.animated_button import AnimatedButton, PrimaryButton
from .styles.theme_manager import ThemeManager, THEMES
from .styles.icon_manager import IconManager

from ..logic.config.config_manager import get_config


# Path to terms JSON
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TERMINOS_FILE = os.path.join(BASE_DIR, "media", "config", "terminos.json")


class ConfigManagerView(QMainWindow):
    """Configuration settings window with expanded layout and tabs."""
    
    config_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.config = get_config()
        self.icon_manager = IconManager.get_instance()
        
        self.setWindowTitle("Configuración")
        self.setWindowIcon(self.icon_manager.get_icon("settings"))
        self.setMinimumSize(700, 600)
        self.resize(750, 650)
        
        # Apply current theme
        ThemeManager.apply_theme(self, self.config.tema)
        font_size = max(8, self.config.tamaño_fuente)  # Ensure valid font size
        self.setFont(QFont(self.config.fuente, font_size))
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the settings UI with tabs."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with icon
        header_layout = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(self.icon_manager.get_pixmap("settings", 24))
        header_layout.addWidget(header_icon)
        header_title = QLabel("Configuración del Sistema")
        header_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)
        
        # Tab widget
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
        
        # Tab 1: General Settings
        self._create_general_tab()
        
        # Tab 2: User Profile
        self._create_profile_tab()
        
        # Tab 3: PDF Settings
        self._create_pdf_tab()
        
        layout.addWidget(self.tabs, 1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_reset = AnimatedButton("Restablecer")
        btn_reset.setIcon(self.icon_manager.get_icon("back", 18))
        btn_reset.clicked.connect(self._reset_defaults)
        btn_layout.addWidget(btn_reset)
        
        btn_layout.addStretch()
        
        self.btn_save = PrimaryButton("Guardar Todo")
        self.btn_save.setIcon(self.icon_manager.get_icon("save", 18))
        self.btn_save.setMinimumWidth(160)
        self.btn_save.setMinimumHeight(45)
        self.btn_save.clicked.connect(self._save_config)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
    
    def _create_general_tab(self):
        """Create general settings tab."""
        tab = QWidget()
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        grid = QGridLayout(content)
        grid.setSpacing(15)
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setColumnStretch(1, 1)
        
        row = 0
        
        # === APPEARANCE ===
        app_header = QHBoxLayout()
        app_icon = QLabel()
        app_icon.setPixmap(self.icon_manager.get_pixmap("theme", 18))
        app_header.addWidget(app_icon)
        app_label = QLabel("APARIENCIA")
        app_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #0A84FF;")
        app_header.addWidget(app_label)
        app_header.addStretch()
        app_widget = QWidget()
        app_widget.setLayout(app_header)
        grid.addWidget(app_widget, row, 0, 1, 2)
        row += 1
        
        grid.addWidget(QLabel("Tema:"), row, 0)
        self.combo_theme = QComboBox()
        self._populate_theme_combobox()
        # Select current theme (must use index-based selection for custom model)
        self._select_initial_theme()
        self.combo_theme.currentTextChanged.connect(self._preview_theme)
        self.combo_theme.setMinimumHeight(40)
        grid.addWidget(self.combo_theme, row, 1)
        row += 1
        
        grid.addWidget(QLabel("Fuente:"), row, 0)
        self.combo_font = QComboBox()
        self.combo_font.addItems(["Segoe UI", "Arial", "Verdana", "Roboto", "Tahoma", "Consolas", "Times New Roman", "Georgia"])
        self.combo_font.setCurrentText(self.config.fuente)
        self.combo_font.setMinimumHeight(40)
        grid.addWidget(self.combo_font, row, 1)
        row += 1
        
        grid.addWidget(QLabel("Tamaño de Fuente:"), row, 0)
        self.spin_size = QSpinBox()
        self.spin_size.setRange(10, 24)
        self.spin_size.setValue(self.config.tamaño_fuente)
        self.spin_size.setMinimumHeight(40)
        self.spin_size.setSuffix(" px")
        grid.addWidget(self.spin_size, row, 1)
        row += 1
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("background-color: rgba(255,255,255,0.2);")
        sep1.setFixedHeight(2)
        grid.addWidget(sep1, row, 0, 1, 2)
        row += 1
        
        # === REGIONAL ===
        reg_header = QHBoxLayout()
        reg_icon = QLabel()
        reg_icon.setPixmap(self.icon_manager.get_pixmap("worldWideLocation", 18))
        reg_header.addWidget(reg_icon)
        reg_label = QLabel("REGIONAL")
        reg_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #34C759;")
        reg_header.addWidget(reg_label)
        reg_header.addStretch()
        reg_widget = QWidget()
        reg_widget.setLayout(reg_header)
        grid.addWidget(reg_widget, row, 0, 1, 2)
        row += 1
        
        grid.addWidget(QLabel("Idioma:"), row, 0)
        self.combo_language = QComboBox()
        self.combo_language.addItems(["es", "en", "pt"])
        self.combo_language.setCurrentText(self.config.idioma)
        self.combo_language.setMinimumHeight(40)
        grid.addWidget(self.combo_language, row, 1)
        row += 1
        
        grid.addWidget(QLabel("Moneda:"), row, 0)
        self.combo_currency = QComboBox()
        self.combo_currency.addItems([
            "Bolivianos (Bs)", "Dólares ($)", "Euros (€)", 
            "Pesos (MXN)", "Pesos (COP)", "Pesos (ARS)",
            "Soles (S/)", "Reales (R$)", "Guaraníes (Gs)"
        ])
        self.combo_currency.setCurrentText(self.config.moneda)
        self.combo_currency.setMinimumHeight(40)
        grid.addWidget(self.combo_currency, row, 1)
        row += 1
        
        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: rgba(255,255,255,0.2);")
        sep2.setFixedHeight(2)
        grid.addWidget(sep2, row, 0, 1, 2)
        row += 1
        
        # === DEFAULTS ===
        def_header = QHBoxLayout()
        def_icon = QLabel()
        def_icon.setPixmap(self.icon_manager.get_pixmap("settings", 18))
        def_header.addWidget(def_icon)
        def_label = QLabel("VALORES PREDETERMINADOS")
        def_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF9500;")
        def_header.addWidget(def_label)
        def_header.addStretch()
        def_widget = QWidget()
        def_widget.setLayout(def_header)
        grid.addWidget(def_widget, row, 0, 1, 2)
        row += 1
        
        grid.addWidget(QLabel("IVA por defecto:"), row, 0)
        self.spin_iva = QDoubleSpinBox()
        self.spin_iva.setRange(0, 50)
        self.spin_iva.setValue(getattr(self.config, 'iva_default', 13.0))
        self.spin_iva.setMinimumHeight(40)
        self.spin_iva.setSuffix(" %")
        grid.addWidget(self.spin_iva, row, 1)
        row += 1
        
        grid.addWidget(QLabel("Validez de cotización:"), row, 0)
        self.spin_validity = QSpinBox()
        self.spin_validity.setRange(1, 365)
        self.spin_validity.setValue(getattr(self.config, 'validez_default', 15))
        self.spin_validity.setMinimumHeight(40)
        self.spin_validity.setSuffix(" días")
        grid.addWidget(self.spin_validity, row, 1)
        row += 1
        
        grid.addWidget(QLabel("Días de entrega:"), row, 0)
        self.spin_delivery = QSpinBox()
        self.spin_delivery.setRange(1, 365)
        self.spin_delivery.setValue(getattr(self.config, 'delivery_default', 7))
        self.spin_delivery.setMinimumHeight(40)
        self.spin_delivery.setSuffix(" días")
        grid.addWidget(self.spin_delivery, row, 1)
        row += 1
        
        # Add stretch
        grid.setRowStretch(row, 1)
        
        scroll.setWidget(content)
        
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)
        
        self.tabs.addTab(tab, self.icon_manager.get_icon("settings", 18), "General")
    
    def _create_profile_tab(self):
        """Create user profile tab."""
        tab = QWidget()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Profile Header
        header_layout = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(self.icon_manager.get_pixmap("user", 24))
        header_layout.addWidget(header_icon)
        header_label = QLabel("PERFIL DE USUARIO")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #0A84FF;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        layout.addWidget(QLabel("Esta información se utilizará para la firma y 'Preparado por' en las cotizaciones."))
        
        # Prepared By
        from PyQt6.QtWidgets import QLineEdit
        layout.addWidget(QLabel("Nombre completo (Preparado por):"))
        self.prepared_by_input = QLineEdit()
        self.prepared_by_input.setPlaceholderText("Ej: Juan Pérez")
        self.prepared_by_input.setText(self.config.prepared_by)
        self.prepared_by_input.setMinimumHeight(40)
        self.prepared_by_input.setStyleSheet("padding: 5px;")
        layout.addWidget(self.prepared_by_input)
        
        # Signature
        layout.addWidget(QLabel("Firma Personal:"))
        
        sig_layout = QHBoxLayout()
        self.sig_path_input = QLineEdit()
        self.sig_path_input.setReadOnly(True)
        self.sig_path_input.setPlaceholderText("Seleccione una imagen de firma (PNG transparente recomendado)...")
        self.sig_path_input.setText(self.config.signature_path)
        self.sig_path_input.setMinimumHeight(40)
        sig_layout.addWidget(self.sig_path_input)
        
        btn_upload = PrimaryButton("Subir Firma")
        btn_upload.setIcon(self.icon_manager.get_icon("upload", 16))
        btn_upload.setMinimumHeight(40)
        btn_upload.clicked.connect(self._upload_signature)
        sig_layout.addWidget(btn_upload)
        
        btn_clear = AnimatedButton("Borrar")
        btn_clear.setIcon(self.icon_manager.get_icon("delete", 16))
        btn_clear.setMinimumHeight(40)
        btn_clear.clicked.connect(self._clear_signature)
        sig_layout.addWidget(btn_clear)
        
        layout.addLayout(sig_layout)
        
        # Signature Preview
        layout.addWidget(QLabel("Vista Previa:"))
        self.sig_preview = QLabel()
        self.sig_preview.setFixedSize(200, 100)
        self.sig_preview.setStyleSheet("border: 1px dashed rgba(255,255,255,0.3); border-radius: 4px;")
        self.sig_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sig_preview)
        
        self._load_signature_preview()
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)
        
        self.tabs.addTab(tab, self.icon_manager.get_icon("user", 18), "Perfil de Usuario")

    def _create_pdf_tab(self):
        """Create PDF settings tab."""
        from PyQt6.QtWidgets import QLineEdit, QCheckBox, QSlider, QColorDialog, QPushButton, QFileDialog
        
        tab = QWidget()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)  # Increased spacing
        layout.setContentsMargins(25, 25, 25, 25)  # More padding
        
        # === MARGINS SECTION ===
        margin_header = QHBoxLayout()
        margin_icon = QLabel()
        margin_icon.setPixmap(self.icon_manager.get_pixmap("note", 18))
        margin_header.addWidget(margin_icon)
        margin_label = QLabel("MÁRGENES DE PÁGINA")
        margin_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #0A84FF;")
        margin_header.addWidget(margin_label)
        margin_header.addStretch()
        layout.addLayout(margin_header)
        
        margin_desc = QLabel("Márgenes en milímetros (se aplican a todas las páginas después de la carátula):")
        margin_desc.setStyleSheet("color: rgba(255,255,255,0.7); margin-bottom: 8px;")
        margin_desc.setWordWrap(True)
        layout.addWidget(margin_desc)
        
        margin_grid = QGridLayout()
        margin_grid.setSpacing(15)  # Increased spacing
        margin_grid.setContentsMargins(10, 10, 10, 10)
        
        margin_grid.addWidget(QLabel("Superior:"), 0, 0)
        self.spin_margin_top = QSpinBox()
        self.spin_margin_top.setRange(10, 100)
        self.spin_margin_top.setValue(self.config.pdf_margin_top)
        self.spin_margin_top.setSuffix(" mm")
        self.spin_margin_top.setMinimumHeight(45)
        self.spin_margin_top.setMinimumWidth(100)
        margin_grid.addWidget(self.spin_margin_top, 0, 1)
        
        margin_grid.addWidget(QLabel("Inferior:"), 0, 2)
        self.spin_margin_bottom = QSpinBox()
        self.spin_margin_bottom.setRange(10, 100)
        self.spin_margin_bottom.setValue(self.config.pdf_margin_bottom)
        self.spin_margin_bottom.setSuffix(" mm")
        self.spin_margin_bottom.setMinimumHeight(45)
        self.spin_margin_bottom.setMinimumWidth(100)
        margin_grid.addWidget(self.spin_margin_bottom, 0, 3)
        
        margin_grid.addWidget(QLabel("Izquierdo:"), 1, 0)
        self.spin_margin_left = QSpinBox()
        self.spin_margin_left.setRange(10, 100)
        self.spin_margin_left.setValue(self.config.pdf_margin_left)
        self.spin_margin_left.setSuffix(" mm")
        self.spin_margin_left.setMinimumHeight(45)
        self.spin_margin_left.setMinimumWidth(100)
        margin_grid.addWidget(self.spin_margin_left, 1, 1)
        
        margin_grid.addWidget(QLabel("Derecho:"), 1, 2)
        self.spin_margin_right = QSpinBox()
        self.spin_margin_right.setRange(10, 100)
        self.spin_margin_right.setValue(self.config.pdf_margin_right)
        self.spin_margin_right.setSuffix(" mm")
        self.spin_margin_right.setMinimumHeight(45)
        self.spin_margin_right.setMinimumWidth(100)
        margin_grid.addWidget(self.spin_margin_right, 1, 3)
        margin_grid.setColumnStretch(4, 1)  # Add stretch at end
        
        layout.addLayout(margin_grid)
        
        # Add spacer before separator
        layout.addSpacing(10)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("background-color: rgba(255,255,255,0.2);")
        sep1.setFixedHeight(2)
        layout.addWidget(sep1)
        
        # === WATERMARK SECTION ===
        wm_header = QHBoxLayout()
        wm_icon = QLabel()
        wm_icon.setPixmap(self.icon_manager.get_pixmap("image", 18))
        wm_header.addWidget(wm_icon)
        wm_label = QLabel("MARCA DE AGUA")
        wm_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #34C759;")
        wm_header.addWidget(wm_label)
        wm_header.addStretch()
        layout.addLayout(wm_header)
        
        self.watermark_check = QCheckBox("Habilitar marca de agua")
        self.watermark_check.setChecked(self.config.watermark_enabled)
        self.watermark_check.stateChanged.connect(self._toggle_watermark_controls)
        layout.addWidget(self.watermark_check)
        
        wm_text_layout = QHBoxLayout()
        wm_text_layout.addWidget(QLabel("Texto:"))
        self.watermark_text_input = QLineEdit()
        self.watermark_text_input.setPlaceholderText("Ej: BORRADOR, CONFIDENCIAL, etc.")
        self.watermark_text_input.setText(self.config.watermark_text)
        self.watermark_text_input.setMinimumHeight(40)
        wm_text_layout.addWidget(self.watermark_text_input)
        layout.addLayout(wm_text_layout)
        
        wm_opacity_layout = QHBoxLayout()
        wm_opacity_layout.addWidget(QLabel("Opacidad:"))
        self.watermark_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.watermark_opacity_slider.setRange(5, 50)
        self.watermark_opacity_slider.setValue(self.config.watermark_opacity)
        wm_opacity_layout.addWidget(self.watermark_opacity_slider)
        self.watermark_opacity_label = QLabel(f"{self.config.watermark_opacity}%")
        self.watermark_opacity_label.setMinimumWidth(50)
        self.watermark_opacity_slider.valueChanged.connect(lambda v: self.watermark_opacity_label.setText(f"{v}%"))
        wm_opacity_layout.addWidget(self.watermark_opacity_label)
        layout.addLayout(wm_opacity_layout)
        
        wm_image_layout = QHBoxLayout()
        wm_image_layout.addWidget(QLabel("Imagen (opcional):"))
        self.watermark_image_input = QLineEdit()
        self.watermark_image_input.setReadOnly(True)
        self.watermark_image_input.setPlaceholderText("Seleccione una imagen de marca de agua...")
        self.watermark_image_input.setText(self.config.watermark_image_path)
        self.watermark_image_input.setMinimumHeight(40)
        wm_image_layout.addWidget(self.watermark_image_input)
        
        btn_wm_image = AnimatedButton("Seleccionar")
        btn_wm_image.setMinimumHeight(40)
        btn_wm_image.clicked.connect(self._select_watermark_image)
        wm_image_layout.addWidget(btn_wm_image)
        layout.addLayout(wm_image_layout)
        
        # Initial state of watermark controls
        self._toggle_watermark_controls(self.watermark_check.isChecked())
        
        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: rgba(255,255,255,0.2);")
        sep2.setFixedHeight(2)
        layout.addWidget(sep2)
        
        # === DESIGN SECTION ===
        design_header = QHBoxLayout()
        design_icon = QLabel()
        design_icon.setPixmap(self.icon_manager.get_pixmap("theme", 18))
        design_header.addWidget(design_icon)
        design_label = QLabel("DISEÑO")
        design_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF9500;")
        design_header.addWidget(design_label)
        design_header.addStretch()
        layout.addLayout(design_header)
        
        highlight_layout = QHBoxLayout()
        highlight_layout.addWidget(QLabel("Color de Resaltado por defecto:"))
        self.highlight_color_btn = QPushButton()
        self.highlight_color_btn.setMinimumSize(100, 40)
        self._update_highlight_color_preview(self.config.highlight_color)
        self.highlight_color_btn.clicked.connect(self._pick_highlight_color)
        highlight_layout.addWidget(self.highlight_color_btn)
        highlight_layout.addStretch()
        layout.addLayout(highlight_layout)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)
        
        self.tabs.addTab(tab, self.icon_manager.get_icon("pdf", 18), "PDF")

    def _toggle_watermark_controls(self, enabled):
        """Enable/disable watermark controls based on checkbox state."""
        self.watermark_text_input.setEnabled(enabled)
        self.watermark_opacity_slider.setEnabled(enabled)
        self.watermark_image_input.setEnabled(enabled)

    def _select_watermark_image(self):
        """Select watermark image file."""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen de Marca de Agua", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.watermark_image_input.setText(file_path)

    def _update_highlight_color_preview(self, color):
        """Update the highlight color button preview."""
        self._current_highlight_color = color
        self.highlight_color_btn.setStyleSheet(
            f"background-color: {color}; border: 2px solid white; border-radius: 4px;"
        )
        self.highlight_color_btn.setText(color)

    def _pick_highlight_color(self):
        """Open color picker for highlight color."""
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        
        current = QColor(self._current_highlight_color)
        color = QColorDialog.getColor(current, self, "Seleccionar Color de Resaltado")
        if color.isValid():
            self._update_highlight_color_preview(color.name())

    def _upload_signature(self):
        """Upload a signature image."""
        from PyQt6.QtWidgets import QFileDialog
        import shutil
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Firma", "", "Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            # Save to config/signatures/
            try:
                sig_dir = os.path.join(BASE_DIR, "media", "config", "signatures")
                os.makedirs(sig_dir, exist_ok=True)
                
                ext = os.path.splitext(file_path)[1]
                dest_path = os.path.join(sig_dir, f"personal_signature{ext}")
                
                shutil.copy2(file_path, dest_path)
                
                self.sig_path_input.setText(dest_path)
                self._load_signature_preview()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo guardar la firma: {e}")

    def _clear_signature(self):
        """Clear signature."""
        self.sig_path_input.clear()
        self.sig_preview.clear()
        self.sig_preview.setText("Sin Firma")

    def _load_signature_preview(self):
        """Load preview of signature."""
        path = self.sig_path_input.text()
        if path and os.path.exists(path):
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.sig_preview.setPixmap(pixmap.scaled(
                    180, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                ))
            else:
                self.sig_preview.setText("Error al cargar")
        else:
            self.sig_preview.setText("Sin Firma")

    def _populate_theme_combobox(self):
        """Populate theme combobox with grouped sections (Official / Unofficial)."""
        from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont as QGFont
        from PyQt6.QtCore import Qt
        
        # Get grouped themes
        grouped = ThemeManager.get_grouped_themes()
        
        # Create model for custom items
        model = QStandardItemModel()
        
        # Add official themes section
        if grouped['official']:
            # Section header - non-selectable
            header_official = QStandardItem("─── Themes Oficiales ───")
            header_official.setEnabled(False)
            header_official.setSelectable(False)
            font = QGFont()
            font.setBold(True)
            header_official.setFont(font)
            header_official.setData(Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
            model.appendRow(header_official)
            
            # Add official themes
            for theme_name in grouped['official']:
                item = QStandardItem(f"  {theme_name}")
                item.setData(theme_name, Qt.ItemDataRole.UserRole)  # Store actual theme name
                model.appendRow(item)
        
        # Add unofficial themes section
        if grouped['unofficial']:
            # Section header - non-selectable
            header_unofficial = QStandardItem("─── Themes No Oficiales ───")
            header_unofficial.setEnabled(False)
            header_unofficial.setSelectable(False)
            font = QGFont()
            font.setBold(True)
            header_unofficial.setFont(font)
            header_unofficial.setData(Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
            model.appendRow(header_unofficial)
            
            # Add unofficial themes
            for theme_name in grouped['unofficial']:
                item = QStandardItem(f"  {theme_name}")
                item.setData(theme_name, Qt.ItemDataRole.UserRole)  # Store actual theme name
                model.appendRow(item)
        
        self.combo_theme.setModel(model)

    def _select_initial_theme(self):
        """Select the current theme from config in the grouped combobox."""
        from PyQt6.QtCore import Qt
        target_theme = self.config.tema
        model = self.combo_theme.model()
        if not model:
            return
        
        for i in range(model.rowCount()):
            item = model.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == target_theme:
                self.combo_theme.setCurrentIndex(i)
                return
        
        # Fallback: try text match
        for i in range(model.rowCount()):
            item = model.item(i)
            if item and item.isEnabled() and target_theme in item.text():
                self.combo_theme.setCurrentIndex(i)
                return

    def _preview_theme(self, theme_name: str):
        """Preview theme when selection changes."""
        # Get actual theme name from UserRole if available (strips leading spaces)
        model = self.combo_theme.model()
        index = self.combo_theme.currentIndex()
        if model and index >= 0:
            item = model.item(index)
            if item:
                actual_name = item.data(Qt.ItemDataRole.UserRole)
                if actual_name:
                    theme_name = actual_name
        
        ThemeManager.apply_theme(self, theme_name)
    
    def _get_current_theme_name(self) -> str:
        """Get the actual theme name from the combobox (without leading spaces)."""
        from PyQt6.QtCore import Qt
        model = self.combo_theme.model()
        index = self.combo_theme.currentIndex()
        if model and index >= 0:
            item = model.item(index)
            if item:
                actual_name = item.data(Qt.ItemDataRole.UserRole)
                if actual_name:
                    return actual_name
        return self.combo_theme.currentText().strip()
    
    def _set_theme_by_name(self, theme_name: str):
        """Set the combobox selection to match the given theme name."""
        from PyQt6.QtCore import Qt
        model = self.combo_theme.model()
        if not model:
            return
        
        for i in range(model.rowCount()):
            item = model.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == theme_name:
                self.combo_theme.setCurrentIndex(i)
                return
        
        # Fallback: try text match
        for i in range(model.rowCount()):
            item = model.item(i)
            if item and theme_name in item.text():
                self.combo_theme.setCurrentIndex(i)
                return
    
    def _reset_defaults(self):
        """Reset to default values."""
        self._set_theme_by_name("Oscuro")
        self.combo_font.setCurrentText("Segoe UI")
        self.spin_size.setValue(14)
        self.combo_language.setCurrentText("es")
        self.combo_currency.setCurrentText("Bolivianos (Bs)")
        self.spin_iva.setValue(13.0)
        self.spin_validity.setValue(15)
        self.spin_delivery.setValue(7)
        
        # PDF defaults
        if hasattr(self, 'spin_margin_top'):
            self.spin_margin_top.setValue(40)
            self.spin_margin_bottom.setValue(40)
            self.spin_margin_left.setValue(40)
            self.spin_margin_right.setValue(40)
            self.watermark_check.setChecked(False)
            self.watermark_text_input.clear()
            self.watermark_opacity_slider.setValue(15)
            self.watermark_image_input.clear()
            self._update_highlight_color_preview('#FFFF00')
    
    def _save_config(self):
        """Save the configuration."""
        self.config.idioma = self.combo_language.currentText()
        self.config.tema = self._get_current_theme_name()
        self.config.fuente = self.combo_font.currentText()
        self.config.tamaño_fuente = self.spin_size.value()
        self.config.moneda = self.combo_currency.currentText()
        
        # Save User Profile
        self.config.prepared_by = self.prepared_by_input.text()
        self.config.signature_path = self.sig_path_input.text()
        
        try:
            self.config.iva_default = self.spin_iva.value()
            self.config.validez_default = self.spin_validity.value()
            self.config.delivery_default = self.spin_delivery.value()
        except AttributeError:
            pass
        
        # Save PDF settings
        if hasattr(self, 'spin_margin_top'):
            self.config.pdf_margin_top = self.spin_margin_top.value()
            self.config.pdf_margin_bottom = self.spin_margin_bottom.value()
            self.config.pdf_margin_left = self.spin_margin_left.value()
            self.config.pdf_margin_right = self.spin_margin_right.value()
            self.config.watermark_enabled = self.watermark_check.isChecked()
            self.config.watermark_text = self.watermark_text_input.text()
            self.config.watermark_opacity = self.watermark_opacity_slider.value()
            self.config.watermark_image_path = self.watermark_image_input.text()
            self.config.highlight_color = self._current_highlight_color
        
        self.config.save()
        self.config_updated.emit()
        QMessageBox.information(self, "Guardado", "Configuración guardada correctamente.")
        self.close()
