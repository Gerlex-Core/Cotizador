import os
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor
from PyQt6.QtCore import Qt, QBuffer, QByteArray

class ImageProcessor:
    """
    Dedicated class for image processing, transformations, and format support.
    Supports: PNG, JPG, WEBP, GIF, BMP, etc.
    Preserves transparency where applicable.
    """
    
    SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp']
    
    @staticmethod
    def load_pixmap(path_or_data) -> QPixmap:
        """Robustly load a QPixmap from path or bytes."""
        pixmap = QPixmap()
        
        if isinstance(path_or_data, (str, os.PathLike)):
            if os.path.exists(path_or_data):
                pixmap.load(path_or_data)
        elif isinstance(path_or_data, (bytes, bytearray)):
            pixmap.loadFromData(path_or_data)
            
        return pixmap

    @staticmethod
    def process_and_save(pixmap: QPixmap, save_path: str, max_size: tuple = None, 
                         keep_aspect: bool = True, quality: int = 90) -> bool:
        """
        Process (resize) and save image.
        Auto-detects format from extension.
        Preserves transparency for PNG/WEBP.
        """
        if pixmap.isNull():
            return False
            
        target_pixmap = pixmap
        
        # Resize if needed
        if max_size and (max_size[0] > 0 and max_size[1] > 0):
            target_w, target_h = max_size
            aspect_mode = Qt.AspectRatioMode.KeepAspectRatio if keep_aspect else Qt.AspectRatioMode.IgnoreAspectRatio
            
            target_pixmap = pixmap.scaled(
                target_w, target_h,
                aspect_mode,
                Qt.TransformationMode.SmoothTransformation
            )
            
        # Determine format
        ext = os.path.splitext(save_path)[1].lower().replace('.', '').upper()
        if ext == 'JPG': ext = 'JPEG'
        
        # Save
        # Qt handles format details automatically based on string or extension usually, 
        # but passing format explicitly is safer.
        return target_pixmap.save(save_path, ext, quality)

    @staticmethod
    def ensure_valid_extension(filename: str) -> str:
        """Ensures filename has a supported extension, defaulting to PNG if none/invalid."""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ImageProcessor.SUPPORTED_FORMATS:
            return filename + ".png"
        return filename

    @staticmethod
    def get_resolution(pixmap: QPixmap) -> str:
        """Returns resolution string 'WxH'."""
        if pixmap.isNull():
            return "0x0"
        return f"{pixmap.width()}x{pixmap.height()}"
