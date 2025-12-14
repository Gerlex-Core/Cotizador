"""
Themed Table Components - Tables with full theme support, animations, and effects.
"""

from PyQt6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, pyqtProperty
from PyQt6.QtGui import QColor

from src.views.styles.theme_base import ThemeConfig


class ThemedTable(QTableWidget):
    """
    Themed table widget with:
    - Theme-aware styling
    - Row animations
    - Header glow effects
    - Transparent background support
    """
    
    def __init__(self, parent=None, theme_config: ThemeConfig = None):
        super().__init__(parent)
        
        self._theme = theme_config
        
        # Default setup
        self.setShowGrid(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        
        if theme_config:
            self.apply_theme(theme_config)
    
    def apply_theme(self, config: ThemeConfig):
        """Apply theme configuration."""
        self._theme = config
        
        bg = config.get('table_bg', '#2C2C2E')
        text_color = config.get('text_primary', '#FFFFFF')
        border = config.get('border', '#3A3A3C')
        accent = config.get('accent', '#0A84FF')
        header_bg = config.get('header_bg', '#1C1C1E')
        hover = config.get('table_hover', 'rgba(255,255,255,0.05)')
        radius = config.get('corner_radius', 8)
        
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {bg};
                color: {text_color};
                gridline-color: {border};
                border: 1px solid {border};
                border-radius: {radius}px;
                selection-background-color: {accent};
                alternate-background-color: rgba(255, 255, 255, 0.02);
            }}
            QTableWidget::item {{
                padding: 10px 8px;
                border-bottom: 1px solid {border};
            }}
            QTableWidget::item:hover {{
                background-color: {hover};
            }}
            QTableWidget::item:selected {{
                background-color: {accent};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: {text_color};
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {accent};
                font-weight: bold;
            }}
            QScrollBar:vertical {{
                background-color: {bg};
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {config.get('scrollbar', '#48484A')};
                border-radius: 6px;
                min-height: 30px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {accent};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
    
    def insertAnimatedRow(self, row: int = -1) -> int:
        """Insert a row with animation."""
        if row < 0:
            row = self.rowCount()
        
        self.insertRow(row)
        
        # Animate row height
        self.setRowHeight(row, 0)
        target_height = 45
        
        # Simple height animation using timer
        from PyQt6.QtCore import QTimer
        current = [0]
        
        def animate():
            current[0] += 5
            if current[0] >= target_height:
                self.setRowHeight(row, target_height)
                timer.stop()
            else:
                self.setRowHeight(row, current[0])
        
        timer = QTimer(self)
        timer.timeout.connect(animate)
        timer.start(16)  # ~60fps
        
        return row
    
    def removeAnimatedRow(self, row: int):
        """Remove a row with animation."""
        if row < 0 or row >= self.rowCount():
            return
        
        from PyQt6.QtCore import QTimer
        current = [self.rowHeight(row)]
        
        def animate():
            current[0] -= 5
            if current[0] <= 0:
                self.removeRow(row)
                timer.stop()
            else:
                self.setRowHeight(row, current[0])
        
        timer = QTimer(self)
        timer.timeout.connect(animate)
        timer.start(16)
    
    def getProducts(self) -> list:
        """Get all products from the table as list of tuples."""
        products = []
        for row in range(self.rowCount()):
            row_data = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                widget = self.cellWidget(row, col)
                
                if widget and hasattr(widget, 'currentText'):
                    row_data.append(widget.currentText())
                elif item:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            
            products.append(tuple(row_data))
        
        return products


class GlassTable(ThemedTable):
    """Table with glass effect for glassmorphism themes."""
    
    def apply_theme(self, config: ThemeConfig):
        """Apply glass theme."""
        self._theme = config
        
        text_color = config.get('text_primary', '#FFFFFF')
        accent = config.get('accent', '#00D4FF')
        border = config.get('border', 'rgba(100, 180, 255, 0.35)')
        
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: rgba(25, 45, 80, 0.4);
                color: {text_color};
                gridline-color: rgba(100, 180, 255, 0.2);
                border: 1px solid {border};
                border-radius: 12px;
                selection-background-color: {accent};
            }}
            QTableWidget::item {{
                padding: 10px 8px;
                border-bottom: 1px solid rgba(100, 180, 255, 0.15);
            }}
            QTableWidget::item:hover {{
                background-color: rgba(0, 212, 255, 0.1);
            }}
            QTableWidget::item:selected {{
                background-color: {accent};
                color: white;
            }}
            QHeaderView::section {{
                background-color: rgba(30, 55, 95, 0.6);
                color: {text_color};
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {accent};
                font-weight: bold;
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 10px;
            }}
            QScrollBar::handle:vertical {{
                background-color: rgba(100, 180, 255, 0.4);
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {accent};
            }}
        """)
