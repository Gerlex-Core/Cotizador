"""
Theme Manager for the Cotizador application.
Handles theme loading, application, and custom theme support.
"""

import os
import json
from typing import Dict, Optional


# Paths for theme files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
THEMES_DIR = os.path.join(BASE_DIR, "media", "themes")
# Legacy support
LEGACY_THEMES_DIR = os.path.join(BASE_DIR, "options", "themes", "custom")


class Theme:
    """Represents a visual theme with complete customization options."""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
    
    def get_stylesheet(self) -> str:
        """Generate the complete CSS stylesheet for this theme."""
        cfg = self.config
        
        # Base styles with modern design
        stylesheet = f"""
            /* === Global Styles === */
            QWidget {{
                background-color: {cfg.get('background', '#121212')};
                color: {cfg.get('text_primary', '#FFFFFF')};
                font-family: {cfg.get('font_family', 'Segoe UI, Arial')};
                font-size: {cfg.get('font_size', '14px')};
            }}
            
            /* === Labels === */
            QLabel {{
                color: {cfg.get('text_primary', '#FFFFFF')};
                font-weight: {cfg.get('label_weight', 'normal')};
                background-color: transparent;
                padding: 4px;
            }}
            
            /* === Buttons with Animation Support === */
            QPushButton {{
                background-color: {cfg.get('button_bg', '#333333')};
                color: {cfg.get('button_text', '#FFFFFF')};
                border: 2px solid {cfg.get('border', '#555555')};
                border-radius: {cfg.get('button_radius', '8px')};
                padding: {cfg.get('button_padding', '10px 20px')};
                font-weight: {cfg.get('button_weight', 'bold')};
                min-height: 36px;
            }}
            
            QPushButton:hover {{
                background-color: {cfg.get('accent', '#0078D4')};
                border-color: {cfg.get('accent', '#0078D4')};
                color: {cfg.get('button_hover_text', '#FFFFFF')};
            }}
            
            QPushButton:pressed {{
                background-color: {cfg.get('accent_dark', '#005a9e')};
                /* Note: transform removed as it is not supported in standard Qt CSS */
            }}
            
            QPushButton:disabled {{
                background-color: {cfg.get('disabled_bg', '#222222')};
                color: {cfg.get('disabled_text', '#666666')};
                border-color: {cfg.get('disabled_border', '#333333')};
            }}
            
            /* === Input Fields === */
            QLineEdit {{
                background-color: {cfg.get('input_bg', cfg.get('background', '#1a1a1a'))};
                color: {cfg.get('text_primary', '#FFFFFF')};
                border: 2px solid {cfg.get('border', '#555555')};
                border-radius: 6px;
                padding: 8px 12px;
                selection-background-color: {cfg.get('accent', '#0078D4')};
                min-height: 36px; /* Added to fix visibility issue */
            }}
            
            QLineEdit:focus {{
                border-color: {cfg.get('accent', '#0078D4')};
            }}
            
            QLineEdit:disabled {{
                background-color: {cfg.get('disabled_bg', '#222222')};
                color: {cfg.get('disabled_text', '#666666')};
            }}
            
            /* === ComboBox === */
            QComboBox {{
                background-color: {cfg.get('input_bg', cfg.get('background', '#1a1a1a'))};
                color: {cfg.get('text_primary', '#FFFFFF')};
                border: 2px solid {cfg.get('border', '#555555')};
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 36px;
                selection-background-color: {cfg.get('accent', '#0078D4')};
            }}
            
            QComboBox:hover {{
                border-color: {cfg.get('accent', '#0078D4')};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border: none;
                /* Arrow created with border trick */
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid {cfg.get('text_primary', '#FFFFFF')};
                margin-right: 10px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {cfg.get('menu_bg', cfg.get('background', '#1a1a1a'))};
                color: {cfg.get('text_primary', '#FFFFFF')};
                border: 1px solid {cfg.get('border', '#555555')};
                selection-background-color: {cfg.get('accent', '#0078D4')};
                selection-color: {cfg.get('button_text', '#FFFFFF')};
                outline: none;
            }}
            
            /* === Menu Bar === */
            QMenuBar {{
                background-color: {cfg.get('menubar_bg', cfg.get('background', '#0d0d0d'))};
                color: {cfg.get('text_primary', '#FFFFFF')};
                border-bottom: 1px solid {cfg.get('border', '#333333')};
                padding: 4px;
            }}
            
            QMenuBar::item {{
                padding: 6px 12px;
                border-radius: 4px;
                background-color: transparent;
            }}
            
            QMenuBar::item:selected {{
                background-color: {cfg.get('accent', '#0078D4')};
            }}
            
            /* === Menus === */
            QMenu {{
                background-color: {cfg.get('menu_bg', cfg.get('background', '#1a1a1a'))};
                color: {cfg.get('text_primary', '#FFFFFF')};
                border: 1px solid {cfg.get('border', '#444444')};
                border-radius: 8px;
                padding: 8px;
            }}
            
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
            }}
            
            QMenu::item:selected {{
                background-color: {cfg.get('accent', '#0078D4')};
            }}
            
            /* === Table Widget === */
            QTableWidget {{
                background-color: {cfg.get('table_bg', cfg.get('background', '#151515'))};
                color: {cfg.get('text_primary', '#FFFFFF')};
                gridline-color: {cfg.get('border', '#333333')};
                border: 1px solid {cfg.get('border', '#333333')};
                border-radius: 8px;
                selection-background-color: {cfg.get('accent', '#0078D4')};
                selection-color: {cfg.get('button_text', '#FFFFFF')};
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {cfg.get('border', '#333333')};
            }}
            
            QTableWidget::item:hover {{
                background-color: {cfg.get('table_hover', 'rgba(255,255,255,0.05)')};
            }}
            
            QTableWidget::item:selected {{
                background-color: {cfg.get('accent', '#0078D4')};
            }}
            
            QHeaderView::section {{
                background-color: {cfg.get('header_bg', '#1a1a1a')};
                color: {cfg.get('text_primary', '#FFFFFF')};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {cfg.get('accent', '#0078D4')};
                font-weight: bold;
            }}
            
            /* === Scroll Bars === */
            QScrollBar:vertical {{
                background-color: {cfg.get('background', '#121212')};
                width: 12px;
                margin: 0px;
                border-radius: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {cfg.get('scrollbar', '#444444')};
                border-radius: 6px;
                min-height: 30px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {cfg.get('accent', '#0078D4')};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            /* === List Widget === */
            QListWidget {{
                background-color: {cfg.get('table_bg', cfg.get('background', '#151515'))};
                color: {cfg.get('text_primary', '#FFFFFF')};
                border: 1px solid {cfg.get('border', '#333333')};
                border-radius: 8px;
                padding: 4px;
            }}
            
            QListWidget::item {{
                padding: 10px;
                border-radius: 4px;
                margin: 2px;
            }}
            
            QListWidget::item:hover {{
                background-color: {cfg.get('table_hover', 'rgba(255,255,255,0.05)')};
            }}
            
            QListWidget::item:selected {{
                background-color: {cfg.get('accent', '#0078D4')};
            }}
            
            /* === Dialog === */
            QDialog {{
                background-color: {cfg.get('background', '#121212')};
            }}
            
            /* === Message Box === */
            QMessageBox {{
                background-color: {cfg.get('background', '#121212')};
            }}
            
            QMessageBox QLabel {{
                color: {cfg.get('text_primary', '#FFFFFF')};
            }}
            
            QMessageBox QPushButton {{
                min-width: 80px;
            }}
            
            /* === TextEdit === */
            QTextEdit {{
                background-color: {cfg.get('input_bg', cfg.get('background', '#1a1a1a'))};
                color: {cfg.get('text_primary', '#FFFFFF')};
                border: 2px solid {cfg.get('border', '#555555')};
                border-radius: 8px;
                padding: 10px;
                selection-background-color: {cfg.get('accent', '#0078D4')};
            }}
            
            QTextEdit:focus {{
                border-color: {cfg.get('accent', '#0078D4')};
            }}
            
            /* === SpinBox === */
            QSpinBox, QDoubleSpinBox {{
                background-color: {cfg.get('input_bg', cfg.get('background', '#1a1a1a'))};
                color: {cfg.get('text_primary', '#FFFFFF')};
                border: 2px solid {cfg.get('border', '#555555')};
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 36px;
            }}
            
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {cfg.get('accent', '#0078D4')};
            }}
            
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border: none;
                background-color: rgba(255, 255, 255, 0.05);
                border-top-right-radius: 5px;
            }}
            
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border: none;
                background-color: rgba(255, 255, 255, 0.05);
                border-bottom-right-radius: 5px;
            }}
            
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {cfg.get('accent', '#0078D4')};
            }}
            
            /* === GroupBox === */
            QGroupBox {{
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid {cfg.get('border', '#444444')};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                background-color: {cfg.get('accent', '#0078D4')};
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }}
            
            /* === ToolTip === */
            QToolTip {{
                background-color: {cfg.get('menu_bg', '#1a1a1a')};
                color: {cfg.get('text_primary', '#FFFFFF')};
                border: 1px solid {cfg.get('border', '#444444')};
                border-radius: 4px;
                padding: 6px 10px;
            }}
        """
        
        # Add background image if specified
        if cfg.get('background_image'):
            stylesheet += f"""
                QWidget#centralWidget {{
                    background-image: url({cfg['background_image']});
                    background-repeat: no-repeat;
                    background-position: center;
                }}
            """
        
        return stylesheet


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
                            
                        # Validate required keys
                        required = ['name', 'background', 'text_primary', 'accent']
                        if all(key in data for key in required):
                            loaded_themes[data['name']] = Theme(data['name'], data)
                    except Exception as e:
                        print(f"Error loading theme {filename}: {e}")
    
    return loaded_themes


# Load themes on module import
THEMES.update(load_themes())


class ThemeManager:
    """Manages theme application and switching with enhanced config support."""
    
    _current_theme: str = "Oscuro"
    _current_config: Dict = {}
    
    @classmethod
    def get_available_themes(cls) -> list:
        """Get list of available theme names."""
        themes = list(THEMES.keys())
        themes.sort()
        return themes
    
    @classmethod
    def get_theme(cls, name: str) -> Optional[Theme]:
        """Get a theme by name."""
        return THEMES.get(name)
    
    @classmethod
    def get_theme_config(cls, name: str) -> Dict:
        """Get theme configuration dict by name."""
        theme = THEMES.get(name)
        if theme:
            return theme.config
        return {}
    
    @classmethod
    def apply_theme(cls, widget, theme_name: str):
        """Apply a theme to a widget."""
        theme = THEMES.get(theme_name)
        if not theme and THEMES:
            # Fallback to first available if requested missing
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
        # Otherwise check background luminance
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
        return config.get('text_primary', '#FFFFFF' if cls.is_current_dark() else '#1D1D1F')
    
    @classmethod
    def get_accent_color(cls) -> str:
        """Get accent color for current theme."""
        config = cls.get_current_theme_config()
        return config.get('accent', '#0A84FF')
    
    @classmethod
    def reload_themes(cls):
        """Reload custom themes from disk."""
        THEMES.clear()
        THEMES.update(load_themes())


# Compatibility function for legacy code
def apply_theme(widget, theme_name: str):
    """Legacy compatibility function."""
    ThemeManager.apply_theme(widget, theme_name)

