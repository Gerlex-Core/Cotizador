"""
Theme Engine - Central theme controller orchestrating all subsystems.
Handles theme loading, application, and management of animations, sounds, effects, and icons.
"""

import os
import json
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QIcon

from .animation_engine import AnimationEngine, get_animation_engine
from .sound_manager import SoundManager, get_sound_manager
from .effects_engine import EffectsEngine, get_effects_engine
from .themeable import ComponentRegistry, get_component_registry
from .icon_manager import IconManager
from .layout_engine import LayoutEngine, get_layout_engine


# Base directory for themes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
THEMES_DIR = os.path.join(BASE_DIR, "media", "themes")
CUSTOM_THEMES_DIR = os.path.join(THEMES_DIR, "custom")
ICONS_DIR = os.path.join(BASE_DIR, "media", "icons")


class ThemeData:
    """Represents a loaded theme with all its configuration."""
    
    def __init__(self, name: str, config: Dict[str, Any], path: str = None, is_official: bool = True):
        self.name = name
        self.config = config
        self.path = path  # Base path for custom theme assets
        self.is_official = is_official
        
        # Extract major sections
        self.colors = config.get('colors', {})
        self.effects = config.get('effects', {})
        self.typography = config.get('typography', {})
        self.animations = config.get('animations', {})
        self.sounds = config.get('sounds', {})
        self.layout = config.get('layout', {})
        self.components = config.get('components', {})
        self.assets = config.get('assets', {})
        self.icons = config.get('icons', {})  # Custom icon mappings
    
    def get_color(self, path: str, default: str = '#FFFFFF') -> str:
        """
        Get a color by path (e.g., 'background.primary', 'accent.glow').
        
        Args:
            path: Dot-separated path to color
            default: Default value if not found
        """
        parts = path.split('.')
        value = self.colors
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value if isinstance(value, str) else default
    
    def get_component_config(self, component_type: str) -> Dict[str, Any]:
        """Get configuration for a specific component type."""
        return self.components.get(component_type, {})
    
    def get_animation_config(self, component_type: str) -> Dict[str, Any]:
        """Get animation config for a component type."""
        return self.animations.get('components', {}).get(component_type, {})


class ThemeIconManager:
    """
    Manages icon loading with custom theme icon override support.
    Wraps IconManager and provides custom icon substitution for custom themes.
    """
    
    def __init__(self, base_icon_manager: IconManager):
        self._base_manager = base_icon_manager
        self._custom_icons: Dict[str, str] = {}  # name -> custom path
        self._custom_theme_path: Optional[str] = None
    
    def configure_for_official(self):
        """Use only base icons (for official themes)."""
        self._custom_icons.clear()
        self._custom_theme_path = None
        self._base_manager._icon_cache.clear()
    
    def configure_for_custom(self, theme_path: str, icon_config: Dict[str, str]):
        """
        Configure custom icon mappings.
        
        Args:
            theme_path: Base path to custom theme
            icon_config: Mapping of icon names to relative paths
        """
        self._custom_theme_path = theme_path
        self._custom_icons = icon_config or {}
        self._base_manager._icon_cache.clear()
    
    def get_icon(self, name: str, size: int = 24) -> QIcon:
        """Get icon by name, checking custom icons first."""
        # Check for custom icon override
        if name in self._custom_icons and self._custom_theme_path:
            custom_path = os.path.join(self._custom_theme_path, self._custom_icons[name])
            if os.path.exists(custom_path):
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(custom_path)
                if not pixmap.isNull():
                    from PyQt6.QtCore import Qt
                    scaled = pixmap.scaled(
                        size, size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    return QIcon(scaled)
        
        # Fall back to base icon manager
        return self._base_manager.get_icon(name, size)
    
    def get_pixmap(self, name: str, size: int = 24):
        """Get pixmap by name, checking custom icons first."""
        if name in self._custom_icons and self._custom_theme_path:
            custom_path = os.path.join(self._custom_theme_path, self._custom_icons[name])
            if os.path.exists(custom_path):
                from PyQt6.QtGui import QPixmap
                from PyQt6.QtCore import Qt
                pixmap = QPixmap(custom_path)
                if not pixmap.isNull():
                    return pixmap.scaled(
                        size, size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
        
        return self._base_manager.get_pixmap(name, size)


class ThemeEngine:
    """
    Central theme engine orchestrating all subsystems.
    
    Manages:
    - Theme loading and switching
    - Animation engine configuration
    - Sound manager configuration  
    - Effects engine configuration
    - Icon management with custom overrides
    - Component registry updates
    """
    
    _instance = None
    
    def __init__(self):
        # Subsystems
        self.animation_engine = get_animation_engine()
        self.sound_manager = get_sound_manager()
        self.effects_engine = get_effects_engine()
        self.layout_engine = get_layout_engine()
        self.component_registry = get_component_registry()
        
        # Icon management
        self._base_icon_manager = IconManager.get_instance()
        self.icon_manager = ThemeIconManager(self._base_icon_manager)
        
        # Current theme
        self.current_theme: Optional[ThemeData] = None
        self._available_themes: Dict[str, ThemeData] = {}
        
        # Theme change callbacks
        self._theme_change_callbacks: List[callable] = []
        
        # Load available themes
        self._discover_themes()
    
    @classmethod
    def get_instance(cls) -> 'ThemeEngine':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = ThemeEngine()
        return cls._instance
    
    def _discover_themes(self):
        """Discover all available themes."""
        self._available_themes.clear()
        
        # Load official themes from themes directory
        if os.path.exists(THEMES_DIR):
            for filename in os.listdir(THEMES_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(THEMES_DIR, filename)
                    theme = self._load_theme_file(filepath, is_official=True)
                    if theme:
                        self._available_themes[theme.name] = theme
        
        # Load custom themes
        if os.path.exists(CUSTOM_THEMES_DIR):
            for theme_name in os.listdir(CUSTOM_THEMES_DIR):
                theme_dir = os.path.join(CUSTOM_THEMES_DIR, theme_name)
                if os.path.isdir(theme_dir):
                    # Look for theme JSON
                    json_path = os.path.join(theme_dir, f"{theme_name}.json")
                    if os.path.exists(json_path):
                        theme = self._load_theme_file(json_path, is_official=False, base_path=theme_dir)
                        if theme:
                            self._available_themes[theme.name] = theme
    
    def _load_theme_file(self, filepath: str, is_official: bool = True, base_path: str = None) -> Optional[ThemeData]:
        """Load a theme from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            name = data.get('name', os.path.splitext(os.path.basename(filepath))[0])
            return ThemeData(
                name=name,
                config=data,
                path=base_path or os.path.dirname(filepath),
                is_official=is_official
            )
        except Exception as e:
            print(f"Error loading theme from {filepath}: {e}")
            return None
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self._available_themes.keys())
    
    def get_theme(self, name: str) -> Optional[ThemeData]:
        """Get a theme by name."""
        return self._available_themes.get(name)
    
    def load_theme(self, theme_name: str) -> bool:
        """
        Load and apply a theme.
        
        Args:
            theme_name: Name of theme to load
        
        Returns:
            True if successful
        """
        theme = self._available_themes.get(theme_name)
        if not theme:
            print(f"Theme '{theme_name}' not found")
            return False
        
        self.current_theme = theme
        
        # Configure subsystems
        self._configure_animations(theme)
        self._configure_sounds(theme)
        self._configure_effects(theme)
        self._configure_icons(theme)
        self._configure_layout(theme)
        
        # Update all registered components
        self.component_registry.apply_theme_to_all(theme.config)
        
        # Notify callbacks
        self._notify_theme_change(theme)
        
        return True
    
    def _configure_animations(self, theme: ThemeData):
        """Configure animation engine for theme."""
        anim_config = theme.animations
        
        # Set global speed
        global_speed = anim_config.get('globalSpeed', 1.0)
        self.animation_engine.set_global_speed(global_speed)
        
        # Set component overrides
        component_anims = anim_config.get('components', {})
        self.animation_engine.set_custom_overrides(component_anims)
    
    def _configure_sounds(self, theme: ThemeData):
        """Configure sound manager for theme."""
        if theme.is_official:
            # Official themes use Windows system sounds
            self.sound_manager.configure_for_official_theme()
        else:
            # Custom themes can have custom sounds
            self.sound_manager.configure_for_custom_theme(
                theme.path,
                theme.sounds
            )
            
            # Check for background music
            music_config = theme.sounds.get('backgroundMusic')
            if music_config:
                music_path = os.path.join(theme.path, music_config.get('file', ''))
                if os.path.exists(music_path):
                    self.sound_manager.play_music(
                        music_path,
                        loop=music_config.get('loop', True)
                    )
    
    def _configure_effects(self, theme: ThemeData):
        """Configure effects engine for theme."""
        self.effects_engine.configure(theme.effects)
    
    def _configure_icons(self, theme: ThemeData):
        """Configure icon manager for theme."""
        if theme.is_official:
            # Official themes use default icons
            self.icon_manager.configure_for_official()
        else:
            # Custom themes can override icons
            self.icon_manager.configure_for_custom(
                theme.path,
                theme.icons
            )
    
    def apply_to_widget(self, widget: QWidget):
        """
        Apply current theme to a widget.
        
        Args:
            widget: Widget to style
        """
        if not self.current_theme:
            return
        
        stylesheet = self._generate_stylesheet(self.current_theme)
        widget.setStyleSheet(stylesheet)
    
    def apply_to_application(self, app: QApplication = None):
        """
        Apply current theme to the entire application.
        
        Args:
            app: QApplication instance (uses current if None)
        """
        if app is None:
            app = QApplication.instance()
        
        if app and self.current_theme:
            stylesheet = self._generate_stylesheet(self.current_theme)
            app.setStyleSheet(stylesheet)
    
    def _generate_stylesheet(self, theme: ThemeData) -> str:
        """Generate complete Qt stylesheet from theme."""
        colors = theme.colors
        layout = theme.layout
        components = theme.components
        typography = theme.typography
        
        # Helper to get nested values
        def get_color(path, default='#FFFFFF'):
            return theme.get_color(path, default)
        
        # Get typography
        font_family = typography.get('fontFamily', 'Segoe UI, Arial')
        font_size_base = typography.get('fontSize', {}).get('base', '14px')
        
        # Get corner radii
        corner_sm = layout.get('cornerRadius', {}).get('small', 4)
        corner_md = layout.get('cornerRadius', {}).get('medium', 8)
        corner_lg = layout.get('cornerRadius', {}).get('large', 12)
        
        # Build stylesheet
        stylesheet = f"""
            /* === Global Styles === */
            QWidget {{
                background-color: {get_color('background.primary', '#1C1C1E')};
                color: {get_color('text.primary', '#FFFFFF')};
                font-family: {font_family};
                font-size: {font_size_base};
            }}
            
            /* === Labels === */
            QLabel {{
                color: {get_color('text.primary', '#FFFFFF')};
                background-color: transparent;
                padding: 4px;
            }}
            
            /* === Buttons === */
            QPushButton {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.primary', '#FFFFFF')};
                border: 1px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_md}px;
                padding: {components.get('button', {}).get('padding', '10px 20px')};
                font-weight: 600;
                min-height: 36px;
            }}
            
            QPushButton:hover {{
                background-color: {get_color('accent.primary', '#0A84FF')};
                border-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            QPushButton:pressed {{
                background-color: {get_color('accent.secondary', '#0066CC')};
            }}
            
            QPushButton:disabled {{
                background-color: {get_color('background.tertiary', 'rgba(255,255,255,0.05)')};
                color: {get_color('text.muted', 'rgba(255,255,255,0.5)')};
            }}
            
            /* === Input Fields === */
            QLineEdit {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.primary', '#FFFFFF')};
                border: 2px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_sm}px;
                padding: 8px 12px;
                selection-background-color: {get_color('accent.primary', '#0A84FF')};
                min-height: 36px;
            }}
            
            QLineEdit:focus {{
                border-color: {get_color('borders.focus', '#0A84FF')};
            }}
            
            /* === ComboBox === */
            QComboBox {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.primary', '#FFFFFF')};
                border: 2px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_sm}px;
                padding: 8px 12px;
                min-height: 36px;
            }}
            
            QComboBox:hover {{
                border-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.primary', '#FFFFFF')};
                border: 1px solid {get_color('borders.default', '#3A3A3C')};
                selection-background-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            /* === Menu Bar === */
            QMenuBar {{
                background-color: {get_color('background.primary', '#1C1C1E')};
                color: {get_color('text.primary', '#FFFFFF')};
                border-bottom: 1px solid {get_color('borders.default', '#3A3A3C')};
                padding: 4px;
            }}
            
            QMenuBar::item {{
                padding: 6px 12px;
                border-radius: {corner_sm}px;
                background-color: transparent;
            }}
            
            QMenuBar::item:selected {{
                background-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            /* === Menus === */
            QMenu {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.primary', '#FFFFFF')};
                border: 1px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_md}px;
                padding: 8px;
            }}
            
            QMenu::item {{
                padding: 8px 24px;
                border-radius: {corner_sm}px;
            }}
            
            QMenu::item:selected {{
                background-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            /* === Table Widget === */
            QTableWidget {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.primary', '#FFFFFF')};
                gridline-color: {get_color('borders.subtle', 'rgba(255,255,255,0.1)')};
                border: 1px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_md}px;
                selection-background-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {get_color('borders.subtle', 'rgba(255,255,255,0.1)')};
            }}
            
            QTableWidget::item:hover {{
                background-color: {get_color('background.tertiary', 'rgba(255,255,255,0.05)')};
            }}
            
            QHeaderView::section {{
                background-color: {get_color('background.primary', '#1C1C1E')};
                color: {get_color('text.primary', '#FFFFFF')};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {get_color('accent.primary', '#0A84FF')};
                font-weight: bold;
            }}
            
            /* === Scroll Bars === */
            QScrollBar:vertical {{
                background-color: {get_color('background.primary', '#1C1C1E')};
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {get_color('borders.default', '#3A3A3C')};
                border-radius: 6px;
                min-height: 30px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            /* === List Widget === */
            QListWidget {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.primary', '#FFFFFF')};
                border: 1px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_md}px;
                padding: 4px;
            }}
            
            QListWidget::item {{
                padding: 10px;
                border-radius: {corner_sm}px;
                margin: 2px;
            }}
            
            QListWidget::item:hover {{
                background-color: {get_color('background.tertiary', 'rgba(255,255,255,0.05)')};
            }}
            
            QListWidget::item:selected {{
                background-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            /* === Dialog === */
            QDialog {{
                background-color: {get_color('background.primary', '#1C1C1E')};
            }}
            
            /* === Text Edit === */
            QTextEdit {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.primary', '#FFFFFF')};
                border: 2px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_md}px;
                padding: 10px;
                selection-background-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            QTextEdit:focus {{
                border-color: {get_color('borders.focus', '#0A84FF')};
            }}
            
            /* === SpinBox === */
            QSpinBox, QDoubleSpinBox {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.primary', '#FFFFFF')};
                border: 2px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_sm}px;
                padding: 8px 12px;
                min-height: 36px;
            }}
            
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {get_color('borders.focus', '#0A84FF')};
            }}
            
            /* === Group Box === */
            QGroupBox {{
                background-color: {get_color('background.tertiary', 'rgba(255,255,255,0.03)')};
                border: 1px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_md}px;
                margin-top: 16px;
                padding-top: 16px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                background-color: {get_color('accent.primary', '#0A84FF')};
                border-radius: {corner_sm}px;
                color: white;
                font-weight: bold;
            }}
            
            /* === Tab Widget === */
            QTabWidget::pane {{
                border: 1px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_md}px;
                background-color: {get_color('background.primary', '#1C1C1E')};
            }}
            
            QTabBar::tab {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.secondary', '#8E8E93')};
                padding: 10px 20px;
                border: 1px solid {get_color('borders.default', '#3A3A3C')};
                border-bottom: none;
                border-top-left-radius: {corner_md}px;
                border-top-right-radius: {corner_md}px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {get_color('accent.primary', '#0A84FF')};
                color: white;
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {get_color('background.tertiary', 'rgba(255,255,255,0.05)')};
            }}
            
            /* === ToolTip === */
            QToolTip {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                color: {get_color('text.primary', '#FFFFFF')};
                border: 1px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_sm}px;
                padding: 6px 10px;
            }}
            
            /* === Check Box === */
            QCheckBox {{
                color: {get_color('text.primary', '#FFFFFF')};
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: {corner_sm}px;
                border: 2px solid {get_color('borders.default', '#3A3A3C')};
                background-color: {get_color('background.secondary', '#2C2C2E')};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {get_color('accent.primary', '#0A84FF')};
                border-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            /* === Radio Button === */
            QRadioButton {{
                color: {get_color('text.primary', '#FFFFFF')};
                spacing: 8px;
            }}
            
            QRadioButton::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid {get_color('borders.default', '#3A3A3C')};
                background-color: {get_color('background.secondary', '#2C2C2E')};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {get_color('accent.primary', '#0A84FF')};
                border-color: {get_color('accent.primary', '#0A84FF')};
            }}
            
            /* === Progress Bar === */
            QProgressBar {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                border: 1px solid {get_color('borders.default', '#3A3A3C')};
                border-radius: {corner_sm}px;
                text-align: center;
                color: {get_color('text.primary', '#FFFFFF')};
            }}
            
            QProgressBar::chunk {{
                background-color: {get_color('accent.primary', '#0A84FF')};
                border-radius: {corner_sm - 1}px;
            }}
            
            /* === Slider === */
            QSlider::groove:horizontal {{
                background-color: {get_color('background.secondary', '#2C2C2E')};
                height: 8px;
                border-radius: 4px;
            }}
            
            QSlider::handle:horizontal {{
                background-color: {get_color('accent.primary', '#0A84FF')};
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }}
            
            QSlider::sub-page:horizontal {{
                background-color: {get_color('accent.primary', '#0A84FF')};
                border-radius: 4px;
            }}
        """
        
        return stylesheet
    
    def get_icon(self, name: str, size: int = 24) -> QIcon:
        """
        Get an icon, respecting custom theme overrides.
        
        Args:
            name: Icon name
            size: Icon size
        
        Returns:
            QIcon
        """
        return self.icon_manager.get_icon(name, size)
    
    def play_sound(self, sound_name: str):
        """
        Play a theme sound effect.
        
        Args:
            sound_name: Name of sound (click, hover, success, error, etc.)
        """
        self.sound_manager.play(sound_name)
    
    def reload_themes(self):
        """Reload all themes from disk."""
        current_name = self.current_theme.name if self.current_theme else None
        self._discover_themes()
        
        if current_name and current_name in self._available_themes:
            self.load_theme(current_name)
    
    def _configure_layout(self, theme: ThemeData):
        """Configure layout engine for theme."""
        self.layout_engine.configure(theme.layout)
    
    def _notify_theme_change(self, theme: ThemeData):
        """Notify all callbacks about theme change."""
        for callback in self._theme_change_callbacks:
            try:
                callback(theme)
            except Exception as e:
                print(f"Error in theme change callback: {e}")
    
    def register_theme_change_callback(self, callback: callable):
        """
        Register a callback to be called when theme changes.
        
        Args:
            callback: Callable that takes ThemeData as argument
        """
        if callback not in self._theme_change_callbacks:
            self._theme_change_callbacks.append(callback)
    
    def unregister_theme_change_callback(self, callback: callable):
        """Unregister a theme change callback."""
        if callback in self._theme_change_callbacks:
            self._theme_change_callbacks.remove(callback)
    
    def get_all_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from all registered components.
        Useful for custom themes to understand interface structure.
        
        Returns:
            Dictionary with all component metadata
        """
        return self.component_registry.get_all_metadata()
    
    def get_color(self, path: str, default: str = '#FFFFFF') -> str:
        """
        Get a color from current theme by path.
        
        Args:
            path: Dot-separated path to color (e.g., 'accent.primary')
            default: Default value if not found
        
        Returns:
            Color string
        """
        if self.current_theme:
            return self.current_theme.get_color(path, default)
        return default
    
    def get_effect_enabled(self, effect_name: str) -> bool:
        """
        Check if a specific effect is enabled in current theme.
        
        Args:
            effect_name: Name of effect (blur, glow, bloom, glassmorphism)
        
        Returns:
            True if enabled
        """
        if not self.current_theme:
            return False
        
        effects = self.current_theme.effects
        if effect_name == 'glassmorphism':
            return effects.get('glassmorphism', False)
        return effects.get(effect_name, {}).get('enabled', False)
    
    def should_use_panels(self) -> bool:
        """Check if panels should be used instead of menus."""
        return self.layout_engine.should_use_panels()
    
    def register_main_window(self, window):
        """Register a main window for layout management."""
        self.layout_engine.register_window(window)


# Global instance accessor
def get_theme_engine() -> ThemeEngine:
    """Get the global theme engine instance."""
    return ThemeEngine.get_instance()
