"""
Resource path utility for CotizadorPro.
Handles path resolution for both development and PyInstaller frozen builds.
"""

import os
import sys


def get_base_dir() -> str:
    """
    Get the base directory of the application.
    Works both in development and when frozen with PyInstaller.
    
    Returns:
        str: Absolute path to the application base directory
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return sys._MEIPASS
    else:
        # Running in normal Python environment
        # Go up from src/logic/utils to project root
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to a resource, works for dev and for PyInstaller.
    
    Args:
        relative_path: Path relative to project root (e.g., 'media/icons/add.png')
        
    Returns:
        str: Absolute path to the resource
    """
    base = get_base_dir()
    return os.path.join(base, relative_path)


def get_user_data_dir() -> str:
    """
    Get the directory for user data (persistent data that survives app updates).
    This is the directory where the .exe is located, not the temp extraction folder.
    
    Returns:
        str: Absolute path to user data directory
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - use executable's directory
        return os.path.dirname(sys.executable)
    else:
        # Development - use project root
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# Common paths as constants
BASE_DIR = get_base_dir()
USER_DATA_DIR = get_user_data_dir()
MEDIA_DIR = get_resource_path('media')
ICONS_DIR = get_resource_path(os.path.join('media', 'icons'))
THEMES_DIR = get_resource_path(os.path.join('media', 'themes'))
COVERS_DIR = get_resource_path(os.path.join('media', 'covers'))
DATA_DIR = get_resource_path(os.path.join('media', 'data'))
