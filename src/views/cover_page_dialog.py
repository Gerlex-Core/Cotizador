"""
Cover Page Dialog - Editor for quotation cover page.
Allows customization of the cover page with project name, description,
logo display options, and professional styling.
Features: Visual grid for style selection, drag-and-drop blocks, and live preview panel.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QLineEdit, QTextEdit, QCheckBox, QComboBox, QPushButton,
    QGroupBox, QFrame, QColorDialog, QSpinBox, QScrollArea,
    QSplitter, QWidget, QSizePolicy, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient, QPainterPath

from .styles.theme_manager import ThemeManager
from ..logic.config.config_manager import ConfigManager
from .components.block.cover_blocks import (
    CoverBlock, CoverTitleBlock, CoverSubtitleBlock, CoverDescriptionBlock,
    CoverReferenceBlock, CoverLogoBlock, CoverCompanyBlock, CoverClientBlock, 
    CoverDateBlock, CoverFooterBlock, COVER_BLOCK_TYPES, COVER_BLOCK_MENU
)
from .components.canvas_editor import CoverCanvasView


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
        self._company_data = {}
        
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 8px;
            }
        """)
    
    def update_preview(self, data: dict, style: str, accent_color: str,
                       company: str = "", client: str = "", date: str = "", 
                       company_data: dict = None):
        """Update preview with current settings."""
        self._data = data
        self._style = style
        self._accent_color = accent_color
        self._company_name = company or "Mi Empresa"
        self._client_name = client or "Cliente"
        self._project_date = date or "12/12/2024"
        self._company_data = company_data or {}
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
        
        renderer.draw_cover_qt(
            painter, 
            self.width(), 
            self.height(),
            self._company_name,
            self._company_data,
            {"name": self._client_name},
            self._project_date,
            cover_data
        )
        
        painter.end()


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
    Features a visual grid for style selection, drag-and-drop blocks, and live preview panel.
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
        self._accent_color = "#0A84FF"  # Default color
        self._design_frozen = data.get("design_frozen", False) if data else False  # Track if user edited template
        
        # Load Company Data (Crucial for Logo)
        try:
            from src.logic.company.company_logic import get_company_logic
            logic = get_company_logic()
            self.company_data = logic.get_company_dict(self.company_name) if self.company_name else {}
        except Exception as e:
            print(f"Error loading company data: {e}")
            self.company_data = {}
        self._accent_color = "#0A84FF"
        self._selected_style = "Clásico Centrado"
        self._style_cards = {}
        self._blocks = []  # List of cover blocks
        
        self.setWindowTitle("Editor de Carátula")
        self.setMinimumSize(1000, 750)
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
        """Initialize the UI components with Office styling."""
        self.setWindowTitle("Editor de Carátula - Modo Diseño")
        self.resize(1400, 900) # Wider for side panel
        
        # Root Layout (Horizontal: Main Area + Side Panel)
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        
        # Main Area (Vertical: Ribbon + Canvas + Status)
        main_area = QWidget()
        layout = QVBoxLayout(main_area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. Ribbon
        from .components.office_ribbon import OfficeRibbon
        self.ribbon = OfficeRibbon()
        layout.addWidget(self.ribbon)
        
        # 2. Canvas Area
        canvas_container = QWidget()
        canvas_container.setStyleSheet("background-color: #505050;")
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(20, 20, 20, 20)
        
        self.canvas_view = CoverCanvasView()
        # Initial fit
        QTimer.singleShot(100, self.canvas_view.fit_to_view)
        
        canvas_layout.addWidget(self.canvas_view)
        layout.addWidget(canvas_container, 1)
        
        # 3. Status Bar
        status_bar = QFrame()
        status_bar.setFixedHeight(40)
        status_bar.setStyleSheet("background-color: #007ACC; color: white;")
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(10, 0, 10, 0)
        
        self.lbl_status = QLabel("Listo")
        status_layout.addWidget(self.lbl_status)
        status_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background: transparent; border: 1px solid white; border-radius: 4px; color: white; padding: 4px 12px;")
        btn_cancel.clicked.connect(self.reject)
        status_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("Guardar y Salir")
        btn_save.setStyleSheet("background: white; border: none; border-radius: 4px; color: #007ACC; font-weight: bold; padding: 4px 12px;")
        btn_save.clicked.connect(self.accept)
        status_layout.addWidget(btn_save)
        
        layout.addWidget(status_bar)
        root_layout.addWidget(main_area, 1) # Expand main area
        
        # 4. Properties Panel и Layers Panel (Side)
        side_panel_container = QWidget()
        side_panel_layout = QVBoxLayout(side_panel_container)
        side_panel_layout.setContentsMargins(0, 0, 0, 0)
        side_panel_layout.setSpacing(10)
        
        # Properties Panel
        from .components.canvas_properties_panel import CanvasPropertiesPanel
        self.props_panel = CanvasPropertiesPanel()
        side_panel_layout.addWidget(self.props_panel)
        
        # Layers Panel
        from .components.layers_panel import LayersPanel
        self.layers_panel = LayersPanel()
        self.layers_panel.setMinimumHeight(250)
        side_panel_layout.addWidget(self.layers_panel)
        
        root_layout.addWidget(side_panel_container)


        # Wire up Ribbon
        self.ribbon.insert_shape.connect(self.canvas_view.add_shape)
        self.ribbon.theme_changed.connect(self._on_style_selected)
        self.ribbon.edit_data_requested.connect(self._open_data_editor)
        self.ribbon.tool_changed.connect(self._set_canvas_tool)
        self.ribbon.accent_color_clicked.connect(self._select_color)
        self.ribbon.toggle_panel.connect(self.props_panel.setVisible)
        self.ribbon.insert_dynamic_text.connect(self._insert_dynamic_text)
        self.ribbon.save_requested.connect(self.accept)  # Save button triggers accept (saves data)
        
        # Wire up Properties Panel
        self.props_panel.color_changed.connect(self.canvas_view._update_item_color)
        self.props_panel.stroke_color_changed.connect(self.canvas_view._update_item_stroke_color)
        self.props_panel.stroke_width_changed.connect(self.canvas_view._update_item_stroke_width)
        self.props_panel.scale_changed.connect(self.canvas_view._update_item_scale)
        self.props_panel.rotation_changed.connect(self.canvas_view._update_item_rotation)
        self.props_panel.opacity_changed.connect(self.canvas_view._update_item_opacity)
        self.props_panel.lock_toggled.connect(self.canvas_view._update_item_lock)
        self.props_panel.delete_active.connect(self.canvas_view._delete_item)
        self.props_panel.z_order_changed.connect(self.canvas_view._update_item_z_order)
        
        # Wire up Layers Panel
        self.layers_panel.layer_visibility_changed.connect(self._on_layer_visibility_changed)
        self.layers_panel.layer_lock_changed.connect(self._on_layer_lock_changed)
        self.layers_panel.layer_order_changed.connect(self._on_layer_order_changed)
        self.layers_panel.layer_selected.connect(self._on_layer_selected)
        
        # Wire up Selection to Panel
        self.canvas_view.scene.selectionChanged.connect(self._on_selection_changed)
        self.canvas_view.scene.changed.connect(self._update_layers_panel)  # Update cuando la escena cambia
        
        # Restore user elements if data contains them
        if self.data and "user_elements" in self.data:
            print(f"\n[COVER-DEBUG] ===== RESTORING USER ELEMENTS =====")
            print(f"[COVER-DEBUG] Found {len(self.data['user_elements'])} elements to restore")
            print(f"[COVER-DEBUG] Design frozen: {self._design_frozen}")
            
            # If design is frozen, user elements contain EVERYTHING (template + custom)
            # So we DON'T load the theme, just restore saved elements
            if self._design_frozen:
                print(f"[COVER-DEBUG] Design is frozen - clear scene and restore all from save")
                self.canvas_view.scene.clear()
            
            self._restore_user_elements(self.data["user_elements"])
            print(f"[COVER-DEBUG] ===================================\n")
        else:
            print(f"[COVER-DEBUG] No user_elements to restore (data={bool(self.data)})")
        
        # Populate Ribbon Themes
        if hasattr(self, "renderer"):
            self.ribbon.theme_combo.addItems(list(self.renderer.styles.keys()))
        if self._selected_style:
            self.ribbon.theme_combo.setCurrentText(self._selected_style)

    def _on_selection_changed(self):
        """Update properties panel when selection changes."""
        items = self.canvas_view.scene.selectedItems()
        if not items:
            self.props_panel.setEnabled(False)
            return
        
        # Enable panel
        self.props_panel.setEnabled(True)
        
        # Take first item values
        item = items[0]
        
        # Detect if this is a text item
        from .components.canvas_editor import CanvasTextItem
        is_text = isinstance(item, CanvasTextItem)
        mode = "text" if is_text else "shape"
        
        # Get properties safely
        color = None
        if hasattr(item, "brush"): color = item.brush().color().name()
        elif hasattr(item, "defaultTextColor"): color = item.defaultTextColor().name()
        opacity = item.opacity()
        scale = item.scale()
        rotation = item.rotation()
        is_locked = getattr(item, "is_locked", False)
        
        self.props_panel.set_values(color, opacity, scale, rotation, is_locked, mode=mode)
    
    def _on_layer_visibility_changed(self, item_id: str, visible: bool):
        """Handle layer visibility toggle."""
        for item in self.canvas_view.scene.items():
            if hasattr(item, "item_id") and item.item_id == item_id:
                item.set_layer_visible(visible)
                break
    
    def _on_layer_lock_changed(self, item_id: str, locked: bool):
        """Handle layer lock toggle."""
        for item in self.canvas_view.scene.items():
            if hasattr(item, "item_id") and item.item_id == item_id:
                item.set_locked(locked)
                break
    
    def _on_layer_order_changed(self, item_id: str, new_z: int):
        """Handle layer order change."""
        for item in self.canvas_view.scene.items():
            if hasattr(item, "item_id") and item.item_id == item_id:
                item.set_z_index(new_z)
                break
    
    def _on_layer_selected(self, item_id: str):
        """Handle layer selection from panel."""
        # Clear current selection
        self.canvas_view.scene.clearSelection()
        # Select the item
        for item in self.canvas_view.scene.items():
            if hasattr(item, "item_id") and item.item_id == item_id:
                item.setSelected(True)
                break
    
    def _update_layers_panel(self):
        """Update layers panel with current canvas items."""
        items_data = []
        for item in self.canvas_view.scene.items():
            if hasattr(item, "item_id") and item.item_id:
                items_data.append({
                    'id': item.item_id,
                    'layer_name': getattr(item, 'layer_name', item.item_id),
                    'visible': getattr(item, 'layer_visible', True),
                    'locked': getattr(item, 'is_locked', False),
                    'z_index': int(item.zValue())
                })
        self.layers_panel.populate_layers(items_data)
            
    def _set_canvas_tool(self, tool):
        if tool == "hand":
            self.canvas_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        else:
            self.canvas_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            
    def _open_data_editor(self):
        """Open a dialog to edit the data blocks."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Datos del Proyecto")
        dlg.resize(500, 600)
        dlg_layout = QVBoxLayout(dlg)
        
        # Add Button
        btn_add = QPushButton("+ Agregar Elemento")
        btn_add.setStyleSheet("background-color: #2D2D2D; color: #0A84FF; border: 1px dashed #0A84FF; padding: 8px; border-radius: 4px;")
        btn_add.clicked.connect(self._show_add_block_menu)
        dlg_layout.addWidget(btn_add)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.blocks_layout = QVBoxLayout(container) 
        
        # Re-create blocks if they don't exist
        if not hasattr(self, "_blocks") or not self._blocks:
            self._init_blocks_logic() 
            
        # Re-parent blocks to this new layout
        for block in self._blocks:
            self.blocks_layout.addWidget(block)
            block.show()
            
        self.blocks_layout.addStretch()
        scroll.setWidget(container)
        dlg_layout.addWidget(scroll)
        
        btn_ok = QPushButton("Guardar y Salir")
        btn_ok.setToolTip("Guardar los cambios y cerrar la ventana")
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #0A84FF; 
                color: white; 
                border-radius: 4px; 
                padding: 6px 16px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: #007ACC; }
        """)
        btn_ok.clicked.connect(lambda: [self._update_preview(), dlg.accept()])
        dlg_layout.addWidget(btn_ok)
        
        dlg.exec()

    def _init_blocks_logic(self):
        """Helper to create blocks."""
        from .components.block.cover_blocks import (
            CoverTitleBlock, CoverSubtitleBlock, CoverDescriptionBlock,
            CoverReferenceBlock, CoverLogoBlock, CoverCompanyBlock, 
            CoverClientBlock, CoverDateBlock, CoverFooterBlock
        )
        self._blocks.clear() # Clear list, widgets might be destroyed or re-parented
        
        defaults = [
            (CoverCompanyBlock, "company"),
            (CoverTitleBlock, "title"),
            (CoverSubtitleBlock, "subtitle"),
            (CoverDescriptionBlock, "description"),
            (CoverClientBlock, "client"),
            (CoverDateBlock, "date"),
            (CoverLogoBlock, "logo"),
            (CoverFooterBlock, "footer")
        ]
        
        for Cls, key in defaults:
            block = Cls()
            
            # Apply project data (CRITICAL Fix for "Seleccionar Empresa")
            if key == "logo":
                block.set_project_data(company_name=self.company_name)
            elif key == "company":
                block.set_project_data(company_name=self.company_name)
            elif key == "client":
                block.set_project_data(client_name=self.client_name)
            elif key == "date":
                block.set_project_data(project_date=self.project_date)
                
            self._blocks.append(block)
            
        # Connect updates
        for block in self._blocks:
            block.data_changed.connect(self._schedule_preview_update)
            block.removed.connect(self._remove_block)
            block.moved_up.connect(self._move_block_up)
            block.moved_down.connect(self._move_block_down)
            block.content_changed.connect(self._schedule_preview_update)
    
    def _show_add_block_menu(self):
        """Show menu to add a new block."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                color: white;
            }
            QMenu::item:selected {
                background-color: #0A84FF;
            }
        """)
        
        for block_type, block_label in COVER_BLOCK_MENU:
            action = menu.addAction(block_label)
            action.setData(block_type)
        
        action = menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
        if action:
            block_type = action.data()
            self._add_block(block_type)
    
    def _add_block(self, block_type: str, data: dict = None):
        """Add a new block of the specified type."""
        block_class = COVER_BLOCK_TYPES.get(block_type)
        if not block_class:
            return
        
        block = block_class()
        if data:
            block.load_data(data)
        
        # Set project data for blocks that display it (read-only values from quotation)
        if block_type == "logo":
            block.set_project_data(company_name=self.company_name)
        elif block_type == "company":
            block.set_project_data(company_name=self.company_name)
        elif block_type == "client":
            block.set_project_data(client_name=self.client_name)
        elif block_type == "date":
            block.set_project_data(project_date=self.project_date)
        
        # Connect signals
        block.removed.connect(self._remove_block)
        block.moved_up.connect(self._move_block_up)
        block.moved_down.connect(self._move_block_down)
        block.content_changed.connect(self._schedule_preview_update)
        
        self._blocks.append(block)
        self.blocks_layout.addWidget(block)
        self._update_block_orders()
        self._schedule_preview_update()
    
    def _remove_block(self, block: CoverBlock):
        """Remove a block."""
        if block in self._blocks:
            self._blocks.remove(block)
            self.blocks_layout.removeWidget(block)
            block.deleteLater()
            self._update_block_orders()
            self._schedule_preview_update()
    
    def _move_block_up(self, block: CoverBlock):
        """Move a block up in the list."""
        if block not in self._blocks:
            return
        index = self._blocks.index(block)
        if index > 0:
            self._blocks.remove(block)
            self._blocks.insert(index - 1, block)
            self._rebuild_blocks_layout()
            self._schedule_preview_update()
    
    def _move_block_down(self, block: CoverBlock):
        """Move a block down in the list."""
        if block not in self._blocks:
            return
        index = self._blocks.index(block)
        if index < len(self._blocks) - 1:
            self._blocks.remove(block)
            self._blocks.insert(index + 1, block)
            self._rebuild_blocks_layout()
            self._schedule_preview_update()
    
    def _init_blocks_logic(self):
        """Helper to create blocks."""
        from .components.block.cover_blocks import (
            CoverTitleBlock, CoverSubtitleBlock, CoverDescriptionBlock,
            CoverReferenceBlock, CoverLogoBlock, CoverCompanyBlock, 
            CoverClientBlock, CoverDateBlock, CoverFooterBlock
        )
        self._blocks.clear() 
        
        defaults = [
            (CoverCompanyBlock, "company"),
            (CoverTitleBlock, "title"),
            (CoverSubtitleBlock, "subtitle"),
            (CoverDescriptionBlock, "description"),
            (CoverClientBlock, "client"),
            (CoverDateBlock, "date"),
            (CoverLogoBlock, "logo"),
            (CoverFooterBlock, "footer")
        ]
        
        for Cls, key in defaults:
            block = Cls()
            self._blocks.append(block)
            
        # Connect updates
        for block in self._blocks:
            block.content_changed.connect(self._schedule_preview_update)

    def _show_add_block_menu(self):
        """Show menu to add a new block."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                color: white;
            }
            QMenu::item:selected {
                background-color: #0A84FF;
            }
        """)
        
        for block_type, block_label in COVER_BLOCK_MENU:
            action = menu.addAction(block_label)
            action.setData(block_type)
        
        action = menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
        if action:
            self._add_block(action.data())

    def _add_block(self, block_type: str, data: dict = None):
        """Add a new block of the specified type."""
        block_class = COVER_BLOCK_TYPES.get(block_type)
        if not block_class: return
        
        block = block_class()
        if data:
            block.load_data(data)
            
        self._blocks.append(block)
        block.content_changed.connect(self._schedule_preview_update)
        
        # Safely add to layout if it exists (Data Dialog open)
        if hasattr(self, "blocks_layout"):
            try:
                self.blocks_layout.addWidget(block)
            except RuntimeError:
                pass # Layout locked or deleted

    def _rebuild_blocks_layout(self):
        """Rebuild the blocks layout after reordering."""
        # Remove all widgets from layout
        while self.blocks_layout.count():
            item = self.blocks_layout.takeAt(0)
            # Don't delete the widgets, just remove from layout
        
        # Re-add in new order
        for block in self._blocks:
            self.blocks_layout.addWidget(block)
        
        self._update_block_orders()
    
    def _update_block_orders(self):
        """Update order numbers for all blocks."""
        for i, block in enumerate(self._blocks):
            block.set_order(i + 1)
    
    def _on_style_selected(self, style_name: str):
        """Handle style selection from Ribbon."""
        self._selected_style = style_name
        
        # Sync Ribbon if needed (prevent loop)
        if hasattr(self, "ribbon") and self.ribbon.theme_combo.currentText() != style_name:
            self.ribbon.theme_combo.setCurrentText(style_name)
            
        # Update description if label exists (it doesn't in new UI, but logic kept safe)
        if hasattr(self, "style_desc"):
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

    def _extracted_logo_path(self):
        """Try to extract logo path from current company file via binary scan."""
        # Find the .emp file
        import glob
        import os
        base_dir = os.path.join(os.getcwd(), "media", "companies")
        emp_files = glob.glob(os.path.join(base_dir, "*.emp"))
        
        for emp_file in emp_files:
            try:
                with open(emp_file, 'rb') as f:
                    content = f.read()
                    # Look for strings ending in .png, .jpg, .jpeg
                    # A simple heuristic regex for bytes
                    import re
                    # Pattern: match typical paths or filenames ending in extensions
                    # We look for sequences of bytes that look like printable ascii ending in extension
                    pattern = re.compile(b'[a-zA-Z0-9_:/\\\\.\\- ]+\.(?:png|jpg|jpeg|PNG|JPG|JPEG)')
                    matches = pattern.findall(content)
                    
                    for match in matches:
                        try:
                            path_str = match.decode('utf-8', errors='ignore')
                            # clean up if it captured too much context
                            if os.path.exists(path_str):
                                return path_str
                            
                            # maybe it's a relative path?
                            abs_path = os.path.abspath(path_str)
                            if os.path.exists(abs_path):
                                return abs_path
                                
                            # check relative to cwd
                            cwd_path = os.path.join(os.getcwd(), path_str)
                            if os.path.exists(cwd_path):
                                return cwd_path
                                
                        except:
                            continue
            except:
                continue
        return ""

    def _get_logo_fallback(self):
        """Try to find logo in standard locations."""
        import os
        
        # 1. Try binary extraction from company file (most accurate if saved but not loaded)
        extracted = self._extracted_logo_path()
        if extracted: return extracted
        
        # 2. Try standard paths
        possible_paths = [
            os.path.join(os.getcwd(), "media", "logo.png"),
            os.path.join(os.getcwd(), "media", "logo.jpg"),
            os.path.join(os.getcwd(), "assets", "logo.png"),
            os.path.join(os.path.dirname(__file__), "..", "..", "media", "logo.png"),
            "media/logo.png"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                return os.path.abspath(p)
        return ""
    
    def _update_preview(self):
        """Update the live canvas."""
        data = self._collect_data_from_blocks()
        
        # Capture current overrides to persist position during text edits
        current_overrides = self._collect_canvas_overrides()
        if "canvas_overrides" not in data:
            data["canvas_overrides"] = {}
        data["canvas_overrides"].update(current_overrides)
        
        # Capture user added items
        data["user_elements"] = self._collect_user_items()
        
        # A4 size in points
        width = 595.0
        height = 842.0
        
        # Prepare company data with logo
        c_data = getattr(self, "company_data", {}).copy()
        if not c_data.get("logo"):
            c_data["logo"] = self._get_logo_fallback()
            print(f"[COVER-DIALOG] Using fallback logo: {c_data['logo']}")

        # Ensure style is passed
        data["layout_style"] = self._selected_style

        self.renderer.populate_scene(
            self.canvas_view.scene,
            width, height,
            self.company_name,
            c_data,
            {"name": self.client_name},
            self.project_date,
            data
        )
        
        # Connect text sync for dynamic items
        self._connect_canvas_items()
        
    def _connect_canvas_items(self):
        """Connect signals from canvas items to dialog."""
        from .components.canvas_editor import CanvasTextItem
        for item in self.canvas_view.scene.items():
            if isinstance(item, CanvasTextItem):
                try:
                    # Disconnect first to avoid duplicates if re-connecting? 
                    # Actually items are recreated so no duplicates.
                    item.content_changed.disconnect()
                except: pass
                item.content_changed.connect(self._on_canvas_item_changed)
                
    def _on_canvas_item_changed(self, item_id, new_text):
        """Handle text changes from canvas."""
        print(f"Canvas Item Changed: {item_id} -> {new_text}")
        
        # 1. Update Blocks (if dynamic)
        if item_id.startswith("dynamic_"):
            block_type = item_id.replace("dynamic_", "")
            # Find block
            for block in self._blocks:
                # How do we know which block? 
                # Block classes have distinct types but we need mapping.
                # Assuming simple mapping for now.
                # Titles/etc usually have 1 instance.
                # If duplication exists, this is ambiguous.
                pass
            
            # Better: Update the DATA that generates blocks?
            # Or map id to block type.
            # "dynamic_title" -> TitleBlock
            # "dynamic_subtitle" -> SubtitleBlock
            
            target_block = None
            for block in self._blocks:
                # We need to identifying block type from instance? 
                # blocks don't store their "type" string explicitly usually.
                # But we can infer.
                if block_type == "title" and "Título" in str(type(block)): target_block = block
                elif block_type == "subtitle" and "Subtítulo" in str(type(block)): target_block = block
                elif block_type == "date" and "Fecha" in str(type(block)): target_block = block
                elif block_type == "client" and "Cliente" in str(type(block)): target_block = block
                elif block_type == "description" and "Descripción" in str(type(block)): target_block = block
                elif block_type == "footer" and "Pie" in str(type(block)): target_block = block
            
            if target_block:
                # Block.load_data? or setText?
                # Most blocks have input widgets.
                # We need a unified "set_content" method or access widget directly.
                # This is "Brutal" mode so let's check attributes.
                if hasattr(target_block, "input"): target_block.input.setText(new_text)
                elif hasattr(target_block, "text_edit"): target_block.text_edit.setPlainText(new_text)
                
                # This update will trigger block.content_changed -> _schedule_preview_update
                # Which loops back.
                # We should block signals or check equality.
                pass

        # 2. Update User Elements (if user)
        # They will be collected next time _update_preview runs.
        # But we don't store text content in a separate list for user items.
        # Correct. user_items are collected from scene. So no action needed for user items.

    
    def _collect_canvas_overrides(self):
        """Collect positions of modified items."""
        overrides = {}
        if not hasattr(self, "canvas_view"): return overrides
        
        for item in self.canvas_view.scene.items():
            if hasattr(item, "item_id") and item.item_id:
                # Save pos/rot/scale
                overrides[item.item_id] = {
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                    "rotation": item.rotation(),
                    "scale": item.scale()
                }
        return overrides

    def _collect_user_items(self):
        """
        Collect ALL canvas items - cover is a complete independent document.
        No longer checks for modifications - ALWAYS saves everything.
        """
        items_data = []
        if not hasattr(self, "canvas_view"): 
            return items_data
        
        from src.views.components.canvas_editor import CanvasRectItem, CanvasPathItem, CanvasTextItem
        
        print(f"[COVER-COLLECT] Starting collection from {len(self.canvas_view.scene.items())} scene items")
        
        for item in self.canvas_view.scene.items():
            if not hasattr(item, "item_id") or not item.item_id: 
                continue
            
            # Save ALL items - no checks, no filters  
            data = {
                "id": item.item_id,
                "x": item.pos().x(),
                "y": item.pos().y(),
                "rotation": item.rotation(),
                "scale": item.scale(),
                "opacity": item.opacity(),
                "z_index": int(item.zValue()),
                "locked": getattr(item, "is_locked", False),
                "layer_name": getattr(item, "layer_name", item.item_id),
                "visible": getattr(item, "layer_visible", True)
            }
            
            # Capture type-specific properties
            if isinstance(item, CanvasPathItem):
                # Detect type from ID
                if "rounded_rect" in item.item_id:
                    data["type"] = "rounded_rect"
                elif "rect" in item.item_id:
                    data["type"] = "rect"
                elif "circle" in item.item_id:
                    data["type"] = "circle"
                elif "line" in item.item_id:
                    data["type"] = "line"
                elif "triangle" in item.item_id: 
                    data["type"] = "triangle"
                elif "pentagon" in item.item_id: 
                    data["type"] = "pentagon"
                elif "hexagon" in item.item_id: 
                    data["type"] = "hexagon"
                elif "octagon" in item.item_id: 
                    data["type"] = "octagon"
                elif "star" in item.item_id: 
                    data["type"] = "star"
                elif "path" in item.item_id:
                    data["type"] = "path"
                else:
                    data["type"] = "shape"
                
                # Capture bounds
                r = item.path().boundingRect()
                data["w"] = r.width()
                data["h"] = r.height()
                
                # Colors
                data["color"] = item.brush().color().name()
                if item.pen().style() != Qt.PenStyle.NoPen:
                    data["stroke_color"] = item.pen().color().name()
                    data["stroke_width"] = item.pen().widthF()
                    
            elif isinstance(item, CanvasRectItem):
                data["type"] = "rect"
                r = item.rect()
                data["w"] = r.width()
                data["h"] = r.height()
                data["color"] = item.brush().color().name()
                if item.pen().style() != Qt.PenStyle.NoPen:
                    data["stroke_color"] = item.pen().color().name()
                    data["stroke_width"] = item.pen().widthF()
                    
            elif isinstance(item, CanvasTextItem):
                data["type"] = "text"
                data["text"] = item.toPlainText()
                data["color"] = item.defaultTextColor().name()
                font = item.font()
                data["size"] = font.pointSize()
                data["font"] = font.family()
                if font.bold(): 
                    data["bold"] = True
                if font.italic(): 
                    data["italic"] = True
            else:
                # Unknown type, skip
                continue
            
            items_data.append(data)
            print(f"[COVER-COLLECT]   Saved: {item.item_id} ({data['type']}) at ({data['x']:.1f}, {data['y']:.1f})")
            
        print(f"[COVER-COLLECT] Collected {len(items_data)} total items from scene")
        return items_data

    
    def _restore_user_elements(self, elements: list):
        """Restore ONLY user-created items (shapes added manually)."""
        if not elements:
            return
        
        print(f"[COVER] Restoring {len(elements)} USER elements...")
        
        for elem in elements:
            elem_type = elem.get("type", "")
            
            # Create the shape
            if elem_type == "text":
                self.canvas_view.add_shape("text")
            elif elem_type in ["rect", "circle", "rounded_rect", "line", "triangle", "pentagon", "hexagon", "octagon", "star"]:
                self.canvas_view.add_shape(elem_type)
            else:
                continue
            
            # Get the newly created item
            items = [it for it in self.canvas_view.scene.items() if hasattr(it, "item_id") and it.item_id.startswith("user_")]
            if not items:
                continue
            item = items[0]
            
            # Restore position and transform
            item.setPos(elem.get("x", 0), elem.get("y", 0))
            item.setRotation(elem.get("rotation", 0))
            item.setScale(elem.get("scale", 1.0))
            item.setOpacity(elem.get("opacity", 1.0))
            
            # Restore locked state
            if elem.get("locked", False):
                item.is_locked = True
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            
            # Restore type-specific properties
            from src.views.components.canvas_editor import CanvasTextItem, CanvasPathItem, CanvasRectItem
            
            if isinstance(item, CanvasTextItem):
                if "text" in elem:
                    item.setPlainText(elem["text"])
                from PyQt6.QtGui import QColor
                if "color" in elem:
                    item.setDefaultTextColor(QColor(elem["color"]))
                if "size" in elem:
                    font = item.font()
                    font.setPointSize(elem["size"])
                    if "bold" in elem:
                        font.setBold(elem["bold"])
                    if "italic" in elem:
                        font.setItalic(elem["italic"])
                    item.setFont(font)
            
            elif isinstance(item, (CanvasPathItem, CanvasRectItem)):
                from PyQt6.QtGui import QColor, QBrush, QPen
                if "color" in elem:
                    item.setBrush(QBrush(QColor(elem["color"])))
                if "stroke_color" in elem:
                    pen = QPen(QColor(elem["stroke_color"]))
                    pen.setWidthF(elem.get("stroke_width", 2.0))
                    item.setPen(pen)
            
            print(f"[COVER] Restored {elem_type} at ({elem.get('x', 0)}, {elem.get('y', 0)})")

    def _collect_data_from_blocks(self) -> dict:
        """Collect data from all blocks into a single dict."""
        data = {
            "project_name": "",
            "subtitle": "",
            "description": "",
            "reference": "",
            "show_logo": True,
            "logo_size": 120,
            "show_company": True,
            "show_client": True,
            "show_date": True,
            "show_reference": True,
            "show_border": True,
            "footer_text": "",
        }
        
        blocks_data = []
        element_order = []  # Track order of elements for rendering
        
        for block in self._blocks:
            block_data = block.get_data()
            blocks_data.append(block_data)
            element_order.append(block_data["type"])
            
            # Map block data to global cover data
            if block_data["type"] == "title":
                data["project_name"] = block_data.get("text", "")
            elif block_data["type"] == "subtitle":
                data["subtitle"] = block_data.get("text", "")
            elif block_data["type"] == "description":
                data["description"] = block_data.get("text", "")
            elif block_data["type"] == "reference":
                data["reference"] = block_data.get("text", "")
            elif block_data["type"] == "logo":
                data["show_logo"] = block_data.get("show_logo", True)
                data["logo_size"] = block_data.get("logo_size", 120)
            elif block_data["type"] == "company":
                data["show_company"] = block_data.get("visible", True)
            elif block_data["type"] == "client":
                data["show_client"] = block_data.get("visible", True)
            elif block_data["type"] == "date":
                data["show_date"] = block_data.get("visible", True)
            elif block_data["type"] == "footer":
                data["footer_text"] = block_data.get("text", "")
                data["show_border"] = block_data.get("show_border", True)
        
        data["blocks"] = blocks_data
        data["element_order"] = element_order  # Pass order to renderer
        return data
    
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
            # Update ribbon button icon/style? 
            # Ideally ribbon has a way to show current color, but for now just update preview
            self._update_preview()
    
    def _load_data(self):
        """Load existing data into the form."""
        # Load blocks from saved data
        blocks_data = self.data.get("blocks", [])
        
        if blocks_data:
            # Load existing blocks
            for block_data in blocks_data:
                block_type = block_data.get("type", "")
                if block_type in COVER_BLOCK_TYPES:
                    self._add_block(block_type, block_data)
        else:
            # Create default blocks with project values when no saved data
            # Order: Logo, Company, Title, Client, Date, Footer
            # Each element is now a separate draggable block
            
            self._add_block("logo", {
                "show_logo": True,
                "logo_size": 120
            })
            self._add_block("company", {})  # Company name from quotation
            self._add_block("title", {"text": ""})  # User can add custom title
            self._add_block("client", {})  # Client from quotation
            self._add_block("date", {})  # Date from quotation
            self._add_block("footer", {
                "text": "",
                "show_border": True
            })
            # Load style
        layout_style = self.data.get("layout_style", "Clásico Centrado")
        self._selected_style = layout_style
        
        if hasattr(self, "ribbon"):
             self.ribbon.theme_combo.setCurrentText(layout_style)
         
        # Load accent color
        if self.data.get("accent_color"):
            self._accent_color = self.data["accent_color"]
            
        # Update preview
        self._update_preview()
        
        # Trigger preview update
        self._schedule_preview_update()
    
    def _save(self):
        """Save the cover page data."""
        data = self._collect_data_from_blocks()
        
        # Capture final state of canvas
        overrides = self._collect_canvas_overrides()
        data["canvas_overrides"] = overrides

        data["enabled"] = True
        data["layout_style"] = self.layout_combo.currentText()
        data["accent_color"] = self._accent_color
        
        self.saved.emit(data)
        self.accept()
    
    def accept(self):
        """Override accept to emit saved data before closing."""
        try:
            # Collect all current data
            data = self._collect_data_from_blocks()
            
            # Capture final state of canvas
            overrides = self._collect_canvas_overrides()
            data["canvas_overrides"] = overrides
            
            # Capture user-added items (custom shapes)
            user_items = self._collect_user_items()
            data["user_elements"] = user_items
            
            # DEBUG: Print captured data
            print(f"\n[COVER-DEBUG] ===== SAVE DATA CAPTURE =====")
            print(f"[COVER-DEBUG] Captured {len(user_items)} user elements:")
            for i, elem in enumerate(user_items):
                print(f"  [{i}] type={elem.get('type')}, pos=({elem.get('x')}, {elem.get('y')}), text={elem.get('text', 'N/A')[:20]}")
            
            data["enabled"] = True
            data["layout_style"] = self.data.get("layout_style", "Clásico Centrado")
            data["accent_color"] = self._accent_color
            data["design_frozen"] = self._design_frozen  # Save frozen state
            
            # Emit the saved signal so MainWindow can capture it
            self.saved.emit(data)
            print(f"[COVER-DEBUG] Signal emitted with {len(data.get('user_elements', []))} elements")
            print(f"[COVER-DEBUG] =============================\n")
        except Exception as e:
            print(f"[COVER] Error collecting data on accept: {e}")
            import traceback
            traceback.print_exc()
        
        # Call parent accept to close dialog
        super().accept()
    
    def closeEvent(self, event):
        """Auto-save when closing the dialog."""
        print("[COVER] closeEvent triggered - auto-saving...")
        # Trigger accept to ensure data is saved
        self.accept()
        event.accept()
    
    def reject(self):
        """Override reject to auto-save even when user presses Escape/Cancel."""
        print("[COVER] reject() called - auto-saving before closing...")
        # Call accept instead to trigger save
        self.accept()
    
    def get_data(self) -> dict:
        """Get the current cover page data."""
        data = self._collect_data_from_blocks()
        data["enabled"] = True
        data["layout_style"] = self.data.get("layout_style", "Clásico Centrado")
        data["accent_color"] = self._accent_color
        return data
    
    def _insert_dynamic_text(self, text_type: str):
        """Insert dynamic text element (company name, client, date)."""
        # Map type to actual text value
        text_mapping = {
            "company_name": self.company_name if hasattr(self, 'company_name') else "Nombre de la Empresa",
            "client_name": self.client_name if hasattr(self, 'client_name') else "Nombre del Cliente",
            "project_date": self.project_date if hasattr(self, 'project_date') else "01/01/2024"
        }
        
        text_content = text_mapping.get(text_type, "Texto")
        
        # Add text to canvas using existing method
        self.canvas_view.add_shape("text")
        
        # Update the text content of the newly created item
        items = self.canvas_view.scene.items()
        for item in items:
            from .components.canvas_editor import CanvasTextItem
            if isinstance(item, CanvasTextItem) and not hasattr(item, '_text_set'):
                item.setPlainText(text_content)
                item._text_set = True  # Mark as set to avoid updating other items
                item._dynamic_type = text_type  # Store type for later updates
                break
        
        print(f"[COVER] Inserted dynamic text: {text_type} = '{text_content}'")
