from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStyledItemDelegate, QLineEdit, QWidget, QMenu, QFileDialog, QMessageBox
)
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, Qt, QTimer, QEvent, QSize, pyqtSignal
)
from PyQt6.QtGui import QColor, QIcon, QAction, QImage

from src.views.styles.icon_manager import IconManager


class TableItemDelegate(QStyledItemDelegate):
    """
    Custom delegate to fix the double textbox issue when editing cells.
    This delegate ensures only one clean editor appears and hides the underlying text.
    """
    
    def createEditor(self, parent: QWidget, option, index):
        """Create a single clean editor for the cell."""
        editor = QLineEdit(parent)
        editor.setFrame(False)
        editor.setAutoFillBackground(True)  # Ensure background fills the cell
        editor.setStyleSheet("""
            QLineEdit {
                background-color: #1A1A1E;
                color: white;
                border: 2px solid #0A84FF;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 14px;
                selection-background-color: #0A84FF;
            }
        """)
        return editor
    
    def setEditorData(self, editor: QLineEdit, index):
        """Set the editor data from the model."""
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        if value:
            editor.setText(str(value))
            editor.selectAll()  # Select all text for easy replacement
        else:
            editor.setText("")
    
    def setModelData(self, editor: QLineEdit, model, index):
        """Set the model data from the editor."""
        model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)
    
    def updateEditorGeometry(self, editor: QWidget, option, index):
        """Set editor geometry to match the cell exactly, covering underlying text."""
        # Expand geometry slightly to ensure full coverage
        rect = option.rect
        editor.setGeometry(rect)
    
    def paint(self, painter, option, index):
        """Custom paint to handle selection and hover states properly."""
        # Call the parent paint method
        super().paint(painter, option, index)


class AnimatedTable(QTableWidget):
    """
    Premium table widget with animated row insertion, smooth scrolling,
    and hover effects.
    """
    
    # Signal for resolution warning (title, message)
    resolution_warning = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup table appearance
        self._setup_appearance()
        
        # Animation settings
        self._animation_duration = 250
        self._pending_animations = []
        
        # Track row animations
        self._row_effects = {}
        
        # Set custom delegate to fix double textbox issue
        self.setItemDelegate(TableItemDelegate(self))
    
    def _setup_appearance(self):
        """Configure table appearance and behavior."""
        # Smooth scrolling
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        
        # Selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Alternating row colors
        self.setAlternatingRowColors(True)
        
        # Hide grid for cleaner look
        self.setShowGrid(False)
        
        # Stretch columns
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setHighlightSections(False)
        
        # Row height
        self.verticalHeader().setDefaultSectionSize(60) # Increased from 50
        self.verticalHeader().setVisible(False)
        
        # Icon size
        self.setIconSize(QSize(24, 24))
        
        # Focus policy
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Edit triggers - single click to edit
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.SelectedClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )
        
        # Custom stylesheet for premium look
        self.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                border-radius: 12px;
                outline: none;
            }
            
            QTableWidget::item {
                padding: 12px 15px; /* Increased padding */
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                color: white;
            }
            
            QTableWidget::item:selected {
                background-color: rgba(10, 132, 255, 0.3);
            }
            
            QTableWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            
            QHeaderView::section {
                background-color: rgba(0, 0, 0, 0.4);
                color: #FFFFFF;
                padding: 15px 10px; /* Increased header padding */
                border: none;
                border-bottom: 2px solid #0A84FF;
                font-weight: bold;
                font-size: 14px; /* Larger font */
            }
            
            /* Scrollbar styling */
            QScrollBar:vertical {
                background-color: transparent;
                width: 10px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #0A84FF;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def insertAnimatedRow(self, position: int = -1) -> int:
        """Insert a new row with fade-in animation."""
        if position < 0:
            position = self.rowCount()
        
        # Insert the row
        self.insertRow(position)
        
        # Create empty items for each column
        for col in range(self.columnCount()):
            if self.item(position, col) is None and self.cellWidget(position, col) is None:
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(position, col, item)
        
        return position
    
    def removeAnimatedRow(self, row: int):
        """Remove a row with fade-out animation."""
        if row < 0 or row >= self.rowCount():
            return
        
        self.removeRow(row)
    
    def setAnimationDuration(self, duration: int):
        """Set the animation duration in milliseconds."""
        self._animation_duration = duration
    
    def addProduct(self, description: str = "", quantity: str = "",
                   unit: str = "", price: str = "", amount: str = "",
                   image_path: str = ""):
        """Add a product row with animation."""
        row = self.rowCount()
        self.insertAnimatedRow(row)
        
        # Determine items
        items = [description, quantity, unit, price, amount]
        
        for col, text in enumerate(items):
            item = QTableWidgetItem(str(text))
            if col == 0: # Description column
                # Store image path if present
                if image_path:
                    item.setData(Qt.ItemDataRole.UserRole, image_path)
                    item.setIcon(IconManager.get_instance().get_icon("image", 24))
                    item.setToolTip(f"Imagen adjunta: {image_path}")
            
            self.setItem(row, col, item)
            
        current_rows = self.rowCount()
        if current_rows > 0:
             self.selectRow(row)
        
        return row
    
    def getProducts(self):
        """Get all products from the table as a list of lists."""
        products = []
        for row in range(self.rowCount()):
            row_data = []
            image_path = ""
            for col in range(self.columnCount()):
                # Column 2 has QComboBox widget for units
                if col == 2:
                    widget = self.cellWidget(row, col)
                    if widget and hasattr(widget, 'currentText'):
                        text = widget.currentText().strip()
                    else:
                        item = self.item(row, col)
                        text = item.text().strip() if item else ""
                else:
                    item = self.item(row, col)
                    text = item.text() if item else ""
                row_data.append(text)
                
                # Check for image in first column
                if col == 0 and item:
                    image_path = item.data(Qt.ItemDataRole.UserRole) or ""
            
            # Extending row_data with image_path for MainWindow to pick up
            # MainWindow expects: [desc, quant, unit, price, amount, image_path]
            row_data.append(image_path)
            
            products.append(row_data)
        return products
    
    def highlightRow(self, row: int, color: QColor = None):
        """Highlight a row with a specific color."""
        if color is None:
            color = QColor(10, 132, 255, 50)
        
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(color)
    
    def clearHighlights(self):
        """Clear all row highlights."""
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    item.setBackground(QColor(0, 0, 0, 0))
    
    def duplicateRow(self, row: int) -> int:
        """Duplicate a row and return the new row index."""
        if row < 0 or row >= self.rowCount():
            return -1
        
        # Get current row data
        row_data = []
        for col in range(self.columnCount()):
            item = self.item(row, col)
            cell_widget = self.cellWidget(row, col)
            
            if cell_widget and hasattr(cell_widget, 'currentText'):
                row_data.append(('widget', cell_widget.currentText()))
            elif item:
                row_data.append(('item', item.text()))
            else:
                row_data.append(('item', ''))
        
        # Insert new row after current
        new_row = row + 1
        self.insertRow(new_row)
        
        return new_row


class QuotationTable(AnimatedTable):
    """
    Specialized table for quotation items with predefined columns.
    """
    
    COLUMNS = ["Descripción", "Cantidad", "Unidad", "Precio Unit.", "Importe"]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_columns()
    
    def _setup_columns(self):
        """Setup the quotation table columns."""
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        
        header = self.horizontalHeader()
        
        # Column resizing
        # Column resizing - Fixed widths for better spacing
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Description
        
        # Fixed widths for data columns to prevent cramping
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed) # Quantity
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed) # Unit
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed) # Price
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed) # Total
        
        self.setColumnWidth(1, 100)  # Quantity
        self.setColumnWidth(2, 160)  # Unit (Clean spacing)
        self.setColumnWidth(3, 140)  # Price
        self.setColumnWidth(4, 140)  # Total
        
        # Context menu for image
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, position):
        """Show context menu for rows."""
        index = self.indexAt(position)
        if not index.isValid():
            return
            
        menu = QMenu()
        
        # Actions
        add_img_action = QAction(IconManager.get_instance().get_icon("image"), "Agregar Imagen", self)
        add_img_action.triggered.connect(lambda: self._add_image(index.row()))
        menu.addAction(add_img_action)
        
        # Check if already has image
        item = self.item(index.row(), 0)
        if item and item.data(Qt.ItemDataRole.UserRole):
            remove_img_action = QAction(IconManager.get_instance().get_icon("cancel"), "Quitar Imagen", self)
            remove_img_action.triggered.connect(lambda: self._remove_image(index.row()))
            menu.addAction(remove_img_action)
        
        menu.exec(self.viewport().mapToGlobal(position))
    
    def _add_image(self, row):
        """Add image to a product row."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen del Producto", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            item = self.item(row, 0) # Description item
            if not item:
                item = QTableWidgetItem("")
                self.setItem(row, 0, item)
            
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setIcon(IconManager.get_instance().get_icon("image", 24))
            item.setToolTip(f"Imagen adjunta: {file_path}")
            
            # Check Resolution
            try:
                img = QImage(file_path)
                if not img.isNull():
                    w, h = img.width(), img.height()
                    std_res = 300
                    if w != std_res or h != std_res:
                        msg = (
                            f"La resolución de la imagen cargada ({w}x{h} px) no es de "
                            f"<b>{std_res}x{std_res} px</b>.<br><br>"
                            f"<span style='color: #FF5252;'>Se ajustará la imagen rellenando o "
                            f"achicando la imagen, <b>lo que sea necesario</b>.</span>"
                        )
                        self.resolution_warning.emit("Precaución", msg)
            except Exception as e:
                print(f"Error checking resolution: {e}")
            
            # Check Resolution
            try:
                img = QImage(file_path)
                if not img.isNull():
                    w, h = img.width(), img.height()
                    std_res = 300
                    if w != std_res or h != std_res:
                        msg = (
                            f"La resolución de la imagen cargada ({w}x{h} px) no es de "
                            f"<b>{std_res}x{std_res} px</b>.<br><br>"
                            f"<span style='color: #FF5252;'>Se ajustará la imagen rellenando o "
                            f"achicando la imagen, <b>lo que sea necesario</b>.</span>"
                        )
                        self.resolution_warning.emit("Precaución", msg)
            except Exception as e:
                print(f"Error checking resolution: {e}")
            
    def _remove_image(self, row):
        """Remove image from a product row."""
        item = self.item(row, 0)
        if item:
            item.setData(Qt.ItemDataRole.UserRole, None)
            item.setIcon(QIcon())
            item.setToolTip("")
        
        # Set fixed widths - unit column now 150px instead of 100
        self.setColumnWidth(1, 90)    # Quantity
        self.setColumnWidth(2, 150)   # Unit - INCREASED from 100 to 150
        self.setColumnWidth(3, 110)   # Price
        self.setColumnWidth(4, 130)   # Amount
