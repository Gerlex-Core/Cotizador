"""
Terms Window - Dedicated interface for managing quotation terms and conditions.
Features live preview and spacious editors.
"""

import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QTextEdit, QLabel, QCheckBox, QSplitter, QFrame,
    QTabWidget, QScrollArea, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtGui import QIcon, QAction, QPainter, QColor, QFont, QPen, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect, QSize

from .components.buttons.animated_button import AnimatedButton, PrimaryButton
from .styles.theme_manager import ThemeManager
from .styles.icon_manager import IconManager
from ..logic.config.config_manager import ConfigManager
from .components.widgets.preview_widget import PreviewWidget
from .components.editor.rich_text_editor import RichTextEditor

class TermsWindow(QMainWindow):
    """Window for managing extended terms and conditions with granular options."""
    
    terms_saved = pyqtSignal(dict)
    
    def __init__(self, current_data: dict = None, parent=None):
        super().__init__(parent)
        self.current_data = current_data or {}
        
        self.icon_manager = IconManager.get_instance()
        self.setWindowTitle("Términos y Condiciones")
        self.setWindowIcon(self.icon_manager.get_icon("termsAndCondition"))
        self.setGeometry(150, 150, 1100, 700)
        
        # Apply current theme
        config = ConfigManager()
        ThemeManager.apply_theme(self, config.tema)
        
        # Load payment options
        self.payment_options = self._load_payment_options()
        
        # Auto-update preview timer
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._update_preview)
        
        self._create_ui()
        self._load_data()

    def _load_payment_options(self):
        """Load payment options from JSON."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            path = os.path.join(base_dir, "media", "data", "pay", "pagos.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading payment options: {e}")
        return {"tipos_pago": ["Efectivo", "Transferencia"], "formas_pago": ["Contra entrega"]}

    def _create_ui(self):
        """Create the user interface with text editors inline in each tab."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main Horizontal Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)
        
        # --- Left Panel: Navigation (Tabs) with inline editors ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(self.icon_manager.get_pixmap("termsAndCondition", 24))
        header.addWidget(icon)
        title = QLabel("Términos y Condiciones")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        left_layout.addLayout(header)
        
        # Tabs for different sections - each tab has its editor inline
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: none; 
                margin-top: 5px;
            }
            QTabBar::tab {
                background: rgba(255,255,255,0.05);
                padding: 10px 20px;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px 6px 0 0;
                margin-right: 3px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: rgba(10, 132, 255, 0.4);
                border-color: #0A84FF;
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(255,255,255,0.1);
            }
        """)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.currentChanged.connect(self._trigger_preview)
        
        # Create tabs with editors inline
        # 1. Installation Tab
        self.install_tab = self._create_install_tab()
        self.tabs.addTab(self.install_tab['widget'], "Instalación")
        
        # 2. Warranty Tab (5 subsections)
        self.warranty_tab = self._create_warranty_tab()
        self.tabs.addTab(self.warranty_tab['widget'], "Garantía")
        
        # 3. Payment Tab
        self.payment_tab = self._create_payment_tab()
        self.tabs.addTab(self.payment_tab['widget'], "Pagos")
        
        # 4. General Tab
        self.general_tab = self._create_general_tab()
        self.tabs.addTab(self.general_tab['widget'], "Generales")
        
        # 5. Contract Acceptance Tab
        self.acceptance_tab = self._create_acceptance_tab()
        self.tabs.addTab(self.acceptance_tab['widget'], "Aceptación")
        
        left_layout.addWidget(self.tabs, 1)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = AnimatedButton("Cancelar")
        btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = PrimaryButton("Guardar")
        btn_save.setIcon(self.icon_manager.get_icon("save", 18))
        btn_save.clicked.connect(self._save_and_close)
        btn_layout.addWidget(btn_save)
        left_layout.addLayout(btn_layout)
        
        splitter.addWidget(left_panel)
        
        # --- Right Panel: Preview Only ---
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        
        preview_label = QLabel("Vista Previa")
        preview_label.setStyleSheet("font-weight: bold; padding: 5px;")
        preview_layout.addWidget(preview_label)
        
        self.preview_widget = PreviewWidget()
        preview_layout.addWidget(self.preview_widget, 1)
        
        splitter.addWidget(preview_container)
        splitter.setSizes([650, 400])
        
        layout.addWidget(splitter)

    # --- TAB CREATORS ---
    
    def _create_install_tab(self):
        """Create installation terms tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Controls
        header = QHBoxLayout()
        lbl_title = QLabel("Términos de Instalación")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(lbl_title)
        header.addStretch()
        
        chk_enable = QCheckBox("Incluir en PDF")
        chk_enable.stateChanged.connect(self._trigger_preview)
        header.addWidget(chk_enable)
        layout.addLayout(header)
        
        layout.addWidget(QLabel("Detalles sobre la instalación, requisitos previos, etc."))
        
        # Editor directly in tab
        editor = self._create_editor()
        editor.setMinimumHeight(180)
        layout.addWidget(editor, 1)
        
        return {'widget': widget, 'editor': editor, 'check': chk_enable}

    def _create_warranty_tab(self):
        """Create warranty terms tab with 5 specific subsections."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header with Enable
        header = QHBoxLayout()
        lbl_title = QLabel("Políticas de Garantía")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(lbl_title)
        header.addStretch()
        chk_enable = QCheckBox("Incluir en PDF")
        chk_enable.stateChanged.connect(self._trigger_preview)
        header.addWidget(chk_enable)
        main_layout.addLayout(header)
        
        # Duration row
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duración:"))
        duration_input = QLineEdit()
        duration_input.setPlaceholderText("Ej: 12 meses")
        duration_input.setMaximumWidth(200)
        duration_input.textChanged.connect(self._trigger_preview)
        duration_layout.addWidget(duration_input)
        duration_layout.addStretch()
        main_layout.addLayout(duration_layout)
        
        # Scroll area for the 5 sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(15)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Section 1: Garantía (General warranty info)
        layout.addWidget(QLabel("<b>1. Garantía</b>"))
        editor_garantia = self._create_editor()
        editor_garantia.setMinimumHeight(150)
        editor_garantia.setPlaceholderText("Descripción general de la garantía...")
        layout.addWidget(editor_garantia)
        
        # Section 2: Lo que cubre
        layout.addWidget(QLabel("<b>2. Lo que cubre</b>"))
        editor_covers = self._create_editor()
        editor_covers.setMinimumHeight(150)
        editor_covers.setPlaceholderText("Lista de lo que cubre la garantía...")
        layout.addWidget(editor_covers)
        
        # Section 3: Lo que no cubre
        layout.addWidget(QLabel("<b>3. Lo que no cubre</b>"))
        editor_excludes = self._create_editor()
        editor_excludes.setMinimumHeight(150)
        editor_excludes.setPlaceholderText("Lista de lo que NO cubre la garantía...")
        layout.addWidget(editor_excludes)
        
        # Section 4: Advertencia
        layout.addWidget(QLabel("<b>4. Advertencia</b>"))
        editor_warning = self._create_editor()
        editor_warning.setMinimumHeight(120)
        editor_warning.setPlaceholderText("Advertencias importantes sobre la garantía...")
        layout.addWidget(editor_warning)
        
        # Section 5: Verificación de la garantía
        layout.addWidget(QLabel("<b>5. Verificación de la garantía</b>"))
        editor_verification = self._create_editor()
        editor_verification.setMinimumHeight(120)
        editor_verification.setPlaceholderText("Cómo verificar y hacer válida la garantía...")
        layout.addWidget(editor_verification)
        
        layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)
        
        return {
            'widget': widget, 
            'check': chk_enable,
            'duration': duration_input,
            'garantia': editor_garantia,
            'covers': editor_covers,
            'excludes': editor_excludes,
            'warning': editor_warning,
            'verification': editor_verification
        }
    
    def _create_acceptance_tab(self):
        """Create contract acceptance tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with Enable
        header = QHBoxLayout()
        lbl_title = QLabel("Aceptación de Contrato")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(lbl_title)
        header.addStretch()
        chk_enable = QCheckBox("Incluir en PDF")
        chk_enable.setChecked(True)
        chk_enable.stateChanged.connect(self._trigger_preview)
        header.addWidget(chk_enable)
        layout.addLayout(header)
        
        info = QLabel("Este texto aparecerá al final del PDF, antes de las firmas.")
        info.setStyleSheet("color: rgba(255,255,255,0.6); font-style: italic;")
        layout.addWidget(info)
        
        # Editor for acceptance text
        editor = self._create_editor()
        editor.setMinimumHeight(200)
        editor.setPlaceholderText(
            "Escriba los términos de aceptación del contrato...\n\n"
            "Ejemplo:\n"
            "Al firmar este documento, el cliente acepta todos los términos "
            "y condiciones establecidos en esta cotización, incluyendo precios, "
            "plazos de entrega y políticas de garantía."
        )
        layout.addWidget(editor, 1)
        
        return {
            'widget': widget, 
            'editor': editor, 
            'check': chk_enable
        }

    def _create_payment_tab(self):
        """Create payment terms tab with specific fields."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header = QHBoxLayout()
        lbl_title = QLabel("Condiciones de Pago")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(lbl_title)
        header.addStretch()
        chk_enable = QCheckBox("Incluir en PDF")
        chk_enable.stateChanged.connect(self._trigger_preview)
        header.addWidget(chk_enable)
        layout.addLayout(header)
        
        # Fields
        form_layout = QGridLayout()
        form_layout.setContentsMargins(0, 0, 0, 10)
        form_layout.setSpacing(10)
        
        form_layout.addWidget(QLabel("Método de Pago:"), 0, 0)
        method_combo = QComboBox()
        method_combo.addItems(self.payment_options.get("tipos_pago", []))
        method_combo.setEditable(True)
        method_combo.currentTextChanged.connect(self._trigger_preview)
        form_layout.addWidget(method_combo, 0, 1)
        
        form_layout.addWidget(QLabel("Condición de Pago:"), 1, 0)
        type_combo = QComboBox()
        type_combo.addItems(self.payment_options.get("formas_pago", []))
        type_combo.setEditable(True)
        type_combo.currentTextChanged.connect(self._trigger_preview)
        form_layout.addWidget(type_combo, 1, 1)
        
        layout.addLayout(form_layout)
        
        layout.addWidget(QLabel("Detalles adicionales de pago:"))
        
        # Editor directly in tab
        editor = self._create_editor()
        editor.setMinimumHeight(180)
        layout.addWidget(editor, 1)
        
        return {
            'widget': widget, 'editor': editor, 'check': chk_enable,
            'method': method_combo, 'type': type_combo
        }

    def _create_general_tab(self):
        """Create general terms tab with specific fields."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header = QHBoxLayout()
        lbl_title = QLabel("Términos Generales")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(lbl_title)
        header.addStretch()
        chk_enable = QCheckBox("Incluir en PDF")
        chk_enable.stateChanged.connect(self._trigger_preview)
        header.addWidget(chk_enable)
        layout.addLayout(header)
        
        # Fields
        form_layout = QGridLayout()
        form_layout.setContentsMargins(0, 0, 0, 10)
        form_layout.setSpacing(10)
        
        form_layout.addWidget(QLabel("Validez de la oferta (días):"), 0, 0)
        validity_spin = QSpinBox()
        validity_spin.setRange(1, 365)
        validity_spin.setValue(15)
        validity_spin.valueChanged.connect(self._trigger_preview)
        form_layout.addWidget(validity_spin, 0, 1)
        
        form_layout.addWidget(QLabel("Tiempo de entrega estimado (días):"), 1, 0)
        delivery_spin = QSpinBox()
        delivery_spin.setRange(0, 365)
        delivery_spin.setValue(7)
        delivery_spin.valueChanged.connect(self._trigger_preview)
        form_layout.addWidget(delivery_spin, 1, 1)
        
        layout.addLayout(form_layout)
        
        layout.addWidget(QLabel("Términos legales y generales del servicio:"))
        
        # Editor directly in tab
        editor = self._create_editor()
        editor.setMinimumHeight(180)
        layout.addWidget(editor, 1)
        
        return {
            'widget': widget, 'editor': editor, 'check': chk_enable,
            'validity': validity_spin, 'delivery': delivery_spin
        }

    def _create_editor(self):
        """Helper to create styled rich text editor."""
        editor = RichTextEditor(self)
        # Apply current theme from config
        config = ConfigManager()
        editor.apply_theme(config.tema)
        editor.textChanged.connect(self._trigger_preview)
        return editor

    def _trigger_preview(self):
        """Trigger preview update with a small delay."""
        self.preview_timer.start(500)

    def _load_data(self):
        """Load data into editors."""
        d = self.current_data
        
        # Install
        self.install_tab['editor'].setHtml(d.get('installation_terms', ''))
        self.install_tab['check'].setChecked(d.get('show_installation', False))
        
        # Warranty (5 sections)
        self.warranty_tab['check'].setChecked(d.get('show_warranty', False))
        self.warranty_tab['duration'].setText(str(d.get('warranty_duration', '')))
        # Load new warranty fields - with legacy fallback
        legacy_warranty = d.get('warranty_terms', '')
        self.warranty_tab['garantia'].setHtml(d.get('warranty_garantia', legacy_warranty))
        self.warranty_tab['covers'].setHtml(d.get('warranty_covers', ''))
        self.warranty_tab['excludes'].setHtml(d.get('warranty_excludes', ''))
        self.warranty_tab['warning'].setHtml(d.get('warranty_warning', ''))
        self.warranty_tab['verification'].setHtml(d.get('warranty_verification', ''))
        
        # Payment
        self.payment_tab['editor'].setHtml(d.get('payment_terms', ''))
        self.payment_tab['check'].setChecked(d.get('show_payment', False))
        self.payment_tab['method'].setCurrentText(str(d.get('payment_method', '')))
        self.payment_tab['type'].setCurrentText(str(d.get('payment_type', '')))
        
        # General
        self.general_tab['editor'].setHtml(d.get('general_terms', ''))
        self.general_tab['check'].setChecked(d.get('show_general', False))
        self.general_tab['validity'].setValue(int(d.get('validez_dias', 15)))
        self.general_tab['delivery'].setValue(int(d.get('estimated_days', 7)))
        
        # Acceptance
        self.acceptance_tab['editor'].setHtml(d.get('acceptance_terms', ''))
        self.acceptance_tab['check'].setChecked(d.get('show_acceptance', False))
        
        self._update_preview()

    def _collect_data(self):
        """Collect data from all editors."""
        return {
            # Install
            'installation_terms': self.install_tab['editor'].toHtml(),
            'show_installation': self.install_tab['check'].isChecked(),
            
            # Warranty (5 sections)
            'show_warranty': self.warranty_tab['check'].isChecked(),
            'warranty_duration': self.warranty_tab['duration'].text(),
            'warranty_garantia': self.warranty_tab['garantia'].toHtml(),
            'warranty_covers': self.warranty_tab['covers'].toHtml(),
            'warranty_excludes': self.warranty_tab['excludes'].toHtml(),
            'warranty_warning': self.warranty_tab['warning'].toHtml(),
            'warranty_verification': self.warranty_tab['verification'].toHtml(),
            # Legacy compatibility field
            'warranty_terms': self.warranty_tab['garantia'].toHtml(),
            
            # Payment
            'payment_terms': self.payment_tab['editor'].toHtml(),
            'show_payment': self.payment_tab['check'].isChecked(),
            'payment_method': self.payment_tab['method'].currentText(),
            'payment_type': self.payment_tab['type'].currentText(),
            
            # General
            'general_terms': self.general_tab['editor'].toHtml(),
            'show_general': self.general_tab['check'].isChecked(),
            'validez_dias': self.general_tab['validity'].value(),
            'estimated_days': self.general_tab['delivery'].value(),
            
            # Acceptance
            'acceptance_terms': self.acceptance_tab['editor'].toHtml(),
            'show_acceptance': self.acceptance_tab['check'].isChecked(),
        }


    def _update_preview(self):
        """Generate and update the preview using QPainter."""
        data = self._collect_data()
        current_index = self.tabs.currentIndex()

        # Prepare pagination simulation
        pages = []
        
        # A4 Size
        width, height = 595, 842 
        margin_x = 40
        margin_y = 50
        content_width = width - 2*margin_x
        content_height = height - 2*margin_y
        
        current_y = 0 # Relative to page content start
        
        # Create first page
        current_pixmap = QPixmap(width, height)
        current_pixmap.fill(Qt.GlobalColor.white)
        current_painter = QPainter(current_pixmap)
        current_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        def new_page():
            nonlocal current_pixmap, current_painter, current_y
            current_painter.end()
            pages.append(current_pixmap)
            
            current_pixmap = QPixmap(width, height)
            current_pixmap.fill(Qt.GlobalColor.white)
            current_painter = QPainter(current_pixmap)
            current_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            current_y = 0
            
        try:
            # === DRAW HEADER ===
            current_painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            current_painter.setPen(QColor(51, 51, 51))
            
            title = ""
            if current_index == 0: title = "Términos de Instalación"
            elif current_index == 1: title = "Políticas de Garantía"
            elif current_index == 2: title = "Condiciones de Pago"
            elif current_index == 3: title = "Términos Generales"
            elif current_index == 4: title = "Aceptación de Contrato"
            
            current_painter.drawText(margin_x, margin_y + current_y + 20, title)
            current_y += 40
            
            # Separator
            current_painter.setPen(QPen(QColor(200, 200, 200), 1))
            current_painter.drawLine(margin_x, margin_y + current_y, width - margin_x, margin_y + current_y)
            current_y += 20
            
            # Check enabled
            is_enabled = True
            if current_index == 0: is_enabled = data['show_installation']
            elif current_index == 1: is_enabled = data['show_warranty']
            elif current_index == 2: is_enabled = data['show_payment']
            elif current_index == 3: is_enabled = data['show_general']
            elif current_index == 4: is_enabled = data['show_acceptance']
            
            if not is_enabled:
                current_painter.save()
                current_painter.translate(width/2, height/2)
                current_painter.rotate(45)
                current_painter.setFont(QFont("Arial", 40, QFont.Weight.Bold))
                current_painter.setPen(QColor(255, 0, 0, 60))
                rect = QRect(-200, -50, 400, 100)
                current_painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "NO INCLUIDO")
                current_painter.restore()
            else:
                # === DRAW KEY FIELDS ===
                current_painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                current_painter.setPen(QColor(80, 80, 80))
                
                if current_index == 1: # Warranty
                    current_painter.drawText(margin_x, margin_y + current_y + 10, f"Duración: {data['warranty_duration']}")
                    current_y += 30
                elif current_index == 2: # Payment
                    current_painter.drawText(margin_x, margin_y + current_y + 10, f"Método: {data['payment_method']}")
                    current_y += 20
                    current_painter.drawText(margin_x, margin_y + current_y + 10, f"Condición: {data['payment_type']}")
                    current_y += 30
                elif current_index == 3: # General
                    current_painter.drawText(margin_x, margin_y + current_y + 10, f"Validez de Oferta: {data['validez_dias']} días")
                    current_y += 20
                    current_painter.drawText(margin_x, margin_y + current_y + 10, f"Tiempo de Entrega: {data['estimated_days']} días")
                    current_y += 30
                
                # === DRAW CONTENT HTML ===
                from PyQt6.QtGui import QTextDocument
                doc = QTextDocument()
                doc.setDefaultFont(QFont("Arial", 10))
                
                # Sanitize content for preview visibility (we want Black text on White paper)
                # Since we are using RAW html (likely white text if dark mode), we must force black for preview
                
                content_html_raw = ""
                if current_index == 0: content_html_raw = data['installation_terms']
                elif current_index == 1:
                    # Multi-section warranty
                    parts = []
                    if data.get('warranty_garantia'): parts.append(f"<b>1. Garantía:</b><br>{data['warranty_garantia']}")
                    if data.get('warranty_covers'): parts.append(f"<b>2. Cubre:</b><br>{data['warranty_covers']}")
                    if data.get('warranty_excludes'): parts.append(f"<b>3. No Cubre:</b><br>{data['warranty_excludes']}")
                    if data.get('warranty_warning'): parts.append(f"<b>4. Advertencia:</b><br>{data['warranty_warning']}")
                    if data.get('warranty_verification'): parts.append(f"<b>5. Verificación:</b><br>{data['warranty_verification']}")
                    content_html_raw = "<br><br>".join(parts)
                elif current_index == 2: content_html_raw = data['payment_terms']
                elif current_index == 3: content_html_raw = data['general_terms']
                elif current_index == 4: 
                    # Acceptance content + Signature space
                    content_html_raw = data['acceptance_terms']
                    content_html_raw += "<br><br><br><br>___________________________<br>Firma de Aceptación"
                
                # Sanitize for preview (force black text)
                clean_html = RichTextEditor.sanitize_for_pdf(content_html_raw)
                doc.setHtml(clean_html)
                doc.setTextWidth(content_width)
                
                # Pagination loop
                # Since we can't easily split QTextDocument across pages with full layout info,
                # we will use a clipping approach or improved flow? 
                # Basic approach: Render full doc, then slice it? No, text scaling issues.
                # Since we want to preview simply, let's assume if it fits we draw. 
                # If it's huge, we should probably just render it clippingly on multipages.
                
                full_height = doc.size().height()
                
                if current_y + full_height < content_height:
                    # Fits on one page
                    current_painter.save()
                    current_painter.translate(margin_x, margin_y + current_y)
                    doc.drawContents(current_painter)
                    current_painter.restore()
                else:
                    # Needs pagination
                    # Draw what fits on page 1
                    available_h = content_height - current_y
                    
                    current_painter.save()
                    current_painter.translate(margin_x, margin_y + current_y)
                    # Clip rect?
                    current_painter.setClipRect(QRect(0, 0, int(content_width), int(available_h)))
                    doc.drawContents(current_painter)
                    current_painter.restore()
                    
                    drawn_h = available_h
                    new_page()
                    
                    # Draw remaining pages
                    while drawn_h < full_height:
                        current_painter.save()
                        # Move doc up to show next chunk
                        current_painter.translate(margin_x, margin_y - drawn_h) 
                        # Clip to page content
                        # Since we translated up, we clip visible area:
                        # Visible area in local coords is (0, drawn_h) to (w, drawn_h + content_height)
                        # But simpler: just draw and clip on painter?
                        # Using painter clip seems safest.
                        current_painter.setClipRect(QRect(0, int(drawn_h), int(content_width), int(content_height)))
                        doc.drawContents(current_painter)
                        current_painter.restore()
                        
                        drawn_h += content_height
                        if drawn_h < full_height:
                            new_page()

        finally:
            current_painter.end()
            pages.append(current_pixmap)
            
        self.preview_widget.set_pages(pages)

    def _save_and_close(self):
        """Save changes and close."""
        self.terms_saved.emit(self._collect_data())
        self.close()
