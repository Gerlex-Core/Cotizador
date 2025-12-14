"""
Themeable Mixin - Base utilities for implementing IThemeable in components.
Provides common functionality to reduce boilerplate in themeable components.
"""

from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import QWidget


class ThemeableMixin:
    """
    Mixin class providing common IThemeable implementation.
    Add this to any QWidget subclass to get basic theme support.
    
    Usage:
        class MyWidget(QWidget, ThemeableMixin, IThemeable):
            def __init__(self):
                super().__init__()
                self._init_themeable('my_widget_type')
    """
    
    def _init_themeable(
        self, 
        component_type: str,
        capabilities: List[str] = None,
        auto_register: bool = True
    ):
        """
        Initialize themeable properties.
        
        Args:
            component_type: Type identifier for this component
            capabilities: List of theme capabilities (defaults to ['colors'])
            auto_register: Whether to auto-register with ComponentRegistry
        """
        self._component_type = component_type
        self._theme_capabilities = capabilities or ['colors']
        self._theme_config: Dict[str, Any] = {}
        self._supports_layout_change = False
        
        if auto_register:
            from src.views.styles.themeable import get_component_registry
            get_component_registry().register(self)
    
    @property
    def component_type(self) -> str:
        """Return component type identifier."""
        return getattr(self, '_component_type', 'widget')
    
    @property
    def theme_capabilities(self) -> List[str]:
        """Return list of theme capabilities."""
        return getattr(self, '_theme_capabilities', ['colors'])
    
    def get_theme_metadata(self) -> Dict[str, Any]:
        """Return component metadata for theme customization."""
        widget = self
        return {
            "type": self.component_type,
            "id": widget.objectName() if hasattr(widget, 'objectName') else f"{self.component_type}_{id(self)}",
            "enabled": widget.isEnabled() if hasattr(widget, 'isEnabled') else True,
            "visible": widget.isVisible() if hasattr(widget, 'isVisible') else True,
            "geometry": self._get_geometry_info(),
            "capabilities": self.theme_capabilities,
            "config": self._theme_config
        }
    
    def _get_geometry_info(self) -> Dict[str, int]:
        """Get geometry as dict."""
        widget = self
        if hasattr(widget, 'geometry'):
            geo = widget.geometry()
            return {
                "x": geo.x(),
                "y": geo.y(),
                "width": geo.width(),
                "height": geo.height()
            }
        return {}
    
    def apply_theme_config(self, config: Dict[str, Any]):
        """
        Apply theme configuration to this component.
        Override in subclass for specific handling.
        """
        self._theme_config = config
        
        # Trigger update if widget
        if hasattr(self, 'update'):
            self.update()
    
    def get_layout_info(self) -> Dict[str, Any]:
        """Return layout information."""
        widget = self
        if hasattr(widget, 'geometry'):
            return {
                "position": (widget.x(), widget.y()),
                "size": (widget.width(), widget.height()),
                "min_size": (widget.minimumWidth(), widget.minimumHeight())
            }
        return {}
    
    def supports_layout_change(self) -> bool:
        """Check if layout changes are supported."""
        return getattr(self, '_supports_layout_change', False)
    
    def on_theme_changed(self, theme_name: str):
        """Called when theme changes. Override for custom handling."""
        if hasattr(self, 'update'):
            self.update()
    
    def set_supports_layout_change(self, supports: bool):
        """Set whether this component supports layout changes."""
        self._supports_layout_change = supports


def make_themeable(widget_class):
    """
    Decorator to add basic themeable functionality to a widget class.
    
    Usage:
        @make_themeable  
        class MyWidget(QWidget):
            ...
    """
    original_init = widget_class.__init__
    
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        
        # Add themeable properties
        component_type = getattr(widget_class, 'COMPONENT_TYPE', 'widget')
        capabilities = getattr(widget_class, 'THEME_CAPABILITIES', ['colors'])
        
        self._component_type = component_type
        self._theme_capabilities = capabilities
        self._theme_config = {}
        
        # Register
        from src.views.styles.themeable import get_component_registry
        get_component_registry().register(self)
    
    widget_class.__init__ = new_init
    
    # Add IThemeable methods if not present
    if not hasattr(widget_class, 'component_type'):
        widget_class.component_type = property(lambda self: self._component_type)
    
    if not hasattr(widget_class, 'theme_capabilities'):
        widget_class.theme_capabilities = property(lambda self: self._theme_capabilities)
    
    if not hasattr(widget_class, 'get_theme_metadata'):
        def get_theme_metadata(self):
            return {
                "type": self.component_type,
                "id": self.objectName() or f"{self.component_type}_{id(self)}",
                "capabilities": self.theme_capabilities
            }
        widget_class.get_theme_metadata = get_theme_metadata
    
    if not hasattr(widget_class, 'apply_theme_config'):
        def apply_theme_config(self, config):
            self._theme_config = config
            self.update()
        widget_class.apply_theme_config = apply_theme_config
    
    return widget_class
