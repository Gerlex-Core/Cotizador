"""
Layers Panel - Photoshop-like layer management for canvas items.
Displays all canvas items with visibility, lock, and z-index controls.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QToolButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont

class LayerItemWidget(QWidget):
    """Widget for a single layer item in the list."""
    
    visibility_toggled = pyqtSignal(str, bool)  # item_id, visible
    lock_toggled = pyqtSignal(str, bool)  # item_id, locked
    
    def __init__(self, item_id: str, layer_name: str, visible: bool = True, locked: bool = False, z_index: int = 0):
        super().__init__()
        self.item_id = item_id
        self.visible = visible
        self.locked = locked
        self.z_index = z_index
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        
        # Visibility button
        self.vis_btn = QToolButton()
        self.vis_btn.setCheckable(True)
        self.vis_btn.setChecked(visible)
        self.vis_btn.setText("👁" if visible else "  ")
        self.vis_btn.setFixedSize(24, 24)
        self.vis_btn.clicked.connect(self._on_visibility_clicked)
        layout.addWidget(self.vis_btn)
        
        # Lock button
        self.lock_btn = QToolButton()
        self.lock_btn.setCheckable(True)
        self.lock_btn.setChecked(locked)
        self.lock_btn.setText("🔒" if locked else "  ")
        self.lock_btn.setFixedSize(24, 24)
        self.lock_btn.clicked.connect(self._on_lock_clicked)
        layout.addWidget(self.lock_btn)
        
        # Layer name
        name_label = QLabel(layer_name)
        name_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(name_label, 1)
        
        # Z-index
        z_label = QLabel(f"z:{z_index}")
        z_label.setFont(QFont("Segoe UI", 8))
        z_label.setStyleSheet("color: rgba(255,255,255,0.5);")
        layout.addWidget(z_label)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255,255,255,0.05);
                border-radius: 3px;
            }
            QWidget:hover {
                background-color: rgba(255,255,255,0.1);
            }
            QToolButton {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 3px;
                font-size: 12px;
            }
            QToolButton:hover {
                background: rgba(255,255,255,0.1);
            }
            QToolButton:checked {
                background: rgba(10, 132, 255, 0.3);
            }
        """)
    
    def _on_visibility_clicked(self):
        self.visible = self.vis_btn.isChecked()
        self.vis_btn.setText("👁" if self.visible else "  ")
        self.visibility_toggled.emit(self.item_id, self.visible)
    
    def _on_lock_clicked(self):
        self.locked = self.lock_btn.isChecked()
        self.lock_btn.setText("🔒" if self.locked else "  ")
        self.lock_toggled.emit(self.item_id, self.locked)


class LayersPanel(QWidget):
    """
    Photoshop-like layers panel for managing canvas items.
    """
    
    layer_visibility_changed = pyqtSignal(str, bool)  # item_id, visible
    layer_lock_changed = pyqtSignal(str, bool)  # item_id, locked
    layer_order_changed = pyqtSignal(str, int)  # item_id, new_z_index
    layer_selected = pyqtSignal(str)  # item_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("Capas")
        header.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        header.setStyleSheet("color: white; padding: 8px;")
        layout.addWidget(header)
        
        # Layer list
        self.layer_list = QListWidget()
        self.layer_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.layer_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.layer_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.layer_list.model().rowsMoved.connect(self._on_rows_moved)
        self.layer_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 0px;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: rgba(10, 132, 255, 0.3);
                border: 1px solid rgba(10, 132, 255, 0.6);
            }
        """)
        layout.addWidget(self.layer_list)
        
        # Layer controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(4)
        
        # Move up/down buttons
        btn_up = QPushButton("↑")
        btn_up.setFixedSize(40, 28)
        btn_up.clicked.connect(self._move_layer_up)
        controls_layout.addWidget(btn_up)
        
        btn_down = QPushButton("↓")
        btn_down.setFixedSize(40, 28)
        btn_down.clicked.connect(self._move_layer_down)
        controls_layout.addWidget(btn_down)
        
        controls_layout.addStretch()
        
        # To front/back buttons
        btn_front = QPushButton("⬆ Frente")
        btn_front.clicked.connect(self._move_layer_to_front)
        controls_layout.addWidget(btn_front)
        
        btn_back = QPushButton("⬇ Fondo")
        btn_back.clicked.connect(self._move_layer_to_back)
        controls_layout.addWidget(btn_back)
        
        layout.addLayout(controls_layout)
        
        # Style buttons
        button_style = """
            QPushButton {
                background-color: rgba(10, 132, 255, 0.2);
                border: 1px solid rgba(10, 132, 255, 0.4);
                border-radius: 3px;
                color: white;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: rgba(10, 132, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(10, 132, 255, 0.4);
            }
        """
        for btn in [btn_up, btn_down, btn_front, btn_back]:
            btn.setStyleSheet(button_style)
    
    def populate_layers(self, items: list):
        """Populate layers from canvas items."""
        self.layer_list.clear()
        
        # Sort by z-index (highest first)
        sorted_items = sorted(items, key=lambda x: -x.get('z_index', 0))
        
        for item_data in sorted_items:
            item_id = item_data.get('id', '')
            layer_name = item_data.get('layer_name', item_id)
            visible = item_data.get('visible', True)
            locked = item_data.get('locked', False)
            z_index = item_data.get('z_index', 0)
            
            # Create layer widget
            layer_widget = LayerItemWidget(item_id, layer_name, visible, locked, z_index)
            layer_widget.visibility_toggled.connect(self.layer_visibility_changed.emit)
            layer_widget.lock_toggled.connect(self.layer_lock_changed.emit)
            
            # Add to list
            list_item = QListWidgetItem()
            list_item.setSizeHint(QSize(0, 32))
            list_item.setData(Qt.ItemDataRole.UserRole, item_id)
            
            self.layer_list.addItem(list_item)
            self.layer_list.setItemWidget(list_item, layer_widget)
    
    def _on_selection_changed(self):
        """Emit signal when layer is selected."""
        items = self.layer_list.selectedItems()
        if items:
            item_id = items[0].data(Qt.ItemDataRole.UserRole)
            self.layer_selected.emit(item_id)
    
    def _on_rows_moved(self, parent, start, end, destination, row):
        """Handle layer reordering via drag & drop."""
        # Recalculate z-indices based on new order
        self._recalculate_z_indices()
    
    def _recalculate_z_indices(self):
        """Recalculate z-indices based on current list order."""
        count = self.layer_list.count()
        for i in range(count):
            item = self.layer_list.item(i)
            item_id = item.data(Qt.ItemDataRole.UserRole)
            # Top item gets highest z-index
            new_z = (count - i) * 10
            self.layer_order_changed.emit(item_id, new_z)
    
    def _move_layer_up(self):
        """Move selected layer up one position."""
        current_row = self.layer_list.currentRow()
        if current_row > 0:
            item = self.layer_list.takeItem(current_row)
            self.layer_list.insertItem(current_row - 1, item)
            self.layer_list.setCurrentRow(current_row - 1)
            self._recalculate_z_indices()
    
    def _move_layer_down(self):
        """Move selected layer down one position."""
        current_row = self.layer_list.currentRow()
        if current_row < self.layer_list.count() - 1:
            item = self.layer_list.takeItem(current_row)
            self.layer_list.insertItem(current_row + 1, item)
            self.layer_list.setCurrentRow(current_row + 1)
            self._recalculate_z_indices()
    
    def _move_layer_to_front(self):
        """Move selected layer to front (top of list)."""
        current_row = self.layer_list.currentRow()
        if current_row > 0:
            item = self.layer_list.takeItem(current_row)
            self.layer_list.insertItem(0, item)
            self.layer_list.setCurrentRow(0)
            self._recalculate_z_indices()
    
    def _move_layer_to_back(self):
        """Move selected layer to back (bottom of list)."""
        current_row = self.layer_list.currentRow()
        count = self.layer_list.count()
        if current_row < count - 1:
            item = self.layer_list.takeItem(current_row)
            self.layer_list.addItem(item)
            self.layer_list.setCurrentRow(count - 1)
            self._recalculate_z_indices()
