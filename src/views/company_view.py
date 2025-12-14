"""
Company Manager View - UI for managing companies.
Clean design without GroupBox to avoid visual issues.
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QListWidget, QLineEdit, QLabel,
    QFileDialog, QMessageBox, QDialog, QListWidgetItem, QFrame,
    QScrollArea
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from .components.buttons.animated_button import AnimatedButton, PrimaryButton, DangerButton
from .components.widgets.logo_widget import LogoWidget
from .components.cards import Card, CompanyListCard, ImageSelectionCard
from .styles.theme_manager import ThemeManager
from .styles.icon_manager import IconManager

from ..logic.config.config_manager import get_config
from ..logic.company.company_logic import get_company_logic, Company


class CompanyManagerView(QMainWindow):
    """Window for managing companies."""
    
    company_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.config = get_config()
        self.company_logic = get_company_logic()
        self.icon_manager = IconManager.get_instance()
        self.selected_company = None
        
        self.setWindowTitle("Gestión de Empresas")
        self.setWindowIcon(self.icon_manager.get_icon("company"))
        self.setGeometry(250, 150, 700, 500)
        self.setMinimumSize(600, 400)
        
        ThemeManager.apply_theme(self, self.config.tema)
        font_size = max(8, self.config.tamaño_fuente)  # Ensure valid font size
        self.setFont(QFont(self.config.fuente, font_size))
        
        self._create_ui()
        self._load_companies()
    
    def _create_ui(self):
        """Create the UI."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(self.icon_manager.get_pixmap("Company", 22))
        header.addWidget(header_icon)
        title = QLabel("Gestión de Empresas")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        
        btn_new = PrimaryButton("Nueva Empresa")
        btn_new.setIcon(self.icon_manager.get_icon("add", 18))
        btn_new.clicked.connect(self._new_company)
        header.addWidget(btn_new)
        
        btn_folder = AnimatedButton("Archivos")
        btn_folder.setIcon(self.icon_manager.get_icon("folder", 18))
        btn_folder.clicked.connect(self._open_folder)
        header.addWidget(btn_folder)
        
        layout.addLayout(header)
        
        # Content
        content = QHBoxLayout()
        content.setSpacing(12)
        
        # Left: List
        left = QVBoxLayout()
        list_header = QHBoxLayout()
        list_icon = QLabel()
        list_icon.setPixmap(self.icon_manager.get_pixmap("termsAndCondition", 16))
        list_header.addWidget(list_icon)
        list_header.addWidget(QLabel("Empresas:"))
        list_header.addStretch()
        left.addLayout(list_header)
        
        # Custom Scroll Area for Cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QWidget#scroll_content {
                background-color: transparent;
            }
        """)
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(0, 0, 10, 0) # Right margin for scrollbar
        self.scroll_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_content)
        left.addWidget(self.scroll_area)
        
        btn_row = QHBoxLayout()
        self.btn_edit = AnimatedButton("Editar")
        self.btn_edit.setIcon(self.icon_manager.get_icon("noteAdd", 16))
        self.btn_edit.clicked.connect(self._edit_company)
        self.btn_edit.setEnabled(False)
        btn_row.addWidget(self.btn_edit)
        
        self.btn_delete = DangerButton("Eliminar")
        self.btn_delete.setIcon(self.icon_manager.get_icon("deleteTrash", 16))
        self.btn_delete.clicked.connect(self._delete_company)
        self.btn_delete.setEnabled(False)
        btn_row.addWidget(self.btn_delete)
        left.addLayout(btn_row)
        
        content.addLayout(left, 1)
        
        # Right: Preview
        right = QVBoxLayout()
        preview_header = QHBoxLayout()
        preview_icon = QLabel()
        preview_icon.setPixmap(self.icon_manager.get_pixmap("preview", 16))
        preview_header.addWidget(preview_icon)
        preview_header.addWidget(QLabel("Vista Previa:"))
        preview_header.addStretch()
        right.addLayout(preview_header)
        
        # Wrap preview in a Card
        self.preview_card = Card()
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(12)
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo - larger for better visibility
        self.preview_logo = LogoWidget(max_width=150, max_height=100)
        preview_layout.addWidget(self.preview_logo, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Company name
        self.preview_name = QLabel("Seleccione una empresa")
        self.preview_name.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.preview_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_name)
        
        # Slogan (if any)
        self.preview_slogan = QLabel("")
        self.preview_slogan.setStyleSheet("font-size: 12px; font-style: italic; color: rgba(255,255,255,0.5);")
        self.preview_slogan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_slogan.hide()
        preview_layout.addWidget(self.preview_slogan)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(255,255,255,0.1);")
        separator.setFixedHeight(1)
        preview_layout.addWidget(separator)
        
        # Info section with labels
        self.preview_nit = QLabel("")
        self.preview_nit.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.8);")
        self.preview_nit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_nit.hide()
        preview_layout.addWidget(self.preview_nit)
        
        self.preview_address = QLabel("")
        self.preview_address.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.7);")
        self.preview_address.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_address.setWordWrap(True)
        self.preview_address.hide()
        preview_layout.addWidget(self.preview_address)
        
        self.preview_phone = QLabel("")
        self.preview_phone.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.7);")
        self.preview_phone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_phone.hide()
        preview_layout.addWidget(self.preview_phone)
        
        self.preview_email = QLabel("")
        self.preview_email.setStyleSheet("font-size: 12px; color: rgba(100,160,255,0.9);")
        self.preview_email.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_email.hide()
        preview_layout.addWidget(self.preview_email)
        
        # Placeholder text when no company selected
        self.preview_placeholder = QLabel("Haz clic en una empresa para ver sus detalles")
        self.preview_placeholder.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.4);")
        self.preview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_placeholder.setWordWrap(True)
        preview_layout.addWidget(self.preview_placeholder)
        
        self.preview_card.addLayout(preview_layout)
        right.addWidget(self.preview_card)
        right.addStretch()
        
        content.addLayout(right, 1)
        layout.addLayout(content)
    
    def _load_companies(self):
        """Load companies into the list."""
        # Clear existing items
        while self.scroll_layout.count() > 1: # Keep the stretch at the end
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Track cards for selection management
        self._company_cards = {}
        
        # Load new items
        for name in self.company_logic.get_company_names():
            company = self.company_logic.get_company(name)
            if company:
                logo_path = self.company_logic.get_logo_absolute_path(name)
                card = CompanyListCard(company.name, company.nit, logo_path)
                card.clicked.connect(self._select_company_by_name)
                card.edit_clicked.connect(self._on_card_double_click)
                # Store reference for selection management
                self._company_cards[company.name] = card
                # Insert before the stretch (which is the last item)
                self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, card)
                
        self._clear_preview()

    def _on_card_double_click(self, name):
        """Handle double click on card."""
        self._select_company_by_name(name)
        self._edit_company()

    def _open_folder(self):
        """Open the companies storage folder."""
        path = self.company_logic.get_companies_directory()
        if os.path.exists(path):
            os.startfile(path)
    
    def _clear_preview(self):
        """Clear the preview panel."""
        self.preview_logo.clear()
        self.preview_name.setText("Seleccione una empresa")
        self.preview_slogan.setText("")
        self.preview_slogan.hide()
        self.preview_nit.setText("")
        self.preview_nit.hide()
        self.preview_address.setText("")
        self.preview_address.hide()
        self.preview_phone.setText("")
        self.preview_phone.hide()
        self.preview_email.setText("")
        self.preview_email.hide()
        self.preview_placeholder.show()
    
    def _select_company_by_name(self, name):
        """Handle company selection from card with visual highlighting."""
        # Deselect previous card
        if hasattr(self, '_company_cards'):
            for card_name, card in self._company_cards.items():
                if card_name == self.selected_company:
                    card.setSelected(False)
        
        # Select new card
        self.selected_company = name
        if hasattr(self, '_company_cards') and name in self._company_cards:
            self._company_cards[name].setSelected(True)
        
        self.btn_edit.setEnabled(True)
        self.btn_delete.setEnabled(True)
        
        company = self.company_logic.get_company(self.selected_company)
        if company:
            # Hide placeholder
            self.preview_placeholder.hide()
            
            # Company name
            self.preview_name.setText(company.name)
            
            # Slogan
            if company.eslogan:
                self.preview_slogan.setText(company.eslogan)
                self.preview_slogan.show()
            else:
                self.preview_slogan.hide()
            
            # NIT
            if company.nit:
                self.preview_nit.setText(f"NIT: {company.nit}")
                self.preview_nit.show()
            else:
                self.preview_nit.hide()
            
            # Address
            if company.direccion:
                self.preview_address.setText(f"📍 {company.direccion}")
                self.preview_address.show()
            else:
                self.preview_address.hide()
            
            # Phone
            if company.telefono:
                self.preview_phone.setText(f"📞 {company.telefono}")
                self.preview_phone.show()
            else:
                self.preview_phone.hide()
            
            # Email
            if company.correo:
                self.preview_email.setText(f"✉️ {company.correo}")
                self.preview_email.show()
            else:
                self.preview_email.hide()
            
            # Logo
            logo_path = self.company_logic.get_logo_absolute_path(self.selected_company)
            if logo_path:
                self.preview_logo.setLogo(logo_path)
            else:
                self.preview_logo.clear()
    
    def _new_company(self):
        """Open dialog to create new company."""
        dialog = CompanyDialog(self)
        if dialog.exec():
            self._load_companies()
            self.company_updated.emit()
    
    def _edit_company(self):
        """Open dialog to edit selected company."""
        if self.selected_company:
            dialog = CompanyDialog(self, self.selected_company)
            if dialog.exec():
                self._load_companies()
                self.company_updated.emit()
    
    def _delete_company(self):
        """Delete the selected company."""
        if not self.selected_company:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Eliminar '{self.selected_company}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.company_logic.delete_company(self.selected_company)
            self._load_companies()
            self.selected_company = None
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self._clear_preview()
            self.company_updated.emit()


class CompanyDialog(QDialog):
    """Dialog for creating/editing a company."""
    
    def __init__(self, parent, company_name: str = None):
        super().__init__(parent)
        
        self.company_logic = get_company_logic()
        self.editing = company_name is not None
        self.original_name = company_name
        self.logo_path = ""
        
        self.setWindowTitle("Editar Empresa" if self.editing else "Nueva Empresa")
        # Ensure it's not squashed, set min size but allow growing
        self.setMinimumSize(600, 650)
        
        config = get_config()
        ThemeManager.apply_theme(self, config.tema)
        
        self._create_ui()
        
        if self.editing:
            self._load_company_data()
    
    def _create_ui(self):
        """Create the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        dialog_header = QHBoxLayout()
        dialog_icon = QLabel()
        dialog_icon.setPixmap(IconManager.get_instance().get_pixmap("company", 20))
        dialog_header.addWidget(dialog_icon)
        header_text = QLabel("Editar Empresa" if self.editing else "Nueva Empresa")
        header_text.setStyleSheet("font-size: 16px; font-weight: bold;")
        dialog_header.addWidget(header_text)
        dialog_header.addStretch()
        layout.addLayout(dialog_header)
        
        # Logo & Signature Cards
        # Use a horizontal layout for both image cards
        images_row = QHBoxLayout()
        images_row.setSpacing(20)
        
        self.logo_card = ImageSelectionCard("Logo de la Empresa")
        images_row.addWidget(self.logo_card)
        
        self.signature_card = ImageSelectionCard("Firma del Representante")
        images_row.addWidget(self.signature_card)
        
        layout.addLayout(images_row)
        
        # Form grid
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setVerticalSpacing(18)
        
        grid.addWidget(QLabel("Nombre *:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre de la empresa")
        self.name_input.setMinimumHeight(40)
        grid.addWidget(self.name_input, 0, 1)
        
        grid.addWidget(QLabel("NIT/RUC:"), 1, 0)
        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("Identificación tributaria")
        self.nit_input.setMinimumHeight(40)
        grid.addWidget(self.nit_input, 1, 1)
        
        grid.addWidget(QLabel("Dirección:"), 2, 0)
        self.address_input = QLineEdit()
        self.address_input.setMinimumHeight(40)
        grid.addWidget(self.address_input, 2, 1)
        
        grid.addWidget(QLabel("Teléfono:"), 3, 0)
        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(40)
        grid.addWidget(self.phone_input, 3, 1)
        
        grid.addWidget(QLabel("Correo:"), 4, 0)
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(40)
        grid.addWidget(self.email_input, 4, 1)
        
        grid.addWidget(QLabel("Eslogan:"), 5, 0)
        self.slogan_input = QLineEdit()
        self.slogan_input.setMinimumHeight(40)
        grid.addWidget(self.slogan_input, 5, 1)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = AnimatedButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = PrimaryButton("Guardar")
        btn_save.setIcon(IconManager.get_instance().get_icon("save", 18))
        btn_save.clicked.connect(self._save)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def _load_company_data(self):
        """Load existing company data."""
        company = self.company_logic.get_company(self.original_name)
        if company:
            self.name_input.setText(company.name)
            self.nit_input.setText(company.nit)
            self.address_input.setText(company.direccion)
            self.phone_input.setText(company.telefono)
            self.email_input.setText(company.correo)
            self.slogan_input.setText(company.eslogan)
            
            logo_path = self.company_logic.get_logo_absolute_path(self.original_name)
            if logo_path:
                self.logo_path = logo_path
                self.logo_card.setImage(logo_path)
            
            signature_path = self.company_logic.get_signature_absolute_path(self.original_name)
            if signature_path:
                self.signature_path = signature_path
                self.signature_card.setImage(signature_path)
    
    # _select_logo, _select_signature, _clear_logo, _clear_signature 
    # replaced by ImageSelectionCard internal logic and getPath() usage
    
    def _save(self):
        """Save the company, preserving logo/signature if not changed."""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return
        
        # Get existing company data if editing
        existing_logo = ""
        existing_signature = ""
        
        if self.editing:
            existing_company = self.company_logic.get_company(self.original_name)
            if existing_company:
                existing_logo = existing_company.logo
                existing_signature = existing_company.signature
        
        company = Company(
            name=name,
            direccion=self.address_input.text().strip(),
            telefono=self.phone_input.text().strip(),
            correo=self.email_input.text().strip(),
            eslogan=self.slogan_input.text().strip(),
            nit=self.nit_input.text().strip(),
            logo=existing_logo,      # Preserve existing logo by default
            signature=existing_signature # Preserve existing signature by default
        )
        
        if self.editing:
            self.company_logic.update_company(self.original_name, company)
        else:
            if not self.company_logic.add_company(company):
                QMessageBox.warning(self, "Error", "Ya existe una empresa con ese nombre.")
                return
        
        # Update Logo if changed
        new_logo_path = self.logo_card.getPath()
        if new_logo_path and os.path.exists(new_logo_path):
            current_logo_path = self.company_logic.get_logo_absolute_path(name)
            if new_logo_path != current_logo_path:
                self.company_logic.set_company_logo(name, new_logo_path)
        
        # Update Signature if changed
        new_sig_path = self.signature_card.getPath()
        if new_sig_path and os.path.exists(new_sig_path):
            current_sig_path = self.company_logic.get_signature_absolute_path(name)
            if new_sig_path != current_sig_path:
                self.company_logic.set_company_signature(name, new_sig_path)
        
        self.accept()
