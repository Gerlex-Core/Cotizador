"""
Reorderable Blocks Component - Drag and drop blocks for quotation observations.
Professional, APA-style formatting without emojis.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QFileDialog, QFrame, QSizePolicy, QTextEdit,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QSpinBox
)
from PyQt6.QtGui import (
    QPixmap, QDragEnterEvent, QDropEvent, QPainter, QColor, 
    QFont, QDrag, QMouseEvent
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint, QByteArray
import json
from src.views.components.editor.rich_text_editor import RichTextEditor


class DraggableBlock(QFrame):
    """Base class for draggable blocks with move and delete controls."""
    
    removed = pyqtSignal(object)
    moved_up = pyqtSignal(object)
    moved_down = pyqtSignal(object)
    content_changed = pyqtSignal()
    
    BLOCK_TYPE = "base"
    BLOCK_TITLE = "Bloque"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._order = 0
        self._setup_base_ui()
    
    def _setup_base_ui(self):
        """Setup base UI with header and controls."""
        self.setFrameShape(QFrame.Shape.Box)
        self.setStyleSheet("""
            DraggableBlock, TitleBlock, NoteBlock, ProductMatrixBlock, 
            ImageBlock, SeparatorBlock {
                background-color: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                margin: 4px;
            }
            DraggableBlock:hover, TitleBlock:hover, NoteBlock:hover, 
            ProductMatrixBlock:hover, ImageBlock:hover, SeparatorBlock:hover {
                border-color: #0A84FF;
                background-color: rgba(10, 132, 255, 0.08);
            }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 8, 12, 12)
        self.main_layout.setSpacing(8)
        
        # Header with title and controls
        header = QHBoxLayout()
        header.setSpacing(8)
        
        # Order indicator
        self.order_label = QLabel("1")
        self.order_label.setStyleSheet("""
            background-color: rgba(10, 132, 255, 0.3);
            color: white;
            font-weight: bold;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
        """)
        self.order_label.setFixedWidth(28)
        self.order_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(self.order_label)
        
        # Block type label
        self.type_label = QLabel(self.BLOCK_TITLE)
        self.type_label.setStyleSheet("font-weight: bold; color: rgba(255,255,255,0.8);")
        header.addWidget(self.type_label)
        
        header.addStretch()
        
        # Control buttons
        btn_style = """
            QPushButton {
                background-color: rgba(255,255,255,0.1);
                border: none;
                border-radius: 4px;
                color: white;
                padding: 4px 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.2);
            }
        """
        
        btn_up = QPushButton("▲")
        btn_up.setFixedSize(28, 28)
        btn_up.setStyleSheet(btn_style)
        btn_up.setToolTip("Mover arriba")
        btn_up.clicked.connect(lambda: self.moved_up.emit(self))
        header.addWidget(btn_up)
        
        btn_down = QPushButton("▼")
        btn_down.setFixedSize(28, 28)
        btn_down.setStyleSheet(btn_style)
        btn_down.setToolTip("Mover abajo")
        btn_down.clicked.connect(lambda: self.moved_down.emit(self))
        header.addWidget(btn_down)
        
        btn_delete = QPushButton("✕")
        btn_delete.setFixedSize(28, 28)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 69, 58, 0.3);
                border: none;
                border-radius: 4px;
                color: white;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 69, 58, 0.6);
            }
        """)
        btn_delete.setToolTip("Eliminar")
        btn_delete.clicked.connect(lambda: self.removed.emit(self))
        header.addWidget(btn_delete)
        
        self.main_layout.addLayout(header)
        
        # Content area (to be filled by subclasses)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.main_layout.addWidget(self.content_widget)
    
    def set_order(self, order: int):
        """Set the display order number."""
        self._order = order
        self.order_label.setText(str(order))
    
    def get_order(self) -> int:
        """Get the current order."""
        return self._order
    
    def get_data(self) -> dict:
        """Get block data for saving. Override in subclasses."""
        return {"type": self.BLOCK_TYPE, "order": self._order}
    
    def load_data(self, data: dict):
        """Load block data. Override in subclasses."""
        self._order = data.get("order", 0)


class TitleBlock(DraggableBlock):
    """Block for section titles/headings."""
    
    BLOCK_TYPE = "title"
    BLOCK_TITLE = "Titulo"
    
    def __init__(self, parent=None):
        self.styles = self._load_styles()  # Load styles BEFORE super().__init__ calls _setup_content
        super().__init__(parent)
        self._setup_content()
    
    def _load_styles(self):
        try:
            import os
            import json
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "logic", "config", "title_styles.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("styles", [])
        except: pass
        return []
    
    def _setup_content(self):
        """Setup title input."""
        # Title level selector
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Nivel:"))
        
        self.level_combo = QComboBox()
        self.level_combo.addItems(["Titulo (Nueva Pagina)", "Subtitulo", "Seccion Normal"])
        self.level_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
            }
        """)
        self.level_combo.currentIndexChanged.connect(self._on_level_changed)
        level_layout.addWidget(self.level_combo)
        
        # Style Selector (Hidden by default unless Title/Subtitle)
        self.style_label = QLabel("Estilo:")
        self.style_combo = QComboBox()
        self.style_combo.addItem("Predeterminado")
        for style in self.styles:
            self.style_combo.addItem(style["name"])
        
        self.style_combo.setStyleSheet(self.level_combo.styleSheet())
        self.style_combo.currentIndexChanged.connect(lambda: self.content_changed.emit())
        
        level_layout.addWidget(self.style_label)
        level_layout.addWidget(self.style_combo)
        
        # Alignment
        self.align_label = QLabel("Alineación:")
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Izquierda", "Centro", "Derecha"])
        self.align_combo.setStyleSheet(self.style_combo.styleSheet())
        self.align_combo.currentIndexChanged.connect(lambda: self.content_changed.emit())
        level_layout.addWidget(self.align_label)
        level_layout.addWidget(self.align_combo)

        level_layout.addStretch()
        
        self.content_layout.addLayout(level_layout)
        
        # Title text input - created once here, not in _on_level_changed
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Escriba el titulo aqui...")
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
        self.title_input.textChanged.connect(lambda: self.content_changed.emit())
        self.content_layout.addWidget(self.title_input)
        
        # Initial state
        self._on_level_changed(0)
        
    def _on_level_changed(self, index):
        """Show/Hide style selector based on level"""
        # 0=Title(NewPage), 1=Subtitle, 2=Section
        # Only toggle visibility of style options, don't create new widgets
        self.content_changed.emit()
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["title"] = self.title_input.text()
        data["level"] = self.level_combo.currentIndex()
        data["style_index"] = self.style_combo.currentIndex()
        data["alignment"] = self.align_combo.currentIndex()
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        self.title_input.setText(data.get("title", ""))
        self.level_combo.setCurrentIndex(data.get("level", 0))
        self.style_combo.setCurrentIndex(data.get("style_index", 0))
        self.align_combo.setCurrentIndex(data.get("alignment", 0))


class NoteBlock(DraggableBlock):
    """Block for text notes and observations."""
    
    BLOCK_TYPE = "note"
    BLOCK_TITLE = "Nota"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_content()
    
    def _setup_content(self):
        """Setup text editor."""
        from src.logic.config.config_manager import ConfigManager
        
        self.text_edit = RichTextEditor(placeholder_text="Escriba su nota u observacion aqui...")
        self.text_edit.setMinimumHeight(150)
        self.text_edit.setMaximumHeight(300)
        
        # Apply current theme
        config = ConfigManager()
        self.text_edit.apply_theme(config.tema)
        
        self.text_edit.textChanged.connect(lambda: self.content_changed.emit())
        self.content_layout.addWidget(self.text_edit)

        # Alignment Control
        align_layout = QHBoxLayout()
        align_layout.addWidget(QLabel("Alineación del Bloque:"))
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Izquierda", "Centro", "Derecha", "Justificado"])
        self.align_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
            }
        """)
        self.align_combo.currentIndexChanged.connect(lambda: self.content_changed.emit())
        align_layout.addWidget(self.align_combo)
        align_layout.addStretch()
        self.content_layout.addLayout(align_layout)
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["content"] = self.text_edit.toExportHtml()
        data["alignment"] = self.align_combo.currentIndex()
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        self.text_edit.setHtml(data.get("content", ""))
        self.align_combo.setCurrentIndex(data.get("alignment", 0))


class ProductMatrixBlock(DraggableBlock):
    """Block for product details matrix with images."""
    
    BLOCK_TYPE = "product_matrix"
    BLOCK_TITLE = "Matriz de Productos"
    STANDARD_IMAGE_SIZE = (300, 300)  # Recommended image dimensions in pixels
    
    # Signal to emit image resolution warnings (title, message)
    image_warning = pyqtSignal(str, str)
    
    def __init__(self, products: list = None, parent=None):
        self._products = products or []
        super().__init__(parent)
        self._setup_content()
    
    def _setup_content(self):
        """Setup product matrix table with improved sizing."""
        # Info and Select All row
        info_row = QHBoxLayout()
        info = QLabel("Seleccione los productos a incluir con detalles adicionales:")
        info.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 11px;")
        info_row.addWidget(info)
        
        # Image size standard info
        size_info = QLabel(f"📷 Tamaño recomendado: {self.STANDARD_IMAGE_SIZE[0]}x{self.STANDARD_IMAGE_SIZE[1]} px")
        size_info.setStyleSheet("color: rgba(255,200,100,0.8); font-size: 10px; font-style: italic;")
        info_row.addWidget(size_info)
        
        info_row.addStretch()
        
        # Select All checkbox
        from PyQt6.QtWidgets import QCheckBox
        self.select_all_check = QCheckBox("Seleccionar Todos")
        self.select_all_check.setStyleSheet("""
            QCheckBox {
                color: #0A84FF;
                font-weight: bold;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        self.select_all_check.stateChanged.connect(self._toggle_all_products)
        info_row.addWidget(self.select_all_check)
        
        self.content_layout.addLayout(info_row)
        
        # Product table with improved sizing
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Incluir", "Producto", "Imagen", "Detalles"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        # Improved column widths for better icon display
        self.table.setColumnWidth(0, 75)   # Wider for checkbox
        self.table.setColumnWidth(2, 100)  # Wider for image button
        
        # Set row height for better visibility
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.verticalHeader().setVisible(False)
        
        self.table.setMinimumHeight(350)  # Increased height
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                color: white;
                gridline-color: rgba(255,255,255,0.1);
            }
            QHeaderView::section {
                background-color: rgba(255,255,255,0.1);
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 6px;
            }
        """)
        self.content_layout.addWidget(self.table)
        
        if self._products:
            self._populate_table()
    
    def _toggle_all_products(self, state):
        """Toggle all product checkboxes based on Select All state."""
        from PyQt6.QtWidgets import QCheckBox
        is_checked = state == Qt.CheckState.Checked.value
        
        # Block signals to prevent multiple content_changed emissions
        self.table.blockSignals(True)
        
        for row in range(self.table.rowCount()):
            checkbox_container = self.table.cellWidget(row, 0)
            if checkbox_container:
                # Find checkbox inside container
                for child in checkbox_container.children():
                    if isinstance(child, QCheckBox):
                        child.setChecked(is_checked)
                        break
        
        self.table.blockSignals(False)
        self.content_changed.emit()
    
    def _populate_table(self):
        """Populate table with products."""
        self.table.setRowCount(len(self._products))
        for i, product in enumerate(self._products):
            # Checkbox for include - centered in cell
            from PyQt6.QtWidgets import QCheckBox, QWidget
            checkbox_container = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_container)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            checkbox = QCheckBox()
            checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)
            checkbox.stateChanged.connect(lambda: self.content_changed.emit())
            checkbox_layout.addWidget(checkbox)
            self.table.setCellWidget(i, 0, checkbox_container)
            
            # Product name
            desc = product.get("description", "") if isinstance(product, dict) else str(product)
            item = QTableWidgetItem(desc)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item)
            
            # Image button with better styling
            btn_img = QPushButton("📷 Agregar")
            btn_img.setToolTip("Agregar imagen al producto")
            btn_img.setStyleSheet("""
                QPushButton {
                    background-color: rgba(10, 132, 255, 0.2);
                    border: 1px solid rgba(10, 132, 255, 0.4);
                    border-radius: 4px;
                    color: white;
                    padding: 6px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: rgba(10, 132, 255, 0.4);
                }
            """)
            
            # Check if product already has an image
            img_path = product.get("image_path", "") if isinstance(product, dict) else ""
            if img_path and os.path.exists(img_path):
                btn_img.setText("✅ Imagen")
                btn_img.setToolTip(f"Imagen: {os.path.basename(img_path)}")
                btn_img.setProperty("image_path", img_path)
                btn_img.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(52, 199, 89, 0.3);
                        border: 1px solid #34C759;
                        border-radius: 4px;
                        color: white;
                        padding: 6px 8px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(52, 199, 89, 0.5);
                    }
                """)
            
            btn_img.clicked.connect(lambda checked, row=i: self._add_product_image(row))
            self.table.setCellWidget(i, 2, btn_img)
            
            # Details input
            details_edit = QLineEdit()
            details_edit.setPlaceholderText("Detalles adicionales...")
            details_edit.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(0,0,0,0.2);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 4px;
                    padding: 6px;
                    color: white;
                }
                QLineEdit:focus {
                    border-color: #0A84FF;
                }
            """)
            details_edit.textChanged.connect(lambda: self.content_changed.emit())
            self.table.setCellWidget(i, 3, details_edit)
    
    def _add_product_image(self, row: int):
        """Add image to product and save to dedicated folder."""
        # Import Dialogs (lazy import to resolve potential circular deps)
        from src.views.components.dialogs.image_source_dialog import ImageSourceDialog
        from src.views.components.dialogs.image_search_dialog import ImageSearchDialog
        
        # 1. Ask Source
        source_dlg = ImageSourceDialog(self)
        if not source_dlg.exec():
            return
            
        file_path = None
        
        # 2. Get File Path based on Source
        if source_dlg.selected_source == ImageSourceDialog.SOURCE_LOCAL:
            path, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar Imagen", "",
                "Imagenes (*.png *.jpg *.jpeg *.gif *.bmp)"
            )
            file_path = path
            
        elif source_dlg.selected_source == ImageSourceDialog.SOURCE_INTERNET:
            # Get product description for auto-search
            desc_item = self.table.item(row, 1)
            initial_query = desc_item.text() if desc_item else ""
            
            search_dlg = ImageSearchDialog(self, initial_query=initial_query)
            if search_dlg.exec():
                file_path = search_dlg.selected_image_path
        
        # 3. Process File if Selected
        if file_path:
            # Check image resolution and emit warning if not standard
            try:
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    w, h = pixmap.width(), pixmap.height()
                    std_w, std_h = self.STANDARD_IMAGE_SIZE
                    # simple tolerance check
                    if abs(w - std_w) > 50 or abs(h - std_h) > 50:
                        msg = (
                            f"La resolución de la imagen cargada ({w}x{h} px) no es exacta a "
                            f"<b>{std_w}x{std_h} px</b>.<br><br>"
                            f"<span style='color: #FF5252;'>Se ajustará automáticamente para el PDF.</span>"
                        )
                        # Only warn if it's wildly different to avoid annoyance
                        if abs(w - std_w) > 100 or abs(h - std_h) > 100:
                            self.image_warning.emit("Aviso de Resolución", msg)
            except Exception as e:
                print(f"Error checking image resolution: {e}")
            
            # Create dedicated folder for product images
            import shutil
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            images_folder = os.path.join(base_dir, "archivocotizacion", "producto", "imagen")
            os.makedirs(images_folder, exist_ok=True)
            
            # Get product description for naming
            desc_item = self.table.item(row, 1)
            product_desc = desc_item.text() if desc_item else f"producto_{row}"
            
            # Sanitize filename
            safe_name = "".join(c for c in product_desc if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name[:50]  # Limit length
            if not safe_name:
                safe_name = f"producto_{row}"
            
            # Get file extension
            _, ext = os.path.splitext(file_path)
            if not ext: ext = ".jpg" # Default if missing
            
            # Create unique filename
            import time
            timestamp = int(time.time())
            new_filename = f"{safe_name}_{timestamp}{ext}"
            new_path = os.path.join(images_folder, new_filename)
            
            try:
                # Copy image to dedicated folder
                shutil.copy2(file_path, new_path)
                saved_path = new_path
            except Exception as e:
                print(f"Error copying image: {e}")
                saved_path = file_path  # Fallback to original path
            
            # Update button
            btn = self.table.cellWidget(row, 2)
            if btn:
                btn.setText("✅ Imagen")
                btn.setToolTip(f"Imagen: {os.path.basename(saved_path)}")
                btn.setProperty("image_path", saved_path)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(52, 199, 89, 0.3);
                        border: 1px solid #34C759;
                        border-radius: 4px;
                        color: white;
                        padding: 6px 8px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(52, 199, 89, 0.5);
                    }
                """)
        self.content_changed.emit()
    
    def set_products(self, products: list):
        """Update products list."""
        self._products = products
        self._populate_table()
    
    def get_data(self) -> dict:
        data = super().get_data()
        products_data = []
        for row in range(self.table.rowCount()):
            # Get checkbox from container
            checkbox_container = self.table.cellWidget(row, 0)
            checkbox = None
            if checkbox_container:
                from PyQt6.QtWidgets import QCheckBox
                for child in checkbox_container.children():
                    if isinstance(child, QCheckBox):
                        checkbox = child
                        break
            
            if checkbox and checkbox.isChecked():
                desc_item = self.table.item(row, 1)
                btn = self.table.cellWidget(row, 2)
                details = self.table.cellWidget(row, 3)
                
                products_data.append({
                    "description": desc_item.text() if desc_item else "",
                    "image_path": btn.property("image_path") if btn else "",
                    "details": details.text() if details else ""
                })
        data["products"] = products_data
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        # Load saved product selections
        saved_products = data.get("products", [])
        for saved in saved_products:
            for row in range(self.table.rowCount()):
                desc_item = self.table.item(row, 1)
                if desc_item and desc_item.text() == saved.get("description"):
                    # Get checkbox from container
                    checkbox_container = self.table.cellWidget(row, 0)
                    if checkbox_container:
                        from PyQt6.QtWidgets import QCheckBox
                        for child in checkbox_container.children():
                            if isinstance(child, QCheckBox):
                                child.setChecked(True)
                                break
                    
                    btn = self.table.cellWidget(row, 2)
                    if btn and saved.get("image_path"):
                        btn.setText("✅ Imagen")
                        btn.setProperty("image_path", saved["image_path"])
                        btn.setStyleSheet("""
                            QPushButton {
                                background-color: rgba(52, 199, 89, 0.3);
                                border: 1px solid #34C759;
                                border-radius: 4px;
                                color: white;
                                padding: 6px 8px;
                                font-size: 11px;
                                font-weight: bold;
                            }
                        """)
                    
                    details = self.table.cellWidget(row, 3)
                    if details:
                        details.setText(saved.get("details", ""))


class ImageBlock(DraggableBlock):
    """Block for images with caption."""
    
    BLOCK_TYPE = "image"
    BLOCK_TITLE = "Imagen"
    
    def __init__(self, image_path: str = "", parent=None):
        self._image_path = image_path
        super().__init__(parent)
        self._setup_content()
        if image_path:
            self._load_image(image_path)
    
    def _setup_content(self):
        """Setup image display and caption."""
        # Image container
        self.image_label = QLabel("Haga clic para agregar una imagen")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(120)
        self.image_label.setMaximumHeight(200)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0,0,0,0.2);
                border: 2px dashed rgba(255,255,255,0.2);
                border-radius: 8px;
                color: rgba(255,255,255,0.5);
            }
        """)
        self.image_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.image_label.mousePressEvent = self._on_image_click
        self.content_layout.addWidget(self.image_label)
        
        # Caption input
        self.caption_input = QLineEdit()
        self.caption_input.setPlaceholderText("Leyenda de la imagen (opcional)...")
        self.caption_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
        """)
        self.caption_input.textChanged.connect(lambda: self.content_changed.emit())
        self.caption_input.textChanged.connect(lambda: self.content_changed.emit())
        self.content_layout.addWidget(self.caption_input)

        # Alignment
        align_layout = QHBoxLayout()
        align_layout.addWidget(QLabel("Alineación:"))
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Izquierda", "Centro", "Derecha"])
        self.align_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
            }
        """)
        self.align_combo.currentIndexChanged.connect(lambda: self.content_changed.emit())
        align_layout.addWidget(self.align_combo)
        align_layout.addStretch()
        self.content_layout.addLayout(align_layout)
    
    def _on_image_click(self, event):
        """Handle image click to select file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "",
            "Imagenes (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if file_path:
            self._load_image(file_path)
            self.content_changed.emit()
    
    def _load_image(self, path: str):
        """Load and display image."""
        self._image_path = path
        if os.path.exists(path):
            pixmap = QPixmap(path)
            scaled = pixmap.scaled(
                350, 180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            self.image_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(0,0,0,0.2);
                    border: 1px solid rgba(255,255,255,0.2);
                    border-radius: 8px;
                }
            """)
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["path"] = self._image_path
        data["caption"] = self.caption_input.text()
        data["alignment"] = self.align_combo.currentIndex()
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        if data.get("path"):
            self._load_image(data["path"])
        if data.get("path"):
            self._load_image(data["path"])
        self.caption_input.setText(data.get("caption", ""))
        self.align_combo.setCurrentIndex(data.get("alignment", 1)) # Default Center


class SeparatorBlock(DraggableBlock):
    """Block for visual separator/divider."""
    
    BLOCK_TYPE = "separator"
    BLOCK_TITLE = "Separador"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_content()
    
    def _setup_content(self):
        """Setup separator line."""
        # Style selector
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Estilo:"))
        
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Linea simple", "Linea doble", "Espacio"])
        self.style_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
            }
        """)
        self.style_combo.currentIndexChanged.connect(lambda: self.content_changed.emit())
        style_layout.addWidget(self.style_combo)
        style_layout.addStretch()
        
        self.content_layout.addLayout(style_layout)
        
        # Preview
        self.preview = QFrame()
        self.preview.setFrameShape(QFrame.Shape.HLine)
        self.preview.setStyleSheet("background-color: rgba(255,255,255,0.3);")
        self.preview.setFixedHeight(2)
        self.content_layout.addWidget(self.preview)
    
    def get_data(self) -> dict:
        data = super().get_data()
        data["style"] = self.style_combo.currentIndex()
        return data
    
    def load_data(self, data: dict):
        super().load_data(data)
        self.style_combo.setCurrentIndex(data.get("style", 0))


class BlockContainer(QScrollArea):
    """Container widget for managing reorderable blocks."""
    
    content_changed = pyqtSignal()
    image_warning = pyqtSignal(str, str)  # Forward image warnings (title, message)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocks = []
        self._products = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the container UI."""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Main container
        self.container = QWidget()
        self.setWidget(self.container)
        
        # Layout
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(8, 8, 8, 8)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        btn_style = """
            QPushButton {
                background-color: rgba(10, 132, 255, 0.2);
                border: 1px solid rgba(10, 132, 255, 0.4);
                border-radius: 6px;
                color: white;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(10, 132, 255, 0.4);
            }
        """
        
        btn_title = QPushButton("+ Titulo")
        btn_title.setStyleSheet(btn_style)
        btn_title.clicked.connect(self._add_title_block)
        toolbar.addWidget(btn_title)
        
        btn_note = QPushButton("+ Nota")
        btn_note.setStyleSheet(btn_style)
        btn_note.clicked.connect(self._add_note_block)
        toolbar.addWidget(btn_note)
        
        btn_matrix = QPushButton("+ Matriz")
        btn_matrix.setStyleSheet(btn_style)
        btn_matrix.clicked.connect(self._add_matrix_block)
        toolbar.addWidget(btn_matrix)
        
        btn_image = QPushButton("+ Imagen")
        btn_image.setStyleSheet(btn_style)
        btn_image.clicked.connect(self._add_image_block)
        toolbar.addWidget(btn_image)
        
        btn_separator = QPushButton("+ Separador")
        btn_separator.setStyleSheet(btn_style)
        btn_separator.clicked.connect(self._add_separator_block)
        toolbar.addWidget(btn_separator)
        
        toolbar.addStretch()
        
        btn_clear = QPushButton("Limpiar Todo")
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 69, 58, 0.2);
                border: 1px solid rgba(255, 69, 58, 0.4);
                border-radius: 6px;
                color: white;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 69, 58, 0.4);
            }
        """)
        btn_clear.clicked.connect(self._clear_all)
        toolbar.addWidget(btn_clear)
        
        self.layout.addLayout(toolbar)
        
        # Blocks container
        self.blocks_widget = QWidget()
        self.blocks_layout = QVBoxLayout(self.blocks_widget)
        self.blocks_layout.setSpacing(4)
        self.blocks_layout.setContentsMargins(0, 0, 0, 0)
        self.blocks_layout.addStretch()
        
        self.layout.addWidget(self.blocks_widget, 1)
        
        # Styling
        self.setStyleSheet("""
            BlockContainer {
                background-color: rgba(0, 0, 0, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
    
    def set_products(self, products: list):
        """Set products list for matrix blocks."""
        self._products = products
        for block in self.blocks:
            if isinstance(block, ProductMatrixBlock):
                block.set_products(products)
    
    def _add_block(self, block: DraggableBlock):
        """Add a block to the container."""
        block.removed.connect(self._remove_block)
        block.moved_up.connect(self._move_block_up)
        block.moved_down.connect(self._move_block_down)
        block.content_changed.connect(lambda: self.content_changed.emit())
        
        # Connect image warning signal for ProductMatrixBlock
        if isinstance(block, ProductMatrixBlock):
            block.image_warning.connect(self.image_warning.emit)
        
        self.blocks.append(block)
        # Insert before the stretch
        self.blocks_layout.insertWidget(self.blocks_layout.count() - 1, block)
        self._update_order()
        self.content_changed.emit()
    
    def _add_title_block(self):
        """Add a title block."""
        self._add_block(TitleBlock())
    
    def _add_note_block(self):
        """Add a note block."""
        self._add_block(NoteBlock())
    
    def _add_matrix_block(self):
        """Add a product matrix block."""
        block = ProductMatrixBlock(self._products)
        self._add_block(block)
    
    def _add_image_block(self):
        """Add an image block."""
        self._add_block(ImageBlock())
    
    def _add_separator_block(self):
        """Add a separator block."""
        self._add_block(SeparatorBlock())
    
    def _remove_block(self, block: DraggableBlock):
        """Remove a block."""
        if block in self.blocks:
            self.blocks.remove(block)
            block.deleteLater()
            self._update_order()
            self.content_changed.emit()
    
    def _move_block_up(self, block: DraggableBlock):
        """Move block up in the order."""
        if block in self.blocks:
            idx = self.blocks.index(block)
            if idx > 0:
                self.blocks[idx], self.blocks[idx - 1] = self.blocks[idx - 1], self.blocks[idx]
                self._reorganize_layout()
                self.content_changed.emit()
    
    def _move_block_down(self, block: DraggableBlock):
        """Move block down in the order."""
        if block in self.blocks:
            idx = self.blocks.index(block)
            if idx < len(self.blocks) - 1:
                self.blocks[idx], self.blocks[idx + 1] = self.blocks[idx + 1], self.blocks[idx]
                self._reorganize_layout()
                self.content_changed.emit()
    
    def _reorganize_layout(self):
        """Reorganize all blocks in the layout."""
        # Remove all blocks from layout (but don't delete them)
        for block in self.blocks:
            self.blocks_layout.removeWidget(block)
        
        # Re-add in order
        for block in self.blocks:
            self.blocks_layout.insertWidget(self.blocks_layout.count() - 1, block)
        
        self._update_order()
    
    def _update_order(self):
        """Update order numbers on all blocks."""
        for i, block in enumerate(self.blocks):
            block.set_order(i + 1)
    
    def _clear_all(self):
        """Clear all blocks."""
        if not self.blocks:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar",
            "Esta seguro de eliminar todos los bloques?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for block in self.blocks[:]:
                block.deleteLater()
            self.blocks.clear()
            self.content_changed.emit()
    
    def get_all_data(self) -> list:
        """Get data from all blocks."""
        return [block.get_data() for block in self.blocks]
    
    def load_data(self, data: list):
        """Load blocks from saved data."""
        # Clear existing
        for block in self.blocks[:]:
            block.deleteLater()
        self.blocks.clear()
        
        # Create blocks from data
        for item in data:
            block_type = item.get("type", "")
            block = None
            
            if block_type == "title":
                block = TitleBlock()
            elif block_type == "note":
                block = NoteBlock()
            elif block_type == "product_matrix":
                block = ProductMatrixBlock(self._products)
            elif block_type == "image":
                block = ImageBlock()
            elif block_type == "separator":
                block = SeparatorBlock()
            
            if block:
                block.load_data(item)
                self._add_block(block)
