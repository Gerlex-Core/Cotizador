"""
Products Window - Dedicated window for managing quotation products and shipping.
Features product table editing, shipping options, and live preview.
"""

import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSplitter, QScrollArea,
    QCheckBox, QDoubleSpinBox, QComboBox, QSpinBox, QSizePolicy
)
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect

from .components.buttons.animated_button import AnimatedButton, PrimaryButton, DangerButton
from .components.tables.animated_table import QuotationTable
from .components.notification.toast_notification import ToastNotification
from .styles.theme_manager import ThemeManager
from .styles.icon_manager import IconManager
from ..logic.config.config_manager import ConfigManager


class ProductsWindow(QMainWindow):
    """
    Dedicated window for managing quotation products.
    Features:
    - Product table with add/edit/duplicate/delete
    - Shipping section with type and cost
    - Live preview of products
    - Auto-save on close
    """
    
    products_saved = pyqtSignal(dict)
    
    def __init__(self, products_data: dict = None, parent=None):
        super().__init__(parent)
        
        self.config = ConfigManager()
        self.icon_manager = IconManager.get_instance()
        self._products_data = products_data or {}
        self._is_modified = False
        
        # Setup preview timer BEFORE anything else that might trigger it
        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._update_preview)
        
        # Load units from JSON
        self._units_list = self._load_units()
        
        # Setup window
        self._setup_window()
        self._create_ui()
        self._load_data()
    
    def _load_units(self) -> list:
        """Load units from units.json file."""
        units_list = ["u", "c/u", "pqt", "kg", "g", "L", "m", "m²"]  # Default fallback
        try:
            # Find the units.json file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            units_path = os.path.join(base_dir, "media", "data", "units", "units.json")
            
            if os.path.exists(units_path):
                with open(units_path, 'r', encoding='utf-8') as f:
                    units_data = json.load(f)
                
                # Extract all unit abbreviations
                units_list = []
                for category, units in units_data.items():
                    if category != "Envio":  # Skip shipping units
                        for unit_name, unit_info in units.items():
                            abbrev = unit_info.get('abreviacion', '')
                            if abbrev and abbrev not in units_list:
                                units_list.append(abbrev)
                
                # Sort alphabetically for easier finding
                units_list.sort()
        except Exception as e:
            print(f"Error loading units: {e}")
        
        return units_list
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Gestión de Productos - Cotización")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        
        # Apply theme
        ThemeManager.apply_theme(self, self.config.tema)
        font_size = max(8, self.config.tamaño_fuente)
        self.setFont(QFont(self.config.fuente, font_size))
        
        # Update icon manager color
        icon_color = "#1D1D1F" if "Claro" in self.config.tema else "#FFFFFF"
        self.icon_manager.set_theme_color(icon_color)
    
    def _create_ui(self):
        """Create the main user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        self._create_header(main_layout)
        
        # Content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: rgba(255, 255, 255, 0.1);
                width: 2px;
            }
        """)
        
        # Left panel - Products table and shipping
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Preview
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set proportions (60% left, 40% right)
        splitter.setSizes([700, 500])
        
        main_layout.addWidget(splitter, 1)
        
        # Footer
        self._create_footer(main_layout)
        
        # Toast notification
        self.toast = ToastNotification(self)
    
    def _create_header(self, parent_layout):
        """Create header section."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(10, 132, 255, 0.3), stop:1 rgba(94, 92, 230, 0.3));
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setStyleSheet("""
            background: rgba(10, 132, 255, 0.4);
            border: 2px solid #0A84FF;
            border-radius: 12px;
        """)
        icon_label.setPixmap(self.icon_manager.get_pixmap("box", 28))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # Title and description
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        title = QLabel("Gestión de Productos")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        text_layout.addWidget(title)
        
        desc = QLabel("Agrega, edita y organiza los productos de tu cotización. Incluye envío si aplica.")
        desc.setStyleSheet("font-size: 13px; color: rgba(255, 255, 255, 0.7);")
        text_layout.addWidget(desc)
        
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        
        # Products count badge
        self.products_count_label = QLabel("0 productos")
        self.products_count_label.setStyleSheet("""
            background: rgba(52, 199, 89, 0.3);
            border: 1px solid #34C759;
            border-radius: 12px;
            padding: 6px 16px;
            font-weight: bold;
            color: #34C759;
        """)
        header_layout.addWidget(self.products_count_label)
        
        parent_layout.addWidget(header)
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with products table and shipping."""
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 8, 16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        toolbar_title = QLabel("Lista de Productos")
        toolbar_title.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        toolbar.addWidget(toolbar_title)
        toolbar.addStretch()
        
        btn_add = AnimatedButton("Agregar")
        btn_add.setIcon(self.icon_manager.get_icon("addItem", 18))
        btn_add.clicked.connect(self._add_product)
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
        
        # Products table
        self.table = QuotationTable()
        self.table.itemChanged.connect(self._on_table_changed)
        self.table.resolution_warning.connect(self._show_warning)
        layout.addWidget(self.table, 1)
        
        # Shipping section
        shipping_frame = QFrame()
        shipping_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(10, 132, 255, 0.15), stop:1 rgba(10, 132, 255, 0.05));
                border: 1px solid rgba(10, 132, 255, 0.3);
                border-radius: 12px;
            }
        """)
        shipping_layout = QHBoxLayout(shipping_frame)
        shipping_layout.setContentsMargins(16, 12, 16, 12)
        shipping_layout.setSpacing(16)
        
        # Shipping icon
        ship_icon = QLabel()
        ship_icon.setPixmap(self.icon_manager.get_pixmap("delivery", 28))
        shipping_layout.addWidget(ship_icon)
        
        # Enable checkbox
        self.enable_shipping_check = QCheckBox("Incluir Envío")
        self.enable_shipping_check.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                font-size: 14px;
                color: white;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid #0A84FF;
            }
            QCheckBox::indicator:checked {
                background: #0A84FF;
            }
        """)
        self.enable_shipping_check.stateChanged.connect(self._on_shipping_toggled)
        shipping_layout.addWidget(self.enable_shipping_check)
        
        # Shipping amount
        self.shipping_input = QDoubleSpinBox()
        self.shipping_input.setRange(0, 99999)
        self.shipping_input.setDecimals(2)
        self.shipping_input.setValue(0)
        self.shipping_input.setPrefix(f"{self.config.moneda} ")
        self.shipping_input.setMinimumHeight(40)
        self.shipping_input.setMinimumWidth(150)
        self.shipping_input.setEnabled(False)
        self.shipping_input.valueChanged.connect(self._trigger_preview)
        self.shipping_input.setStyleSheet("""
            QDoubleSpinBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                font-size: 14px;
            }
        """)
        shipping_layout.addWidget(self.shipping_input)
        
        # Shipping type
        self.shipping_type_combo = QComboBox()
        self.shipping_type_combo.addItems([
            "Gratis",
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
        self.shipping_type_combo.setMinimumHeight(40)
        self.shipping_type_combo.setEnabled(False)
        self.shipping_type_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                min-width: 180px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background: #2D2D30;
                color: white;
                selection-background-color: #0A84FF;
            }
        """)
        self.shipping_type_combo.currentTextChanged.connect(self._trigger_preview)
        shipping_layout.addWidget(self.shipping_type_combo)
        
        shipping_layout.addStretch()
        
        # Shipping total display
        self.shipping_display = QLabel("+ 0.00")
        self.shipping_display.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #0A84FF;
        """)
        shipping_layout.addWidget(self.shipping_display)
        
        layout.addWidget(shipping_frame)
        
        # Totals section
        totals_frame = QFrame()
        totals_frame.setStyleSheet("""
            QFrame {
                background: rgba(52, 199, 89, 0.1);
                border: 1px solid rgba(52, 199, 89, 0.3);
                border-radius: 12px;
            }
        """)
        totals_layout = QHBoxLayout(totals_frame)
        totals_layout.setContentsMargins(16, 12, 16, 12)
        
        totals_layout.addWidget(QLabel("Subtotal:"))
        self.subtotal_label = QLabel(f"0.00 {self.config.moneda}")
        self.subtotal_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        totals_layout.addWidget(self.subtotal_label)
        
        totals_layout.addStretch()
        
        totals_layout.addWidget(QLabel("Total:"))
        self.total_label = QLabel(f"0.00 {self.config.moneda}")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #34C759;")
        totals_layout.addWidget(self.total_label)
        
        layout.addWidget(totals_frame)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with live preview."""
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 16, 16, 16)
        
        # Preview header
        preview_header = QHBoxLayout()
        preview_title = QLabel("Vista Previa")
        preview_title.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        preview_header.addWidget(preview_title)
        preview_header.addStretch()
        
        btn_refresh = AnimatedButton("Actualizar")
        btn_refresh.setIcon(self.icon_manager.get_icon("reload", 16))
        btn_refresh.clicked.connect(self._update_preview)
        preview_header.addWidget(btn_refresh)
        
        layout.addLayout(preview_header)
        
        # Preview scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.preview_label.setStyleSheet("background: white; padding: 20px;")
        self.preview_label.setMinimumWidth(350)
        scroll.setWidget(self.preview_label)
        
        layout.addWidget(scroll, 1)
        
        return panel
    
    def _create_footer(self, parent_layout):
        """Create footer with action buttons."""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 12, 24, 12)
        
        # Summary
        self.summary_label = QLabel("Sin productos agregados")
        self.summary_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 13px;")
        footer_layout.addWidget(self.summary_label)
        
        footer_layout.addStretch()
        
        # Cancel button
        btn_cancel = AnimatedButton("Cancelar")
        btn_cancel.setMinimumWidth(120)
        btn_cancel.setMinimumHeight(42)
        btn_cancel.clicked.connect(self._on_cancel)
        footer_layout.addWidget(btn_cancel)
        
        # Save button
        btn_save = PrimaryButton("Guardar Productos")
        btn_save.setIcon(self.icon_manager.get_icon("save", 20))
        btn_save.setMinimumWidth(180)
        btn_save.setMinimumHeight(42)
        btn_save.clicked.connect(self._save_and_close)
        footer_layout.addWidget(btn_save)
        
        parent_layout.addWidget(footer)
    
    def _load_data(self):
        """Load existing products data into UI."""
        if not self._products_data:
            self._update_preview()
            return
        
        # Load products
        products = self._products_data.get('products', [])
        for prod in products:
            row = self._add_product_with_unit(
                description=prod.get('descripcion', ''),
                quantity=str(prod.get('cantidad', '')),
                unit=prod.get('unidad', ''),
                price=str(prod.get('precio_unitario', '')),
                amount=str(prod.get('importe', '')),
                image_path=prod.get('imagen', '')
            )
        
        # Load shipping
        shipping = self._products_data.get('shipping', {})
        if shipping.get('enabled', False):
            self.enable_shipping_check.setChecked(True)
            self.shipping_input.setValue(shipping.get('amount', 0))
            idx = self.shipping_type_combo.findText(shipping.get('type', 'Envío Local'))
            if idx >= 0:
                self.shipping_type_combo.setCurrentIndex(idx)
        
        self._update_counts()
        self._update_preview()
    
    def _add_product_with_unit(self, description='', quantity='', unit='', price='', amount='', image_path='') -> int:
        """Add a product row with a unit combobox."""
        row = self.table.addProduct(
            description=description,
            quantity=quantity,
            unit='',  # We'll use combobox instead
            price=price,
            amount=amount,
            image_path=image_path
        )
        
        # Create unit combobox for this row
        unit_combo = QComboBox()
        unit_combo.setEditable(True)  # Allow custom units
        unit_combo.addItems(self._units_list)
        unit_combo.setCurrentText(unit if unit else 'u')
        unit_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
                min-height: 30px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: #2D2D30;
                color: white;
                selection-background-color: #0A84FF;
            }
        """)
        unit_combo.currentTextChanged.connect(lambda: self._on_unit_changed())
        self.table.setCellWidget(row, 2, unit_combo)  # Column 2 is Unit
        
        return row
    
    def _on_unit_changed(self):
        """Handle unit combobox change."""
        self._mark_modified()
        self._trigger_preview()
    
    def _collect_data(self) -> dict:
        """Collect all data from UI."""
        # Get products from table
        products = []
        for row in range(self.table.rowCount()):
            prod = {}
            desc_item = self.table.item(row, 0)
            qty_item = self.table.item(row, 1)
            price_item = self.table.item(row, 3)
            amount_item = self.table.item(row, 4)
            
            prod['descripcion'] = desc_item.text() if desc_item else ''
            prod['cantidad'] = qty_item.text() if qty_item else ''
            
            # Get unit from combobox widget
            unit_widget = self.table.cellWidget(row, 2)
            if unit_widget and hasattr(unit_widget, 'currentText'):
                prod['unidad'] = unit_widget.currentText()
            else:
                unit_item = self.table.item(row, 2)
                prod['unidad'] = unit_item.text() if unit_item else ''
            
            prod['precio_unitario'] = price_item.text() if price_item else ''
            prod['importe'] = amount_item.text() if amount_item else ''
            
            # Get image if stored
            if desc_item and desc_item.data(Qt.ItemDataRole.UserRole):
                prod['imagen'] = desc_item.data(Qt.ItemDataRole.UserRole)
            
            products.append(prod)
        
        # Calculate subtotal
        subtotal = 0
        for prod in products:
            try:
                subtotal += float(prod.get('importe', 0) or 0)
            except ValueError:
                pass
        
        # Get shipping
        shipping = {
            'enabled': self.enable_shipping_check.isChecked(),
            'amount': self.shipping_input.value(),
            'type': self.shipping_type_combo.currentText()
        }
        
        # Calculate total
        total = subtotal
        if shipping['enabled']:
            total += shipping['amount']
        
        return {
            'products': products,
            'shipping': shipping,
            'subtotal': subtotal,
            'total': total
        }
    
    def _add_product(self):
        """Add a new product row."""
        self._add_product_with_unit()
        self._mark_modified()
        self._update_counts()
        self._trigger_preview()
    
    def _duplicate_product(self):
        """Duplicate selected product."""
        row = self.table.currentRow()
        if row >= 0:
            self.table.duplicateRow(row)
            self._mark_modified()
            self._update_counts()
            self._trigger_preview()
    
    def _remove_product(self):
        """Remove selected product."""
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
            self._mark_modified()
            self._update_counts()
            self._trigger_preview()
    
    def _clear_table(self):
        """Clear all products."""
        self.table.setRowCount(0)
        self._mark_modified()
        self._update_counts()
        self._trigger_preview()
    
    def _on_table_changed(self, item):
        """Handle table cell changes."""
        row = item.row()
        col = item.column()
        
        # Auto-calculate amount if quantity or price changed
        if col in [1, 3]:  # Quantity or Price
            try:
                qty_item = self.table.item(row, 1)
                price_item = self.table.item(row, 3)
                
                qty = float(qty_item.text()) if qty_item and qty_item.text() else 0
                price = float(price_item.text()) if price_item and price_item.text() else 0
                
                amount = qty * price
                amount_item = self.table.item(row, 4)
                if amount_item:
                    self.table.blockSignals(True)
                    amount_item.setText(f"{amount:.2f}")
                    self.table.blockSignals(False)
            except ValueError:
                pass
        
        self._mark_modified()
        self._trigger_preview()
    
    def _on_shipping_toggled(self, state):
        """Enable/disable shipping inputs."""
        enabled = state == Qt.CheckState.Checked.value
        self.shipping_input.setEnabled(enabled)
        self.shipping_type_combo.setEnabled(enabled)
        self._mark_modified()
        self._trigger_preview()
    
    def _trigger_preview(self):
        """Trigger preview update with delay."""
        self._preview_timer.start(300)
        self._update_counts()
    
    def _update_counts(self):
        """Update product count and totals."""
        count = self.table.rowCount()
        self.products_count_label.setText(f"{count} producto{'s' if count != 1 else ''}")
        
        # Calculate totals
        data = self._collect_data()
        subtotal = data['subtotal']
        total = data['total']
        shipping = data['shipping']
        
        self.subtotal_label.setText(f"{subtotal:.2f} {self.config.moneda}")
        self.total_label.setText(f"{total:.2f} {self.config.moneda}")
        
        if shipping['enabled']:
            self.shipping_display.setText(f"+ {shipping['amount']:.2f}")
        else:
            self.shipping_display.setText("+ 0.00")
        
        # Update summary
        if count == 0:
            self.summary_label.setText("Sin productos agregados")
        else:
            self.summary_label.setText(f"{count} productos • Subtotal: {subtotal:.2f} • Total: {total:.2f} {self.config.moneda}")
    
    def _update_preview(self):
        """Generate preview of products."""
        data = self._collect_data()
        products = data['products']
        shipping = data['shipping']
        
        # Create preview pixmap
        width = 400
        row_height = 40
        header_height = 50
        padding = 20
        
        # Calculate height
        height = header_height + padding * 2
        height += max(1, len(products)) * row_height
        if shipping['enabled']:
            height += row_height
        height += row_height  # Total row
        height += 40  # Extra padding
        
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#FFFFFF"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        y = padding
        
        # Header
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.setPen(QColor("#1D1D1F"))
        painter.drawText(padding, y + 20, "Listado de Productos")
        y += header_height
        
        # Table header
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.fillRect(padding, y, width - padding * 2, row_height - 5, QColor("#F0F0F0"))
        
        col_widths = [160, 50, 50, 70, 70]
        headers = ["Descripción", "Cant.", "Unid.", "P.Unit.", "Importe"]
        x = padding + 5
        for i, header in enumerate(headers):
            painter.drawText(x, y + 25, header)
            x += col_widths[i]
        y += row_height
        
        # Products
        painter.setFont(QFont("Arial", 10))
        for prod in products:
            x = padding + 5
            values = [
                prod.get('descripcion', '')[:20],
                str(prod.get('cantidad', '')),
                prod.get('unidad', ''),
                str(prod.get('precio_unitario', '')),
                str(prod.get('importe', ''))
            ]
            for i, val in enumerate(values):
                painter.drawText(x, y + 25, val)
                x += col_widths[i]
            y += row_height
            
            # Separator line
            painter.setPen(QPen(QColor("#E0E0E0"), 1))
            painter.drawLine(padding, y - 5, width - padding, y - 5)
            painter.setPen(QColor("#1D1D1F"))
        
        if not products:
            painter.setPen(QColor("#888888"))
            painter.drawText(padding + 5, y + 25, "Sin productos")
            y += row_height
        
        y += 10
        
        # Shipping row
        if shipping['enabled']:
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.setPen(QColor("#0A84FF"))
            painter.drawText(padding + 5, y + 20, f"Envío ({shipping['type']})")
            painter.drawText(width - padding - 70, y + 20, f"+ {shipping['amount']:.2f}")
            y += row_height
        
        # Total
        painter.fillRect(padding, y, width - padding * 2, row_height, QColor("#34C759").lighter(170))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.setPen(QColor("#1D1D1F"))
        painter.drawText(padding + 5, y + 25, "TOTAL")
        painter.drawText(width - padding - 100, y + 25, f"{data['total']:.2f} {self.config.moneda}")
        
        painter.end()
        
        self.preview_label.setPixmap(pixmap)
    
    def _mark_modified(self):
        """Mark data as modified."""
        self._is_modified = True
    
    def _show_warning(self, title, message):
        """Show warning toast."""
        self.toast.show_toast(title, message, self, duration=5000, type="warning")
    
    def _save_and_close(self):
        """Save data and close window."""
        data = self._collect_data()
        self.products_saved.emit(data)
        self._is_modified = False
        self.close()
    
    def _on_cancel(self):
        """Handle cancel button."""
        self.close()
    
    def closeEvent(self, event):
        """Handle window close - auto-save if modified."""
        if self._is_modified:
            data = self._collect_data()
            self.products_saved.emit(data)
        event.accept()
    
    def get_products_data(self) -> dict:
        """Get current products data."""
        return self._collect_data()
