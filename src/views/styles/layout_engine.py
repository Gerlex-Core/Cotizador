"""
Layout Engine - Controls interface structure and layout dynamically based on themes.
Supports different layout modes: panels vs menus, sidebar positions, header styles, etc.
"""

import os
from typing import Dict, Any, Optional, List, Callable
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QMenuBar, QToolBar, QDockWidget,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal


class LayoutConfig:
    """Configuration for interface layout."""
    
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {}
        
        # Layout mode
        self.use_panels_instead_of_menus = config.get('usePanelsInsteadOfMenus', False)
        self.sidebar_position = config.get('sidebarPosition', 'left')  # left, right, top, bottom
        self.header_style = config.get('headerStyle', 'modern')  # modern, classic, minimal, hidden
        self.footer_visible = config.get('footerVisible', True)
        self.window_borderless = config.get('windowBorderless', False)
        
        # Spacing and sizing
        self.content_margins = config.get('contentMargins', {'top': 16, 'right': 16, 'bottom': 16, 'left': 16})
        self.sidebar_width = config.get('sidebarWidth', 250)
        self.header_height = config.get('headerHeight', 60)
        self.footer_height = config.get('footerHeight', 40)
        
        # Component visibility
        self.show_toolbar = config.get('showToolbar', True)
        self.show_statusbar = config.get('showStatusbar', True)
        self.compact_mode = config.get('compactMode', False)
        
        # Custom layout structure (for advanced themes)
        self.custom_structure = config.get('customStructure', None)


class LayoutEngine(QObject):
    """
    Manages interface layout based on theme configuration.
    Can dynamically reorganize widgets, switch between layout modes,
    and apply structural changes to the interface.
    """
    
    _instance = None
    
    # Signals
    layout_changed = pyqtSignal(dict)  # Emitted when layout changes
    structure_changed = pyqtSignal()   # Emitted when interface structure changes
    
    def __init__(self):
        super().__init__()
        self._current_config = LayoutConfig()
        self._registered_windows: Dict[str, QMainWindow] = {}
        self._layout_handlers: Dict[str, Callable] = {}
        self._original_layouts: Dict[str, Dict] = {}  # Store original layouts for restoration
    
    @classmethod
    def get_instance(cls) -> 'LayoutEngine':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = LayoutEngine()
        return cls._instance
    
    def configure(self, config: Dict[str, Any]):
        """
        Configure layout from theme settings.
        
        Args:
            config: Layout configuration from theme JSON
        """
        old_config = self._current_config
        self._current_config = LayoutConfig(config)
        
        # Apply changes to registered windows
        self._apply_layout_changes(old_config)
        
        # Emit signal
        self.layout_changed.emit(config)
    
    def get_config(self) -> LayoutConfig:
        """Get current layout configuration."""
        return self._current_config
    
    def register_window(self, window: QMainWindow, window_id: str = None):
        """
        Register a main window for layout management.
        
        Args:
            window: The main window to manage
            window_id: Optional identifier
        """
        if window_id is None:
            window_id = f"window_{id(window)}"
        
        self._registered_windows[window_id] = window
        
        # Store original layout for restoration
        self._store_original_layout(window, window_id)
    
    def unregister_window(self, window_id: str):
        """Unregister a window."""
        if window_id in self._registered_windows:
            del self._registered_windows[window_id]
        if window_id in self._original_layouts:
            del self._original_layouts[window_id]
    
    def _store_original_layout(self, window: QMainWindow, window_id: str):
        """Store original window layout for potential restoration."""
        self._original_layouts[window_id] = {
            'menubar_visible': window.menuBar().isVisible() if window.menuBar() else True,
            'toolbar_visible': True,  # Would need to track actual toolbars
            'statusbar_visible': window.statusBar().isVisible() if window.statusBar() else True,
        }
    
    def _apply_layout_changes(self, old_config: LayoutConfig):
        """Apply layout changes to all registered windows."""
        for window_id, window in self._registered_windows.items():
            try:
                self._apply_window_layout(window, old_config)
            except Exception as e:
                print(f"Error applying layout to {window_id}: {e}")
    
    def _apply_window_layout(self, window: QMainWindow, old_config: LayoutConfig):
        """Apply layout configuration to a window."""
        config = self._current_config
        
        # Handle borderless mode
        if config.window_borderless:
            window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Handle menu bar visibility (panels vs menus)
        if window.menuBar():
            if config.use_panels_instead_of_menus:
                window.menuBar().hide()
            else:
                window.menuBar().show()
        
        # Handle status bar
        if window.statusBar():
            window.statusBar().setVisible(config.show_statusbar)
        
        # Apply header style
        self._apply_header_style(window, config.header_style)
    
    def _apply_header_style(self, window: QMainWindow, style: str):
        """Apply header style to window."""
        if style == 'hidden':
            if window.menuBar():
                window.menuBar().hide()
        elif style == 'minimal':
            if window.menuBar():
                window.menuBar().setFixedHeight(30)
        elif style == 'modern':
            if window.menuBar():
                window.menuBar().setFixedHeight(40)
        # 'classic' uses default
    
    def get_content_margins(self) -> tuple:
        """Get current content margins as (left, top, right, bottom)."""
        m = self._current_config.content_margins
        return (
            m.get('left', 16),
            m.get('top', 16),
            m.get('right', 16),
            m.get('bottom', 16)
        )
    
    def get_sidebar_info(self) -> Dict[str, Any]:
        """Get sidebar configuration."""
        return {
            'position': self._current_config.sidebar_position,
            'width': self._current_config.sidebar_width,
            'visible': True
        }
    
    def should_use_panels(self) -> bool:
        """Check if panels should be used instead of menus."""
        return self._current_config.use_panels_instead_of_menus
    
    def is_compact_mode(self) -> bool:
        """Check if compact mode is enabled."""
        return self._current_config.compact_mode
    
    def register_layout_handler(self, layout_type: str, handler: Callable):
        """
        Register a custom handler for specific layout types.
        
        Args:
            layout_type: Type of layout (e.g., 'sidebar', 'header')
            handler: Callable that applies the layout
        """
        self._layout_handlers[layout_type] = handler
    
    def apply_custom_structure(self, structure: Dict[str, Any], target: QWidget):
        """
        Apply a custom layout structure to a widget.
        Used by advanced themes to completely restructure the interface.
        
        Args:
            structure: Layout structure definition
            target: Target widget to restructure
        """
        if not structure:
            return
        
        # Get structure type
        struct_type = structure.get('type', 'vertical')
        
        # Create appropriate layout
        if struct_type == 'vertical':
            layout = QVBoxLayout()
        elif struct_type == 'horizontal':
            layout = QHBoxLayout()
        else:
            layout = QVBoxLayout()
        
        # Apply spacing
        layout.setSpacing(structure.get('spacing', 8))
        
        # Apply margins
        margins = structure.get('margins', {})
        layout.setContentsMargins(
            margins.get('left', 0),
            margins.get('top', 0),
            margins.get('right', 0),
            margins.get('bottom', 0)
        )
        
        # Set layout to target
        if target.layout():
            # Clear existing layout
            QWidget().setLayout(target.layout())
        target.setLayout(layout)
    
    def create_panel_from_menu(self, menu_data: Dict[str, Any]) -> QFrame:
        """
        Create a panel widget from menu data.
        Used when usePanelsInsteadOfMenus is true.
        
        Args:
            menu_data: Menu configuration
        
        Returns:
            QFrame panel widget
        """
        from PyQt6.QtWidgets import QLabel, QPushButton
        
        panel = QFrame()
        panel.setObjectName("menu_panel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Add title if provided
        title = menu_data.get('title', '')
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("panel_title")
            layout.addWidget(title_label)
        
        # Add items as buttons
        for item in menu_data.get('items', []):
            btn = QPushButton(item.get('text', ''))
            btn.setObjectName(f"panel_btn_{item.get('id', '')}")
            if item.get('action'):
                # Connect action if provided
                pass
            layout.addWidget(btn)
        
        layout.addStretch()
        return panel
    
    def restore_original_layout(self, window_id: str = None):
        """
        Restore original layout for a window or all windows.
        
        Args:
            window_id: Specific window to restore, or None for all
        """
        if window_id:
            if window_id in self._original_layouts:
                window = self._registered_windows.get(window_id)
                if window:
                    self._restore_window_layout(window, self._original_layouts[window_id])
        else:
            for wid, window in self._registered_windows.items():
                if wid in self._original_layouts:
                    self._restore_window_layout(window, self._original_layouts[wid])
    
    def _restore_window_layout(self, window: QMainWindow, original: Dict):
        """Restore a window to its original layout."""
        if window.menuBar():
            window.menuBar().setVisible(original.get('menubar_visible', True))
        if window.statusBar():
            window.statusBar().setVisible(original.get('statusbar_visible', True))
        
        # Remove borderless flag
        window.setWindowFlags(Qt.WindowType.Window)


# Global instance accessor
def get_layout_engine() -> LayoutEngine:
    """Get the global layout engine instance."""
    return LayoutEngine.get_instance()
