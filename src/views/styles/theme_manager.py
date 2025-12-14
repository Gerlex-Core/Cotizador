"""
Theme Manager for the Cotizador application.
Handles theme loading, application, and custom theme support.
Now uses ThemeEngine as backend for enhanced functionality.
"""

import os
import sys
import json
from typing import Dict, Optional

from .theme_engine import ThemeEngine, ThemeData, get_theme_engine
from .theme_base import ThemeConfig


# Paths for theme files - handles both development and frozen (PyInstaller) builds
def _get_base_dir():
    """Get base directory, works for both dev and PyInstaller frozen builds."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

BASE_DIR = _get_base_dir()
THEMES_DIR = os.path.join(BASE_DIR, "media", "themes")
# Legacy support
LEGACY_THEMES_DIR = os.path.join(BASE_DIR, "options", "themes", "custom")


class Theme:
    """
    Represents a visual theme with complete customization options.
    This is a compatibility wrapper around ThemeData.
    """
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self._theme_data: Optional[ThemeData] = None
    
    def get_stylesheet(self) -> str:
        """Generate the complete CSS stylesheet for this theme."""
        # Use the new ThemeEngine to generate stylesheet
        engine = get_theme_engine()
        
        # Try to get theme from engine
        theme_data = engine.get_theme(self.name)
        if theme_data:
            self._theme_data = theme_data
            return engine._generate_stylesheet(theme_data)
        
        # Fallback: Create ThemeData from legacy config
        self._theme_data = ThemeData(self.name, self._convert_legacy_config(), is_official=False)
        return engine._generate_stylesheet(self._theme_data)
    
    def _convert_legacy_config(self) -> Dict:
        """Convert legacy flat config to new nested format."""
        cfg = self.config
        
        return {
            "name": self.name,
            "version": "1.0",
            "colors": {
                "background": {
                    "primary": cfg.get('background', '#1C1C1E'),
                    "secondary": cfg.get('button_bg', '#2C2C2E'),
                    "tertiary": cfg.get('table_hover', 'rgba(255,255,255,0.05)')
                },
                "accent": {
                    "primary": cfg.get('accent', '#0A84FF'),
                    "secondary": cfg.get('accent_dark', '#0066CC'),
                    "glow": cfg.get('accent_glow', 'rgba(10, 132, 255, 0.4)')
                },
                "text": {
                    "primary": cfg.get('text_primary', '#FFFFFF'),
                    "secondary": cfg.get('text_secondary', '#8E8E93'),
                    "muted": 'rgba(255, 255, 255, 0.5)',
                    "link": cfg.get('accent', '#0A84FF')
                },
                "borders": {
                    "default": cfg.get('border', '#3A3A3C'),
                    "focus": cfg.get('accent', '#0A84FF'),
                    "subtle": 'rgba(255, 255, 255, 0.1)'
                }
            },
            "effects": {
                "transparency": cfg.get('transparency', 0),
                "glassmorphism": cfg.get('glassmorphism', False),
                "glow": {
                    "enabled": cfg.get('glow_enabled', False),
                    "color": cfg.get('glow_color', '#0A84FF'),
                    "intensity": cfg.get('glow_intensity', 0.3)
                },
                "blur": {
                    "enabled": cfg.get('blur_enabled', False),
                    "radius": cfg.get('blur_intensity', 12)
                }
            },
            "typography": {
                "fontFamily": cfg.get('font_family', 'Segoe UI, Arial'),
                "fontSize": {
                    "base": cfg.get('font_size', '14px')
                }
            },
            "animations": {
                "globalSpeed": cfg.get('animation_speed', 1.0),
                "components": {
                    "button": {
                        "hover": {"scale": cfg.get('hover_scale', 1.02)},
                        "press": {"scale": cfg.get('press_scale', 0.98)}
                    }
                }
            },
            "layout": {
                "cornerRadius": {
                    "medium": cfg.get('corner_radius', 8)
                }
            },
            "components": {
                "button": {
                    "padding": cfg.get('button_padding', '10px 20px'),
                    "borderRadius": cfg.get('button_radius', '8px')
                }
            }
        }


# Global theme registry
THEMES: Dict[str, Theme] = {}


def load_themes() -> Dict[str, Theme]:
    """Load all themes from the themes directory."""
    loaded_themes = {}
    
    # Ensure directory exists
    os.makedirs(THEMES_DIR, exist_ok=True)
    
    # Check new themes directory only
    for themes_dir in [THEMES_DIR]:
        if os.path.exists(themes_dir):
            for filename in os.listdir(themes_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(themes_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # Get name from config, not filename
                        name = data.get('name', os.path.splitext(filename)[0])
                        loaded_themes[name] = Theme(name, data)
                    except Exception as e:
                        print(f"Error loading theme {filename}: {e}")
    
    return loaded_themes


# Load themes on module import
THEMES.update(load_themes())


class ThemeManager:
    """
    Manages theme application and switching.
    Now uses ThemeEngine as backend for enhanced functionality.
    """
    
    _current_theme: str = "Oscuro"
    _current_config: Dict = {}
    _engine: ThemeEngine = None
    
    @classmethod
    def _get_engine(cls) -> ThemeEngine:
        """Get or initialize the theme engine."""
        if cls._engine is None:
            cls._engine = get_theme_engine()
        return cls._engine
    
    @classmethod
    def get_available_themes(cls) -> list:
        """Get list of available theme names."""
        engine = cls._get_engine()
        return engine.get_available_themes()
    
    @classmethod
    def get_grouped_themes(cls) -> dict:
        """
        Get themes grouped by official/unofficial status.
        
        Returns:
            Dict with 'official' and 'unofficial' lists of theme names
        """
        engine = cls._get_engine()
        official = []
        unofficial = []
        
        for name in engine.get_available_themes():
            theme_data = engine.get_theme(name)
            if theme_data and theme_data.is_official:
                official.append(name)
            else:
                unofficial.append(name)
        
        return {
            'official': official,
            'unofficial': unofficial
        }
    
    @classmethod
    def get_theme(cls, name: str) -> Optional[Theme]:
        """Get a theme by name."""
        return THEMES.get(name)
    
    @classmethod
    def get_theme_config(cls, name: str) -> Dict:
        """Get theme configuration dict by name."""
        engine = cls._get_engine()
        theme_data = engine.get_theme(name)
        if theme_data:
            return theme_data.config
        
        # Fallback to legacy themes
        theme = THEMES.get(name)
        if theme:
            return theme.config
        return {}
    
    @classmethod
    def apply_theme(cls, widget, theme_name: str):
        """Apply a theme to a widget."""
        engine = cls._get_engine()
        
        # Load theme via engine
        if engine.load_theme(theme_name):
            engine.apply_to_widget(widget)
            cls._current_theme = theme_name
            cls._current_config = engine.current_theme.config.copy() if engine.current_theme else {}
        else:
            # Fallback to legacy theme loading
            theme = THEMES.get(theme_name)
            if not theme and THEMES:
                theme = list(THEMES.values())[0]
                theme_name = theme.name
                
            if theme:
                widget.setStyleSheet(theme.get_stylesheet())
                cls._current_theme = theme_name
                cls._current_config = theme.config.copy()
            else:
                print(f"Warning: Theme '{theme_name}' not found and no themes loaded.")
    
    @classmethod
    def get_current_theme(cls) -> str:
        """Get the current theme name."""
        return cls._current_theme
    
    @classmethod
    def get_current_theme_config(cls) -> Dict:
        """Get the current theme's configuration dictionary."""
        engine = cls._get_engine()
        if engine.current_theme:
            return engine.current_theme.config
        
        if cls._current_config:
            return cls._current_config
        theme = THEMES.get(cls._current_theme)
        if theme:
            return theme.config
        return {}
    
    @classmethod
    def is_current_dark(cls) -> bool:
        """Check if current theme is a dark theme."""
        config = cls.get_current_theme_config()
        # Check explicit flag first
        if 'is_dark' in config:
            return config['is_dark']
        
        # Check new schema
        if 'colors' in config:
            bg = config.get('colors', {}).get('background', {}).get('primary', '#121212')
        else:
            bg = config.get('background', '#121212')
        
        return cls._get_luminance(bg) < 0.5
    
    @classmethod
    def _get_luminance(cls, color: str) -> float:
        """Calculate luminance of a color."""
        if color.startswith('rgba'):
            parts = color.replace('rgba(', '').replace(')', '').split(',')
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        elif color.startswith('#'):
            hex_color = color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        else:
            return 0.5
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    @classmethod
    def get_text_color(cls) -> str:
        """Get appropriate text color for current theme."""
        config = cls.get_current_theme_config()
        
        # New schema
        if 'colors' in config:
            return config.get('colors', {}).get('text', {}).get('primary', '#FFFFFF')
        
        # Legacy
        return config.get('text_primary', '#FFFFFF' if cls.is_current_dark() else '#1D1D1F')
    
    @classmethod
    def get_accent_color(cls) -> str:
        """Get accent color for current theme."""
        config = cls.get_current_theme_config()
        
        # New schema
        if 'colors' in config:
            return config.get('colors', {}).get('accent', {}).get('primary', '#0A84FF')
        
        # Legacy
        return config.get('accent', '#0A84FF')
    
    @classmethod
    def reload_themes(cls):
        """Reload custom themes from disk."""
        THEMES.clear()
        THEMES.update(load_themes())
        
        # Also reload engine themes
        engine = cls._get_engine()
        engine.reload_themes()
    
    @classmethod
    def get_icon(cls, name: str, size: int = 24):
        """Get a themed icon."""
        engine = cls._get_engine()
        return engine.get_icon(name, size)
    
    @classmethod
    def play_sound(cls, sound_name: str):
        """Play a theme sound effect."""
        engine = cls._get_engine()
        engine.play_sound(sound_name)


# Compatibility function for legacy code
def apply_theme(widget, theme_name: str):
    """Legacy compatibility function."""
    ThemeManager.apply_theme(widget, theme_name)


