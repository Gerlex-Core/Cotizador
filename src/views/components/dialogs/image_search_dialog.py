"""
Image Search Dialog - Allows searching and downloading images from the internet with multi-engine support.
Includes DuckDuckGo (robust), Pixabay (stock), and others.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import re
import time
import requests # Use requests for better session/header handling
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QSplitter, QWidget,
    QProgressBar, QMessageBox, QComboBox, QSpinBox, QFileDialog,
    QStyledItemDelegate, QStyle
)
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, QRect
from src.logic.utils.image_processor import ImageProcessor

# Delegate for custom drawing (Red overlay for non-standard sizes)
class ImageItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Draw standard item
        super().paint(painter, option, index)
        
        data = index.data(Qt.ItemDataRole.UserRole)
        if not data: return
        
        width = data.get('width', 0)
        height = data.get('height', 0)
        
        # Draw resolution at bottom
        if width > 0 and height > 0:
            res_text = f"{width}x{height}"
            
            painter.save()
            
            # Setup Font
            font = painter.font()
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)
            
            # Helper to measure text
            fm = painter.fontMetrics()
            text_w = fm.horizontalAdvance(res_text)
            text_h = fm.height()
            
            # Position: Bottom Center
            rect = option.rect
            x = rect.x() + (rect.width() - text_w) / 2
            y = rect.y() + rect.height() - 8 
            
            # Draw pill background
            bg_rect = QRect(int(x - 6), int(y - text_h + 2), int(text_w + 12), int(text_h + 2))
            painter.setBrush(QColor(0, 0, 0, 150))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(bg_rect, 4, 4)
            
            # Draw Text
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(int(x), int(y), res_text)
            
            painter.restore()

# Worker thread for searching to keep UI responsive
class SearchWorker(QThread):
    results_found = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, query, engine="DuckDuckGo", filters=None):
        super().__init__()
        self.query = query
        self.engine = engine
        self.filters = filters or {}
        
    def run(self):
        try:
            results = []
            if self.engine == "DuckDuckGo":
                results = self._search_duckduckgo()
            elif self.engine == "Pixabay (Stock)":
                results = self._search_pixabay()
            elif self.engine == "Bing":
                results = self._search_bing()
            elif self.engine == "Google":
                results = self._search_google()
            elif self.engine == "Unsplash":
                results = self._search_unsplash()
            
            # Unique results
            unique_results = []
            seen = set()
            for r in results:
                url = r.get('image')
                if url and url not in seen and url.startswith('http'):
                    seen.add(url)
                    unique_results.append(r)
                if len(unique_results) >= 50:
                    break
            
            if unique_results:
                self.results_found.emit(unique_results)
            else:
                self.error_occurred.emit(f"No se encontraron imágenes en {self.engine}.")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"Error en {self.engine}: {str(e)}")

    def _get_headers(self):
        """Headers simples que funcionan bien para scraping."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Connection': 'keep-alive',
        }

    def _search_duckduckgo(self):
        """DuckDuckGo JSON API search."""
        print("\n" + "="*60)
        print("[DEBUG DDG] Iniciando busqueda DuckDuckGo")
        print(f"[DEBUG DDG] Query: '{self.query}'")
        print("="*60)
        
        # 1. Get VQD Token
        url = "https://duckduckgo.com/"
        params = {'q': self.query}
        
        session = requests.Session()
        session.headers.update(self._get_headers())
        
        print(f"[DEBUG DDG] Paso 1: Obteniendo pagina inicial de DDG...")
        try:
            resp = session.get(url, params=params, timeout=15)
            print(f"[DEBUG DDG] Status Code inicial: {resp.status_code}")
            print(f"[DEBUG DDG] URL final: {resp.url}")
        except Exception as e:
            print(f"[DEBUG DDG] ERROR al obtener pagina inicial: {e}")
            return []
            
        html = resp.text
        print(f"[DEBUG DDG] Tamaño HTML recibido: {len(html)} caracteres")
        
        # Save HTML for debugging (first 2000 chars)
        print(f"[DEBUG DDG] Primeros 500 chars del HTML:")
        print(html[:500])
        print("[DEBUG DDG] ...")
        
        # Extract VQD using multiple patterns (DDG changes format periodically)
        vqd = None
        patterns = [
            r'vqd=["\']?([^"\'\&]+)',
            r'vqd=([0-9-]+)',
            r'"vqd":"([^"]+)"',
            r"'vqd':'([^']+)'",
            r'vqd%3D([^%\&"]+)',
        ]
        
        print(f"[DEBUG DDG] Paso 2: Buscando token VQD con {len(patterns)} patrones...")
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, html)
            if match:
                vqd = match.group(1)
                print(f"[DEBUG DDG] [OK] VQD encontrado con patron #{i+1}: '{vqd[:20]}...' (truncado)")
                break
            else:
                print(f"[DEBUG DDG] [X] Patron #{i+1} no coincidio: {pattern}")

        if not vqd:
            print("[DEBUG DDG] [WARN] No se encontro token VQD en ningun patron!")
            print("[DEBUG DDG] Buscando 'vqd' en el HTML manualmente...")
            if 'vqd' in html.lower():
                # Find context around 'vqd'
                idx = html.lower().find('vqd')
                context = html[max(0, idx-50):idx+100]
                print(f"[DEBUG DDG] Contexto encontrado: ...{context}...")
            else:
                print("[DEBUG DDG] 'vqd' NO aparece en ninguna parte del HTML")
            
            print("[DEBUG DDG] No se pudo obtener token VQD, retornando vacio")
            return []
            
        # 2. Get JSON Results
        print(f"\n[DEBUG DDG] Paso 3: Obteniendo resultados JSON...")
        json_url = "https://duckduckgo.com/i.js"
        params = {
            'l': 'us-en',
            'o': 'json',
            'q': self.query,
            'vqd': vqd,
            'f': ',,,',
            'p': '1'
        }
        
        # Apply filters
        size_param = ""
        if self.filters.get('type') == 'standard':
            size_param = "size:Medium"
        elif self.filters.get('type') == 'custom':
            w = self.filters.get('w', 0)
            if w > 1000:
                size_param = "size:Wallpaper"
            else:
                size_param = "size:Medium"
        
        if size_param:
            params['f'] = f"{size_param},,,"
        
        print(f"[DEBUG DDG] URL JSON: {json_url}")
        print(f"[DEBUG DDG] Params: {params}")
        
        try:
            resp = session.get(json_url, params=params, timeout=15)
            print(f"[DEBUG DDG] Status Code JSON: {resp.status_code}")
            print(f"[DEBUG DDG] Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
            print(f"[DEBUG DDG] Tamaño respuesta: {len(resp.text)} caracteres")
        except Exception as e:
            print(f"[DEBUG DDG] ERROR al obtener JSON: {e}")
            return []
        
        results = []
        try:
            print(f"[DEBUG DDG] Primeros 500 chars de respuesta JSON:")
            print(resp.text[:500])
            
            data = resp.json()
            print(f"[DEBUG DDG] [OK] JSON parseado correctamente")
            print(f"[DEBUG DDG] Claves en respuesta: {list(data.keys())}")
            
            raw_results = data.get("results", [])
            print(f"[DEBUG DDG] Número de resultados raw: {len(raw_results)}")
            
            if raw_results:
                print(f"[DEBUG DDG] Ejemplo primer resultado: {raw_results[0]}")
            
            for r in raw_results:
                results.append({
                    'image': r.get('image'),
                    'thumbnail': r.get('thumbnail'),
                    'width': r.get('width'),
                    'height': r.get('height'),
                    'source': 'DuckDuckGo'
                })
            
            print(f"[DEBUG DDG] [OK] Total resultados procesados: {len(results)}")
            
        except json.JSONDecodeError as e:
            print(f"[DEBUG DDG] [ERROR] Error parseando JSON: {e}")
            print(f"[DEBUG DDG] Respuesta completa (primeros 1000 chars):")
            print(resp.text[:1000])
        except Exception as e:
            print(f"[DEBUG DDG] [ERROR] Error inesperado: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n[DEBUG DDG] === FIN BÚSQUEDA DDG - {len(results)} resultados ===\n")
        return results

    def _search_pixabay(self):
        """Scrape Pixabay search results."""
        # Pixabay scraping is tricky, but lets try to get json via html matching if possible or just regex
        # Using public API key is safer if available, but requirements said "apis gratuitas".
        # Scraping:
        
        q = urllib.parse.quote(self.query)
        url = f"https://pixabay.com/images/search/{q}/"
        headers = self._get_headers()
        resp = requests.get(url, headers=headers)
        html = resp.text
        
        # Regex for data-lazy-src or src
        # Pixabay often puts JSON in a script tag now
        results = []
        
        # Try to find JSON blob
        # Look for: window.__INITIAL_STATE__ = { ... }
        # Or just standard img tags
        
        # Regex for image tags
        # <img ... src="url" ... alt="description">
        # Pixabay uses srcset usually
        
        # Simple regex for src with .jpg
        matches = re.findall(r'src="(https://cdn\.pixabay\.com/photo/[^"]+)"', html)
        for m in matches:
            # These are usually thumbnails
             # Try to guess full size or higher res
             # _150.jpg -> _640.jpg or _1280.jpg
             full = m
             if '_150.' in m: full = m.replace('_150.', '_1280.')
             elif '_340.' in m: full = m.replace('_340.', '_1280.') # fallback
             elif '_640.' in m: full = m.replace('_640.', '_1280.')
             
             results.append({
                 'image': full,
                 'thumbnail': m,
                 'width': 0, # Unkown from simple scrape
                 'height': 0,
                 'source': 'Pixabay'
             })
             
        return results

    def _search_bing(self):
        """Scraping Bing Images with multiple fallback patterns."""
        print("[DEBUG BING] Iniciando busqueda en Bing...")
        headers = self._get_headers()
        headers['Referer'] = 'https://www.bing.com/'
        q = urllib.parse.quote(self.query)
        url = f"https://www.bing.com/images/search?q={q}&form=HDRSC2&first=1"
        
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            print(f"[DEBUG BING] Status Code: {resp.status_code}")
            html = resp.text
            print(f"[DEBUG BING] HTML recibido: {len(html)} caracteres")
        except Exception as e:
            print(f"[DEBUG BING] Error al obtener pagina: {e}")
            return []
        
        results = []
        
        # Pattern 1: murl with html entities (most common)
        pattern1 = r'murl&quot;:&quot;(https?://[^&]+)&quot;'
        matches1 = re.findall(pattern1, html)
        print(f"[DEBUG BING] Patron 1 (murl entities): {len(matches1)} resultados")
        
        # Pattern 2: murl with JSON format
        pattern2 = r'"murl":"(https?://[^"]+)"'
        matches2 = re.findall(pattern2, html)
        print(f"[DEBUG BING] Patron 2 (murl JSON): {len(matches2)} resultados")
        
        # Pattern 3: mediaurl in data attributes
        pattern3 = r'mediaurl=(https?://[^&"]+)'
        matches3 = re.findall(pattern3, html)
        print(f"[DEBUG BING] Patron 3 (mediaurl): {len(matches3)} resultados")
        
        # Combine all matches
        all_urls = set()
        for url in matches1 + matches2 + matches3:
            # Decode URL if needed
            decoded = urllib.parse.unquote(url)
            if decoded.startswith('http') and any(ext in decoded.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                all_urls.add(decoded)
        
        print(f"[DEBUG BING] URLs unicas encontradas: {len(all_urls)}")
        
        # Try to get dimensions from the full pattern
        dim_pattern = r'murl&quot;:&quot;(https?://[^&]+)&quot;.*?&quot;h&quot;:(\d+).*?&quot;w&quot;:(\d+)'
        dim_matches = re.findall(dim_pattern, html)
        dim_dict = {m[0]: (int(m[2]), int(m[1])) for m in dim_matches}  # {url: (width, height)}
        
        for img_url in list(all_urls)[:50]:  # Limit to 50
            width, height = dim_dict.get(img_url, (0, 0))
            results.append({
                'image': img_url,
                'thumbnail': img_url,
                'width': width,
                'height': height,
                'source': 'Bing'
            })
        
        print(f"[DEBUG BING] Total resultados: {len(results)}")
        return results

    def _search_google(self):
        """Google Images scraping with multiple patterns."""
        print("[DEBUG GOOGLE] Iniciando busqueda en Google Images...")
        headers = self._get_headers()
        headers['Referer'] = 'https://www.google.com/'
        q = urllib.parse.quote(self.query)
        
        # Use async parameter for better results
        url = f"https://www.google.com/search?q={q}&tbm=isch&hl=en"
        
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            print(f"[DEBUG GOOGLE] Status Code: {resp.status_code}")
            html = resp.text
            print(f"[DEBUG GOOGLE] HTML recibido: {len(html)} caracteres")
        except Exception as e:
            print(f"[DEBUG GOOGLE] Error: {e}")
            return []
        
        results = []
        
        # Pattern 1: Data URLs in JSON-like structures (most reliable)
        # Look for ["URL",width,height] patterns
        pattern1 = r'\["(https?://[^"]+\.(?:jpg|jpeg|png|gif|webp)[^"]*)",(\d+),(\d+)\]'
        matches1 = re.findall(pattern1, html, re.IGNORECASE)
        print(f"[DEBUG GOOGLE] Patron 1 (JSON array): {len(matches1)} resultados")
        
        for m in matches1:
            url_img = m[0].replace('\\u003d', '=').replace('\\u0026', '&')
            if 'encrypted-tbn' not in url_img and 'gstatic' not in url_img:
                results.append({
                    'image': url_img,
                    'thumbnail': url_img,
                    'width': int(m[1]),
                    'height': int(m[2]),
                    'source': 'Google'
                })
        
        # Pattern 2: ou (original url) parameter
        pattern2 = r'"ou":"(https?://[^"]+)"'
        matches2 = re.findall(pattern2, html)
        print(f"[DEBUG GOOGLE] Patron 2 (ou param): {len(matches2)} resultados")
        
        for url_img in matches2:
            url_img = url_img.replace('\\u003d', '=').replace('\\u0026', '&')
            if url_img not in [r['image'] for r in results]:
                results.append({
                    'image': url_img,
                    'thumbnail': url_img,
                    'width': 0,
                    'height': 0,
                    'source': 'Google'
                })
        
        # Pattern 3: Fallback to encrypted thumbnails if no results
        if not results:
            pattern3 = r'src="(https://encrypted-tbn[^"]+)"'
            matches3 = re.findall(pattern3, html)
            print(f"[DEBUG GOOGLE] Patron 3 (thumbnails): {len(matches3)} resultados")
            for img in matches3[:30]:
                results.append({
                    'image': img,
                    'thumbnail': img,
                    'width': 0,
                    'height': 0,
                    'source': 'Google'
                })
        
        print(f"[DEBUG GOOGLE] Total resultados: {len(results)}")
        return results

    def _search_unsplash(self):
        # Unsplash scrape
        q = urllib.parse.quote(self.query)
        url = f"https://unsplash.com/s/photos/{q}"
        headers = self._get_headers()
        
        resp = requests.get(url, headers=headers)
        html = resp.text
        
        # Look for standard image urls
        # https://images.unsplash.com/photo-...?ixlib=...
        matches = re.findall(r'(https://images\.unsplash\.com/photo-[^"]+)', html)
        
        results = []
        for m in matches:
            # Minimal cleanup
            clean = m.split('?')[0] + "?auto=format&fit=crop&w=1600&q=80" # Force high qual
            thumb = m.split('?')[0] + "?auto=format&fit=crop&w=300&q=60"
            
            results.append({
                'image': clean,
                'thumbnail': thumb,
                'width': 0,
                'height': 0,
                'source': 'Unsplash'
            })
        return results


class ImageDownloader(QThread):
    image_downloaded = pyqtSignal(str, bytes)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            # Handle local files if needed, but this is usually web
            if self.url.startswith("file:///"):
                path = self.url.replace("file:///", "")
                with open(path, 'rb') as f:
                    data = f.read()
                    self.image_downloaded.emit(self.url, data)
                return

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            resp = requests.get(self.url, headers=headers, timeout=10)
            if resp.status_code == 200:
                self.image_downloaded.emit(self.url, resp.content)
        except:
            pass # Fail silently for individual images


class ImageSearchDialog(QDialog):
    """Dialog for searching and selecting images."""
    
    def __init__(self, parent=None, initial_query=""):
        super().__init__(parent)
        self.setWindowTitle("Buscar Imagen en Internet")
        self.resize(1200, 800)
        self.selected_image_path = None
        self._initial_query = initial_query
        self.current_image_data = None
        
        self._setup_ui()
        
        if self._initial_query:
            self.search_input.setText(self._initial_query)
            self._start_search()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Search Container
        search_container = QWidget()
        search_container.setStyleSheet("background-color: rgba(30,30,30,1); border-radius: 8px; padding: 10px;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 10, 10, 10)
        
        # Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar imagen (ej. Laptop HP)...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c2c2e;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 0 10px;
                color: white;
                font-size: 14px;
            }
        """
        )
        self.search_input.returnPressed.connect(self._start_search)
        search_layout.addWidget(self.search_input, 1)

        # Engine Selector ComboBox
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["Google", "Bing", "DuckDuckGo", "Pixabay (Stock)", "Unsplash"])
        self.engine_combo.setCurrentIndex(0)  # Google by default
        self.engine_combo.setMinimumHeight(40)
        self.engine_combo.setMinimumWidth(150)
        self.engine_combo.setStyleSheet("""
            QComboBox {
                background-color: #2c2c2e;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 0 10px;
                color: white;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid white;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #2c2c2e;
                color: white;
                selection-background-color: #0A84FF;
            }
        """)
        search_layout.addWidget(self.engine_combo)

        # Standardize Checkbox
        from PyQt6.QtWidgets import QCheckBox
        self.standardize_check = QCheckBox("300x300")
        self.standardize_check.setChecked(True)
        self.standardize_check.setToolTip("Transformar a imagen estandar (300x300)")
        self.standardize_check.setStyleSheet("""
            QCheckBox { color: white; margin-left: 10px; }
            QCheckBox::indicator { width: 18px; height: 18px; }
        """)
        search_layout.addWidget(self.standardize_check)
        
        # Search Button
        self.btn_search = QPushButton("Buscar")
        self.btn_search.setMinimumHeight(40)
        self.btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #0A84FF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #0077ED; }
            QPushButton:pressed { background-color: #005BB5; }
        """)
        self.btn_search.clicked.connect(self._start_search)
        search_layout.addWidget(self.btn_search)
        
        layout.addWidget(search_container)

        # Local File Button
        file_btn_container = QHBoxLayout()
        self.btn_local_file = QPushButton("📂 Cargar desde Archivo Local")
        self.btn_local_file.setMinimumHeight(35)
        self.btn_local_file.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_local_file.setStyleSheet("""
             QPushButton {
                background-color: #3A3A3C;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover { background-color: #4A4A4C; }
        """)
        self.btn_local_file.clicked.connect(self._load_local_file)
        file_btn_container.addWidget(self.btn_local_file)
        file_btn_container.addStretch()
        layout.addLayout(file_btn_container)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 0) # Indeterminate
        self.progress.setStyleSheet("QProgressBar { height: 4px; border: none; background: #333; } QProgressBar::chunk { background: #0A84FF; }")
        layout.addWidget(self.progress)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background-color: #444; }")
        
        # Results List
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(220, 220)) # Larger icons
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setGridSize(QSize(240, 260)) # Larger grid
        self.list_widget.setSpacing(15)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1c1c1e;
                border: 1px solid #333;
                border-radius: 8px;
            }
            QListWidget::item {
                border-radius: 6px;
                padding: 5px;
                background-color: #252525;
            }
            QListWidget::item:selected {
                background-color: rgba(10, 132, 255, 0.3);
                border: 2px solid #0A84FF;
            }
            QListWidget::item:hover {
                background-color: #333;
            }
        """)
        self.list_widget.setItemDelegate(ImageItemDelegate(self.list_widget)) # Custom delegate for red box
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        splitter.addWidget(self.list_widget)
        
        # Preview
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(15, 0, 0, 0)
        
        lbl_preview_title = QLabel("Vista Previa")
        lbl_preview_title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 5px; color: #EEE;")
        preview_layout.addWidget(lbl_preview_title)
        
        self.preview_lbl = QLabel()
        self.preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_lbl.setStyleSheet("background-color: #000; border-radius: 8px; border: 1px solid #333;")
        self.preview_lbl.setMinimumSize(400, 400)
        preview_layout.addWidget(self.preview_lbl, 1)
        
        self.btn_select = QPushButton("Utilizar Esta Imagen")
        self.btn_select.setEnabled(False)
        self.btn_select.setMinimumHeight(50)
        self.btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                font-size: 16px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:disabled { background-color: #333; color: #555; }
            QPushButton:hover { background-color: #32D74B; }
        """)
        self.btn_select.clicked.connect(self._confirm_selection)
        preview_layout.addWidget(self.btn_select)
        
        splitter.addWidget(preview_container)
        splitter.setSizes([750, 450]) # Better initial ratio
        layout.addWidget(splitter)
        
    def _on_filter_changed(self, index):
        self.custom_size_widget.setVisible(index == 2)
        
    def _start_search(self):
        query = self.search_input.text().strip()
        if not query: return
        
        # Get selected engine from ComboBox
        engine = self.engine_combo.currentText()
        
        self.list_widget.clear()
        self.preview_lbl.clear()
        self.preview_lbl.setText(f"Buscando en {engine}...")
        self.btn_select.setEnabled(False)
        self.progress.setVisible(True)
        self.btn_search.setEnabled(False)
        self.current_image_data = None
        
        # No filters passed to worker for now, plain search
        self.worker = SearchWorker(query, engine, {})
        self.worker.results_found.connect(self._on_results)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.finished.connect(lambda: self.progress.setVisible(False))
        self.worker.start()

    def _on_results(self, results):
        self.btn_search.setEnabled(True)
        self.preview_lbl.setText("Seleccione una imagen")
        
        if not results:
            QMessageBox.information(self, "Info", "No se encontraron resultados.")
            return

        for data in results:
            # data is a dict: {image, thumbnail, width, height, source}
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, data)
            item.setText("Cargando...")
            self.list_widget.addItem(item)
            
            # Download thumbnail
            thumb_url = data.get('thumbnail') or data.get('image')
            dl = ImageDownloader(thumb_url)
            dl.image_downloaded.connect(self._on_thumb_downloaded)
            dl.start()
            # Keep reference to avoid garbage collection? Not strictly needed if thread handles itself but good practice
            item.downloader = dl 
            
    def _on_thumb_downloaded(self, url, data_bytes):
        # Find item with this url
        # Naive linear search is fine for 50 items
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_data = item.data(Qt.ItemDataRole.UserRole)
            
            # Match against thumbnail or image url
            if item_data and (item_data.get('thumbnail') == url or item_data.get('image') == url):
                pixmap = QPixmap()
                pixmap.loadFromData(data_bytes)
                
                if not pixmap.isNull():
                    # Scale for icon
                    icon_pix = pixmap.scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    # If expanding, we might need to crop to fit square, but QListWidget centers it.
                    
                    item.setIcon(QIcon(icon_pix))
                    item.setText("") # Remove loading text
                else:
                    item.setText("Error")
                break

    def _on_error(self, msg):
        self.btn_search.setEnabled(True)
        self.preview_lbl.setText(f"{msg}")
        QMessageBox.warning(self, "Error de Búsqueda", msg)
        
    def _on_item_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data: return
        
        full_url = data.get('image')
        self.preview_lbl.setText("Cargando alta resolución...")
        
        # Download full image
        self.dl_full = ImageDownloader(full_url)
        self.dl_full.image_downloaded.connect(self._on_full_downloaded)
        self.dl_full.start()
        
    def _on_full_downloaded(self, url, data_bytes):
        self.current_image_data = data_bytes
        pixmap = QPixmap()
        pixmap.loadFromData(data_bytes)
        
        if pixmap.isNull():
            self.preview_lbl.setText("Error al cargar imagen.")
            return
            
        scaled = pixmap.scaled(
            self.preview_lbl.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_lbl.setPixmap(scaled)
        self.btn_select.setEnabled(True)
        
    def _load_local_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.webp)")
        if path:
            with open(path, 'rb') as f:
                data = f.read()
            self.current_image_data = data
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            
            scaled = pixmap.scaled(
                self.preview_lbl.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_lbl.setPixmap(scaled)
            self.btn_select.setEnabled(True)
    
    def _confirm_selection(self):
        if not self.current_image_data:
            return
        
        # Save to project's product images folder (persistent, not temp)
        # Get base directory of the project
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        downloads_dir = os.path.join(base_dir, "archivocotizacion", "producto", "imagen")
        
        # Create directory if it doesn't exist
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
    
        # Processing Logic using new ImageProcessor
        pixmap = ImageProcessor.load_pixmap(self.current_image_data)
    
        target_size = None
        keep_aspect = True
    
        # Check standard resize
        if self.standardize_check.isChecked():
            target_size = (300, 300)
            keep_aspect = False # Strict 300x300 as requested for standard
        
        # Unique filename with timestamp
        filename = f"img_{int(time.time())}.png"
        save_path = os.path.join(downloads_dir, filename)
    
        success = ImageProcessor.process_and_save(
            pixmap=pixmap,
            save_path=save_path,
            max_size=target_size,
            keep_aspect=keep_aspect,
            quality=100
        )
        
        if success:
            self.selected_image_path = save_path
            print(f"[IMAGE] Imagen guardada en: {save_path}")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo procesar la imagen.")
