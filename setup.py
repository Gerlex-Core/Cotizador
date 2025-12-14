"""
Cotizador Pro - Setup Script
Installer for the Quotation Application.

Usage:
    pip install -e .
    
Or for development:
    pip install -e .[dev]
"""

from setuptools import setup, find_packages
import os

# Read version from main.py or define here
VERSION = "2.0.0"

# Get the directory where setup.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Read README if exists
readme_path = os.path.join(BASE_DIR, "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

# Core dependencies required for application execution
INSTALL_REQUIRES = [
    "PyQt6>=6.4.0",           # GUI framework
    "reportlab>=4.0.0",       # PDF generation
]

# Optional development dependencies
DEV_REQUIRES = [
    "pyinstaller>=5.0",       # For creating executables
    "black",                   # Code formatting
    "flake8",                  # Linting
]

setup(
    name="cotizador-pro",
    version=VERSION,
    author="Cotizador Team",
    author_email="contacto@cotizador.com",
    description="Sistema profesional de cotizaciones con generación de PDF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cotizador/cotizador-pro",
    
    # Package configuration
    packages=find_packages(where="."),
    package_dir={"": "."},
    
    # Include non-Python files
    include_package_data=True,
    package_data={
        "": [
            "config/*.conf",
            "media/**/*",
            "options/**/*",
        ],
    },
    
    # Dependencies
    python_requires=">=3.9",
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "dev": DEV_REQUIRES,
    },
    
    # Entry point
    entry_points={
        "console_scripts": [
            "cotizador=main:main",
        ],
        "gui_scripts": [
            "cotizador-gui=main:main",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Printing",
    ],
    
    # Keywords
    keywords="quotation invoice pdf business qt6 pyqt6",
)
