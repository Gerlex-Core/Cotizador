"""
Quotation Logic - Business logic for quotation management.
Separates data handling from UI concerns.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Product:
    """Represents a product in a quotation."""
    description: str = ""
    quantity: float = 0.0
    unit: str = "unidad (u)"
    price: float = 0.0
    
    @property
    def amount(self) -> float:
        """Calculate the line item amount."""
        return self.quantity * self.price
    
    def to_list(self) -> list:
        """Convert to list format for table/PDF."""
        return [
            self.description,
            str(self.quantity),
            self.unit,
            f"{self.price:.2f}",
            f"{self.amount:.2f}"
        ]
    
    @classmethod
    def from_list(cls, data: list) -> 'Product':
        """Create Product from list data."""
        return cls(
            description=data[0] if len(data) > 0 else "",
            quantity=float(data[1]) if len(data) > 1 and data[1] else 0.0,
            unit=data[2] if len(data) > 2 else "unidad (u)",
            price=float(data[3]) if len(data) > 3 and data[3] else 0.0
        )


@dataclass
class Quotation:
    """Represents a complete quotation."""
    company_name: str = ""
    company_data: dict = field(default_factory=dict)
    products: List[Product] = field(default_factory=list)
    date: str = field(default_factory=lambda: datetime.today().strftime("%d/%m/%Y"))
    currency: str = "Bolivianos (Bs)"
    
    @property
    def total(self) -> float:
        """Calculate the total amount of the quotation."""
        return sum(product.amount for product in self.products)
    
    def add_product(self, product: Product):
        """Add a product to the quotation."""
        self.products.append(product)
    
    def remove_product(self, index: int) -> Optional[Product]:
        """Remove a product by index."""
        if 0 <= index < len(self.products):
            return self.products.pop(index)
        return None
    
    def update_product(self, index: int, product: Product):
        """Update a product at the given index."""
        if 0 <= index < len(self.products):
            self.products[index] = product
    
    def get_products_as_lists(self) -> List[list]:
        """Get all products as list of lists for PDF generation."""
        return [product.to_list() for product in self.products]
    
    def clear(self):
        """Clear all products."""
        self.products.clear()


class QuotationLogic:
    """
    Business logic for quotation operations.
    Manages the current quotation state and calculations.
    """
    
    def __init__(self):
        self._quotation = Quotation()
    
    @property
    def quotation(self) -> Quotation:
        """Get the current quotation."""
        return self._quotation
    
    def set_company(self, name: str, data: dict):
        """Set the company for the quotation."""
        self._quotation.company_name = name
        self._quotation.company_data = data
    
    def set_currency(self, currency: str):
        """Set the currency for the quotation."""
        self._quotation.currency = currency
    
    def set_date(self, date: str):
        """Set the quotation date."""
        self._quotation.date = date
    
    def add_product(self, description: str = "", quantity: float = 0.0,
                    unit: str = "unidad (u)", price: float = 0.0) -> Product:
        """Add a new product and return it."""
        product = Product(
            description=description,
            quantity=quantity,
            unit=unit,
            price=price
        )
        self._quotation.add_product(product)
        return product
    
    def remove_product(self, index: int) -> bool:
        """Remove a product by index. Returns True if successful."""
        return self._quotation.remove_product(index) is not None
    
    def update_product(self, index: int, description: str = None,
                       quantity: float = None, unit: str = None,
                       price: float = None):
        """Update specific fields of a product."""
        if 0 <= index < len(self._quotation.products):
            product = self._quotation.products[index]
            if description is not None:
                product.description = description
            if quantity is not None:
                product.quantity = quantity
            if unit is not None:
                product.unit = unit
            if price is not None:
                product.price = price
    
    def get_total(self) -> float:
        """Get the total amount."""
        return self._quotation.total
    
    def get_formatted_total(self) -> str:
        """Get the total formatted with currency."""
        return f"{self._quotation.total:.2f} {self._quotation.currency}"
    
    def calculate_amount(self, quantity: float, price: float) -> float:
        """Calculate amount for given quantity and price."""
        return quantity * price
    
    def validate_product(self, product: Product) -> List[str]:
        """Validate a product and return list of errors."""
        errors = []
        if not product.description.strip():
            errors.append("La descripción es requerida")
        if product.quantity <= 0:
            errors.append("La cantidad debe ser mayor a 0")
        if product.price < 0:
            errors.append("El precio no puede ser negativo")
        return errors
    
    def is_valid(self) -> tuple:
        """Check if quotation is valid. Returns (valid, errors)."""
        errors = []
        
        if not self._quotation.company_name:
            errors.append("Debe seleccionar una empresa")
        
        if not self._quotation.products:
            errors.append("Debe agregar al menos un producto")
        
        for i, product in enumerate(self._quotation.products):
            product_errors = self.validate_product(product)
            for error in product_errors:
                errors.append(f"Producto {i+1}: {error}")
        
        return len(errors) == 0, errors
    
    def prepare_pdf_data(self) -> dict:
        """Prepare all data needed for PDF generation."""
        return {
            "empresa": self._quotation.company_name,
            "datos_empresa": self._quotation.company_data,
            "productos": self._quotation.get_products_as_lists(),
            "total": self._quotation.total,
            "moneda": self._quotation.currency,
            "fecha": self._quotation.date
        }
    
    def clear(self):
        """Clear the current quotation."""
        self._quotation = Quotation()
    
    def new_quotation(self):
        """Start a new quotation."""
        self.clear()
