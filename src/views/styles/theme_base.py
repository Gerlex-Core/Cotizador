"""
Theme Base Module - Core theme configuration and utilities.
Provides enhanced theme support with transparency, animations, and glow effects.
"""

from typing import Dict, Any, Optional
from PyQt6.QtGui import QColor


def get_luminance(color: str) -> float:
    """Calculate luminance of a color to determine if it's light or dark."""
    if color.startswith('rgba'):
        # Extract RGB from rgba
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
        return 0.5  # Default middle
    
    # Calculate relative luminance
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def is_dark_theme(config: Dict[str, Any]) -> bool:
    """Determine if a theme is dark based on background color."""
    bg = config.get('background', '#121212')
    if config.get('is_dark') is not None:
        return config.get('is_dark')
    return get_luminance(bg) < 0.5


def get_contrast_color(config: Dict[str, Any]) -> str:
    """Get contrasting text color based on theme brightness."""
    if is_dark_theme(config):
        return config.get('text_primary', '#FFFFFF')
    else:
        return config.get('text_primary', '#1D1D1F')


def ensure_contrast(config: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure text colors have proper contrast with backgrounds."""
    enhanced = config.copy()
    
    # Auto-set text color if not specified correctly
    if is_dark_theme(config):
        if 'text_primary' not in config:
            enhanced['text_primary'] = '#FFFFFF'
        if 'text_secondary' not in config:
            enhanced['text_secondary'] = 'rgba(255, 255, 255, 0.7)'
    else:
        if 'text_primary' not in config:
            enhanced['text_primary'] = '#1D1D1F'
        if 'text_secondary' not in config:
            enhanced['text_secondary'] = 'rgba(0, 0, 0, 0.6)'
    
    return enhanced


class ThemeConfig:
    """Enhanced theme configuration with advanced effects support."""
    
    # Default values for all theme properties
    DEFAULTS = {
        # Base colors
        'background': '#1C1C1E',
        'background_solid': '#1C1C1E',
        'text_primary': '#FFFFFF',
        'text_secondary': '#8E8E93',
        
        # Button styling
        'button_bg': '#2C2C2E',
        'button_text': '#FFFFFF',
        'button_hover_text': '#FFFFFF',
        'button_radius': '8px',
        'button_padding': '10px 20px',
        'button_weight': '600',
        
        # Borders and accents
        'border': '#3A3A3C',
        'accent': '#0A84FF',
        'accent_dark': '#0064D2',
        'accent_glow': 'rgba(10, 132, 255, 0.4)',
        
        # Component backgrounds
        'menu_bg': '#2C2C2E',
        'menubar_bg': '#1C1C1E',
        'table_bg': '#2C2C2E',
        'table_hover': 'rgba(255,255,255,0.05)',
        'header_bg': '#1C1C1E',
        'input_bg': '#2C2C2E',
        
        # Disabled state
        'disabled_bg': '#1C1C1E',
        'disabled_text': '#48484A',
        'disabled_border': '#2C2C2E',
        
        # Typography
        'font_family': 'Segoe UI, Arial',
        'font_size': '14px',
        'label_weight': 'normal',
        
        # Advanced effects
        'transparency': 0.0,
        'glassmorphism': False,
        'glow_enabled': False,
        'glow_color': '#0A84FF',
        'glow_intensity': 0.3,
        'blur_enabled': False,
        'blur_intensity': 10,
        'corner_radius': 8,
        
        # Animation
        'animation_speed': 1.0,
        'hover_scale': 1.02,
        'press_scale': 0.98,
        
        # Panel styling
        'panel_bg': 'rgba(255, 255, 255, 0.05)',
        'panel_border': 'rgba(255, 255, 255, 0.1)',
        'panel_glow': 'rgba(10, 132, 255, 0.1)',
        
        # Card styling
        'card_bg': 'rgba(255, 255, 255, 0.08)',
        'card_border': 'rgba(255, 255, 255, 0.12)',
        'card_shadow': 'rgba(0, 0, 0, 0.3)',
        
        # Gradients
        'gradient_start': '#2C2C2E',
        'gradient_end': '#1C1C1E',
        'gradient_accent_start': '#0A84FF',
        'gradient_accent_end': '#0064D2',
        
        # Scrollbar
        'scrollbar': '#48484A',
    }
    
    def __init__(self, config: Dict[str, Any]):
        self._config = ensure_contrast(config)
        self._is_dark = is_dark_theme(self._config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value with fallback to defaults."""
        if key in self._config:
            return self._config[key]
        if key in self.DEFAULTS:
            return self.DEFAULTS[key]
        return default
    
    @property
    def is_dark(self) -> bool:
        return self._is_dark
    
    @property
    def has_transparency(self) -> bool:
        return self.get('transparency', 0) > 0 or self.get('glassmorphism', False)
    
    @property
    def has_glow(self) -> bool:
        return self.get('glow_enabled', False)
    
    @property
    def has_animations(self) -> bool:
        return self.get('animation_speed', 1.0) > 0
    
    @property
    def animation_duration(self) -> int:
        """Get animation duration in ms, scaled by animation_speed."""
        base_duration = 200
        speed = self.get('animation_speed', 1.0)
        return int(base_duration / max(speed, 0.1))
    
    def get_qcolor(self, key: str) -> QColor:
        """Get a config value as QColor."""
        color_str = self.get(key, '#FFFFFF')
        if color_str.startswith('rgba'):
            # Parse rgba(r, g, b, a)
            parts = color_str.replace('rgba(', '').replace(')', '').split(',')
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
            a = float(parts[3].strip()) if len(parts) > 3 else 1.0
            color = QColor(r, g, b)
            color.setAlphaF(a)
            return color
        else:
            return QColor(color_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Get full config as dict with defaults applied."""
        result = self.DEFAULTS.copy()
        result.update(self._config)
        return result
