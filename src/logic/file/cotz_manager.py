"""
Cotz Manager - Handles saving and loading of .cotz files.
Uses ZIP format to embed images and data together.
"""

import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from typing import Optional, Dict, List, Tuple


class CotzManager:
    """
    Manages the lifecycle of a quotation file (.cotz).
    Uses ZIP format to store JSON data and images together.
    
    File structure:
        archivo.cotz (ZIP)
        ├── data.json          # Quotation data (JSON)
        └── images/            # Images folder
            ├── product_0.png  # Product image
            ├── obs_0.png      # Observation image
            └── ...
    """
    
    VERSION = "2.0"
    
    def __init__(self):
        self.current_file: Optional[str] = None
        self._temp_dir: Optional[str] = None
        self._image_mapping: Dict[str, str] = {}  # original_path -> temp_path
        self._modified = False
        self._last_modification_time = None
    
    def _ensure_temp_dir(self) -> str:
        """Ensure temp directory exists for image extraction."""
        if not self._temp_dir or not os.path.exists(self._temp_dir):
            self._temp_dir = tempfile.mkdtemp(prefix="cotz_")
        return self._temp_dir
    
    def _cleanup_temp(self):
        """Clean up temporary directory."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
            except Exception:
                pass
            self._temp_dir = None
        self._image_mapping.clear()
    
    def _is_zip_file(self, filepath: str) -> bool:
        """Check if file is a ZIP format."""
        try:
            with open(filepath, 'rb') as f:
                # ZIP files start with PK (0x50, 0x4B)
                header = f.read(2)
                return header == b'PK'
        except Exception:
            return False
    
    def _copy_image_to_temp(self, image_path: str, prefix: str, index: int) -> str:
        """Copy an image to temp directory and return the new path."""
        if not os.path.exists(image_path):
            return ""
        
        temp_dir = self._ensure_temp_dir()
        ext = os.path.splitext(image_path)[1].lower()
        if not ext:
            ext = ".png"
        
        temp_filename = f"{prefix}_{index}{ext}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        try:
            shutil.copy2(image_path, temp_path)
            self._image_mapping[image_path] = temp_path
            return temp_path
        except Exception as e:
            print(f"Error copying image: {e}")
            return image_path
    
    def save_quotation(self, filepath: str, data: dict) -> bool:
        """
        Save the quotation data to a .cotz file (ZIP format).
        
        Args:
            filepath: Path to save the file
            data: Dictionary containing quotation data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import copy
            # Prepare a deep copy of data to ensure we modify only the data to be saved
            save_data = copy.deepcopy(data)
            save_data["_cotz_version"] = self.VERSION
            save_data["_saved_at"] = datetime.now().isoformat()
            
            # Collect all images to embed
            images_to_embed: List[Tuple[str, str]] = []  # (original_path, archive_name)
            image_counter = 0
            
            # Process product images
            if "products" in save_data:
                for i, product in enumerate(save_data["products"]):
                    if product.get("image_path") and os.path.exists(product["image_path"]):
                        ext = os.path.splitext(product["image_path"])[1].lower()
                        
                        # Generate structured path: cot/imagen/producto/name.ext
                        product_name = product.get("name", f"product_{i}")
                        # Sanitize name
                        safe_name = "".join([c for c in product_name if c.isalnum() or c in (' ', '-', '_')]).strip()
                        if not safe_name:
                            safe_name = f"product_{i}"
                            
                        archive_name = f"cot/imagen/producto/{safe_name}{ext}"
                        
                        # Check for duplicates in this save session to avoid overwriting
                        # (Simple fix: append index if needed, but for now assuming unique names or index fallback)
                        # Actually if user adds same product twice? 
                        # Let's append index to be safe and unique
                        if any(x[1] == archive_name for x in images_to_embed):
                             archive_name = f"cot/imagen/producto/{safe_name}_{i}{ext}"

                        images_to_embed.append((product["image_path"], archive_name))
                        product["image_path"] = archive_name
                        image_counter += 1
            
            # Process observation images
            if "observations" in save_data and "images" in save_data["observations"]:
                for i, img_data in enumerate(save_data["observations"]["images"]):
                    if img_data.get("path") and os.path.exists(img_data["path"]):
                        ext = os.path.splitext(img_data["path"])[1].lower()
                        archive_name = f"images/obs_{i}{ext}"
                        images_to_embed.append((img_data["path"], archive_name))
                        img_data["path"] = archive_name
                        image_counter += 1
            
            # Process canvas data images
            if "canvas_data" in save_data:
                for i, item in enumerate(save_data["canvas_data"]):
                    if item.get("type") == "image" and item.get("path"):
                        if os.path.exists(item["path"]):
                            ext = os.path.splitext(item["path"])[1].lower()
                            archive_name = f"images/canvas_{i}{ext}"
                            images_to_embed.append((item["path"], archive_name))
                            item["path"] = archive_name
            
            # Create ZIP file
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add JSON data
                json_data = json.dumps(save_data, indent=2, ensure_ascii=False)
                zf.writestr("data.json", json_data)
                
                # Add images
                for original_path, archive_name in images_to_embed:
                    try:
                        zf.write(original_path, archive_name)
                    except Exception as e:
                        print(f"Warning: Could not embed image {original_path}: {e}")
            
            self.current_file = filepath
            self._modified = False
            return True
            
        except Exception as e:
            print(f"Error saving quotation: {e}")
            return False
    
    def load_quotation(self, filepath: str) -> Optional[dict]:
        """
        Load a quotation from a .cotz file.
        Supports both old JSON format and new ZIP format.
        
        Returns:
            Quotation data dict or None if error
        """
        try:
            # Check if it's a ZIP file or legacy JSON
            if self._is_zip_file(filepath):
                return self._load_zip_format(filepath)
            else:
                return self._load_json_format(filepath)
                
        except Exception as e:
            print(f"Error loading quotation: {e}")
            return None
    
    def _load_json_format(self, filepath: str) -> Optional[dict]:
        """Load legacy JSON format."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.current_file = filepath
            self._modified = False
            return data
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None
    
    def _load_zip_format(self, filepath: str) -> Optional[dict]:
        """Load new ZIP format with embedded images."""
        try:
            # Clean up previous temp files
            self._cleanup_temp()
            temp_dir = self._ensure_temp_dir()
            
            with zipfile.ZipFile(filepath, 'r') as zf:
                # Read JSON data
                json_content = zf.read("data.json").decode('utf-8')
                data = json.loads(json_content)
                
                # Extract images to temp directory
                for name in zf.namelist():
                    # Extract standard images folder and new cot structure
                    if name.startswith("images/") or name.startswith("cot/"):
                        zf.extract(name, temp_dir)
                
                # Update image paths to point to extracted files
                if "products" in data:
                    for product in data["products"]:
                        archive_path = product.get("image_path", "")
                        if archive_path:
                            # If it's a legacy path (just filename or images/...), handle it
                            # If it's full path cot/..., use it
                            
                            # Construct absolute temp path
                            # We treat the text in 'image_path' as the relative path in zip
                            # If for some reason it was absolute (bug), we must sanitize it
                            clean_path = archive_path.replace("\\", "/")
                            if ":" in clean_path: # Remove drive letter if present
                                clean_path = clean_path.split(":")[-1].strip("/")
                            
                            full_path = os.path.join(temp_dir, clean_path)
                            
                            # Fallback for legacy "images/product_X.png" if "images" dir is flattened?
                            # Zip extract preserves structure.
                            
                            if os.path.exists(full_path):
                                product["image_path"] = full_path
                                product["_original_archive_path"] = archive_path
                            else:
                                # Try legacy fallback logic (looking in images/ flat dir)
                                img_name = os.path.basename(archive_path)
                                legacy_path = os.path.join(temp_dir, "images", img_name)
                                if os.path.exists(legacy_path):
                                    product["image_path"] = legacy_path
                                    product["_original_archive_path"] = archive_path
                
                # Update observation images
                if "observations" in data and "images" in data["observations"]:
                    for img_data in data["observations"]["images"]:
                        archive_path = img_data.get("path", "")
                        if archive_path:
                            # Try absolute relative path first
                            full_path = os.path.join(temp_dir, archive_path)
                            if os.path.exists(full_path):
                                img_data["path"] = full_path
                            else:
                                # Fallback
                                img_name = os.path.basename(archive_path)
                                legacy_path = os.path.join(temp_dir, "images", img_name)
                                if os.path.exists(legacy_path):
                                    img_data["path"] = legacy_path
                
                # Update canvas data images
                if "canvas_data" in data:
                    for item in data["canvas_data"]:
                        if item.get("type") == "image" and item.get("path"):
                            archive_path = item["path"]
                            
                            full_path = os.path.join(temp_dir, archive_path)
                            if os.path.exists(full_path):
                                item["path"] = full_path
                            else:
                                # Fallback
                                img_name = os.path.basename(archive_path)
                                legacy_path = os.path.join(temp_dir, "images", img_name)
                                if os.path.exists(legacy_path):
                                    item["path"] = legacy_path
            
            self.current_file = filepath
            self._modified = False
            return data
            
        except Exception as e:
            print(f"Error loading ZIP format: {e}")
            return None
    
    def get_current_filename(self) -> str:
        """Get the current file basename or default."""
        if self.current_file:
            return os.path.basename(self.current_file)
        return "Sin Título"
    
    def mark_modified(self):
        """Mark the quotation as modified."""
        self._modified = True
        self._last_modification_time = datetime.now()
    
    def is_modified(self) -> bool:
        """Check if quotation has unsaved changes."""
        return self._modified
    
    def get_last_modification_time(self):
        """Get the last modification timestamp."""
        return self._last_modification_time
    
    def __del__(self):
        """Cleanup on destruction."""
        self._cleanup_temp()


# Singleton instance
_cotz_manager_instance: Optional[CotzManager] = None


def get_cotz_manager() -> CotzManager:
    """Get the singleton CotzManager instance."""
    global _cotz_manager_instance
    if _cotz_manager_instance is None:
        _cotz_manager_instance = CotzManager()
    return _cotz_manager_instance
