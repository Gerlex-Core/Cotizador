"""
Company Logic - Business logic for company management.
Handles company data storage using .emp (ZIP) format.
"""

import os
import shutil
import json
import zipfile
import glob
from dataclasses import dataclass
from typing import Dict, List, Optional


# Paths

CONFIG_DIR = os.path.join("media", "config")
COMPANIES_DIR = os.path.join("media", "companies")  # New directory for .emp files
MEDIA_DIR = os.path.join("media")
LOGOS_DIR = os.path.join(MEDIA_DIR, "logos")
LEGACY_COMPANIES_FILE = os.path.join("media", "companies.conf")


@dataclass
class Company:
    """Represents a company with all its data."""
    name: str
    direccion: str = ""
    telefono: str = ""
    correo: str = ""
    eslogan: str = ""
    logo: str = ""      # Path to logo inside the zip (or relative path for migration)
    signature: str = "" # Path to signature inside the zip
    nit: str = ""       # NIT/RUC/Tax ID
    
    # Internal paths used when company is loaded
    _logo_temp_path: str = "" 
    _signature_temp_path: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "correo": self.correo,
            "eslogan": self.eslogan,
            "nit": self.nit,
            # We don't store absolute paths in JSON, just flags or relative names if needed
            "has_logo": bool(self.logo),
            "has_signature": bool(self.signature)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Company':
        """Create Company from dictionary."""
        return cls(
            name=data.get("name", "Empresa"),
            direccion=data.get("direccion", ""),
            telefono=data.get("telefono", ""),
            correo=data.get("correo", ""),
            eslogan=data.get("eslogan", ""),
            nit=data.get("nit", ""),
            logo="logo.png" if data.get("has_logo") else "",
            signature="signature.png" if data.get("has_signature") else ""
        )


class CompanyLogic:
    """
    Business logic for company management.
    Uses .emp (ZIP) file format for persistence.
    Structure of .emp file:
        - data.json
        - logo.png (optional)
        - signature.png (optional)
    """
    
    def __init__(self):
        self._companies: Dict[str, Company] = {}
        self._temp_dir = os.path.join(CONFIG_DIR, "temp_companies")
        
        # Ensure directories exist
        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(COMPANIES_DIR, exist_ok=True)
        os.makedirs(self._temp_dir, exist_ok=True)
        
        # Load or migrate
        self._initialize()
    
    def _initialize(self):
        """Initialize by loading data or migrating from legacy format."""
        # Check for legacy file
        if os.path.exists(LEGACY_COMPANIES_FILE):
             self._migrate_from_conf()
        
        self._load_all_companies()
    
    def _migrate_from_conf(self):
        """Migrate from legacy .conf format to .emp files."""
        import configparser
        print("Migrating companies from .conf to .emp...")
        
        config = configparser.ConfigParser()
        config.read(LEGACY_COMPANIES_FILE, encoding='utf-8')
        
        for section in config.sections():
            data = dict(config.items(section))
            
            # Create temp company object
            company = Company(
                name=section,
                direccion=data.get("direccion", ""),
                telefono=data.get("telefono", ""),
                correo=data.get("correo", ""),
                eslogan=data.get("eslogan", ""),
                nit=data.get("nit", ""),
                logo=data.get("logo", "")
            )
            
            # Save as .emp
            self.save_company(company)
            
            # If it had a logo in the old 'media/logos' path, try to embed it
            if company.logo:
                 old_logo_path = os.path.join(MEDIA_DIR, company.logo)
                 if os.path.exists(old_logo_path):
                     self.set_company_logo(company.name, old_logo_path)
        
        # Rename legacy file to avoid re-migration
        try:
            os.rename(LEGACY_COMPANIES_FILE, LEGACY_COMPANIES_FILE + ".bak")
        except:
            pass
            
    def _get_emp_path(self, company_name: str) -> str:
        """Get path for company .emp file."""
        safe_name = "".join([c for c in company_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        return os.path.join(COMPANIES_DIR, f"{safe_name}.emp")

    def _cleanup_temp(self):
        """Clean up temp directory."""
        if os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
                os.makedirs(self._temp_dir, exist_ok=True)
            except:
                pass

    def _load_all_companies(self):
        """Load all .emp files from companies directory."""
        self._companies.clear()
        emp_files = glob.glob(os.path.join(COMPANIES_DIR, "*.emp"))
        
        for emp_file in emp_files:
            try:
                company = self._load_single_company(emp_file)
                if company:
                    self._companies[company.name] = company
            except Exception as e:
                print(f"Error loading {emp_file}: {e}")

    def _load_single_company(self, filepath: str) -> Optional[Company]:
        """Load a single company from .emp file."""
        try:
            # Create a localized temp dir for this company to extract assets
            base_name = os.path.basename(filepath)
            comp_temp_dir = os.path.join(self._temp_dir, base_name.replace('.emp', ''))
            os.makedirs(comp_temp_dir, exist_ok=True)
            
            with zipfile.ZipFile(filepath, 'r') as zf:
                # Read data
                json_data = zf.read("data.json").decode('utf-8')
                data = json.loads(json_data)
                
                company = Company.from_dict(data)
                
                # Extract logo if exists
                if company.logo:
                    # Look for any image file starting with 'logo'
                    for name in zf.namelist():
                         if name.startswith("logo."):
                             zf.extract(name, comp_temp_dir)
                             company._logo_temp_path = os.path.join(comp_temp_dir, name)
                             company.logo = name # keep relative name
                             break
                
                # Extract signature if exists
                if company.signature:
                    for name in zf.namelist():
                         if name.startswith("signature."):
                             zf.extract(name, comp_temp_dir)
                             company._signature_temp_path = os.path.join(comp_temp_dir, name)
                             company.signature = name
                             break
                
                return company
        except Exception as e:
            print(f"Error reading company file {filepath}: {e}")
            return None

    def save_company(self, company: Company) -> bool:
        """Save company to .emp file."""
        try:
            filepath = self._get_emp_path(company.name)
            
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Save JSON
                json_data = json.dumps(company.to_dict(), indent=2, ensure_ascii=False)
                zf.writestr("data.json", json_data)
                
                # Save Logo
                if company._logo_temp_path and os.path.exists(company._logo_temp_path):
                    ext = os.path.splitext(company._logo_temp_path)[1]
                    zf.write(company._logo_temp_path, f"logo{ext}")
                
                # Save Signature
                if company._signature_temp_path and os.path.exists(company._signature_temp_path):
                    ext = os.path.splitext(company._signature_temp_path)[1]
                    zf.write(company._signature_temp_path, f"signature{ext}")
            
            # Reload to ensure paths are correct
            self._companies[company.name] = self._load_single_company(filepath)
            return True
            
        except Exception as e:
            print(f"Error saving company {company.name}: {e}")
            return False

    def get_companies(self) -> Dict[str, Company]:
        """Get all companies."""
        return self._companies

    def get_company_names(self) -> List[str]:
        """Get list of company names."""
        return list(self._companies.keys())

    def get_company(self, name: str) -> Optional[Company]:
        """Get a specific company by name."""
        return self._companies.get(name)

    def get_company_dict(self, name: str) -> dict:
        """Get company data as dictionary (for compatibility)."""
        company = self._companies.get(name)
        if not company:
            return {}
        
        d = company.to_dict()
        # For legacy compatibility and UI usage, provide absolute paths if they exist
        if company._logo_temp_path:
            d["logo_path"] = company._logo_temp_path
        if company._signature_temp_path:
            d["signature_path"] = company._signature_temp_path
        return d

    def add_company(self, company: Company) -> bool:
        """Add a new company."""
        if company.name in self._companies:
            return False
        return self.save_company(company)

    def update_company(self, name: str, company: Company) -> bool:
        """Update an existing company."""
        # If name changed, delete old file
        if name != company.name:
            old_path = self._get_emp_path(name)
            if os.path.exists(old_path):
                os.remove(old_path)
            if name in self._companies:
                del self._companies[name]
        
        return self.save_company(company)

    def delete_company(self, name: str) -> bool:
        """Delete a company."""
        if name not in self._companies:
            return False
        
        filepath = self._get_emp_path(name)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error deleting file {filepath}: {e}")
        
        del self._companies[name]
        return True

    def set_company_logo(self, company_name: str, logo_source_path: str) -> str:
        """Set a logo for a company."""
        if company_name not in self._companies:
            return ""
        
        company = self._companies[company_name]
        company._logo_temp_path = logo_source_path # Temporarily point to source or temp copy
        company.logo = "logo" + os.path.splitext(logo_source_path)[1]
        
        if self.save_company(company):
             # After save (which reloads), return the new temp path
             updated = self._companies[company_name]
             return updated._logo_temp_path
        return ""

    def set_company_signature(self, company_name: str, signature_source_path: str) -> str:
        """Set a signature for a company."""
        if company_name not in self._companies:
            return ""
        
        company = self._companies[company_name]
        company._signature_temp_path = signature_source_path
        company.signature = "signature" + os.path.splitext(signature_source_path)[1]
        
        if self.save_company(company):
             updated = self._companies[company_name]
             return updated._signature_temp_path
        return ""
    
    def get_logo_absolute_path(self, company_name: str) -> str:
        """Get the absolute path to a company's logo (extracted in temp)."""
        company = self._companies.get(company_name)
        return company._logo_temp_path if company else ""

    def get_signature_absolute_path(self, company_name: str) -> str:
        """Get the absolute path to a company's signature (extracted in temp)."""
        company = self._companies.get(company_name)
        return company._signature_temp_path if company else ""


    def get_companies_directory(self) -> str:
        """Get the directory where company files are stored."""
        return COMPANIES_DIR


# Singleton instance
_instance: Optional[CompanyLogic] = None

def get_company_logic() -> CompanyLogic:
    """Get the singleton CompanyLogic instance."""
    global _instance
    if _instance is None:
        _instance = CompanyLogic()
    return _instance
