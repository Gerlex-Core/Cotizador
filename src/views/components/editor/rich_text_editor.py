from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QTextEdit, 
    QComboBox, QFontComboBox, QColorDialog, QToolButton, QMenu, QLabel
)
from PyQt6.QtGui import QFont, QColor, QIcon, QTextCharFormat, QAction, QTextCursor
from PyQt6.QtCore import Qt, pyqtSignal, QSize

from src.views.styles.icon_manager import IconManager

class RichTextEditor(QWidget):
    """
    A Rich Text Editor widget with a formatting toolbar.
    
    KEY BEHAVIOR:
    - In dark mode: ALL text displays as WHITE (for visibility)
    - In light mode: ALL text displays as BLACK (for visibility)
    - The "Color" button sets the EXPORT color (for PDF only)
    - Export HTML preserves the actual user-set color
    """
    
    textChanged = pyqtSignal()
    
    def __init__(self, parent=None, placeholder_text=""):
        super().__init__(parent)
        self.placeholder_text = placeholder_text
        self._is_dark_theme = True
        self._user_selected_color = None  # Track user's explicit color choice for PDF
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 2px;
                spacing: 4px;
            }
            QToolButton {
                border-radius: 4px;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QToolButton:checked {
                background-color: rgba(10, 132, 255, 0.3);
            }
        """)
        
        # Font Family
        self.font_combo = QFontComboBox()
        self.font_combo.setFixedWidth(120)
        self.font_combo.currentFontChanged.connect(self._set_font_family)
        self.toolbar.addWidget(self.font_combo)
        
        # Font Size
        self.size_combo = QComboBox()
        self.size_combo.setFixedWidth(50)
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 48]
        self.size_combo.addItems([str(s) for s in sizes])
        self.size_combo.setCurrentText("10")
        self.size_combo.textActivated.connect(self._set_font_size)
        self.toolbar.addWidget(self.size_combo)
        
        self.toolbar.addSeparator()
        
        # Bold
        self.bold_action = QAction(IconManager.get_instance().get_icon("bold", 16), "Negrita", self)
        self.bold_action.setCheckable(True)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(self._toggle_bold)
        self.toolbar.addWidget(self._create_tool_button(self.bold_action))
        
        # Italic
        self.italic_action = QAction(IconManager.get_instance().get_icon("italic", 16), "Cursiva", self)
        self.italic_action.setCheckable(True)
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.triggered.connect(self._toggle_italic)
        self.toolbar.addWidget(self._create_tool_button(self.italic_action))
        
        # Underline
        self.underline_action = QAction(IconManager.get_instance().get_icon("underline", 16), "Subrayado", self)
        self.underline_action.setCheckable(True)
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.triggered.connect(self._toggle_underline)
        self.toolbar.addWidget(self._create_tool_button(self.underline_action))

        # Strikeout
        self.strike_action = QAction(IconManager.get_instance().get_icon("strikethrough", 16), "Tachado", self)
        self.strike_action.setCheckable(True)
        self.strike_action.triggered.connect(self._toggle_strikeout)
        self.toolbar.addWidget(self._create_tool_button(self.strike_action))
        
        self.toolbar.addSeparator()
        
        # Highlight (Background Color)
        self.highlight_action = QAction(IconManager.get_instance().get_icon("fill", 16), "Resaltador", self)
        self.highlight_action.triggered.connect(self._toggle_highlight)
        self.toolbar.addWidget(self._create_tool_button(self.highlight_action))
        
        layout.addWidget(self.toolbar)
        
        layout.addWidget(self.toolbar)
        
        # Text Edit - ALWAYS uses theme-appropriate display color
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(self.placeholder_text)
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.currentCharFormatChanged.connect(self._update_toolbar_state)
        
        layout.addWidget(self.editor)
        
        # Set default font
        font = QFont("Arial", 10)
        self.editor.setCurrentFont(font)
        
        # Apply theme
        self.apply_theme()

    def _create_tool_button(self, action):
        """Create a tool button from action."""
        btn = QToolButton()
        btn.setDefaultAction(action)
        return btn

    def apply_theme(self, theme_name="Oscuro"):
        """Apply theme styles. Text is ALWAYS visible regardless of export color."""
        is_dark = "Oscuro" in theme_name or "Dark" in theme_name
        self._is_dark_theme = is_dark
        
        # Display Color: ALWAYS readable
        # Dark mode = white text, Light mode = dark text
        display_color = "#ffffff" if is_dark else "#1d1d1f"
        bg_color = "rgba(30, 30, 30, 0.8)" if is_dark else "rgba(255, 255, 255, 0.9)"
        border_color = "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.1)"
        
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {display_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 10px;
                font-family: Arial;
                font-size: 14px;
            }}
        """)
        
        # Set the editor's text color for new text
        self.editor.setTextColor(QColor(display_color))

    # === Actions ===
    
    def _set_font_family(self, font):
        self.editor.setCurrentFont(font)
        self.editor.setFocus()
        
    def _set_font_size(self, size_str):
        try:
            size = float(size_str)
            if size > 0:
                fmt = QTextCharFormat()
                fmt.setFontPointSize(size)
                self.editor.mergeCurrentCharFormat(fmt)
        except ValueError:
            pass
        self.editor.setFocus()
        
    def _toggle_bold(self):
        if self.bold_action.isChecked():
            self.editor.setFontWeight(QFont.Weight.Bold)
        else:
            self.editor.setFontWeight(QFont.Weight.Normal)
        self.editor.setFocus()
        
    def _toggle_italic(self):
        self.editor.setFontItalic(self.italic_action.isChecked())
        self.editor.setFocus()
        
    def _toggle_underline(self):
        self.editor.setFontUnderline(self.underline_action.isChecked())
        self.editor.setFocus()
        
    def _toggle_strikeout(self):
        fmt = self.editor.currentCharFormat()
        fmt.setFontStrikeOut(self.strike_action.isChecked())
        self.editor.mergeCurrentCharFormat(fmt)
        
    def _toggle_highlight(self):
        """Toggle yellow highlighter background."""
        fmt = self.editor.currentCharFormat()
        current_bg = fmt.background().color()
        
        # Check if already highlighted (yellow)
        if current_bg == QColor("#FFFF00"):
            # Remove highlight (set to transparent)
            fmt.setBackground(Qt.GlobalColor.transparent)
        else:
            # Add highlight (Yellow)
            fmt.setBackground(QColor("#FFFF00"))
            
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()
            
    # === Output ===
    
    def toHtml(self):
        """Get raw HTML from editor."""
        return self.editor.toHtml()
    
    def toExportHtml(self):
        """
        Get HTML for export (PDF/Save).
        - ALWAYS applies black as default text color for PDF.
        - Preserves highlighting (background color).
        """
        html = self.editor.toHtml()
        return RichTextEditor.sanitize_for_pdf(html)

    @staticmethod
    def sanitize_for_pdf(html: str) -> str:
        """
        Static helper to clean HTML for PDF export.
        Forces text to black while preserving highlights.
        """
        import re
        
        # 1. Force all text color to BLACK for export
        # Strip ALL color declarations (text foreground)
        # We can be aggressive here since we want NO colors except highlight.
        
        # Regex to remove color: ...; properties
        html = re.sub(r'color\s*:[^;"\']+;?', '', html, flags=re.IGNORECASE)
        
        # 2. Add style attribute to body to force black text
        export_color = "#000000"
        
        if '<body' in html:
            # If body has style attribute, add color to it
            if re.search(r'<body[^>]*style="', html):
                html = re.sub(
                    r'<body([^>]*)style="([^"]*)"',
                    f'<body\\1style="color:{export_color}; \\2"',
                    html
                )
            else:
                # Add style attribute to body
                html = re.sub(
                    r'<body([^>]*)>',
                    f'<body\\1 style="color:{export_color};">',
                    html
                )
        else:
            # No body tag? Wrap it (unlikely for QTextEdit html but possible)
            html = f'<body style="color:{export_color};">{html}</body>'
            
        return html

    def setHtml(self, html):
        self.editor.setHtml(html)
        
    def toPlainText(self):
        return self.editor.toPlainText()
        
    def setPlainText(self, text):
        self.editor.setPlainText(text)
        
    def setPlaceholderText(self, text):
        """Set placeholder text for the editor."""
        self.placeholder_text = text
        self.editor.setPlaceholderText(text)
        
    def clear(self):
        self.editor.clear()
        # Reset any specific state if needed
        
    # === Internal Signal Handling ===
    
    def _on_text_changed(self):
        self.textChanged.emit()
        
    def _update_toolbar_state(self, fmt: QTextCharFormat):
        """Update toolbar buttons based on current cursor style."""
        self.bold_action.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
        self.italic_action.setChecked(fmt.fontItalic())
        self.underline_action.setChecked(fmt.fontUnderline())
        self.strike_action.setChecked(fmt.fontStrikeOut())
