from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, 
    QTableWidgetItem, QHeaderView, QPushButton, QLabel, QMenu, QMessageBox,
    QComboBox, QDateEdit, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QIcon
import os
from datetime import datetime
from .styles.theme_manager import ThemeManager

class HistoryWindow(QDialog):
    file_selected = pyqtSignal(str) # Emitted when a file is opened

    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setWindowTitle("Historial de Archivos")
        self.resize(800, 600)
        
        # Theme integration if parent has icon_manager
        self.icon_manager = getattr(parent, 'icon_manager', None)
        
        self._create_ui()
        self._load_data()
        
        # Apply theme
        if parent and hasattr(parent, 'config'):
            ThemeManager.apply_theme(self, parent.config.tema)

    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Historial de Cotizaciones")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre, fecha, cliente...")
        self.search_input.textChanged.connect(self._apply_filters)
        self.search_input.setMinimumHeight(40)
        if self.icon_manager:
            self.search_input.addAction(QIcon(self.icon_manager.get_icon("search", 16)), QLineEdit.ActionPosition.LeadingPosition)
        
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Advanced Filters
        filter_group = QGroupBox("Filtros Avanzados")
        filter_layout = QHBoxLayout(filter_group)
        
        # Type Filter
        filter_layout.addWidget(QLabel("Tipo:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Todos", "Cotizaci", "Recibo"]) # Matches doc_type text roughly
        self.type_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        # Date Range
        filter_layout.addWidget(QLabel("Desde:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("Hasta:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.date_to)
        
        # Reset Filters Button
        btn_reset = QPushButton("Limpiar Filtros")
        btn_reset.clicked.connect(self._reset_filters)
        filter_layout.addWidget(btn_reset)
        
        layout.addWidget(filter_group)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nombre", "Fecha Modificación", "Cliente", "Ruta"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.doubleClicked.connect(self._on_row_double_clicked)
        
        # Style table
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                background-color: rgba(0, 0, 0, 0.2);
                gridline-color: rgba(255, 255, 255, 0.05);
            }
            QHeaderView::section {
                background-color: rgba(0, 0, 0, 0.3);
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Footer
        footer = QHBoxLayout()
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        btn_close.setMinimumHeight(35)
        footer.addStretch()
        footer.addWidget(btn_close)
        layout.addLayout(footer)

    def _load_data(self):
        """Load history data into table."""
        history = self.history_manager.get_history()
        # Sort by date desc
        history.sort(key=lambda x: x["date_modified"], reverse=True)
        self._populate_table(history)

    def _populate_table(self, data):
        self.table.setRowCount(0)
        for item in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(item.get("name", "Unknown"))
            if self.icon_manager:
                name_item.setIcon(self.icon_manager.get_icon("note", 16))
            self.table.setItem(row, 0, name_item)
            
            # Date
            self.table.setItem(row, 1, QTableWidgetItem(item.get("date_modified", "")))
            
            # Client (from metadata)
            meta = item.get("metadata", {})
            client = "Unknown"
            if isinstance(meta, dict):
                client = meta.get("client", "")
            self.table.setItem(row, 2, QTableWidgetItem(str(client)))
            
            # Path
            path_item = QTableWidgetItem(item.get("path", ""))
            path_item.setData(Qt.ItemDataRole.UserRole, item.get("path"))
            self.table.setItem(row, 3, path_item)

    def _reset_filters(self):
        """Reset all filters to default."""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self._load_data()

    def _apply_filters(self):
        """Apply all active filters."""
        query = self.search_input.text().lower()
        doc_type = self.type_filter.currentText()
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        
        history = self.history_manager.get_history()
        filtered = []
        
        for item in history:
            # 1. Text Search
            match_text = (
                query in item.get("name", "").lower() or 
                query in item.get("date_modified", "") or
                query in str(item.get("metadata", "")).lower()
            )
            if query and not match_text:
                continue
                
            # 2. Type Filter
            meta = item.get("metadata", {})
            item_type = meta.get("doc_type", "") if isinstance(meta, dict) else ""
            if doc_type != "Todos" and doc_type not in item_type:
                continue
            
            # 3. Date Range
            try:
                # Parse date "YYYY-MM-DD HH:MM:SS"
                item_date_str = item.get("date_modified", "").split(" ")[0]
                item_date = datetime.strptime(item_date_str, "%Y-%m-%d").date()
                
                if not (date_from <= item_date <= date_to):
                    continue
            except Exception:
                pass # Skip date check if error
                
            filtered.append(item)
            
        # Sort by date desc
        filtered.sort(key=lambda x: x["date_modified"], reverse=True)
        self._populate_table(filtered)

    def _filter_table(self, text):
        """Legacy slot, redirects to _apply_filters."""
        self._apply_filters()

    def _show_context_menu(self, position):
        row = self.table.rowAt(position.y())
        if row < 0: return
        
        path = self.table.item(row, 3).data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu()
        action_open = menu.addAction("Abrir Cotización")
        action_folder = menu.addAction("Abrir Ubicación del Archivo")
        
        if self.icon_manager:
            action_open.setIcon(self.icon_manager.get_icon("openFolder", 16))
        
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action == action_open:
            self.file_selected.emit(path)
            self.accept()
        elif action == action_folder:
            self._open_folder(path)

    def _open_folder(self, path):
        if os.path.exists(path):
            try:
                os.startfile(os.path.dirname(path))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo abrir la carpeta: {e}")

    def _on_row_double_clicked(self, index):
        path = self.table.item(index.row(), 3).data(Qt.ItemDataRole.UserRole)
        self.file_selected.emit(path)
        self.accept()
