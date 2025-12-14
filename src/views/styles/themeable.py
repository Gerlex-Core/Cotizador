"""
Themeable Interface and Base Classes - Component metadata system for theme customization.
All visual components should implement IThemeable for full theme support.

NOTE: IThemeable does NOT inherit from ABC to avoid metaclass conflicts with PyQt classes.
PyQt uses sip.wrappertype metaclass which is incompatible with ABCMeta.
"""

from typing import Dict, Any, List, Optional
import weakref
from PyQt6.QtCore import QRect, QObject


class IThemeable:
    """
    Interface for themeable components.
    All visual components that support theming should implement this interface.
    
    Note: This class does not inherit from ABC to avoid metaclass conflicts
    with PyQt classes. Subclasses should override all methods marked with
    NotImplementedError.
    """
    
    def get_theme_metadata(self) -> Dict[str, Any]:
        """
        Return component metadata for theme customization.
        
        This metadata describes the component's structure and current state,
        allowing themes to fully customize its appearance and behavior.
        
        Returns:
            Dictionary containing:
            - type: Component type identifier
            - id: Unique component identifier
            - properties: Current visual properties
            - children: Nested themeable components
            - capabilities: List of supported theme features
        """
        raise NotImplementedError("Subclasses must implement get_theme_metadata()")
    
    def apply_theme_config(self, config: Dict[str, Any]):
        """
        Apply theme configuration to this component.
        
        Args:
            config: Theme configuration for this component type
        """
        raise NotImplementedError("Subclasses must implement apply_theme_config()")
    
    @property
    def component_type(self) -> str:
        """
        Return component type identifier.
        Used by the theme engine to apply appropriate styles.
        
        Common types: 'button', 'panel', 'input', 'table', 'dialog', 'window'
        """
        raise NotImplementedError("Subclasses must implement component_type property")
    
    @property
    def theme_capabilities(self) -> List[str]:
        """
        Return list of theme capabilities supported by this component.
        
        Common capabilities:
        - 'colors': Supports color theming
        - 'animations': Supports animation customization
        - 'effects': Supports visual effects (blur, glow, etc.)
        - 'sounds': Supports sound effects
        - 'layout': Supports layout restructuring
        - 'icons': Uses theme icons
        
        Returns:
            List of capability strings
        """
        return ['colors']  # Default to just colors
    
    def get_layout_info(self) -> Dict[str, Any]:
        """
        Return layout information for theme-based reorganization.
        
        Returns:
            Dictionary containing:
            - position: Current position in parent
            - size: Current size
            - constraints: Size constraints (min/max)
            - children: Child components that can be reorganized
        """
        return {}
    
    def supports_layout_change(self) -> bool:
        """
        Indicate if this component supports layout changes by themes.
        
        Returns:
            True if layout can be modified by themes
        """
        return False
    
    def on_theme_changed(self, theme_name: str):
        """
        Called when the global theme changes.
        Override to perform additional theme-change handling.
        
        Args:
            theme_name: Name of the new theme
        """
        pass


class ComponentRegistry:
    """
    Central registry for all themeable components.
    Allows the theme engine to track and update all components.
    """
    
    _instance = None
    
    def __init__(self):
        self._components: Dict[str, weakref.ref] = {}
        self._type_groups: Dict[str, List[str]] = {}  # type -> [component_ids]
    
    @classmethod
    def get_instance(cls) -> 'ComponentRegistry':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = ComponentRegistry()
        return cls._instance
    
    def register(self, component: IThemeable, component_id: str = None):
        """
        Register a themeable component.
        
        Args:
            component: The themeable component
            component_id: Optional unique ID (auto-generated if not provided)
        """
        if component_id is None:
            component_id = f"{component.component_type}_{id(component)}"
        
        self._components[component_id] = weakref.ref(component)
        
        # Add to type group
        comp_type = component.component_type
        if comp_type not in self._type_groups:
            self._type_groups[comp_type] = []
        if component_id not in self._type_groups[comp_type]:
            self._type_groups[comp_type].append(component_id)
    
    def unregister(self, component_id: str):
        """Unregister a component."""
        if component_id in self._components:
            # Remove from type groups
            for type_list in self._type_groups.values():
                if component_id in type_list:
                    type_list.remove(component_id)
            
            del self._components[component_id]
    
    def get_component(self, component_id: str) -> Optional[IThemeable]:
        """Get a component by ID."""
        ref = self._components.get(component_id)
        if ref:
            return ref()  # Dereference weak reference
        return None
    
    def get_components_by_type(self, component_type: str) -> List[IThemeable]:
        """Get all components of a specific type."""
        result = []
        for comp_id in self._type_groups.get(component_type, []):
            comp = self.get_component(comp_id)
            if comp:
                result.append(comp)
        return result
    
    def get_all_components(self) -> List[IThemeable]:
        """Get all registered components."""
        result = []
        for ref in self._components.values():
            comp = ref()
            if comp:
                result.append(comp)
        return result
    
    def get_all_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from all registered components.
        
        Returns:
            Dictionary mapping component IDs to their metadata
        """
        metadata = {}
        dead_refs = []
        
        for comp_id, ref in self._components.items():
            comp = ref()
            if comp:
                metadata[comp_id] = comp.get_theme_metadata()
            else:
                dead_refs.append(comp_id)
        
        # Clean up dead references
        for comp_id in dead_refs:
            self.unregister(comp_id)
        
        return metadata
    
    def apply_theme_to_type(self, component_type: str, config: Dict[str, Any]):
        """
        Apply theme config to all components of a type.
        
        Args:
            component_type: Type of components to update
            config: Theme configuration to apply
        """
        for component in self.get_components_by_type(component_type):
            try:
                component.apply_theme_config(config)
            except Exception as e:
                print(f"Error applying theme to {component_type}: {e}")
    
    def apply_theme_to_all(self, theme_config: Dict[str, Any]):
        """
        Apply theme config to all components.
        
        Args:
            theme_config: Full theme configuration with per-type settings
        """
        for comp_type in self._type_groups.keys():
            type_config = theme_config.get('components', {}).get(comp_type, {})
            if type_config:
                self.apply_theme_to_type(comp_type, type_config)
    
    def clear(self):
        """Clear all registered components."""
        self._components.clear()
        self._type_groups.clear()
    
    def cleanup_dead_refs(self):
        """Remove dead weak references."""
        dead_refs = []
        for comp_id, ref in self._components.items():
            if ref() is None:
                dead_refs.append(comp_id)
        
        for comp_id in dead_refs:
            self.unregister(comp_id)


# Global instance accessor
def get_component_registry() -> ComponentRegistry:
    """Get the global component registry instance."""
    return ComponentRegistry.get_instance()
