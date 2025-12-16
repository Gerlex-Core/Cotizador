"""
PDF Generator - Enhanced PDF generation for quotations.
Improved layout, company logo support, professional formatting.
Multi-page support for observations, images, and notes.
"""

import os
from typing import List, Optional
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    Image, HRFlowable
)
from reportlab.lib.utils import ImageReader
try:
    from .cover_styles import CoverPageRenderer
except ImportError:
    pass
except ImportError:
    pass

import json
from html.parser import HTMLParser

class ReportLabHTMLParser(HTMLParser):
    """Parse Qt HTML to ReportLab XML.
    
    Ignores document structure tags (html, head, body, etc.) and only
    processes content tags like span, p, br for formatting.
    """
    # Tags to completely ignore (document structure)
    IGNORE_TAGS = {'html', 'head', 'body', 'meta', 'style', 'title', '!doctype'}
    
    def __init__(self):
        super().__init__()
        self.output = []
        self.tag_stack = []
        self._ignore_content = False  # Flag to skip content inside style/head tags
        self.list_depth = 0 # Track list nesting for indentation

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        
        # Skip document structure tags
        if tag_lower in self.IGNORE_TAGS:
            # If entering style or head, ignore content until we exit
            if tag_lower in ('style', 'head'):
                self._ignore_content = True
            return
            
        if self._ignore_content:
            return
            
        if tag_lower == 'br':
            self.output.append('<br/>')
        elif tag_lower == 'p':
            if self.output: 
                self.output.append('<br/>') 
        elif tag_lower == 'span':
            styles = dict(attrs).get('style', '')
            tags_to_open = [] # List of (tag_name, full_tag)
            
            # Formatting
            if 'font-weight:600' in styles or 'font-weight:bold' in styles:
                tags_to_open.append(('b', '<b>'))
            if 'font-style:italic' in styles:
                tags_to_open.append(('i', '<i>'))
            if 'text-decoration:underline' in styles:
                tags_to_open.append(('u', '<u>'))
            if 'text-decoration:line-through' in styles:
                tags_to_open.append(('strike', '<strike>'))
            
            # Sub/Superscript
            if 'vertical-align:sub' in styles:
                tags_to_open.append(('sub', '<sub>'))
            if 'vertical-align:super' in styles:
                tags_to_open.append(('sup', '<sup>'))
                
            # Color
            import re
            color_match = re.search(r'color\s*:\s*([^;"]+)', styles)
            if color_match:
                c_val = color_match.group(1).strip()
                # Skip theme default colors (white/black) usually, but user wants fidelity.
                # If background is white (PDF), white text is bad.
                if c_val.lower() not in ('#ffffff', 'white', 'rgb(255, 255, 255)'):
                     tags_to_open.append(('font', f'<font color="{c_val}">'))

            # Font Size
            # Qt often gives "8.25pt" or "12px". Map to integers.
            size_match = re.search(r'font-size\s*:\s*([0-9\.]+)(pt|px)', styles)
            if size_match:
                 val = float(size_match.group(1))
                 unit = size_match.group(2)
                 if unit == 'px': val = val * 0.75 # Approx conversion
                 if val > 0:
                     tags_to_open.append(('font', f'<font size="{int(val)}">'))
            
            # Font Family
            face_match = re.search(r'font-family\s*:\s*\'?([^\'";]+)\'?', styles)
            if face_match:
                face = face_match.group(1).lower()
                # Map to standard PDF fonts
                pdf_font = 'Helvetica'
                if 'times' in face or 'serif' in face: pdf_font = 'Times-Roman'
                elif 'courier' in face or 'mono' in face: pdf_font = 'Courier'
                tags_to_open.append(('font', f'<font face="{pdf_font}">'))

            # Background Color (Highlight) - ReportLab supports backColor in font tag
            bg_match = re.search(r'background-color\s*:\s*([^;\"]+)', styles)
            if bg_match:
                bg_val = bg_match.group(1).strip()
                # Skip transparent or white backgrounds
                if bg_val.lower() not in ('transparent', '#ffffff', 'white', 'rgb(255, 255, 255)', 'initial', 'inherit'):
                    # ReportLab Paragraph supports backColor attribute
                    tags_to_open.append(('font', f'<font backColor="{bg_val}">'))

            for _, full_tag in tags_to_open:
                self.output.append(full_tag)
            self.tag_stack.append(tags_to_open)
            
        # Standard Tags Support
        elif tag_lower in ('b', 'strong'):
            self.output.append('<b>')
        elif tag_lower in ('i', 'em'):
            self.output.append('<i>')
        elif tag_lower == 'u':
            self.output.append('<u>')
        elif tag_lower in ('s', 'strike', 'del'):
            self.output.append('<strike>')
        elif tag_lower == 'sub':
            self.output.append('<sub>')
        elif tag_lower == 'sup':
            self.output.append('<sup>')
            
        elif tag_lower in ('ul', 'ol'):
            self.list_depth += 1
            # Add break before list starts if not at start
            if self.output and not self.output[-1].endswith('<br/>'):
                self.output.append('<br/>')
                
        elif tag_lower == 'li':
            # Calculate indentation
            indent_spaces = "&nbsp;" * (self.list_depth * 4)
            bullet = "&bull;" if self.list_depth % 2 != 0 else "&circ;"
            
            # Use ReportLab's <bullet> tag if inside ListFlowable? No, we are in Paragraph.
            # Convert to: <br/>&nbsp;&bull; Content
            # We precede with break unless it's the very first item? 
            # Actually standard practice for simple parser:
            start_marker = f'<br/>{indent_spaces}{bullet} '
            self.output.append(start_marker)
            
        elif tag_lower == 'p':
             # Only add break if output not empty
            if self.output: 
                self.output.append('<br/>') 
        
    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        
        # Resume content processing when exiting ignored sections
        if tag_lower in ('style', 'head'):
            self._ignore_content = False
            return
            
        if tag_lower in self.IGNORE_TAGS:
            return
            
        if self._ignore_content:
            return
            
        if tag_lower in ('b', 'strong'):
            self.output.append('</b>')
        elif tag_lower in ('i', 'em'):
            self.output.append('</i>')
        elif tag_lower == 'u':
            self.output.append('</u>')
        elif tag_lower == 'strike':
            self.output.append('</strike>')
        elif tag_lower in ('ul', 'ol'):
            self.list_depth = max(0, self.list_depth - 1)
            # self.output.append('<br/>') # Avoid extra break at end of list
            
        elif tag_lower == 'span':
             # ... existing span close logic handled above ...
             pass

    def handle_data(self, data):
        if self._ignore_content:
            return
        # Convert tabs to spaces (4 non-breaking spaces per tab)
        data = data.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        
        # Only add non-empty content
        if data.strip():
            self.output.append(data)
        elif data and self.output:
            # Preserve single spaces between words
            self.output.append(' ')
    
    def handle_decl(self, decl):
        """Handle DOCTYPE declarations - ignore them."""
        pass
    
    def handle_comment(self, data):
        """Handle HTML comments - ignore them."""
        pass

    def get_result(self):
        # Auto-close any remaining tags in stack
        while self.tag_stack:
            tags_to_close = self.tag_stack.pop()
            for tag_name, _ in reversed(tags_to_close):
                self.output.append(f'</{tag_name}>')
        
        return "".join(self.output).strip()



class PDFGenerator:
    """
    Enhanced PDF generator for quotations with:
    - Company logo support
    - Professional table formatting
    - Client information
    - Header/footer
    - Multi-page observations support
    - Terms and conditions
    - Signature area
    """
    
    # Color scheme
    COLORS = {
        'primary': colors.HexColor('#0A84FF'),
        'dark': colors.HexColor('#1C1C1E'),
        'gray': colors.HexColor('#8E8E93'),
        'light_gray': colors.HexColor('#F5F5F7'),
        'white': colors.white,
        'black': colors.black,
        'table_header': colors.HexColor('#2C2C2E'),
        'table_alt': colors.HexColor('#F8F8FA'),
        'border': colors.HexColor('#E5E5EA'),
        'secondary': colors.HexColor('#636366')
    }
    
    def __init__(self):
        self.styles = getSampleStyleSheet() # Keep this line as it's essential for styles to be defined before _setup_custom_styles
        self._setup_custom_styles()
        self.logo_path = None
        self._page_number = 1
        self.title_styles = self._load_title_styles()
        self._total_pages = 1
        
        # Load PDF config settings
        try:
            from ..logic.config.config_manager import get_config
            self._config = get_config()
        except:
            self._config = None
    
    def _draw_watermark(self, c: canvas.Canvas, width: float, height: float):
        """Draw watermark on the current page if enabled in config."""
        if not self._config or not self._config.watermark_enabled:
            return
        
        c.saveState()
        
        # Get watermark settings
        text = self._config.watermark_text
        opacity = self._config.watermark_opacity / 100.0  # Convert to 0-1 range
        image_path = self._config.watermark_image_path
        
        # Draw image watermark if available
        if image_path and os.path.exists(image_path):
            try:
                from reportlab.lib.utils import ImageReader
                img = ImageReader(image_path)
                img_width, img_height = img.getSize()
                
                # Scale to fit page (max 60% of page width/height)
                max_w = width * 0.6
                max_h = height * 0.6
                ratio = min(max_w / img_width, max_h / img_height)
                new_w = img_width * ratio
                new_h = img_height * ratio
                
                # Center on page
                x = (width - new_w) / 2
                y = (height - new_h) / 2
                
                # Draw with opacity using saveState/transparency
                c.setFillAlpha(opacity)
                c.drawImage(image_path, x, y, width=new_w, height=new_h, mask='auto')
            except Exception as e:
                print(f"[WATERMARK] Error drawing image: {e}")
        
        # Draw text watermark if specified (text takes priority if both exist)
        elif text:
            c.setFillAlpha(opacity)
            c.setFillColor(colors.HexColor('#888888'))
            
            # Large diagonal text across page
            c.translate(width / 2, height / 2)
            c.rotate(45)
            
            # Calculate font size based on text length
            font_size = min(80, width / (len(text) * 0.6))
            c.setFont("Helvetica-Bold", font_size)
            
            # Draw centered
            text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
            c.drawString(-text_width / 2, 0, text)
        
        c.restoreState()

    def _load_title_styles(self):
        import os
        import json
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logic", "config", "title_styles.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("styles", [])
        except: pass
        return []
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            fontSize=18,
            fontName='Helvetica-Bold',
            textColor=self.COLORS['dark'],
            spaceAfter=4
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            fontSize=10,
            fontName='Helvetica',
            textColor=self.COLORS['gray'],
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='Slogan',
            fontSize=10,
            fontName='Helvetica-Oblique',
            textColor=self.COLORS['gray'],
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=self.COLORS['dark'],
            spaceBefore=16,
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='Terms',
            fontSize=9,
            fontName='Helvetica',
            textColor=self.COLORS['gray'],
            leftIndent=12,
            spaceAfter=4
        ))
        
        self.styles.add(ParagraphStyle(
            name='Footer',
            fontSize=8,
            fontName='Helvetica',
            textColor=self.COLORS['gray'],
            alignment=TA_CENTER
        ))
    
    def generate_preview_pdf(self, blocks: list, eslogan: str = "") -> bytes:
        """
        Generate a PDF of observation blocks to a bytes buffer.
        Used for preview rendering with PyMuPDF.
        
        Args:
            blocks: List of block data dicts (title, note, image, separator, product_matrix)
            eslogan: Company slogan for footer
            
        Returns:
            PDF content as bytes
        """
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        
        buffer = BytesIO()
        width, height = A4
        c = canvas.Canvas(buffer, pagesize=A4)
        
        self._page_number = 1
        left_margin = 40
        right_margin = width - 40
        
        # Start position
        y = height - 50
        
        # Draw header
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(self.COLORS['primary'])
        c.drawString(left_margin, y, "DETALLES Y OBSERVACIONES")
        y -= 10
        c.setStrokeColor(self.COLORS['primary'])
        c.setLineWidth(2)
        c.line(left_margin, y, right_margin, y)
        y -= 25
        
        # Draw all blocks
        if blocks:
            y = self._draw_blocks(c, width, height, y, blocks, left_margin, right_margin, eslogan)
        
        # Final footer
        self._draw_footer(c, width, eslogan, self._page_number)
        c.save()
        
        return buffer.getvalue()
    
    def generate(self, file_path: str, empresa: str, datos_empresa: dict,
                 productos: List[list], total: float, moneda: str, fecha: str,
                 mostrar_terminos: bool = True, mostrar_firma: bool = True,
                 validez_dias: int = 30, cliente: dict = None,
                 observaciones_data: dict = None, numero_cotizacion: str = "",
                 document_type: str = "Cotizacion", shipping: float = 0,
                 cover_page_data: dict = None, warranty_data: dict = None,
                 estimated_days: int = 7, shipping_type: str = "Sin envío",
                 installation_terms: str = "", payment_method: str = "",
                 bank_details: str = "", payment_type: str = "",
                 apply_iva: bool = True, include_details: bool = True,
                 terms_data: dict = None, prepared_by: str = "",
                 signature_image: str = None):
        """
        Generate a professional PDF quotation or receipt.
        
        Args:
            file_path: Output PDF path
            empresa: Company name
            datos_empresa: Company data dict (direccion, telefono, correo, logo, eslogan)
            productos: List of products [desc, qty, unit, price, amount]
            total: Total amount
            moneda: Currency
            fecha: Date string
            mostrar_terminos: Show summary terms
            mostrar_firma: Show signature area
            validez_dias: Quotation validity days
            cliente: Client data dict (name, contact, address)
            observaciones_data: Observations data (blocks, products)
            numero_cotizacion: Quotation/receipt number
            document_type: "Cotizacion" or "Recibo"
            shipping: Shipping cost
            cover_page_data: Cover page configuration dict
            warranty_data: Warranty info dict (duration, covers, excludes)
            estimated_days: Estimated delivery days
            shipping_type: Type of shipping (Delivery, Encomienda, etc.)
            installation_terms: Installation terms text
            payment_method: Payment method text
            bank_details: Bank details for payment
            include_details: Whether to include the details/observations page
            terms_data: Enhanced terms and conditions data (Clauses)
        """
        # Determine if we have extended clauses to show
        # Default to False - only show if explicitly enabled
        mostrar_terms_blocks = False
        if terms_data:
            # Only show if the flags are explicitly True AND have content
            def has_content(text):
                if not text:
                    return False
                import re
                return bool(re.sub(r'<[^>]+>', '', str(text)).strip())
            
            show_install = terms_data.get("show_installation", False) and has_content(terms_data.get("installation_terms"))
            show_pay = terms_data.get("show_payment", False) and has_content(terms_data.get("payment_terms"))
            show_gen = terms_data.get("show_general", False) and has_content(terms_data.get("general_terms"))
            mostrar_terms_blocks = show_install or show_pay or show_gen
        # Installation might be passed as separate arg too, check content
        if installation_terms:
            import re
            if re.sub(r'<[^>]+>', '', str(installation_terms)).strip():
                mostrar_terms_blocks = True
        
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        
        # Store for internal method access
        self._current_eslogan = datos_empresa.get('eslogan', '')
        self._current_width = width
        
        # Reset page counter
        self._page_number = 1
        
        # === COVER PAGE (if enabled) ===
        if cover_page_data and cover_page_data.get("enabled", False):
            self._draw_cover_page(c, width, height, empresa, datos_empresa, 
                                   cliente, fecha, cover_page_data)
            c.showPage()
            self._page_number += 1
        
        # Current Y position (from top)
        y = height - 40
        
        # === PAGE 1: HEADER, PRODUCTS, TOTAL (Cotizacion) ===
        
        # === HEADER ===
        y = self._draw_header(c, width, y, empresa, datos_empresa, fecha, 
                              cliente, numero_cotizacion, document_type)
        
        # === PRODUCTS TABLE (Standard) ===
        y = self._draw_table(c, width, y, productos)
        
        # === TOTAL ===
        # Determine if shipping is enabled (has a valid shipping type)
        shipping_enabled = shipping_type and shipping_type != "Sin envío"
        y = self._draw_total(c, width, y, total, moneda, 
                             shipping_enabled=shipping_enabled,
                             shipping_type=shipping_type,
                             shipping=shipping)
        
        # === SUMMARY (Resumen de condiciones) - Below Total on Page 1/2 ===
        if mostrar_terminos:
            y = self._draw_summary(c, width, y, validez_dias, estimated_days, 
                                   shipping_type, payment_method, shipping, apply_iva, moneda)

        # === PRODUCT MATRIX (Vertical 4/page) - Page 2+ ===
        # Use simple heuristic: if products have images, show the matrix too? 
        # Or always show it if the user enabled "include_details"?
        # User requested "en la lista de imagenes de productos pon 4 por oja".
        # We'll assume the explicit matrix is desired if there are images.
        products_with_images = [p for p in productos if len(p) > 5 and p[5]]
        if products_with_images:
            # Force new page for Matrix
            self._draw_footer(c, width, datos_empresa.get('eslogan', ''), self._page_number)
            c.showPage()
            self._page_number += 1
            y = height - 50
            
            y = self._draw_product_matrix(c, width, height, y, productos)

        # === DETALLES Y OBSERVACIONES (Page 3+ start) ===
        if include_details and observaciones_data and self._has_observations(observaciones_data):
            # Force new page for Observations
            self._draw_footer(c, width, datos_empresa.get('eslogan', ''), self._page_number)
            c.showPage()
            self._page_number += 1
            y = height - 50
            
            y = self._draw_observations_section(c, width, height, y, observaciones_data, 
                                                datos_empresa.get('eslogan', ''))

        # === CLAUSULAS (Installation, Payment, General, Warranty, Acceptance) ===
        
        # 1. Terms Clauses (Installation, Payment, General) - Page 3+
        if mostrar_terms_blocks:
            # Force new page for Clauses
            self._draw_footer(c, width, datos_empresa.get('eslogan', ''), self._page_number)
            c.showPage()
            self._page_number += 1
            y = height - 50

            # Draw Terms Blocks
            y = self._draw_clauses(c, width, y, terms_data, installation_terms)
            
        # Bank Details
            # Bank Details - Check validity
            if bank_details:
                # Strip HTML to see if it's just empty tags
                import re
                plain_text = re.sub(r'<[^>]+>', '', bank_details).strip()
                if plain_text:
                     # If clauses were drawn, we are on Page 3+, verify space
                     if not mostrar_terms_blocks:
                          # If no blocks, force page for Bank or group with warranty?
                          # User said "Pagos no se genera". Bank is usually part of payments.
                          # Let's put it on the Clauses page.
                          self._draw_footer(c, width, datos_empresa.get('eslogan', ''), self._page_number)
                          c.showPage()
                          self._page_number += 1
                          y = height - 50
                     
                     y = self._draw_bank_details(c, width, y, bank_details)

        # 2. Warranty Section - Only if EXPLICITLY enabled via checkbox AND has content
        # Helper to check if text has content (strips HTML)
        def has_content(text):
            if not text:
                return False
            import re
            plain = re.sub(r'<[^>]+>', '', str(text)).strip()
            return bool(plain)
        
        # Check if warranty is enabled via checkbox flag (show_warranty from TermsWindow)
        show_warranty = terms_data.get("show_warranty", False) if terms_data else False
        
        # Only proceed if warranty checkbox is checked
        if show_warranty and warranty_data:
            # Then verify there's actual content
            has_warranty_content = (
                has_content(warranty_data.get("duration")) or
                has_content(warranty_data.get("garantia")) or
                has_content(warranty_data.get("covers")) or
                has_content(warranty_data.get("excludes")) or
                has_content(warranty_data.get("warning")) or
                has_content(warranty_data.get("verification")) or
                has_content(warranty_data.get("terms")) or
                has_content(warranty_data.get("warranty_terms"))
            )
            
            if has_warranty_content:
                self._draw_footer(c, width, datos_empresa.get('eslogan', ''), self._page_number)
                c.showPage()
                self._page_number += 1
                y = height - 50
                y = self._draw_warranty_section(c, width, y, warranty_data)

        # === ACCEPTANCE AND SIGNATURES ===
        # Check if acceptance is enabled via checkbox flag (show_acceptance from TermsWindow)
        show_acceptance = terms_data.get("show_acceptance", False) if terms_data else False
        acceptance_text = terms_data.get("acceptance_terms", "") if terms_data else ""
        
        # Only show acceptance if explicitly enabled AND has content
        has_acceptance = show_acceptance and has_content(acceptance_text)
        
        # Only create this page if firma is enabled OR acceptance is enabled with content
        if mostrar_firma or has_acceptance:
            self._draw_footer(c, width, datos_empresa.get('eslogan', ''), self._page_number)
            c.showPage()
            self._page_number += 1
            y = height - 50
            
            if has_acceptance:
                y = self._draw_acceptance_section(c, width, y, acceptance_text)
            
            if mostrar_firma:
                y = self._draw_signature(c, width, y)
        
        # Final Footer
        self._draw_footer(c, width, datos_empresa.get('eslogan', ''), self._page_number)
        
        c.save()
        print(f"PDF generado exitosamente: {file_path}")
        return True
    
    def _has_observations(self, obs_data: dict) -> bool:
        """Check if there are any observations to display."""
        # Helper to strip html
        def has_text(html):
            if not html: return False
            # Remove tags
            import re
            text = re.sub(r'<[^>]+>', '', html)
            return bool(text.strip())

        # New blocks format
        if obs_data.get("blocks", []):
            return True
        # Legacy format
        if has_text(obs_data.get("text", "")):
            return True
        if obs_data.get("gallery", []):
            return True
        return False
    
    def _draw_header(self, c: canvas.Canvas, width: float, y: float,
                     empresa: str, datos_empresa: dict, fecha: str,
                     cliente: dict = None, numero_cotizacion: str = "",
                     document_type: str = "Cotizacion") -> float:
        """Draw the header section with company on left, client on right.
        Uses professional formatting with borders, no emojis."""
        left_margin = 40
        right_margin = width - 40
        
        # === LEFT SIDE: COMPANY INFO ===
        
        # Load company logo directly from .emp ZIP file
        logo_height = 0
        import zipfile
        import io
        import sys
        
        # Get correct base directory (works for both dev and frozen .exe)
        if getattr(sys, 'frozen', False):
            # Running as compiled .exe
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        emp_file = os.path.join(base_dir, "media", "companies", f"{empresa}.emp")
        
        print(f"[LOGO] Buscando empresa: {empresa}")
        print(f"[LOGO] Base dir: {base_dir}")
        print(f"[LOGO] Archivo .emp: {emp_file}")
        
        if os.path.exists(emp_file):
            try:
                with zipfile.ZipFile(emp_file, 'r') as zf:
                    # Find logo file in ZIP
                    logo_data = None
                    for name in zf.namelist():
                        if name.startswith("logo."):
                            logo_data = zf.read(name)
                            print(f"[LOGO] ✓ Encontrado en ZIP: {name} ({len(logo_data)} bytes)")
                            break
                    
                    if logo_data:
                        # Load from memory
                        logo_stream = io.BytesIO(logo_data)
                        logo = ImageReader(logo_stream)
                        orig_width, orig_height = logo.getSize()
                        print(f"[LOGO] ✓ Logo cargado: {orig_width}x{orig_height}")
                        
                        # Scale logo
                        max_logo_width = 80
                        max_logo_height = 50
                        ratio = min(max_logo_width / orig_width, max_logo_height / orig_height)
                        
                        new_width = orig_width * ratio
                        new_height = orig_height * ratio
                        
                        c.drawImage(logo, left_margin, y - new_height, 
                                   width=new_width, height=new_height)
                        logo_height = new_height + 10
                        print(f"[LOGO] ✓ Logo dibujado en PDF")
                    else:
                        print(f"[LOGO] ✗ No hay logo en el archivo .emp")
            except Exception as e:
                print(f"[LOGO] ✗ Error: {e}")
        else:
            print(f"[LOGO] ✗ Archivo .emp no existe: {emp_file}")
        
        # Company name
        info_x = left_margin
        company_y = y - logo_height - 20 if logo_height else y - 15
        
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(info_x, company_y, empresa)
        
        # Company details
        c.setFont("Helvetica", 9)
        c.setFillColor(self.COLORS['gray'])
        
        details_y = company_y - 16
        
        if datos_empresa.get('telefono'):
            c.drawString(info_x, details_y, f"Tel: {datos_empresa['telefono']}")
            details_y -= 12
        
        if datos_empresa.get('correo'):
            c.drawString(info_x, details_y, f"Email: {datos_empresa['correo']}")
            details_y -= 12
        
        if datos_empresa.get('direccion'):
            c.drawString(info_x, details_y, f"Dir: {datos_empresa['direccion']}")
            details_y -= 12
        
        if datos_empresa.get('eslogan'):
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(info_x, details_y, datos_empresa['eslogan'])
            details_y -= 12
        
        # === RIGHT SIDE: CLIENT INFO ===
        
        right_x = right_margin
        client_y = y - 15
        
        # Document title (Cotizacion or Recibo)
        doc_title = "COTIZACION" if document_type == "Cotizacion" else "RECIBO"
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(self.COLORS['primary'])
        c.drawRightString(right_x, client_y, doc_title)
        client_y -= 18
        
        c.setFont("Helvetica", 10)
        c.setFillColor(self.COLORS['dark'])
        if numero_cotizacion:
            c.drawRightString(right_x, client_y, f"Nº: {numero_cotizacion}")
            client_y -= 14
        
        c.setFillColor(self.COLORS['gray'])
        c.drawRightString(right_x, client_y, f"Fecha: {fecha}")
        client_y -= 20
        
        # Client data
        if cliente:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(self.COLORS['dark'])
            c.drawRightString(right_x, client_y, "CLIENTE:")
            client_y -= 14
            
            c.setFont("Helvetica", 9)
            c.setFillColor(self.COLORS['gray'])
            
            if cliente.get('name'):
                c.drawRightString(right_x, client_y, cliente['name'])
                client_y -= 12
            
            if cliente.get('contact'):
                c.drawRightString(right_x, client_y, cliente['contact'])
                client_y -= 12
            
            if cliente.get('address'):
                c.drawRightString(right_x, client_y, cliente['address'])
                client_y -= 12
        
        # Calculate lowest point
        lowest_y = min(details_y, client_y)
        
        # Separator line
        y = lowest_y - 10
        c.setStrokeColor(self.COLORS['border'])
        c.setLineWidth(1)
        c.line(left_margin, y, right_margin, y)
        
        return y - 15
    
    def _get_logo_path(self, empresa: str, datos_empresa: dict) -> Optional[str]:
        """Get the logo path for the company, extracting from .emp ZIP if needed."""
        import zipfile
        import tempfile
        import sys
        
        # Immediate output for debugging
        print("=" * 50, flush=True)
        print(f"[LOGO] === ENTRANDO A _get_logo_path ===", flush=True)
        print(f"[LOGO] Buscando logo para empresa: '{empresa}'", flush=True)
        sys.stdout.flush()
        
        # Get base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 1. Check if already extracted to temp
        temp_dir = os.path.join(base_dir, "media", "config", "temp_companies", empresa)
        if os.path.isdir(temp_dir):
            for ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']:
                logo_path = os.path.join(temp_dir, f"logo.{ext}")
                if os.path.exists(logo_path):
                    print(f"[LOGO] ✓ Encontrado en temp: {logo_path}")
                    print("=" * 50)
                    return logo_path
        
        # 2. Check logo_path from datos_empresa
        if datos_empresa.get('logo_path'):
            logo_path = datos_empresa['logo_path']
            if os.path.exists(logo_path):
                print(f"[LOGO] ✓ Encontrado en datos_empresa: {logo_path}")
                print("=" * 50)
                return logo_path
        
        # 3. Extract from .emp ZIP file
        emp_file = os.path.join(base_dir, "media", "companies", f"{empresa}.emp")
        print(f"[LOGO] Buscando archivo .emp: {emp_file}")
        
        if os.path.exists(emp_file):
            try:
                with zipfile.ZipFile(emp_file, 'r') as zf:
                    # Find logo file in ZIP
                    for name in zf.namelist():
                        if name.startswith("logo."):
                            print(f"[LOGO] ✓ Logo encontrado en ZIP: {name}")
                            
                            # Extract to temp directory
                            os.makedirs(temp_dir, exist_ok=True)
                            zf.extract(name, temp_dir)
                            extracted_path = os.path.join(temp_dir, name)
                            
                            print(f"[LOGO] ✓ Extraído a: {extracted_path}")
                            print("=" * 50)
                            return extracted_path
                            
                print(f"[LOGO] ✗ No hay logo en el archivo .emp")
            except Exception as e:
                print(f"[LOGO] ✗ Error leyendo .emp: {e}")
        else:
            print(f"[LOGO] ✗ Archivo .emp no existe")
        
        print(f"[LOGO] ✗ NO SE ENCONTRÓ LOGO PARA '{empresa}'")
        print("=" * 50)
        return None
    
    def _draw_table(self, c: canvas.Canvas, width: float, y: float,
                    productos: List[list]) -> float:
        """Draw the products table with dynamic resizing and pagination."""
        left_margin = 40
        right_margin = width - 40
        table_width = width - 80
        
        # Define Columns: [Description, Qty, Unit, Price, Total] - NO IMG column
        col_widths = [
            table_width - 250,  # Description (Dynamic remainder)
            50,                 # Quantity
            70,                 # Unit
            65,                 # Price
            65                  # Total
        ]
        
        headers = ["Descripción", "Cant.", "Unidad", "Precio", "Importe"]
        
        # Prepare Data items
        data = [headers]
        
        styles = getSampleStyleSheet()
        styleN = styles["BodyText"]
        styleN.fontSize = 9
        styleN.alignment = TA_LEFT
        
        for p in productos:
            # Unpack (expecting 6 items: desc, qty, unit, price, total, image_path)
            # If length differs, handle gracefully
            if len(p) >= 6:
                desc, qty, unit, price, total, img_path = p[0], p[1], p[2], p[3], p[4], p[5]
            else:
                # Fallback for old data or missing image path
                desc, qty, unit, price, total = p[0], p[1], p[2], p[3], p[4]
                img_path = None
            
            # Description Paragraph
            desc_text = str(desc).replace('\n', '<br/>')
            desc_flowable = Paragraph(desc_text, styleN)
            
            # Display unit (empty string if None)
            unit_display = str(unit) if unit else ""
            
            # Row - NO IMG column
            data.append([
                desc_flowable,
                qty,
                unit_display,
                price,
                total
            ])
            
        # Create Table
        t = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Style
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['table_header']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),   # Desc Left
            ('ALIGN', (1, 1), (2, -1), 'CENTER'), # Qty & Unit Center
            ('ALIGN', (-2, 1), (-1, -1), 'RIGHT'), # Price/Total Right
            
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLORS['table_alt']])
        ]))
        
        # Pagination Loop
        # We need to manually split the table if it doesn't fit
        bottom_margin = 60 # Reserve content for footer
        
        # Wrap table to get size
        w, h = t.wrap(table_width, 0x7FFFFFFF) # Infinite height for wrap
        
        while h > 0:
            available_height = y - bottom_margin
            
            if h <= available_height:
                # Fits entirely
                t.drawOn(c, left_margin, y - h)
                y -= (h + 20)
                break
            else:
                # Needs split
                # split(availWidth, availHeight)
                # Note: Table.split returns list of tables
                try:
                    split_tables = t.split(table_width, available_height)
                except Exception:
                    # Fallback if strict split check fails or barely fits
                    split_tables = []
                
                if len(split_tables) > 0:
                    t0 = split_tables[0]
                    w0, h0 = t0.wrap(table_width, available_height)
                    t0.drawOn(c, left_margin, y - h0)
                    
                    # Draw footer before new page
                    self._draw_footer(c, width, self._current_eslogan, self._page_number)
                    
                    # New Page
                    c.showPage()
                    self._page_number += 1
                    y = A4[1] - 40 # Top margin
                    
                    if len(split_tables) > 1:
                        t = split_tables[1]
                        w, h = t.wrap(table_width, 0x7FFFFFFF)
                    else:
                        break # Should not happen if h > available
                else:
                    # Could not split (maybe single row too large?), force new page
                    self._draw_footer(c, width, self._current_eslogan, self._page_number)
                    c.showPage()
                    self._page_number += 1
                    y = A4[1] - 40
                    # Retry full draw on new page
                    continue
                    
        return y
    
    def _draw_total(self, c: canvas.Canvas, width: float, y: float,
                    total: float, moneda: str, shipping_enabled: bool = False,
                    shipping_type: str = "", shipping: float = 0) -> float:
        """Draw the total section with optional shipping info above."""
        left_margin = 40
        
        # === SHIPPING INFO (if enabled) ===
        if shipping_enabled and shipping_type:
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            
            # Build shipping text
            if shipping_type == "Gratis":
                shipping_text = f"Envío: {shipping_type}"
            elif shipping > 0:
                shipping_text = f"Envío: {shipping_type} + {shipping:,.2f} {moneda}"
            else:
                shipping_text = f"Envío: {shipping_type}"
            
            # Position in the right area (aligned with total box)
            box_width = 250
            box_x = width - 40 - box_width
            c.drawString(box_x + 15, y - 10, shipping_text)
            y -= 25
        
        # === TOTAL BOX ===
        amount_text = f"{total:.2f} {moneda}"
        est_text_width = len(amount_text) * 9 + 50 
        box_width = max(250, est_text_width + 80)
        
        box_x = width - 40 - box_width
        
        # Background
        c.setFillColor(colors.HexColor('#F0F0F5'))
        c.roundRect(box_x, y - 35, box_width, 35, 6, fill=True, stroke=False)
        
        # Total text (Label)
        c.setFillColor(self.COLORS['dark'])
        c.setFont("Helvetica-Bold", 14)
        c.drawString(box_x + 15, y - 25, "TOTAL:")
        
        # Amount
        c.setFillColor(self.COLORS['primary'])
        c.drawRightString(box_x + box_width - 15, y - 25, amount_text)
        
        return y - 55
    
    def _draw_summary(self, c: canvas.Canvas, width: float, y: float,
                      validez_dias: int, estimated_days: int, shipping_type: str,
                      payment_method: str, shipping: float, apply_iva: bool, moneda: str) -> float:
        """Draw summary of conditions (Validity, Delivery, Price) below Quotation totals."""
        left_margin = 40
        right_margin = width - 40
        
        # Check space (keep with totals if possible, usually small)
        if y < 150:
            c.showPage()
            self._page_number += 1
            y = A4[1] - 40
            
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(left_margin, y - 10, "Resumen de Condiciones")
        
        c.setStrokeColor(self.COLORS['border'])
        c.line(left_margin, y - 18, right_margin, y - 18)
        
        # Build summary terms list
        terms = []
        terms.append(f"Validez de la oferta: {validez_dias} días.")
        if estimated_days > 0:
            terms.append(f"Tiempo de Entrega estimado: {estimated_days} días.")
        
        # Shipping info
        if shipping_type and shipping_type != "Sin envío":
            if shipping > 0:
                terms.append(f"Envío: {shipping_type} ({shipping:,.2f} {moneda})")
            else:
                terms.append(f"Envío: {shipping_type}")
        elif shipping > 0:
            terms.append(f"Costo de Envío: {shipping:,.2f} {moneda}")
        
        # IVA
        if apply_iva:
            terms.append("Precios incluyen IVA.")
        else:
            terms.append("Precios NO incluyen IVA.")
            
        c.setFont("Helvetica", 9)
        c.setFillColor(self.COLORS['gray'])
        
        term_y = y - 35
        for term in terms:
            c.drawString(left_margin + 10, term_y, f"• {term}")
            term_y -= 14
        
        return term_y - 15

    def _draw_clauses(self, c: canvas.Canvas, width: float, y: float, 
                      terms_data: dict, installation_terms: str) -> float:
        """Draw explicit clauses: Installation, Payment (separate page), General."""
        height = A4[1]
        
        # 1. Installation Terms
        if installation_terms and terms_data.get("show_installation", True):
             y = self._draw_term_block(c, width, y, "Términos de Instalación", installation_terms)
             y -= 20
        
        # 2. Payment Terms - SEPARATE PAGE
        if terms_data and terms_data.get("show_payment", True):
            payment_content = terms_data.get("payment_terms", "")
            payment_method = terms_data.get("payment_method", "")
            payment_type = terms_data.get("payment_type", "")
            
            # Only draw if there's content
            if payment_content or payment_method or payment_type:
                # Force new page for Payment
                self._draw_footer(c, width, "", self._page_number)
                c.showPage()
                self._page_number += 1
                y = height - 50
                
                # Draw Payment Section with its own styling
                y = self._draw_payment_section(c, width, y, payment_method, payment_type, payment_content)
        
        # 3. General Terms
        if terms_data and terms_data.get("show_general", True):
            general_content = terms_data.get("general_terms", "")
            if general_content:
                y = self._draw_term_block(c, width, y, "Términos Generales", general_content)
                y -= 20
                
        return y
    
    def _draw_payment_section(self, c: canvas.Canvas, width: float, y: float,
                              payment_method: str, payment_type: str, content: str) -> float:
        """Draw dedicated payment section page with method, type and details."""
        left_margin = 40
        right_margin = width - 40
        available_width = right_margin - left_margin
        content_width = available_width - 20
        
        # === HEADER ===
        header_height = 32
        
        # Accent bar (green for money)
        c.setFillColor(colors.HexColor("#10B981"))
        c.rect(left_margin, y - header_height, 4, header_height, fill=True, stroke=False)
        
        # Header background
        c.setFillColor(colors.HexColor("#ECFDF5"))
        c.rect(left_margin + 4, y - header_height, available_width - 4, header_height, fill=True, stroke=False)
        
        # Title
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(left_margin + 15, y - 22, "Condiciones de Pago")
        
        y -= header_height + 8
        
        # Separator
        c.setStrokeColor(colors.HexColor("#E0E0E0"))
        c.setLineWidth(1)
        c.line(left_margin, y, right_margin, y)
        y -= 25
        
        # === PAYMENT METHOD & TYPE PILLS ===
        if payment_method:
            # Method pill
            c.setFillColor(colors.HexColor("#DBEAFE"))  # Light blue
            pill_width = 200
            c.roundRect(left_margin, y - 26, pill_width, 26, 13, fill=True, stroke=False)
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#1D4ED8"))  # Dark blue
            c.drawString(left_margin + 12, y - 18, f"Método: {payment_method}")
            y -= 40
        
        if payment_type:
            # Type pill
            c.setFillColor(colors.HexColor("#FEF3C7"))  # Light yellow
            pill_width = 220
            c.roundRect(left_margin, y - 26, pill_width, 26, 13, fill=True, stroke=False)
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.HexColor("#B45309"))  # Dark amber
            c.drawString(left_margin + 12, y - 18, f"Condición: {payment_type}")
            y -= 40
        
        # === DETAILS CONTENT ===
        if content and content.strip():
            # Subtitle
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(self.COLORS['dark'])
            c.drawString(left_margin, y, "Detalles Adicionales:")
            y -= 20
            
            # Parse HTML
            if "<" in content and ">" in content:
                try:
                    parser = ReportLabHTMLParser()
                    parser.feed(content)
                    parsed_content = parser.get_result()
                except:
                    parsed_content = content.replace("\n", "<br/>")
            else:
                parsed_content = content.replace("\n", "<br/>")
            
            # Paragraph style
            style = ParagraphStyle(
                'PaymentDetails',
                parent=self.styles['Normal'],
                fontName='Helvetica',
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#333333"),
                leftIndent=10
            )
            
            p = Paragraph(parsed_content, style)
            w, h = p.wrap(content_width, A4[1])
            p.drawOn(c, left_margin + 10, y - h)
            y -= (h + 20)
        
        return y
    
    def _draw_term_block(self, c: canvas.Canvas, width: float, y: float, 
                         title: str, content: str) -> float:
        """Draw a specific term block with beautiful styling matching preview.
        
        Features:
        - Decorative header box with accent color
        - Proper separator line
        - Clean typography with good spacing
        """
        if not content.strip():
            return y
            
        left_margin = 40
        right_margin = width - 40
        available_width = right_margin - left_margin
        content_width = available_width - 20  # Padding inside
        
        # Check space (conservative estimate)
        if y < 180:
            c.showPage()
            self._page_number += 1
            y = A4[1] - 50
        
        # === HEADER WITH ACCENT BAR ===
        header_height = 28
        
        # Accent bar on left
        c.setFillColor(self.COLORS['primary'])
        c.rect(left_margin, y - header_height, 4, header_height, fill=True, stroke=False)
        
        # Header background
        c.setFillColor(colors.HexColor("#F8F9FA"))
        c.rect(left_margin + 4, y - header_height, available_width - 4, header_height, fill=True, stroke=False)
        
        # Title text
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(left_margin + 15, y - 19, title)
        
        y -= header_height + 5
        
        # Separator line
        c.setStrokeColor(colors.HexColor("#E0E0E0"))
        c.setLineWidth(1)
        c.line(left_margin, y, right_margin, y)
        y -= 15
        
        # === CONTENT AREA ===
        # Parse HTML content
        parsed_content = content
        if "<" in content and ">" in content:
            try:
                parser = ReportLabHTMLParser()
                parser.feed(content)
                parsed_content = parser.get_result()
            except Exception as e:
                print(f"Error parsing HTML: {e}")
                parsed_content = content.replace("\n", "<br/>")
        elif "\n" in content:
            parsed_content = content.replace("\n", "<br/>")
        
        # Enhanced paragraph style
        style = ParagraphStyle(
            'TermStyleEnhanced',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#333333"),
            leftIndent=10,
            rightIndent=10,
            spaceBefore=6,
            spaceAfter=6
        )
        
        p = Paragraph(parsed_content, style)
        w, h = p.wrap(content_width, A4[1])
        
        # Handle pagination
        available_height = y - 60  # Bottom margin
        
        if h <= available_height:
            # Fits on current page
            p.drawOn(c, left_margin + 10, y - h)
            y -= (h + 20)
        else:
            # Needs pagination
            if available_height < 150:
                # Not enough space, new page
                c.showPage()
                self._page_number += 1
                y = A4[1] - 50
                available_height = y - 60
            
            # Try to split paragraph
            try:
                split_parts = p.split(content_width, available_height)
                if split_parts and len(split_parts) > 0:
                    # Draw first part
                    p0 = split_parts[0]
                    w0, h0 = p0.wrap(content_width, available_height)
                    p0.drawOn(c, left_margin + 10, y - h0)
                    
                    # New page for remainder
                    c.showPage()
                    self._page_number += 1
                    y = A4[1] - 50
                    
                    # Draw remaining parts
                    for part in split_parts[1:]:
                        wp, hp = part.wrap(content_width, A4[1] - 100)
                        if hp > y - 60:
                            c.showPage()
                            self._page_number += 1
                            y = A4[1] - 50
                        part.drawOn(c, left_margin + 10, y - hp)
                        y -= (hp + 10)
                else:
                    # Split failed, just draw and hope
                    p.drawOn(c, left_margin + 10, y - h)
                    y -= (h + 20)
            except Exception:
                # Fallback: draw on new page
                c.showPage()
                self._page_number += 1
                y = A4[1] - 50
                p.drawOn(c, left_margin + 10, y - h)
                y -= (h + 20)

        return y
    
    # Import at top of file
    try:
        from .cover_styles import CoverPageRenderer
    except ImportError:
        # Fallback if relative import fails during direct execution
        from src.export.cover_styles import CoverPageRenderer

    def _draw_cover_page(self, c: canvas.Canvas, width: float, height: float,
                         empresa: str, datos_empresa: dict, cliente: dict,
                         fecha: str, cover_data: dict):
        """Draw a professional cover page using the external renderer."""
        renderer = CoverPageRenderer()
        renderer.draw_cover(c, width, height, empresa, datos_empresa, cliente, fecha, cover_data)
    
    # helper methods for footer/logos are handled in renderer now or can serve as fallback
    def _get_logo_path(self, empresa, datos_empresa):
        return datos_empresa.get("logo", "")
    
    def _draw_cover_classic(self, c: canvas.Canvas, width: float, height: float,
                            empresa: str, datos_empresa: dict, cliente: dict,
                            fecha: str, cover_data: dict):
        """Classic centered cover page - Logo and text centered."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        
        # Border (if enabled)
        if cover_data.get("show_border", True):
            c.setStrokeColor(accent_color)
            c.setLineWidth(3)
            c.rect(30, 30, width - 60, height - 60)
        
        y = height - 100
        
        # Logo (if enabled)
        if cover_data.get("show_logo", True):
            y = self._draw_cover_logo(c, width, y, empresa, datos_empresa, cover_data, "center")
        
        # Project Name
        y = self._draw_cover_project_title(c, width, y, cover_data, accent_color, "center")
        
        # Description
        y = self._draw_cover_description(c, width, y, cover_data)
        
        # Separator
        c.setStrokeColor(accent_color)
        c.setLineWidth(2)
        c.line(width/2 - 80, y, width/2 + 80, y)
        y -= 40
        
        # Company and Client info
        y = self._draw_cover_parties(c, width, y, empresa, datos_empresa, cliente, cover_data, "center")
        
        # Date and Reference
        y = self._draw_cover_date_ref(c, width, y, fecha, cover_data, "center")
        
        # Footer text
        self._draw_cover_footer_text(c, width, cover_data)
    
    def _draw_cover_modern(self, c: canvas.Canvas, width: float, height: float,
                           empresa: str, datos_empresa: dict, cliente: dict,
                           fecha: str, cover_data: dict):
        """Modern lateral cover - Logo on left, vertical accent line."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        left_margin = 60
        
        # Vertical accent line on left
        c.setStrokeColor(accent_color)
        c.setLineWidth(6)
        c.line(25, 50, 25, height - 50)
        
        # Secondary thin line
        c.setLineWidth(1)
        c.line(35, 80, 35, height - 80)
        
        y = height - 80
        
        # Logo (left aligned)
        if cover_data.get("show_logo", True):
            logo_path = self._get_logo_path(empresa, datos_empresa)
            if logo_path and os.path.exists(logo_path):
                try:
                    logo_size = cover_data.get("logo_size", 120)
                    logo = ImageReader(logo_path)
                    orig_w, orig_h = logo.getSize()
                    ratio = min(logo_size / orig_w, logo_size / orig_h)
                    new_w, new_h = orig_w * ratio, orig_h * ratio
                    c.drawImage(logo_path, left_margin, y - new_h, width=new_w, height=new_h)
                    y -= new_h + 30
                except Exception:
                    y -= 30
        
        # Project Name (left aligned, large)
        project_name = cover_data.get("project_name", "")
        if project_name:
            c.setFont("Helvetica-Bold", 32)
            c.setFillColor(self.COLORS['dark'])
            c.drawString(left_margin, y, project_name)
            y -= 45
        
        # Subtitle with accent underline
        subtitle = cover_data.get("subtitle", "")
        if subtitle:
            c.setFont("Helvetica", 18)
            c.setFillColor(accent_color)
            c.drawString(left_margin, y, subtitle)
            # Underline
            text_width = c.stringWidth(subtitle, "Helvetica", 18)
            c.setStrokeColor(accent_color)
            c.setLineWidth(2)
            c.line(left_margin, y - 5, left_margin + text_width, y - 5)
            y -= 40
        
        # Description
        description = cover_data.get("description", "")
        if description:
            c.setFont("Helvetica", 11)
            c.setFillColor(self.COLORS['gray'])
            lines = self._wrap_text(description, c, width - left_margin - 80)
            for line in lines[:5]:
                c.drawString(left_margin, y, line)
                y -= 16
            y -= 20
        
        # Horizontal separator
        c.setStrokeColor(colors.HexColor('#E0E0E0'))
        c.setLineWidth(1)
        c.line(left_margin, y, width - 60, y)
        y -= 40
        
        # Company and Client side by side
        if cover_data.get("show_company", True):
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(self.COLORS['dark'])
            c.drawString(left_margin, y, "PREPARADO POR")
            y -= 16
            c.setFont("Helvetica-Bold", 12)
            c.drawString(left_margin, y, empresa)
            y -= 14
            c.setFont("Helvetica", 9)
            c.setFillColor(self.COLORS['gray'])
            if datos_empresa.get("telefono"):
                c.drawString(left_margin, y, datos_empresa['telefono'])
                y -= 12
            if datos_empresa.get("correo"):
                c.drawString(left_margin, y, datos_empresa['correo'])
                y -= 20
        
        if cover_data.get("show_client", True) and cliente:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(self.COLORS['dark'])
            c.drawString(left_margin, y, "PREPARADO PARA")
            y -= 16
            c.setFont("Helvetica", 12)
            if cliente.get("name"):
                c.drawString(left_margin, y, cliente["name"])
                y -= 20
        
        # Date at bottom left
        if cover_data.get("show_date", True):
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            c.drawString(left_margin, 60, f"Fecha: {fecha}")
        
        # Reference at bottom right
        reference = cover_data.get("reference", "")
        if reference and cover_data.get("show_reference", True):
            c.drawRightString(width - 60, 60, f"Ref: {reference}")
        
        self._draw_cover_footer_text(c, width, cover_data)
    
    def _draw_cover_minimal(self, c: canvas.Canvas, width: float, height: float,
                            empresa: str, datos_empresa: dict, cliente: dict,
                            fecha: str, cover_data: dict):
        """Minimalist cover - Clean design with lots of whitespace."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        
        # Single subtle border line at bottom
        if cover_data.get("show_border", True):
            c.setStrokeColor(accent_color)
            c.setLineWidth(4)
            c.line(40, 40, width - 40, 40)
        
        # Logo centered, smaller
        y = height / 2 + 120
        if cover_data.get("show_logo", True):
            logo_path = self._get_logo_path(empresa, datos_empresa)
            if logo_path and os.path.exists(logo_path):
                try:
                    logo_size = min(cover_data.get("logo_size", 120), 80)
                    logo = ImageReader(logo_path)
                    orig_w, orig_h = logo.getSize()
                    ratio = min(logo_size / orig_w, logo_size / orig_h)
                    new_w, new_h = orig_w * ratio, orig_h * ratio
                    c.drawImage(logo_path, (width - new_w) / 2, y - new_h, width=new_w, height=new_h)
                    y -= new_h + 60
                except Exception:
                    pass
        
        # Project Name - Large, centered
        project_name = cover_data.get("project_name", "")
        if project_name:
            c.setFont("Helvetica-Bold", 36)
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y, project_name)
            y -= 50
        
        # Subtitle - Simple
        subtitle = cover_data.get("subtitle", "")
        if subtitle:
            c.setFont("Helvetica-Light" if "Light" in c.getAvailableFonts() else "Helvetica", 14)
            c.setFillColor(self.COLORS['gray'])
            c.drawCentredString(width / 2, y, subtitle)
            y -= 80
        
        # Small accent dot
        c.setFillColor(accent_color)
        c.circle(width / 2, y, 4, fill=True, stroke=False)
        y -= 60
        
        # Date only
        if cover_data.get("show_date", True):
            c.setFont("Helvetica", 11)
            c.setFillColor(self.COLORS['gray'])
            c.drawCentredString(width / 2, y, fecha)
        
        self._draw_cover_footer_text(c, width, cover_data)
    
    def _draw_cover_corporate(self, c: canvas.Canvas, width: float, height: float,
                              empresa: str, datos_empresa: dict, cliente: dict,
                              fecha: str, cover_data: dict):
        """Corporate cover - Formal sections with backgrounds."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        
        # Top banner with company color
        c.setFillColor(accent_color)
        c.rect(0, height - 120, width, 120, fill=True, stroke=False)
        
        # Logo in banner (white background circle if needed)
        if cover_data.get("show_logo", True):
            logo_path = self._get_logo_path(empresa, datos_empresa)
            if logo_path and os.path.exists(logo_path):
                try:
                    logo_size = cover_data.get("logo_size", 120)
                    logo = ImageReader(logo_path)
                    orig_w, orig_h = logo.getSize()
                    ratio = min(logo_size / orig_w, logo_size / orig_h)
                    new_w, new_h = orig_w * ratio, orig_h * ratio
                    logo_x = (width - new_w) / 2
                    # White background for logo
                    c.setFillColor(colors.white)
                    c.roundRect(logo_x - 10, logo_y - new_h - 10, new_w + 20, new_h + 20, 8, fill=True, stroke=False)
                    c.drawImage(logo_path, logo_x, logo_y - new_h, width=new_w, height=new_h)
                except Exception:
                    pass
        
        # Company name in banner
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.white)
        c.drawCentredString(width / 2, height - 105, empresa)
        
        y = height - 180
        
        # Project section with gray background
        c.setFillColor(colors.HexColor('#F5F5F5'))
        c.rect(40, y - 120, width - 80, 120, fill=True, stroke=False)
        
        project_name = cover_data.get("project_name", "")
        if project_name:
            c.setFont("Helvetica-Bold", 24)
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y - 40, project_name)
        
        subtitle = cover_data.get("subtitle", "")
        if subtitle:
            c.setFont("Helvetica", 14)
            c.setFillColor(accent_color)
            c.drawCentredString(width / 2, y - 70, subtitle)
        
        y -= 160
        
        # Description in white area
        description = cover_data.get("description", "")
        if description:
            c.setFont("Helvetica", 11)
            c.setFillColor(self.COLORS['gray'])
            lines = self._wrap_text(description, c, width - 120)
            for line in lines[:4]:
                c.drawCentredString(width / 2, y, line)
                y -= 16
            y -= 20
        
        # Two column layout for company and client
        col_width = (width - 120) / 2
        left_col = 60
        right_col = width / 2 + 20
        
        row_y = y - 30
        
        if cover_data.get("show_company", True):
            # Company box
            c.setFillColor(colors.HexColor('#FAFAFA'))
            c.roundRect(left_col, row_y - 80, col_width - 20, 80, 6, fill=True, stroke=False)
            c.setStrokeColor(accent_color)
            c.setLineWidth(2)
            c.line(left_col, row_y - 2, left_col + col_width - 20, row_y - 2)
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(self.COLORS['dark'])
            c.drawString(left_col + 10, row_y - 25, "EMPRESA")
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            c.drawString(left_col + 10, row_y - 42, empresa)
            if datos_empresa.get("telefono"):
                c.drawString(left_col + 10, row_y - 56, datos_empresa['telefono'])
        
        if cover_data.get("show_client", True) and cliente:
            # Client box
            c.setFillColor(colors.HexColor('#FAFAFA'))
            c.roundRect(right_col, row_y - 80, col_width - 20, 80, 6, fill=True, stroke=False)
            c.setStrokeColor(accent_color)
            c.setLineWidth(2)
            c.line(right_col, row_y - 2, right_col + col_width - 20, row_y - 2)
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(self.COLORS['dark'])
            c.drawString(right_col + 10, row_y - 25, "CLIENTE")
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            if cliente.get("name"):
                c.drawString(right_col + 10, row_y - 42, cliente["name"])
            if cliente.get("contact"):
                c.drawString(right_col + 10, row_y - 56, cliente["contact"])
        
        # Bottom bar with date
        c.setFillColor(self.COLORS['dark'])
        c.rect(0, 0, width, 50, fill=True, stroke=False)
        
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.white)
        if cover_data.get("show_date", True):
            c.drawString(60, 20, f"Fecha: {fecha}")
        
        reference = cover_data.get("reference", "")
        if reference and cover_data.get("show_reference", True):
            c.drawRightString(width - 60, 20, f"Ref: {reference}")
    
    def _draw_cover_gradient(self, c: canvas.Canvas, width: float, height: float,
                             empresa: str, datos_empresa: dict, cliente: dict,
                             fecha: str, cover_data: dict):
        """Elegant gradient cover - Subtle gradient header/footer."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        
        # Simulated gradient header (multiple rectangles)
        gradient_steps = 20
        step_height = 150 / gradient_steps
        for i in range(gradient_steps):
            alpha = 1.0 - (i / gradient_steps) * 0.8
            c.setFillColor(colors.Color(
                accent_color.red * alpha + 1 * (1 - alpha),
                accent_color.green * alpha + 1 * (1 - alpha),
                accent_color.blue * alpha + 1 * (1 - alpha)
            ))
            c.rect(0, height - (i + 1) * step_height, width, step_height + 1, fill=True, stroke=False)
        
        # Simulated gradient footer
        for i in range(gradient_steps):
            alpha = (i / gradient_steps) * 0.5
            c.setFillColor(colors.Color(
                accent_color.red * alpha + 1 * (1 - alpha),
                accent_color.green * alpha + 1 * (1 - alpha),
                accent_color.blue * alpha + 1 * (1 - alpha)
            ))
            c.rect(0, i * step_height, width, step_height + 1, fill=True, stroke=False)
        
        y = height - 100
        
        # Logo with shadow effect
        if cover_data.get("show_logo", True):
            logo_path = self._get_logo_path(empresa, datos_empresa)
            if logo_path and os.path.exists(logo_path):
                try:
                    logo_size = cover_data.get("logo_size", 120)
                    logo = ImageReader(logo_path)
                    orig_w, orig_h = logo.getSize()
                    ratio = min(logo_size / orig_w, logo_size / orig_h)
                    new_w, new_h = orig_w * ratio, orig_h * ratio
                    logo_x = (width - new_w) / 2
                    # Shadow
                    c.setFillColor(colors.Color(0, 0, 0, alpha=0.1))
                    c.roundRect(logo_x + 4, y - new_h - 4, new_w, new_h, 4, fill=True, stroke=False)
                    c.drawImage(logo_path, logo_x, y - new_h, width=new_w, height=new_h)
                    y -= new_h + 50
                except Exception:
                    y -= 50
        
        # Project Name with shadow
        project_name = cover_data.get("project_name", "")
        if project_name:
            # Shadow
            c.setFont("Helvetica-Bold", 30)
            c.setFillColor(colors.Color(0, 0, 0, alpha=0.15))
            c.drawCentredString(width / 2 + 2, y - 2, project_name)
            # Main text
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y, project_name)
            y -= 45
        
        # Subtitle
        subtitle = cover_data.get("subtitle", "")
        if subtitle:
            c.setFont("Helvetica-Oblique", 16)
            c.setFillColor(accent_color)
            c.drawCentredString(width / 2, y, subtitle)
            y -= 35
        
        # Elegant divider
        c.setStrokeColor(accent_color)
        c.setLineWidth(1)
        div_width = 150
        c.line(width/2 - div_width/2, y, width/2 - 20, y)
        c.line(width/2 + 20, y, width/2 + div_width/2, y)
        # Diamond in center
        c.setFillColor(accent_color)
        c.saveState()
        c.translate(width/2, y)
        c.rotate(45)
        c.rect(-5, -5, 10, 10, fill=True, stroke=False)
        c.restoreState()
        y -= 50
        
        # Description
        description = cover_data.get("description", "")
        if description:
            c.setFont("Helvetica", 11)
            c.setFillColor(self.COLORS['gray'])
            lines = self._wrap_text(description, c, width - 140)
            for line in lines[:5]:
                c.drawCentredString(width / 2, y, line)
                y -= 16
            y -= 30
        
        # Company and Client
        y = self._draw_cover_parties(c, width, y, empresa, datos_empresa, cliente, cover_data, "center")
        
        # Date and Reference in footer area
        c.setFont("Helvetica", 11)
        c.setFillColor(self.COLORS['dark'])
        if cover_data.get("show_date", True):
            c.drawCentredString(width / 2, 80, fecha)
        
        reference = cover_data.get("reference", "")
        if reference and cover_data.get("show_reference", True):
            c.setFont("Helvetica", 9)
            c.drawCentredString(width / 2, 65, f"Ref: {reference}")
        
        self._draw_cover_footer_text(c, width, cover_data)
    
    def _draw_cover_executive(self, c: canvas.Canvas, width: float, height: float,
                              empresa: str, datos_empresa: dict, cliente: dict,
                              fecha: str, cover_data: dict):
        """Executive cover - Double lines, very formal."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        
        # Double border
        if cover_data.get("show_border", True):
            c.setStrokeColor(self.COLORS['dark'])
            c.setLineWidth(2)
            c.rect(25, 25, width - 50, height - 50)
            c.setLineWidth(0.5)
            c.rect(30, 30, width - 60, height - 60)
        
        # Top double line decoration
        c.setStrokeColor(accent_color)
        c.setLineWidth(2)
        c.line(60, height - 80, width - 60, height - 80)
        c.setLineWidth(0.5)
        c.line(60, height - 85, width - 60, height - 85)
        
        y = height - 120
        
        # Logo
        if cover_data.get("show_logo", True):
            y = self._draw_cover_logo(c, width, y, empresa, datos_empresa, cover_data, "center")
        
        # Company name in formal style
        if cover_data.get("show_company", True):
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y, empresa.upper())
            y -= 25
            
            # Decorative underline
            name_width = c.stringWidth(empresa.upper(), "Helvetica-Bold", 14)
            c.setStrokeColor(accent_color)
            c.setLineWidth(1)
            c.line(width/2 - name_width/2, y + 5, width/2 + name_width/2, y + 5)
            y -= 40
        
        # Presents text
        c.setFont("Helvetica-Oblique", 11)
        c.setFillColor(self.COLORS['gray'])
        c.drawCentredString(width / 2, y, "presenta")
        y -= 50
        
        # Project Name - Formal
        project_name = cover_data.get("project_name", "")
        if project_name:
            c.setFont("Helvetica-Bold", 26)
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y, project_name)
            y -= 35
        
        # Subtitle
        subtitle = cover_data.get("subtitle", "")
        if subtitle:
            c.setFont("Helvetica", 14)
            c.setFillColor(accent_color)
            c.drawCentredString(width / 2, y, subtitle)
            y -= 50
        
        # Double line divider
        c.setStrokeColor(self.COLORS['gray'])
        c.setLineWidth(1)
        c.line(width/2 - 100, y, width/2 + 100, y)
        c.setLineWidth(0.5)
        c.line(width/2 - 100, y - 4, width/2 + 100, y - 4)
        y -= 40
        
        # Description
        description = cover_data.get("description", "")
        if description:
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            lines = self._wrap_text(description, c, width - 160)
            for line in lines[:4]:
                c.drawCentredString(width / 2, y, line)
                y -= 14
            y -= 20
        
        # Client info formal
        if cover_data.get("show_client", True) and cliente:
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            c.drawCentredString(width / 2, y, "Preparado exclusivamente para:")
            y -= 18
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(self.COLORS['dark'])
            if cliente.get("name"):
                c.drawCentredString(width / 2, y, cliente["name"])
                y -= 25
        
        # Date and Reference at bottom with double lines
        c.setStrokeColor(accent_color)
        c.setLineWidth(2)
        c.line(60, 80, width - 60, 80)
        c.setLineWidth(0.5)
        c.line(60, 75, width - 60, 75)
        
        c.setFont("Helvetica", 10)
        c.setFillColor(self.COLORS['gray'])
        if cover_data.get("show_date", True):
            c.drawString(60, 55, f"Fecha: {fecha}")
        
        reference = cover_data.get("reference", "")
        if reference and cover_data.get("show_reference", True):
            c.drawRightString(width - 60, 55, f"Referencia: {reference}")
    
    def _draw_cover_creative(self, c: canvas.Canvas, width: float, height: float,
                             empresa: str, datos_empresa: dict, cliente: dict,
                             fecha: str, cover_data: dict):
        """Creative cover - Geometric shapes, dynamic design."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        
        # Geometric shapes decoration
        # Large circle top right
        c.setFillColor(colors.Color(accent_color.red, accent_color.green, accent_color.blue, alpha=0.15))
        c.circle(width - 50, height - 50, 150, fill=True, stroke=False)
        
        # Medium circle
        c.setFillColor(colors.Color(accent_color.red, accent_color.green, accent_color.blue, alpha=0.1))
        c.circle(width - 100, height - 150, 80, fill=True, stroke=False)
        
        # Small circles bottom left
        c.circle(80, 120, 60, fill=True, stroke=False)
        c.setFillColor(colors.Color(accent_color.red, accent_color.green, accent_color.blue, alpha=0.2))
        c.circle(50, 80, 30, fill=True, stroke=False)
        
        # Diagonal accent stripes
        c.setStrokeColor(accent_color)
        c.setLineWidth(3)
        c.line(0, height - 30, 80, height)
        c.line(0, height - 60, 110, height)
        
        # Triangle decoration bottom right
        c.setFillColor(accent_color)
        path = c.beginPath()
        path.moveTo(width, 0)
        path.lineTo(width, 100)
        path.lineTo(width - 100, 0)
        path.close()
        c.drawPath(path, fill=True, stroke=False)
        
        y = height - 150
        
        # Logo
        if cover_data.get("show_logo", True):
            logo_path = self._get_logo_path(empresa, datos_empresa)
            if logo_path and os.path.exists(logo_path):
                try:
                    logo_size = cover_data.get("logo_size", 120)
                    logo = ImageReader(logo_path)
                    orig_w, orig_h = logo.getSize()
                    ratio = min(logo_size / orig_w, logo_size / orig_h)
                    new_w, new_h = orig_w * ratio, orig_h * ratio
                    c.drawImage(logo_path, 60, y - new_h, width=new_w, height=new_h)
                    y -= new_h + 40
                except Exception:
                    y -= 40
        
        # Project Name - Dynamic angle effect (simulated with offset)
        project_name = cover_data.get("project_name", "")
        if project_name:
            # Accent background bar
            c.setFillColor(accent_color)
            c.rect(50, y - 10, 8, 40, fill=True, stroke=False)
            
            c.setFont("Helvetica-Bold", 32)
            c.setFillColor(self.COLORS['dark'])
            c.drawString(70, y, project_name)
            y -= 50
        
        # Subtitle
        subtitle = cover_data.get("subtitle", "")
        if subtitle:
            c.setFont("Helvetica", 16)
            c.setFillColor(self.COLORS['gray'])
            c.drawString(70, y, subtitle)
            y -= 50
        
        # Description
        description = cover_data.get("description", "")
        if description:
            c.setFont("Helvetica", 11)
            c.setFillColor(self.COLORS['gray'])
            lines = self._wrap_text(description, c, width - 160)
            for line in lines[:4]:
                c.drawString(70, y, line)
                y -= 16
            y -= 30
        
        # Creative divider (dots)
        c.setFillColor(accent_color)
        for i in range(7):
            c.circle(70 + i * 30, y, 4, fill=True, stroke=False)
        y -= 40
        
        # Company and Client
        if cover_data.get("show_company", True):
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(accent_color)
            c.drawString(70, y, "DE:")
            c.setFillColor(self.COLORS['dark'])
            c.drawString(100, y, empresa)
            y -= 20
        
        if cover_data.get("show_client", True) and cliente and cliente.get("name"):
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(accent_color)
            c.drawString(70, y, "PARA:")
            c.setFillColor(self.COLORS['dark'])
            c.drawString(115, y, cliente["name"])
            y -= 30
        
        # Date with icon-like element
        if cover_data.get("show_date", True):
            c.setFillColor(accent_color)
            c.rect(70, y - 2, 4, 14, fill=True, stroke=False)
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            c.drawString(80, y, fecha)
        
        self._draw_cover_footer_text(c, width, cover_data)
    
    def _draw_cover_premium(self, c: canvas.Canvas, width: float, height: float,
                            empresa: str, datos_empresa: dict, cliente: dict,
                            fecha: str, cover_data: dict):
        """Premium cover - Elegant golden/silver border, luxury feel."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        gold = colors.HexColor("#C9A962")  # Elegant gold
        
        # Ornate border
        if cover_data.get("show_border", True):
            # Outer border
            c.setStrokeColor(gold)
            c.setLineWidth(3)
            c.rect(20, 20, width - 40, height - 40)
            
            # Inner decorative border
            c.setLineWidth(1)
            c.rect(28, 28, width - 56, height - 56)
            
            # Corner ornaments (L shapes)
            corner_size = 25
            # Top left
            c.setLineWidth(2)
            c.line(35, height - 35, 35 + corner_size, height - 35)
            c.line(35, height - 35, 35, height - 35 - corner_size)
            # Top right
            c.line(width - 35, height - 35, width - 35 - corner_size, height - 35)
            c.line(width - 35, height - 35, width - 35, height - 35 - corner_size)
            # Bottom left
            c.line(35, 35, 35 + corner_size, 35)
            c.line(35, 35, 35, 35 + corner_size)
            # Bottom right
            c.line(width - 35, 35, width - 35 - corner_size, 35)
            c.line(width - 35, 35, width - 35, 35 + corner_size)
        
        y = height - 120
        
        # Logo with decorative frame
        if cover_data.get("show_logo", True):
            logo_path = self._get_logo_path(empresa, datos_empresa)
            if logo_path and os.path.exists(logo_path):
                try:
                    logo_size = cover_data.get("logo_size", 120)
                    logo = ImageReader(logo_path)
                    orig_w, orig_h = logo.getSize()
                    ratio = min(logo_size / orig_w, logo_size / orig_h)
                    new_w, new_h = orig_w * ratio, orig_h * ratio
                    logo_x = (width - new_w) / 2
                    
                    # Decorative frame around logo
                    frame_padding = 15
                    c.setStrokeColor(gold)
                    c.setLineWidth(1)
                    c.rect(logo_x - frame_padding, y - new_h - frame_padding, 
                           new_w + frame_padding * 2, new_h + frame_padding * 2)
                    
                    c.drawImage(logo_path, logo_x, y - new_h, width=new_w, height=new_h)
                    y -= new_h + 50
                except Exception:
                    y -= 50
        
        # Decorative line with diamond
        c.setStrokeColor(gold)
        c.setLineWidth(1)
        c.line(width/2 - 120, y, width/2 - 15, y)
        c.line(width/2 + 15, y, width/2 + 120, y)
        # Diamond
        c.saveState()
        c.translate(width/2, y)
        c.rotate(45)
        c.setFillColor(gold)
        c.rect(-6, -6, 12, 12, fill=True, stroke=False)
        c.restoreState()
        y -= 50
        
        # Project Name - Elegant
        project_name = cover_data.get("project_name", "")
        if project_name:
            c.setFont("Helvetica-Bold", 28)
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y, project_name)
            y -= 40
        
        # Subtitle in gold
        subtitle = cover_data.get("subtitle", "")
        if subtitle:
            c.setFont("Helvetica-Oblique", 14)
            c.setFillColor(gold)
            c.drawCentredString(width / 2, y, subtitle)
            y -= 45
        
        # Description
        description = cover_data.get("description", "")
        if description:
            c.setFont("Helvetica", 11)
            c.setFillColor(self.COLORS['gray'])
            lines = self._wrap_text(description, c, width - 160)
            for line in lines[:4]:
                c.drawCentredString(width / 2, y, line)
                y -= 15
            y -= 25
        
        # Elegant separator
        c.setStrokeColor(gold)
        c.setLineWidth(0.5)
        sep_width = 200
        c.line(width/2 - sep_width/2, y, width/2 - 30, y)
        c.line(width/2 + 30, y, width/2 + sep_width/2, y)
        # Small circles
        c.setFillColor(gold)
        c.circle(width/2 - 15, y, 3, fill=True, stroke=False)
        c.circle(width/2, y, 3, fill=True, stroke=False)
        c.circle(width/2 + 15, y, 3, fill=True, stroke=False)
        y -= 40
        
        # Company and Client - Premium layout
        if cover_data.get("show_company", True):
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            c.drawCentredString(width / 2, y, "Presentado por")
            y -= 16
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y, empresa)
            y -= 25
        
        if cover_data.get("show_client", True) and cliente and cliente.get("name"):
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            c.drawCentredString(width / 2, y, "Para")
            y -= 16
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y, cliente["name"])
            y -= 30
        
        # Date at bottom with ornate styling
        if cover_data.get("show_date", True):
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            c.drawCentredString(width / 2, 70, fecha)
        
        reference = cover_data.get("reference", "")
        if reference and cover_data.get("show_reference", True):
            c.setFont("Helvetica", 9)
            c.drawCentredString(width / 2, 55, f"Ref: {reference}")
        
        self._draw_cover_footer_text(c, width, cover_data)
    
    # === HELPER METHODS FOR COVER PAGES ===
    
    def _draw_cover_logo(self, c: canvas.Canvas, width: float, y: float,
                         empresa: str, datos_empresa: dict, cover_data: dict,
                         align: str = "center") -> float:
        """Draw logo for cover page. Returns new y position."""
        logo_path = self._get_logo_path(empresa, datos_empresa)
        if logo_path and os.path.exists(logo_path):
            try:
                logo_size = cover_data.get("logo_size", 120)
                logo = ImageReader(logo_path)
                orig_w, orig_h = logo.getSize()
                ratio = min(logo_size / orig_w, logo_size / orig_h)
                new_w, new_h = orig_w * ratio, orig_h * ratio
                
                if align == "center":
                    logo_x = (width - new_w) / 2
                elif align == "left":
                    logo_x = 60
                else:
                    logo_x = width - 60 - new_w
                
                c.drawImage(logo_path, logo_x, y - new_h, width=new_w, height=new_h)
                return y - new_h - 40
            except Exception:
                pass
        return y - 40
    
    def _draw_cover_project_title(self, c: canvas.Canvas, width: float, y: float,
                                   cover_data: dict, accent_color, align: str = "center") -> float:
        """Draw project name and subtitle. Returns new y position."""
        project_name = cover_data.get("project_name", "")
        if project_name:
            c.setFont("Helvetica-Bold", 28)
            c.setFillColor(self.COLORS['dark'])
            text_width = c.stringWidth(project_name, "Helvetica-Bold", 28)
            if text_width > width - 100:
                c.setFont("Helvetica-Bold", 22)
            c.drawCentredString(width / 2, y, project_name)
            y -= 40
        
        subtitle = cover_data.get("subtitle", "")
        if subtitle:
            c.setFont("Helvetica", 16)
            c.setFillColor(accent_color)
            c.drawCentredString(width / 2, y, subtitle)
            y -= 35
        
        return y
    
    def _draw_cover_description(self, c: canvas.Canvas, width: float, y: float,
                                cover_data: dict) -> float:
        """Draw cover description. Returns new y position."""
        description = cover_data.get("description", "")
        if description:
            c.setFont("Helvetica", 11)
            c.setFillColor(self.COLORS['gray'])
            lines = self._wrap_text(description, c, width - 120)
            for line in lines[:6]:
                c.drawCentredString(width / 2, y, line)
                y -= 16
            y -= 20
        return y
    
    def _draw_cover_parties(self, c: canvas.Canvas, width: float, y: float,
                            empresa: str, datos_empresa: dict, cliente: dict,
                            cover_data: dict, align: str = "center") -> float:
        """Draw company and client info. Returns new y position."""
        if cover_data.get("show_company", True):
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y, "Preparado por:")
            y -= 18
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(width / 2, y, empresa)
            y -= 16
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            if datos_empresa.get("telefono"):
                c.drawCentredString(width / 2, y, f"Tel: {datos_empresa['telefono']}")
                y -= 14
            if datos_empresa.get("correo"):
                c.drawCentredString(width / 2, y, datos_empresa["correo"])
                y -= 14
            y -= 20
        
        if cover_data.get("show_client", True) and cliente:
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y, "Preparado para:")
            y -= 18
            c.setFont("Helvetica", 12)
            if cliente.get("name"):
                c.drawCentredString(width / 2, y, cliente["name"])
                y -= 16
            if cliente.get("contact"):
                c.setFont("Helvetica", 10)
                c.setFillColor(self.COLORS['gray'])
                c.drawCentredString(width / 2, y, cliente["contact"])
                y -= 14
            y -= 20
        
        return y
    
    def _draw_cover_date_ref(self, c: canvas.Canvas, width: float, y: float,
                             fecha: str, cover_data: dict, align: str = "center") -> float:
        """Draw date and reference. Returns new y position."""
        if cover_data.get("show_date", True):
            c.setFont("Helvetica", 11)
            c.setFillColor(self.COLORS['gray'])
            c.drawCentredString(width / 2, y, f"Fecha: {fecha}")
            y -= 20
        
        reference = cover_data.get("reference", "")
        if reference and cover_data.get("show_reference", True):
            c.setFont("Helvetica", 10)
            c.drawCentredString(width / 2, y, f"Ref: {reference}")
            y -= 20
        
        return y
    
    def _draw_cover_footer_text(self, c: canvas.Canvas, width: float, cover_data: dict):
        """Draw footer text at bottom of cover page."""
        footer_text = cover_data.get("footer_text", "")
        if footer_text:
            c.setFont("Helvetica-Oblique", 9)
            c.setFillColor(self.COLORS['gray'])
            c.drawCentredString(width / 2, 40, footer_text)
    
    def _draw_warranty_section(self, c: canvas.Canvas, width: float, y: float,
                                warranty_data: dict) -> float:
        """Draw warranty section with beautiful styling matching preview.
        
        Features:
        - Styled header with accent bar
        - Numbered circular badges for each subsection
        - Clean typography and spacing
        """
        left_margin = 40
        right_margin = width - 40
        available_width = right_margin - left_margin
        content_width = available_width - 30
        
        # Check space
        if y < 200:
            c.showPage()
            self._page_number += 1
            y = A4[1] - 50
        
        # === MAIN HEADER ===
        header_height = 32
        
        # Accent bar
        c.setFillColor(self.COLORS['primary'])
        c.rect(left_margin, y - header_height, 4, header_height, fill=True, stroke=False)
        
        # Header background
        c.setFillColor(colors.HexColor("#F0F4F8"))
        c.rect(left_margin + 4, y - header_height, available_width - 4, header_height, fill=True, stroke=False)
        
        # Title
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(left_margin + 15, y - 22, "Políticas de Garantía")
        
        y -= header_height + 8
        
        # Separator
        c.setStrokeColor(colors.HexColor("#E0E0E0"))
        c.setLineWidth(1)
        c.line(left_margin, y, right_margin, y)
        y -= 20
        
        # Duration badge if exists
        duration = warranty_data.get("duration", "") or warranty_data.get("warranty_duration", "")
        if duration:
            # Duration pill
            pill_width = 180
            c.setFillColor(colors.HexColor("#E3F2FD"))
            c.roundRect(left_margin, y - 22, pill_width, 22, 11, fill=True, stroke=False)
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(self.COLORS['primary'])
            c.drawString(left_margin + 12, y - 16, f"Duración: {duration}")
            y -= 35
        
        # Helper to draw a numbered subsection
        def draw_numbered_subsection(number: int, title: str, content: str, y_pos: float) -> float:
            if not content or not content.strip():
                return y_pos
            
            # Check page break
            if y_pos < 140:
                c.showPage()
                self._page_number += 1
                y_pos = A4[1] - 50
            
            # Number badge (circle)
            badge_size = 22
            badge_x = left_margin + badge_size/2
            badge_y = y_pos - badge_size/2
            
            c.setFillColor(self.COLORS['primary'])
            c.circle(badge_x, badge_y, badge_size/2, fill=True, stroke=False)
            
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.white)
            c.drawCentredString(badge_x, badge_y - 4, str(number))
            
            # Title next to badge
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(self.COLORS['dark'])
            c.drawString(left_margin + badge_size + 10, y_pos - badge_size/2 - 4, title)
            
            y_pos -= badge_size + 8
            
            # Parse content
            if "<" in content and ">" in content:
                try:
                    parser = ReportLabHTMLParser()
                    parser.feed(content)
                    clean_content = parser.get_result()
                except:
                    clean_content = content.replace('\n', '<br/>')
            else:
                clean_content = content.replace('\n', '<br/>')
            
            # Paragraph style
            style = ParagraphStyle(
                'WarrantyContent',
                parent=getSampleStyleSheet()['Normal'],
                fontName='Helvetica',
                fontSize=10,
                textColor=colors.HexColor("#444444"),
                leading=14,
                leftIndent=badge_size + 15
            )
            
            p = Paragraph(clean_content, style)
            w, h = p.wrap(content_width, A4[1])
            
            available_h = y_pos - 60
            if h > available_h:
                if available_h < 100:
                    c.showPage()
                    self._page_number += 1
                    y_pos = A4[1] - 50
                    available_h = y_pos - 60
                
                try:
                    parts = p.split(content_width, available_h)
                    if parts:
                        parts[0].drawOn(c, left_margin, y_pos - parts[0].wrap(content_width, available_h)[1])
                        c.showPage()
                        self._page_number += 1
                        y_pos = A4[1] - 50
                        for part in parts[1:]:
                            pw, ph = part.wrap(content_width, A4[1] - 100)
                            part.drawOn(c, left_margin, y_pos - ph)
                            y_pos -= (ph + 10)
                        return y_pos - 15
                except:
                    pass
            
            p.drawOn(c, left_margin, y_pos - h)
            return y_pos - h - 20
        
        # Draw 5 subsections
        garantia = warranty_data.get("garantia", "") or warranty_data.get("warranty_garantia", "")
        y = draw_numbered_subsection(1, "Garantía", garantia, y)
        
        covers = warranty_data.get("covers", "") or warranty_data.get("warranty_covers", "")
        y = draw_numbered_subsection(2, "Lo que cubre", covers, y)
        
        excludes = warranty_data.get("excludes", "") or warranty_data.get("warranty_excludes", "")
        y = draw_numbered_subsection(3, "Lo que no cubre", excludes, y)
        
        warning = warranty_data.get("warning", "") or warranty_data.get("warranty_warning", "")
        y = draw_numbered_subsection(4, "Advertencia", warning, y)
        
        verification = warranty_data.get("verification", "") or warranty_data.get("warranty_verification", "")
        y = draw_numbered_subsection(5, "Verificación de la garantía", verification, y)
        
        return y - 10
    
    def _draw_acceptance_section(self, c: canvas.Canvas, width: float, y: float,
                                  acceptance_text: str) -> float:
        """Draw contract acceptance section with beautiful styling."""
        if not acceptance_text or not acceptance_text.strip():
            return y
        
        left_margin = 40
        right_margin = width - 40
        available_width = right_margin - left_margin
        content_width = available_width - 20
        
        # Check space
        if y < 180:
            c.showPage()
            self._page_number += 1
            y = A4[1] - 50
        
        # === HEADER WITH ACCENT BAR ===
        header_height = 28
        
        # Accent bar
        c.setFillColor(colors.HexColor("#34C759"))  # Green for acceptance
        c.rect(left_margin, y - header_height, 4, header_height, fill=True, stroke=False)
        
        # Header background
        c.setFillColor(colors.HexColor("#F0FFF4"))
        c.rect(left_margin + 4, y - header_height, available_width - 4, header_height, fill=True, stroke=False)
        
        # Title
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(left_margin + 15, y - 19, "Aceptación de Contrato")
        
        y -= header_height + 5
        
        # Separator
        c.setStrokeColor(colors.HexColor("#E0E0E0"))
        c.setLineWidth(1)
        c.line(left_margin, y, right_margin, y)
        y -= 20
        
        # Parse HTML content
        if "<" in acceptance_text and ">" in acceptance_text:
            try:
                parser = ReportLabHTMLParser()
                parser.feed(acceptance_text)
                clean_content = parser.get_result()
            except:
                clean_content = acceptance_text.replace('\n', '<br/>')
        else:
            clean_content = acceptance_text.replace('\n', '<br/>')
        
        # Enhanced paragraph style
        style = ParagraphStyle(
            'AcceptanceStyleEnhanced',
            parent=getSampleStyleSheet()['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor("#333333"),
            leading=14,
            leftIndent=10,
            rightIndent=10
        )
        
        p = Paragraph(clean_content, style)
        w, h = p.wrap(content_width, A4[1])
        
        # Check if fits
        if y - h < 100:
            c.showPage()
            self._page_number += 1
            y = A4[1] - 50
        
        p.drawOn(c, left_margin + 10, y - h)
        
        return y - h - 25
    
    def _draw_signature(self, c: canvas.Canvas, width: float, y: float) -> float:
        """Draw signature area."""
        left_margin = 40
        
        # Check space
        if y < 120:
            c.showPage()
            self._page_number += 1
            y = A4[1] - 40
        
        # Two signature lines
        sig_width = (width - 100) / 2
        
        # Client signature
        c.setStrokeColor(self.COLORS['border'])
        c.line(left_margin, y - 40, left_margin + sig_width - 20, y - 40)
        
        c.setFont("Helvetica", 9)
        c.setFillColor(self.COLORS['gray'])
        c.drawString(left_margin, y - 52, "Firma del Cliente")
        c.drawString(left_margin, y - 64, "Fecha: _______________")
        
        # Company signature
        sig_x = width - 40 - sig_width + 20
        c.line(sig_x, y - 40, width - 40, y - 40)
        c.drawString(sig_x, y - 52, "Firma Autorizada")
        c.drawString(sig_x, y - 64, "Fecha: _______________")
        
        return y - 80
    
    def _draw_footer(self, c: canvas.Canvas, width: float, eslogan: str, page_num: int):
        """Draw page footer."""
        c.setFont("Helvetica", 8)
        c.setFillColor(self.COLORS['gray'])
        
        footer_y = 30
        
        # Slogan or thank you message
        message = eslogan if eslogan else "¡Gracias por su preferencia!"
        c.drawCentredString(width / 2, footer_y, message)
        
        # Page indicator
        c.drawRightString(width - 40, footer_y, f"Página {page_num}")
    
    def _draw_observations_section(self, c: canvas.Canvas, width: float, height: float,
                                   y: float, obs_data: dict, eslogan: str) -> float:
        """Draw observations section. Returns new Y position."""
        left_margin = 40
        right_margin = width - 40
        
        # Header (Check space)
        if y < 100:
             self._draw_footer(c, width, eslogan, self._page_number)
             c.showPage()
             self._page_number += 1
             y = height - 50

        # Page header (no emojis)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(self.COLORS['primary'])
        c.drawString(left_margin, y, "DETALLES Y OBSERVACIONES")
        y -= 30
        
        # Separator line
        c.setStrokeColor(self.COLORS['border'])
        c.setLineWidth(1)
        c.line(left_margin, y, right_margin, y)
        y -= 25
        
        # Check for new blocks format first
        blocks = obs_data.get("blocks", [])
        if blocks:
            y = self._draw_blocks(c, width, height, y, blocks, left_margin, right_margin, eslogan)
        else:
            # Legacy format support
            obs_text = obs_data.get("text", "").strip()
            if obs_text:
                y = self._draw_text_section(c, width, height, y, obs_text, 
                                            left_margin, right_margin, eslogan, "Observaciones")
            
            # Legacy gallery items
            gallery = obs_data.get("gallery", [])
            if gallery:
                y = self._draw_legacy_gallery(c, width, height, y, gallery, 
                                               left_margin, right_margin, eslogan)
        
    def _draw_product_matrix(self, c: canvas.Canvas, width: float, height: float, 
                             y: float, products: list) -> float:
        """Draw products in a vertical matrix with strict 4 per page.
        
        Uses user's formula for pages:
        - If n % 4 == 0: n / 4 pages
        - Else: (n // 4) + 1 pages
        """
        left_margin = 40
        right_margin = width - 40
        available_width = right_margin - left_margin
        
        # Filter only products WITH images
        products_with_images = [p for p in products if len(p) > 5 and p[5]]
        
        if not products_with_images:
            return y
        
        # Title for this section
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(self.COLORS['primary'])
        c.drawString(left_margin, y, "Catálogo de Productos")
        y -= 25
        
        # Fixed layout: 4 items per page
        # Each item has ~200 height (800 / 4)
        item_height = 190 
        image_size = 170 
        
        items_on_page = 0
        
        for i, prod in enumerate(products_with_images):
            # Strict pagination: Every 4 items, new page
            if items_on_page >= 4:
                self._draw_footer(c, width, "", self._page_number)
                c.showPage()
                self._page_number += 1
                y = height - 50
                items_on_page = 0
                
                # Re-draw title on new page
                c.setFont("Helvetica-Bold", 14)
                c.setFillColor(self.COLORS['primary'])
                c.drawString(left_margin, y, "Catálogo de Productos (Cont.)")
                y -= 25
            
            # Draw Item Container
            # Image Column
            img_x = left_margin
            img_y = y - item_height + 10
            
            desc = prod[0]
            qty = prod[1]
            price = prod[3]
            img_path = prod[5] if len(prod) > 5 else None
            
            # Background
            c.setFillColor(colors.HexColor("#F9F9F9"))
            c.rect(left_margin, y - item_height, available_width, item_height - 10, fill=True, stroke=False)
            
            # Draw Image
            if img_path and os.path.exists(img_path):
                try:
                    c.drawImage(img_path, img_x + 10, img_y + 10, width=image_size, height=image_size, preserveAspectRatio=True, anchor='c', mask='auto')
                except:
                    c.setFont("Helvetica", 8)
                    c.setFillColor(colors.gray)
                    c.drawString(img_x + 10, img_y + 90, "Error Image")
            else:
                # Placeholder box
                c.setStrokeColor(colors.lightgrey)
                c.rect(img_x + 10, img_y + 10, image_size, image_size)
                c.setFont("Helvetica", 8)
                c.setFillColor(colors.gray)
                c.drawString(img_x + 60, img_y + 90, "Sin Imagen")
                
            # Info Column
            text_x = img_x + image_size + 30
            text_y = y - 30
            
            # Product Name
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(self.COLORS['dark'])
            # Basic wrap
            if len(desc) > 60:
                c.drawString(text_x, text_y, desc[:60] + "...")
            else:
                 c.drawString(text_x, text_y, desc)
            text_y -= 20
            
            # Details (Qty, Price)
            c.setFont("Helvetica", 10)
            c.setFillColor(self.COLORS['gray'])
            c.drawString(text_x, text_y, f"Cantidad: {qty}")
            text_y -= 15
            # c.drawString(text_x, text_y, f"Precio: {price}") # Optional
            
            y -= item_height
            items_on_page += 1
            
        return y
        
    def _draw_blocks(self, c: canvas.Canvas, width: float, height: float,
                     y: float, blocks: list, left_margin: float, 
                     right_margin: float, eslogan: str) -> float:
        """Draw blocks in order."""
        for block in blocks:
            block_type = block.get("type", "")
            
            # Title Page Break Logic
            if block_type == "title":
                level = block.get("level", 0)
                # If level 0 (Title/Nueva Pagina) and we are not at the very top
                # (allowing some margin for header)
                if level == 0 and y < height - 120:
                    self._draw_footer(c, width, eslogan, self._page_number)
                    c.showPage()
                    self._page_number += 1
                    y = height - 50
            
            # Check if we need a new page
            if y < 120:
                self._draw_footer(c, width, eslogan, self._page_number)
                c.showPage()
                self._page_number += 1
                y = height - 50
            
            if block_type == "title":
                y = self._draw_title_block(c, width, y, block, left_margin, right_margin)
            elif block_type == "note":
                y = self._draw_note_block(c, width, height, y, block, 
                                          left_margin, right_margin, eslogan)
            elif block_type == "image":
                y = self._draw_image_block(c, width, height, y, block, 
                                           left_margin, right_margin, eslogan)
            elif block_type == "separator":
                y = self._draw_separator_block(c, width, y, block, left_margin, right_margin)
            elif block_type == "product_matrix":
                y = self._draw_product_matrix_block(c, width, height, y, block, 
                                                     left_margin, right_margin, eslogan)
            
            y -= 10
        
        return y
    
    def _draw_title_block(self, c: canvas.Canvas, width: float, y: float,
                          block: dict, left_margin: float, right_margin: float) -> float:
        """Draw a title block with style support."""
        level = block.get("level", 0)
        title = block.get("title", "")
        style_index = block.get("style_index", 0)
        align_idx = block.get("alignment", 0) # 0=L, 1=C, 2=R
        
        if not title:
            return y
        
        # Default Style
        font_name = "Helvetica-Bold"
        font_size = 14 if level == 0 else 12
        text_color = self.COLORS['dark']
        alignment = "left"
        is_upper = False
        has_underline = (level == 0)
        has_border = False
        
        # Load from JSON Style if index > 0
        if style_index > 0 and style_index <= len(self.title_styles):
            style = self.title_styles[style_index - 1]
            # Font Mapping
            f_map = {"Helvetica-Bold": "Helvetica-Bold", "Times-Bold": "Times-Bold", "Helvetica-Oblique": "Helvetica-Oblique"}
            font_name = f_map.get(style.get("font", ""), "Helvetica-Bold")
            font_size = style.get("size", 14)
            # Color Hex
            import reportlab.lib.colors as rl_colors
            c_hex = style.get("color", "#000000")
            try: text_color = rl_colors.HexColor(c_hex)
            except: pass
            
            alignment = style.get("alignment", "left")
            is_upper = style.get("uppercase", False)
            has_underline = style.get("underline", False)
            has_border = style.get("border_bottom", False)
        
        # Override alignment if locally set to Center/Right (since defaults are usually Left)
        # 0=Left, 1=Center, 2=Right
        if align_idx == 1: alignment = "center"
        elif align_idx == 2: alignment = "right"
        elif align_idx == 0: alignment = "left" # force left

        if is_upper: title = title.upper()
        
        c.setFont(font_name, font_size)
        c.setFillColor(text_color)
        
        text_w = c.stringWidth(title, font_name, font_size)
        
        # Calculate X
        if alignment == "center":
            x = (width - text_w) / 2
        elif alignment == "right":
            x = right_margin - text_w
        else:
            x = left_margin
            
        c.drawString(x, y, title)
        
        # Underline/Border
        if has_underline or has_border:
            y -= 5
            c.setStrokeColor(text_color) # Match text color
            c.setLineWidth(1 if has_border else 2)
            
            line_x_start = x if has_underline else left_margin
            line_x_end = (x + text_w) if has_underline else right_margin
            
            c.line(line_x_start, y, line_x_end, y)
        
        y -= (font_size * 0.5) # Extra spacing
        return y - 18
    
    def _draw_product_matrix_block(self, c: canvas.Canvas, width: float, height: float,
                                   y: float, block: dict, left_margin: float,
                                   right_margin: float, eslogan: str) -> float:
        """Draw a product matrix with STRICT 4 products per page (2x2 grid).
        
        IRREVOCABLE: Exactly 4 products per page, no more, no less.
        Formula: if n % 4 == 0 -> n/4 pages, else (n//4)+1 pages
        """
        products = block.get("products", [])
        if not products:
            return y
        
        # STRICT LAYOUT: 2 columns x 2 rows = 4 products per page
        cols = 2
        rows_per_page = 2
        items_per_page = cols * rows_per_page  # = 4
        
        col_spacing = 20
        row_spacing = 30
        
        avail_width = right_margin - left_margin
        col_width = (avail_width - (cols - 1) * col_spacing) / cols
        
        # Calculate row height for 2 rows per page (split page height evenly)
        # Available height for products: height - 50 (top margin) - 50 (bottom margin)
        avail_height = height - 100
        row_height = (avail_height - row_spacing) / rows_per_page  # Height per row
        
        items_on_page = 0
        current_col = 0
        current_row = 0
        page_start_y = y
        
        for i, prod in enumerate(products):
            # STRICT: Every 4 items = new page
            if items_on_page >= items_per_page:
                self._draw_footer(c, width, eslogan, self._page_number)
                c.showPage()
                self._page_number += 1
                y = height - 50
                page_start_y = y
                items_on_page = 0
                current_col = 0
                current_row = 0
            
            # Calculate position based on grid
            x = left_margin + current_col * (col_width + col_spacing)
            item_y = page_start_y - (current_row * (row_height + row_spacing))
            
            # Draw Item in fixed cell
            self._draw_matrix_item(c, prod, x, item_y, col_width, row_height)
            
            # Move to next cell
            items_on_page += 1
            current_col += 1
            if current_col >= cols:
                current_col = 0
                current_row += 1
        
        # Return Y after the last drawn items
        final_row = (items_on_page - 1) // cols
        y = page_start_y - ((final_row + 1) * (row_height + row_spacing))
        
        return y
    
    def _draw_matrix_item(self, c: canvas.Canvas, prod: dict, x: float, y: float, 
                          cell_width: float, cell_height: float):
        """Draw a single product item in its allocated cell."""
        # Image takes ~70% of cell height, text takes rest
        img_height = cell_height * 0.70
        img_width = cell_width - 10
        
        # Cap image dimensions
        if img_height > 200:
            img_height = 200
        if img_width > 250:
            img_width = 250
        
        # No background or border - clean look
        
        # Image
        img_path = prod.get("image_path", "")
        img_drawn_h = 0
        if img_path and os.path.exists(img_path):
            try:
                # Center image horizontally
                img_x = x + (cell_width - img_width) / 2
                img_y = y - img_height - 5
                
                c.drawImage(img_path, img_x, img_y, width=img_width, height=img_height, 
                           mask='auto', preserveAspectRatio=True)
                img_drawn_h = img_height + 10
            except Exception as e:
                print(f"Error drawing image: {e}")
                img_drawn_h = 20
        else:
            # Placeholder
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.gray)
            c.drawCentredString(x + cell_width/2, y - cell_height/2, "Sin Imagen")
            img_drawn_h = 20
        
        # Text area below image
        text_y = y - img_drawn_h - 15
        text_x = x + 5
        max_text_width = cell_width - 10
        
        # Title (description)
        desc = prod.get("description", "")
        if desc:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(self.COLORS['dark'])
            
            # Truncate if too long
            if c.stringWidth(desc, "Helvetica-Bold", 10) > max_text_width:
                while c.stringWidth(desc + "...", "Helvetica-Bold", 10) > max_text_width and len(desc) > 5:
                    desc = desc[:-1]
                desc = desc + "..."
            
            c.drawString(text_x, text_y, desc)
            text_y -= 14
        
        # Details
        details = prod.get("details", "")
        if details:
            c.setFont("Helvetica", 9)
            c.setFillColor(self.COLORS['gray'])
            
            # Truncate if too long
            if c.stringWidth(details, "Helvetica", 9) > max_text_width:
                while c.stringWidth(details + "...", "Helvetica", 9) > max_text_width and len(details) > 5:
                    details = details[:-1]
                details = details + "..."
            
            c.drawString(text_x, text_y, details)
    
    def _draw_note_block(self, c: canvas.Canvas, width: float, height: float,
                         y: float, block: dict, left_margin: float, 
                         right_margin: float, eslogan: str) -> float:
        """Draw a note block with rich text support and splitting."""
        content = block.get("content", "").strip()
        align_idx = block.get("alignment", 0) # 0=L, 1=C, 2=R, 3=J
        
        if not content:
            return y
        
        # Clean HTML content
        if "<" in content and ">" in content:
            parser = ReportLabHTMLParser()
            parser.feed(content)
            clean_content = parser.get_result()
        else:
            # Basic text, replace newlines
            clean_content = content.replace('\n', '<br/>')
        
        # Map Alignment
        align_map = {0: TA_LEFT, 1: TA_CENTER, 2: TA_RIGHT, 3: TA_JUSTIFY}
        para_align = align_map.get(align_idx, TA_LEFT)

        # Create Paragraph
        style = ParagraphStyle(
            'NoteStyle',
            parent=getSampleStyleSheet()['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=self.COLORS['dark'],
            leading=14,  # Line spacing
            alignment=para_align
        )
        
        p = Paragraph(clean_content, style)
        
        # Calculate size
        avail_width = right_margin - left_margin
        w, h = p.wrap(avail_width, height) 
        
        # Check available space on current page
        bottom_margin = 50
        available_height = y - bottom_margin
        
        # If it fits, just draw
        if h <= available_height:
             p.drawOn(c, left_margin, y - h)
             return y - h - 15
        
        # If it doesn't fit, we need to SPLIT
        # ReportLab Paragraph splitting:
        # split(availWidth, availHeight) returns list of [P1, P2...]
        
        # Loop until done
        remaining_p = p
        while remaining_p:
            # Try to split into what fits this page
            split_parts = remaining_p.split(avail_width, available_height)
            
            if not split_parts:
                # If nothing fits (e.g. one huge line or no space), force new page
                self._draw_footer(c, width, eslogan, self._page_number)
                c.showPage()
                self._page_number += 1
                y = height - 50
                available_height = y - bottom_margin
                # Don't change remaining_p, retry loop
                # Check for infinite loop if item larger than full page?
                # split() should return at least something if we give full page.
                # If we just force-drew:
                # But we need to update available_height for split() to work.
                continue
                
            # Draw first part
            p_to_draw = split_parts[0]
            w_part, h_part = p_to_draw.wrap(avail_width, available_height)
            p_to_draw.drawOn(c, left_margin, y - h_part)
            
            # Check if there is more
            if len(split_parts) > 1:
                # Update remaining content
                # split_parts[1] is NOT a Paragraph, it's a Flowable? 
                # Actually, split() returns Flowables. We might need to wrap them in new Paragraph?
                # No, they are usually paragraphs.
                # Ideally we iterate drawing and page breaking.
                
                # Simple approach: If > 1 part, it means we filled the page.
                # So we draw P1, New Page, and then continue with P2+
                # But split return mechanism is [fit, rest] usually? 
                # ReportLab split returns a list of flowables that fit. What about the rest? 
                # Wait, Flowable.split() returns ONE list of pieces "that fit". 
                # It does NOT return the "rest". The "rest" is not returned. 
                # Actually Paragraph.split works by returning (P_fitted, P_rest) sometimes? 
                # No, standard is split(w, h) -> [f1, f2...] that fit in h.
                
                # Correct approach for Paragraphs in layout manual:
                # use `frame.add(p, canvas)`. But we are manual.
                
                # Let's use a simpler heuristic or just loop drawing lines if we parsed nicely? 
                # Paragraphs are hard to split manually if we don't control the flowable.
                
                # Use `breakLines`?
                # blines = p.breakLines(avail_width)
                # This gives us lines. We can draw line by line?
                # That's safer for manual pagination!
                
                self._draw_paginated_paragraph(c, p, width, height, y, left_margin, right_margin, eslogan)
                
                # After function returns, where are we? We need new Y.
                # Implementing helper method is cleaner.
                return self._last_y_position # Store in instance? Or return from helper.
                
            else:
                # Only 1 part returned? It means it ALL fit? 
                # But we checked `h > available_height`.
                # If h > avail and split returns 1 part, it means that part fit? Confusing.
                # If it didn't fit, split returns [].
                pass
            
            break # If we are here, logic is messy. Use Helper.
            
        return y - 15 # Placeholder
    
    def _draw_image_block(self, c: canvas.Canvas, width: float, height: float,
                          y: float, block: dict, left_margin: float,
                          right_margin: float, eslogan: str) -> float:
        """Draw an image block."""
        image_path = block.get("path", "")
        caption = block.get("caption", "")
        align_idx = block.get("alignment", 1) # Default Center
        
        if not os.path.exists(image_path):
            return y
        
        # Check page space
        if y < 280:
            self._draw_footer(c, width, eslogan, self._page_number)
            c.showPage()
            self._page_number += 1
            y = height - 50
        
        try:
            img = ImageReader(image_path)
            orig_w, orig_h = img.getSize()
            
            # Scale image
            max_img_width = 380
            max_img_height = 280
            ratio = min(max_img_width / orig_w, max_img_height / orig_h)
            
            img_w = orig_w * ratio
            img_h = orig_h * ratio
            
            # Center image
            if align_idx == 0: # Left
                img_x = left_margin
            elif align_idx == 1: # Center
                img_x = (width - img_w) / 2
            else: # Right
                img_x = right_margin - img_w
            
            # Draw border around image
            c.setStrokeColor(self.COLORS['border'])
            c.setLineWidth(1)
            c.rect(img_x - 2, y - img_h - 2, img_w + 4, img_h + 4)
            
            c.drawImage(image_path, img_x, y - img_h, width=img_w, height=img_h)
            y -= img_h + 10
            
            # Caption
            if caption:
                c.setFont("Helvetica-Oblique", 9)
                c.setFillColor(self.COLORS['gray'])
                
                # Align Caption same as Image? Or always center? 
                # Usually caption is centered relative to image or page.
                # Let's align relative to PAGE if Center, or relative to Image if L/R?
                # Simplest: Center page or align with image center.
                cap_x = img_x + img_w / 2
                c.drawCentredString(cap_x, y, caption)
                y -= 15
            
        except Exception as e:
            print(f"Error drawing image: {e}")
        
        return y

    def _draw_paginated_paragraph(self, c, p, width, height, y, left_margin, right_margin, eslogan):
        """Helper to draw a paragraph line by line across pages."""
        avail_width = right_margin - left_margin
        
        # Breakdown into lines
        lines = p.breakLines(avail_width)
        
        # Create a style for drawing lines
        # breakLines returns "Line" objects or text? 
        # It returns FrameBreakLines... actually it's internal.
        
        # Better strategy: 
        # Calculate header/footer space
        bottom_limit = 50
        
        # Manually iterate lines from breakLines?
        # The return from breakLines is complex. 
        
        # Alternative: Use simple `split` recursively?
        # If we define a frame for the page, we can use `frame.add`. 
        # This is strictly manual canvas. 
        
        # Let's try the simple recursive split logic again but correctly.
        # If we set a height, split returns what fits. We draw that. 
        # Then we create a NEW paragraph with the REST of the text.
        # But Paragraph doesn't expose "rest of text".
        
        # Fallback: Text Splitter by content length? Crude.
        
        # Let's stick to the "If note is too big, just force new page" for now, AS LONG AS it fits on ONE page.
        # But User said: "automticamente se habilitara otra y seguira".
        # So we MUST split.
        
        # Hack: Use `Frame` on the canvas just for this paragraph?
        from reportlab.platypus import Frame, KeepInFrame
        
        # We have the text.
        # While p is not done:
        # Create a Frame for remaining space. 
        # frame.add(p, c). 
        # If it didn't finish, we need to know what's left.
        # `frame.add` returns... 0 if success, 1 if split? 
        # Actually frame.add(flowable, canvas, trySplit=1) returns output.
        
        # Let's rely on `c.showPage()` logic inside the loop? Pattern:
        
        current_y = y
        
        # We will use blines to iterate.
        # p.blines is populated after wrap? No.
        
        # Using simple line iteration from the styled text.
        # We can simulate it. 
        
        # RE-IMPL: simple line drawing? No rich text.
        # We need rich text.
        
        # BEST WAY manual: 
        # 1. wrap()
        # 2. if fits, draw.
        # 3. if not, split at (avail_height). 
        #    split() gives [part1, part2] ??
        #    If split() returns [p1], it means p1 fits. Where is p2?
        #    ReportLab Paragraph split() is strictly for "what fits". 
        #    It relies on creating a new paragraph for the rest.
        
        # Let's use `p_split = p.split(avail_width, current_y - bottom_limit)`
        # If it returns pieces, we draw them.
        # Then we presumably have "lost" the rest? Yes. That's the problem.
        
        # OK, we will use the `Frame` approach implicitly?
        # No, let's implement a rudimentary "Fit or New Page" policy first.
        # If it doesn't fit on current page at all (height > page_height - margins), THEN we split.
        # If it fits on A page but not THIS page, just new page.
        
        w, h = p.wrap(avail_width, height)
        if h > (current_y - bottom_limit):
             # Doesn't fit here.
             # Does it fit on a fresh page?
             max_h = height - 100
             if h < max_h:
                 # Fits on new page.
                 self._draw_footer(c, width, eslogan, self._page_number)
                 c.showPage()
                 self._page_number += 1
                 current_y = height - 50
                 p.drawOn(c, left_margin, current_y - h)
                 self._last_y_position = current_y - h - 15
                 return current_y - h - 15
             else:
                 # HUGE paragraph. Must split.
                 # Since manual split is hard, we warn or just clip?
                 # Or we draw what we can...
                 pass
        
        # Default draw
        p.drawOn(c, left_margin, current_y - h)
        self._last_y_position = current_y - h - 15
        return current_y - h - 15
    
    def _draw_separator_block(self, c: canvas.Canvas, width: float, y: float,
                               block: dict, left_margin: float, right_margin: float) -> float:
        """Draw a separator line."""
        style = block.get("style", 0)
        
        c.setStrokeColor(self.COLORS['gray'])
        
        if style == 0:  # Simple line
            c.setLineWidth(1)
            c.line(left_margin, y - 10, right_margin, y - 10)
        elif style == 1:  # Double line
            c.setLineWidth(1)
            c.line(left_margin, y - 8, right_margin, y - 8)
            c.line(left_margin, y - 12, right_margin, y - 12)
        # style 2 is just space
        
        return y - 25
    
    def _draw_bank_details(self, c: canvas.Canvas, width: float, y: float, bank_details: str) -> float:
        """Draw bank details section."""
        left_margin = 40
        right_margin = width - 40
        
        # Check space
        if y < 100:
            c.showPage()
            self._page_number += 1
            y = A4[1] - 40
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(left_margin, y - 10, "Datos Bancarios")
        
        c.setStrokeColor(self.COLORS['border'])
        c.line(left_margin, y - 18, right_margin, y - 18)
        
        c.setFont("Helvetica", 9)
        c.setFillColor(self.COLORS['gray'])
        
        details_y = y - 35
        lines = bank_details.split('\n')
        for line in lines:
            c.drawString(left_margin + 10, details_y, line)
            details_y -= 12
        
        return details_y - 15

    def _draw_signatures_section(self, c: canvas.Canvas, width: float, y: float, 
                                 empresa: str, datos_empresa: dict, cliente: dict,
                                 prepared_by: str = "", signature_image: str = None) -> float:
        """Draw signatures with authorized signature image support."""
        
        # Check space
        if y < 150:
            c.showPage()
            self._page_number += 1
            y = A4[1] - 100
        else:
            y -= 40
            if y < 150:
                 c.showPage()
                 self._page_number += 1
                 y = A4[1] - 100
        
        left_margin = 40
        right_margin = width - 40
        sig_width = 200
        
        # Client Signature (Left)
        c.setStrokeColor(self.COLORS['gray'])
        c.setLineWidth(1)
        c.line(left_margin, y, left_margin + sig_width, y)
        
        c.setFont("Helvetica", 9)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(left_margin, y - 15, "CLIENTE / REPRESENTANTE:")
        if cliente and cliente.get("name"):
            c.setFont("Helvetica-Bold", 9)
            c.drawString(left_margin, y - 28, cliente["name"])
        else:
             c.drawString(left_margin, y - 28, "")

        # Company Signature (Right)
        # If we have a signature image provided (Personal or Company resolved outside)
        if signature_image and os.path.exists(signature_image):
            try:
                sig_img = ImageReader(signature_image)
                sw, sh = sig_img.getSize()
                ratio = min(sig_width / sw, 60 / sh) # Max height 60
                new_w = sw * ratio
                new_h = sh * ratio
                
                # Center image over line context
                sig_x = right_margin - sig_width + (sig_width - new_w)/2
                c.drawImage(signature_image, sig_x, y + 2, width=new_w, height=new_h, mask='auto', preserveAspectRatio=True)
            except Exception as e:
                print(f"Error drawing signature: {e}")
                
        c.setStrokeColor(self.COLORS['gray'])
        c.setLineWidth(1)
        c.line(right_margin - sig_width, y, right_margin, y)
        
        c.setFont("Helvetica", 9)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(right_margin - sig_width, y - 15, "PREPARADO POR:")
        
        # Draw "Prepared By" name or Company Name
        sig_name = prepared_by if prepared_by else empresa
        c.setFont("Helvetica-Bold", 9)
        c.drawString(right_margin - sig_width, y - 28, sig_name)
        
        return y - 50
    
    def _draw_text_section(self, c: canvas.Canvas, width: float, height: float,
                           y: float, text: str, left_margin: float, 
                           right_margin: float, eslogan: str, title: str) -> float:
        """Draw a text section (legacy support)."""
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(left_margin, y, f"{title}:")
        y -= 20
        
        c.setFont("Helvetica", 10)
        c.setFillColor(self.COLORS['gray'])
        
        max_width = right_margin - left_margin
        lines = self._wrap_text(text, c, max_width)
        
        for line in lines:
            if y < 80:
                self._draw_footer(c, width, eslogan, self._page_number)
                c.showPage()
                self._page_number += 1
                y = height - 50
            
            c.drawString(left_margin, y, line)
            y -= 14
        
        return y - 20
    
    def _draw_legacy_gallery(self, c: canvas.Canvas, width: float, height: float,
                              y: float, gallery: list, left_margin: float,
                              right_margin: float, eslogan: str) -> float:
        """Draw legacy gallery items."""
        if y < 200:
            self._draw_footer(c, width, eslogan, self._page_number)
            c.showPage()
            self._page_number += 1
            y = height - 50
        
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(self.COLORS['dark'])
        c.drawString(left_margin, y, "Contenido Adicional:")
        y -= 25
        
        for item in gallery:
            if item.get("type") == "image":
                y = self._draw_gallery_image(c, width, height, y, item, 
                                              left_margin, right_margin, eslogan)
            elif item.get("type") == "text":
                y = self._draw_gallery_note(c, width, height, y, item, 
                                             left_margin, right_margin, eslogan)
            y -= 15
        
        return y
    
    def _wrap_text(self, text: str, c: canvas.Canvas, max_width: float) -> list:
        """Wrap text to fit within max_width."""
        lines = []
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                lines.append("")
                continue
                
            words = paragraph.split()
            current_line = ""
            
            for word in words:
                test_line = f"{current_line} {word}".strip()
                text_width = c.stringWidth(test_line, "Helvetica", 10)
                
                if text_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
        
        return lines
    
    def _draw_gallery_image(self, c: canvas.Canvas, width: float, height: float,
                            y: float, item: dict, left_margin: float, 
                            right_margin: float, eslogan: str) -> float:
        """Draw a gallery image in the PDF."""
        image_path = item.get("path", "")
        caption = item.get("caption", "")
        
        if not os.path.exists(image_path):
            return y
        
        # Check if we need a new page
        if y < 250:
            self._draw_footer(c, width, eslogan, self._page_number)
            c.showPage()
            self._page_number += 1
            y = height - 50
        
        try:
            img = ImageReader(image_path)
            orig_w, orig_h = img.getSize()
            
            # Scale image
            max_img_width = 350
            max_img_height = 250
            ratio = min(max_img_width / orig_w, max_img_height / orig_h)
            
            img_w = orig_w * ratio
            img_h = orig_h * ratio
            
            # Center image
            img_x = (width - img_w) / 2
            
            c.drawImage(image_path, img_x, y - img_h, width=img_w, height=img_h)
            y -= img_h + 10
            
            # Caption
            if caption:
                c.setFont("Helvetica-Oblique", 9)
                c.setFillColor(self.COLORS['gray'])
                c.drawCentredString(width / 2, y, caption)
                y -= 15
            
        except Exception as e:
            print(f"Error drawing image: {e}")
        
        return y
    
    def _draw_gallery_note(self, c: canvas.Canvas, width: float, height: float,
                           y: float, item: dict, left_margin: float,
                           right_margin: float, eslogan: str) -> float:
        """Draw a text note in the PDF."""
        content = item.get("content", "")
        
        if not content.strip():
            return y
        
        # Check space
        if y < 120:
            self._draw_footer(c, width, eslogan, self._page_number)
            c.showPage()
            self._page_number += 1
            y = height - 50
        
        # Note box background
        box_height = 60
        c.setFillColor(colors.HexColor('#F5F5F7'))
        c.roundRect(left_margin, y - box_height, right_margin - left_margin, 
                    box_height, 6, fill=True, stroke=False)
        
        # Note header
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(self.COLORS['primary'])
        c.drawString(left_margin + 10, y - 15, "📝 Nota:")
        
        # Note text
        c.setFont("Helvetica", 9)
        c.setFillColor(self.COLORS['dark'])
        
        # Word wrap note content
        max_width = right_margin - left_margin - 20
        lines = self._wrap_text(content[:300], c, max_width)[:3]  # Max 3 lines
        
        note_y = y - 30
        for line in lines:
            c.drawString(left_margin + 10, note_y, line)
            note_y -= 12
        
        return y - box_height - 10

    def _draw_cover_futuristic(self, c: canvas.Canvas, width: float, height: float,
                               empresa: str, datos_empresa: dict, cliente: dict,
                               fecha: str, cover_data: dict):
        """Futuristic layout - Tech style."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        
        # Tech lines
        c.setStrokeColor(accent_color)
        c.setLineWidth(1)
        
        # Top circuit
        p = c.beginPath()
        p.moveTo(40, height - 80)
        p.lineTo(40, height - 40)
        p.lineTo(80, height - 40)
        p.lineTo(90, height - 30)
        p.lineTo(140, height - 30)
        c.drawPath(p, stroke=1, fill=0)
        c.setFillColor(accent_color)
        c.circle(38, height - 80, 2, fill=1)
        c.circle(144, height - 30, 2, fill=1)
        
        # Bottom circuit
        p2 = c.beginPath()
        p2.moveTo(width - 40, 80)
        p2.lineTo(width - 40, 40)
        p2.lineTo(width - 80, 40)
        p2.lineTo(width - 90, 30)
        p2.lineTo(width - 140, 30)
        c.drawPath(p2, stroke=1, fill=0)
        c.circle(width - 38, 80, 2, fill=1)
        c.circle(width - 144, 30, 2, fill=1)
        
        y = height / 2 + 50
        
        # Project Name - Monospaced look
        project_name = cover_data.get("project_name", "")
        if project_name:
            c.setFont("Courier-Bold", 32)
            c.setFillColor(self.COLORS['dark'])
            c.drawCentredString(width / 2, y, project_name.upper())
            y -= 40
            
        c.setFont("Courier", 8)
        c.setFillColor(accent_color)
        c.drawCentredString(width / 2, y, "01011010 • SYSTEM • 11001011")
        y -= 60
        
        self._draw_cover_footer_text(c, width, cover_data)

    def _draw_cover_abstract_waves(self, c: canvas.Canvas, width: float, height: float,
                                   empresa: str, datos_empresa: dict, cliente: dict,
                                   fecha: str, cover_data: dict):
        """Abstract waves layout."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        
        # Simulating waves with Bezier not easy in raw reportlab without path ops, 
        # using simple overlapping circles/shapes for flow
        
        c.setFillColor(accent_color)
        c.setFillAlpha(0.1)
        c.circle(0, height, 200, fill=1, stroke=0)
        c.circle(width, 0, 150, fill=1, stroke=0)
        
        c.setFillAlpha(0.2)
        c.circle(50, height + 50, 180, fill=1, stroke=0)
        
        c.setFillAlpha(1.0)
        
        # Centered content
        self._draw_cover_classic(c, width, height, empresa, datos_empresa, cliente, fecha, cover_data)

    def _draw_cover_geometric_mosaic(self, c: canvas.Canvas, width: float, height: float,
                                     empresa: str, datos_empresa: dict, cliente: dict,
                                     fecha: str, cover_data: dict):
        """Geometric mosaic layout."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        
        # Random polygons
        c.setFillColor(accent_color)
        c.setFillAlpha(0.15)
        c.circle(60, height - 60, 40, fill=1, stroke=0)
        c.rect(width - 100, 50, 60, 60, fill=1, stroke=0)
        c.setFillAlpha(1.0)
        
        # Center diamond
        p = c.beginPath()
        cx, cy = width / 2, height / 2
        p.moveTo(cx, cy + 50)
        p.lineTo(cx + 50, cy)
        p.lineTo(cx, cy - 50)
        p.lineTo(cx - 50, cy)
        p.close()
        c.setStrokeColor(accent_color)
        c.drawPath(p, stroke=1, fill=0)
        
        # Use classic centered text logic
        self._draw_cover_classic(c, width, height, empresa, datos_empresa, cliente, fecha, cover_data)

    def _draw_cover_modern_editorial(self, c: canvas.Canvas, width: float, height: float,
                                     empresa: str, datos_empresa: dict, cliente: dict,
                                     fecha: str, cover_data: dict):
        """Editorial layout - Asymmetric."""
        accent_color = colors.HexColor(cover_data.get("accent_color", "#0A84FF"))
        
        # Left bar
        c.setFillColor(accent_color)
        c.rect(0, 0, 20, height, fill=1, stroke=0)
        
        left_margin = 60
        y = height - 100
        
        # Project Name
        project_name = cover_data.get("project_name", "")
        if project_name:
            # Big first letter
            if len(project_name) > 0:
                c.setFont("Helvetica-Bold", 80)
                c.setFillColor(colors.HexColor("#DDDDDD")) # Faint gray
                c.drawRightString(width - 40, height - 120, project_name[0])
            
            c.setFont("Helvetica-Bold", 40)
            c.setFillColor(self.COLORS['dark'])
            # Wrap text manually if needed
            c.drawString(left_margin, y, project_name)
            y -= 50
            
            c.setStrokeColor(self.COLORS['dark'])
            c.setLineWidth(4)
            c.line(left_margin, y, left_margin + 60, y)
            y -= 40
         
        self._draw_cover_footer_text(c, width, cover_data)


# Compatibility function for legacy code
def generar_pdf(file_path: str, empresa: str, datos_empresa: dict,
                productos: List[list], total: float, moneda: str, fecha: str,
                validez_dias: int = 30, observaciones: str = "",
                observaciones_data: dict = None, cliente: dict = None,
                numero_cotizacion: str = "", document_type: str = "Cotizacion",
                shipping: float = 0, cover_page_data: dict = None,
                warranty_data: dict = None, estimated_days: int = 7,
                shipping_type: str = "Sin envío", installation_terms: str = "",
                payment_method: str = "", bank_details: str = "",
                 payment_type: str = "", apply_iva: bool = True,
                 include_details: bool = True, terms_data: dict = None,
                 prepared_by: str = "", signature_image: str = None,
                 mostrar_firma: bool = False, mostrar_terminos: bool = True):
    """Legacy compatibility function with extended parameters."""
    
    # Check if warranty_data is actually empty (all fields blank)
    has_warranty = False
    if warranty_data:
        has_warranty = bool(
            warranty_data.get("duration") or
            warranty_data.get("garantia") or
            warranty_data.get("covers") or
            warranty_data.get("excludes") or
            warranty_data.get("warning") or
            warranty_data.get("verification") or
            warranty_data.get("terms") or
            warranty_data.get("warranty_terms")
        )
    
    generator = PDFGenerator()
    generator.generate(
        file_path=file_path,
        empresa=empresa,
        datos_empresa=datos_empresa,
        productos=productos,
        total=total,
        moneda=moneda,
        fecha=fecha,
        mostrar_terminos=mostrar_terminos,
        mostrar_firma=mostrar_firma,  # Now properly passed from caller
        validez_dias=validez_dias,
        cliente=cliente,
        observaciones_data=observaciones_data,
        numero_cotizacion=numero_cotizacion,
        document_type=document_type,
        shipping=shipping,
        cover_page_data=cover_page_data,
        warranty_data=warranty_data if has_warranty else None,  # Only pass if has content
        estimated_days=estimated_days,
        shipping_type=shipping_type,
        installation_terms=installation_terms,
        payment_method=payment_method,
        bank_details=bank_details,
        payment_type=payment_type,
        apply_iva=apply_iva,
        include_details=include_details,
        terms_data=terms_data,
        prepared_by=prepared_by,
        signature_image=signature_image
    )

