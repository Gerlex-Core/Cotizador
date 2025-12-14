"""
Icon Manager - Handles dynamic icon loading and theme-aware coloring.
Supports PNG icons (Win11 Color style from iconos8.es).
"""

import os
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt6.QtCore import Qt, QSize

class IconManager:
    """
    Manages loading of PNG icons with optional theme-based coloring.
    Icons are stored in media/icons/ folder at 96x96 resolution.
    """
    
    _instance = None
    
    # Icon name mappings for semantic access
    ICON_NAMES = {
        # Actions
        "add": "add",
        "addItem": "addItem",
        "save": "save",
        "delete": "delete",
        "deleteTrash": "deleteTrash",
        "clear": "clear",
        "copy": "copyPaste",
        "cancel": "cancel",
        "check": "check",
        "checkgreen": "checkgreen",
        "back": "back",
        "back1": "back1",
        "openFolder": "openFolder",
        "saveAs": "saveAs",
        
        # Documents & History
        "pdf": "pdf",
        "note": "note",
        "noteAdd": "noteAdd",
        "preview": "preview",
        "termsAndCondition": "termsAndCondition",
        "history": "history",
        "recent": "history",
        "time": "history", 
        
        # Business
        "box": "box",
        "money": "money",
        "bank": "bank",
        "paymentMethod": "paymentMethod",
        "delivery": "delivery",
        "imageCompany": "imageCompany",
        "imageProducts": "imageProducts",
        "company": "company",
        
        # Protection
        "shield": "shield",
        "shieldOk": "shieldOk",
        "shieldWarning": "shieldWarning",
        "warranty": "warranty",
        
        # Settings & Tools
        "settings": "settings",
        "maintenance": "maintenance",
        "theme": "theme",
        "filter": "filter",
        "search": "search",
        
        # Status
        "checkverif": "checkverif",
        "cancelverif": "cancelverif",
        "highPriority": "highPriority",
        "warninCircle": "warninCircle",
        "forbidden": "forbidden",
        
        # Contact & Location
        "phone": "phone",
        "mail": "mail",
        "direction": "direction",
        "worldWideLocation": "worldWideLocation",
        "calendar": "calendar",
        
        # Media
        "image": "image",
        
        # Formatting
        "bold": "bold",
        "italic": "italic",
        "underline": "underline",
        "strikethrough": "strikethrough",
        "palette": "palette",
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IconManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        """Initialize the manager."""
        # Navigate from src/views/styles to project root
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.icons_dir = os.path.join(self.base_dir, "media", "icons")
        self.current_color = "#FFFFFF"  # Default to white
        self._icon_cache = {}  # Cache for loaded icons
        
    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_theme_color(self, color: str):
        """Set the current icon color based on theme."""
        self.current_color = color
        self._icon_cache.clear()  # Clear cache when theme changes
    
    def get_pixmap(self, name: str, size: int = 24) -> QPixmap:
        """
        Get a pixmap for an icon (original colors preserved).
        
        Args:
            name: Icon name (e.g. 'save', 'box')
            size: Desired size (width and height)
        
        Returns:
            QPixmap scaled to the requested size
        """
        # Resolve icon name
        icon_file = self.ICON_NAMES.get(name, name)
        path = os.path.join(self.icons_dir, f"{icon_file}.png")
        
        if not os.path.exists(path):
            # Try direct name
            path = os.path.join(self.icons_dir, f"{name}.png")
            if not os.path.exists(path):
                return QPixmap()
        
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return QPixmap()
        
        # Scale to requested size with smooth transformation
        return pixmap.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
    def get_icon(self, name: str, size: int = 24) -> QIcon:
        """
        Get an icon (original colors preserved - Win11 Color style).
        
        Args:
            name: Icon name (e.g. 'save', 'box', 'money')
            size: Desired icon size
            
        Returns:
            QIcon with the colored icon
        """
        cache_key = f"{name}_{size}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        pixmap = self.get_pixmap(name, size)
        if pixmap.isNull():
            return QIcon()
        
        icon = QIcon(pixmap)
        self._icon_cache[cache_key] = icon
        return icon
    
    def get_colored_icon(self, name: str, color: str = None, size: int = 24) -> QIcon:
        """
        Get an icon with custom color overlay (for monochrome icons).
        
        Args:
            name: Icon name
            color: Hex color (e.g. '#FFFFFF'). If None, uses theme color.
            size: Icon size
            
        Returns:
            QIcon with color applied
        """
        target_color = color if color else self.current_color
        cache_key = f"{name}_{size}_{target_color}"
        
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        pixmap = self.get_pixmap(name, size)
        if pixmap.isNull():
            return QIcon()
        
        # Apply color overlay
        colored_pixmap = self._colorize_pixmap(pixmap, target_color)
        icon = QIcon(colored_pixmap)
        self._icon_cache[cache_key] = icon
        return icon
        
    def _colorize_pixmap(self, pixmap: QPixmap, color_str: str) -> QPixmap:
        """Apply color overlay to pixmap (useful for monochrome icons)."""
        if not color_str:
            return pixmap
            
        result = QPixmap(pixmap.size())
        result.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Draw original
        painter.drawPixmap(0, 0, pixmap)
        
        # Apply color overlay
        painter.setCompositionMode(QPainter.CompositionMode.SourceIn)
        painter.fillRect(result.rect(), QColor(color_str))
        
        painter.end()
        
        return result

    def list_available_icons(self) -> list:
        """List all available icon names."""
        icons = []
        if os.path.exists(self.icons_dir):
            for f in os.listdir(self.icons_dir):
                if f.endswith('.png'):
                    icons.append(f[:-4])  # Remove .png extension
        return sorted(icons)
