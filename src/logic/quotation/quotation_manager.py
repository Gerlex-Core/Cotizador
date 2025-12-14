"""
Quotation Manager - Handles saving and loading of .cotz files.
"""

import json
import os
from datetime import datetime

class QuotationManager:
    """
    Manages the lifecycle of a quotation file (.cotz).
    """
    
    def __init__(self):
        self.current_file = None
        
    def save_quotation(self, filepath: str, data: dict):
        """
        Save the quotation data to a .cotz file (JSON).
        
        Args:
            filepath: Path to save the file
            data: Dictionary containing:
                - company_name
                - date
                - validity
                - products (list of dicts)
                - total
                - currency
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            self.current_file = filepath
            return True
        except Exception as e:
            print(f"Error saving quotation: {e}")
            return False
            
    def load_quotation(self, filepath: str) -> dict:
        """
        Load a quotation from a .cotz file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.current_file = filepath
            return data
        except Exception as e:
            print(f"Error loading quotation: {e}")
            return None
            
    def get_current_filename(self) -> str:
        if self.current_file:
            return os.path.basename(self.current_file)
        return "Sin Título"
