
import json
import glob
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os
import math

try:
    from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QImage
    from PyQt6.QtCore import Qt, QRectF
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

class CoverPageRenderer:
    """
    Handles the drawing of professional cover pages using a JSON-driven engine.
    Supports "brutal" customization via external definition files.
    """
    
    COLORS = {
        'primary': colors.HexColor('#0A84FF'),
        'dark': colors.HexColor('#1C1C1E'),
        'gray': colors.HexColor('#8E8E93'),
        'light_gray': colors.HexColor('#F5F5F7'),
        'white': colors.white
    }
    
    # Named color mapping for ReportLab
    NAMED_COLORS = {
        'white': colors.white,
        'black': colors.black,
        'red': colors.red,
        'green': colors.green,
        'blue': colors.blue,
        'yellow': colors.yellow,
        'orange': colors.orange,
        'gray': colors.gray,
        'grey': colors.grey,
        'lightgray': colors.lightgrey,
        'lightgrey': colors.lightgrey,
        'darkgray': colors.darkgrey,
        'darkgrey': colors.darkgrey,
    }

    def __init__(self):
        self.covers_dir = os.path.join(os.getcwd(), "media", "covers")
        self._ensure_covers_dir()
        self.styles = self._load_styles()

    def _ensure_covers_dir(self):
        if not os.path.exists(self.covers_dir):
            os.makedirs(self.covers_dir)
            # Create default classic style if empty
            self._create_default_style()

    def _create_default_style(self):
        default = {
            "name": "Clásico JSON",
            "description": "Estilo clásico generado por JSON",
            "elements": [
                {"type": "rect", "rect": [0.05, 0.05, 0.9, 0.9], "stroke": "#0A84FF", "stroke_width": 2},
                {"type": "text", "text": "{project_name}", "x": 0.5, "y": 0.6, "align": "center", "size": 30, "font": "Helvetica-Bold"}
            ]
        }
        with open(os.path.join(self.covers_dir, "classic.json"), 'w') as f:
            json.dump(default, f, indent=2)

    def _load_styles(self):
        styles = {}
        for path in glob.glob(os.path.join(self.covers_dir, "*.json")):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    styles[data.get("name")] = data
            except Exception as e:
                print(f"Error loading style {path}: {e}")
        return styles

    def reload_styles(self):
        """Reload all cover styles from disk."""
        self.styles = self._load_styles()
        return self.get_available_styles()

    def get_available_styles(self):
        return [(name, data.get("description", "")) for name, data in self.styles.items()]

    def draw_cover(self, c: canvas.Canvas, width: float, height: float,
                   empresa: str, datos_empresa: dict, cliente: dict,
                   fecha: str, cover_data: dict):
        """Draw cover based on JSON definition."""
        style_name = cover_data.get("layout_style")
        style = self.styles.get(style_name)
        
        if not style:
            # Fallback to first available or empty
            if self.styles:
                style = list(self.styles.values())[0]
            else:
                return

        context = {
            "width": width,
            "height": height,
            "project_name": cover_data.get("project_name", ""),
            "subtitle": cover_data.get("subtitle", ""),
            "company_name": empresa,
            "client_name": cliente.get("name", ""),
            "date": fecha,
            "accent_color": cover_data.get("accent_color", "#0A84FF"),
            "logo_path": datos_empresa.get("logo", "")
        }

        self._render_elements(c, style.get("elements", []), context)


    def draw_cover_qt(self, painter, width: float, height: float,
                      empresa: str, datos_empresa: dict, cliente: dict,
                      fecha: str, cover_data: dict):
        """Draw cover on QPainter based on JSON definition."""
        if not QT_AVAILABLE:
            return

        style_name = cover_data.get("layout_style")
        style = self.styles.get(style_name)
        
        if not style:
            if self.styles:
                style = list(self.styles.values())[0]
            else:
                return

        context = {
            "width": width,
            "height": height,
            "project_name": cover_data.get("project_name", ""),
            "subtitle": cover_data.get("subtitle", ""),
            "company_name": empresa,
            "client_name": cliente.get("name", ""),
            "date": fecha,
            "accent_color": cover_data.get("accent_color", "#0A84FF"),
            "logo_path": datos_empresa.get("logo", "")
        }

        self._render_elements_qt(painter, style.get("elements", []), context)

    def _render_elements_qt(self, p, elements, ctx):
        w, h = ctx["width"], ctx["height"]
        
        for el in elements:
            try:
                etype = el.get("type")
                if "if" in el:
                    if not ctx.get(el["if"]): continue

                # Resolve colors
                fill_color = self._resolve_color_qt(el.get("color"), ctx)
                stroke_color = self._resolve_color_qt(el.get("stroke"), ctx)
                stroke_width = el.get("stroke_width", 0)
                opacity = el.get("opacity", 1.0)
                
                p.save()
                
                if fill_color:
                    fill_color.setAlphaF(opacity)
                    p.setBrush(QBrush(fill_color))
                else:
                    p.setBrush(Qt.BrushStyle.NoBrush)
                
                if stroke_color and stroke_width > 0:
                    stroke_color.setAlphaF(opacity)
                    pen = QPen(stroke_color)
                    pen.setWidthF(stroke_width)
                    p.setPen(pen)
                else:
                    p.setPen(Qt.PenStyle.NoPen)

                # Draw
                if etype == "rect":
                    rx, ry, rw, rh = el.get("rect", [0,0,0,0])
                    radius = el.get("radius", 0)
                    rect = QRectF(rx*w, ry*h, rw*w, rh*h)
                    if radius > 0:
                        p.drawRoundedRect(rect, radius*w, radius*w)
                    else:
                        p.drawRect(rect)
                
                elif etype == "rounded_rect":
                    rx, ry, rw, rh = el.get("rect", [0,0,0,0])
                    radius = el.get("radius", 0.02)
                    rect = QRectF(rx*w, ry*h, rw*w, rh*h)
                    p.drawRoundedRect(rect, radius*w, radius*w)
                
                elif etype == "circle":
                    cx, cy = el.get("x", 0)*w, el.get("y", 0)*h
                    r = el.get("r", 0)
                    if r < 1.0: r *= w
                    p.drawEllipse(QRectF(cx-r, cy-r, r*2, r*2))
                    
                elif etype == "line":
                    x1, y1 = el.get("x1", 0)*w, el.get("y1", 0)*h
                    x2, y2 = el.get("x2", 0)*w, el.get("y2", 0)*h
                    p.drawLine(int(x1), int(y1), int(x2), int(y2))
                    
                elif etype == "text" or etype == "wrapped_text":
                    text = el.get("text", "").format(**ctx)
                    font_name = el.get("font", "Arial")
                    # Map standard PDF fonts to system fonts if needed
                    if "Helvetica" in font_name: font_name = "Arial"
                    elif "Times" in font_name: font_name = "Times New Roman"
                    elif "Courier" in font_name: font_name = "Courier New"
                    
                    # Heuristic size adjustment (PDF points vs Screen pixels)
                    # Assuming preview is small, we mostly rely on relative position, but font size is tricky.
                    # QPainter on widget uses pixels. PDF uses points. 1 pt = 1/72 inch.
                    # We typically just use the number as is.
                    size = el.get("size", 12)
                    # Validate font size - must be > 0
                    if not isinstance(size, (int, float)) or size <= 0:
                        size = 12
                    
                    font = QFont(font_name, max(1, int(size)))
                    if "Bold" in el.get("font", ""): font.setBold(True)
                    p.setFont(font)
                    
                    # For text, if no color specified, use default dark
                    if not fill_color:
                        p.setPen(QPen(QColor("#1C1C1E")))
                    else:
                        p.setPen(QPen(fill_color))
                    
                    align = el.get("align", "left")
                    x, y = el.get("x", 0)*w, el.get("y", 0)*h
                    
                    flags = Qt.AlignmentFlag.AlignLeft
                    if align == "center": flags = Qt.AlignmentFlag.AlignCenter
                    elif align == "right": flags = Qt.AlignmentFlag.AlignRight
                    
                    # Qt draws text in rect. We need a rect.
                    # Construct a large rect around the point based on alignment
                    border_w = 1000 # Arbitrary large width
                    if align == "center":
                        rect = QRectF(x - border_w/2, y - size, border_w, size*1.5)
                    elif align == "right":
                        rect = QRectF(x - border_w, y - size, border_w, size*1.5)
                    else:
                        rect = QRectF(x, y - size, border_w, size*1.5)
                        
                    if etype == "wrapped_text":
                         # Basic wrap support
                         flags |= Qt.TextFlag.TextWordWrap
                         max_w = el.get("width", 0.8) * w
                         rect.setWidth(max_w)
                         if align == "center": rect.setX(x - max_w/2)
                    
                    p.drawText(rect, flags, text)

                elif etype == "image":
                    path_key = el.get("path_var", "logo_path")
                    path = ctx.get(path_key)
                    if path and os.path.exists(path):
                        target_w = el.get("w", 0.2) * w
                        x, y = el.get("x", 0)*w, el.get("y", 0)*h
                        
                        img = QImage(path)
                        if not img.isNull():
                            aspect = img.height() / img.width()
                            draw_h = target_w * aspect
                            
                            # Draw centered image
                            # p.drawImage(QRectF(x - target_w/2, y - draw_h, target_w, draw_h), img)
                            # PDF coordinates are bottom-up usually, but our JSON x,y are 0-1, so 0 is top or bottom?
                            # In PDF 0,0 is bottom-left. In Qt 0,0 is top-left.
                            # The renderer code in draw_cover (PDF) uses ry*h. If ry=0, it draws at bottom.
                            # So JSON coordinates are Y-up (Cartesian). 
                            # But Qt is Y-down.
                            # I need to invert Y!
                            pass # Handled below
                
                elif etype == "path":
                    path = QPainterPath()
                    points = el.get("points", [])
                    if points:
                        start = points[0]
                        path.moveTo(start[0]*w, self._inv_y(start[1], h))
                        for pt in points[1:]:
                            if len(pt) == 2:
                                path.lineTo(pt[0]*w, self._inv_y(pt[1], h))
                            elif len(pt) == 6:
                                path.cubicTo(
                                    pt[0]*w, self._inv_y(pt[1], h),
                                    pt[2]*w, self._inv_y(pt[3], h),
                                    pt[4]*w, self._inv_y(pt[5], h)
                                )
                        if el.get("close", False):
                            path.closeSubpath()
                        p.drawPath(path)

                p.restore()
            except Exception as e:
                print(f"Error render qt: {e}")

    def _inv_y(self, y_factor, h):
        """Convert Cartesian Y-factor (0-1) to Qt Y (pixels)"""
        # PDF: 0=Bottom, 1=Top. 
        # Qt: 0=Top, h=Bottom.
        return h - (y_factor * h)

    def _resolve_color_qt(self, color_str, ctx):
        """Resolve color string to QColor, supporting hex, named colors, and variables."""
        if not color_str: return None
        if color_str.startswith("{") and color_str.endswith("}"):
            var = color_str[1:-1]
            color_str = ctx.get(var, "#000000")
        
        # QColor can handle both hex and named colors directly
        color = QColor(color_str)
        if color.isValid():
            return color
        # Fallback to black if invalid
        return QColor("#000000")

    # Legacy method signature adapter if needed
    def _render_elements(self, c, elements, ctx):
        w, h = ctx["width"], ctx["height"]
        
        for el in elements:
            try:
                etype = el.get("type")
                
                # Check condition
                if "if" in el:
                    var = el["if"]
                    if not ctx.get(var):
                        continue

                # Common style props
                color = self._resolve_color(el.get("color"), ctx)
                stroke = self._resolve_color(el.get("stroke"), ctx)
                width = el.get("stroke_width", 0)
                alpha = el.get("opacity", 1.0)
                
                c.saveState()
                if color: 
                    c.setFillColor(color)
                    c.setFillAlpha(alpha)
                else:
                    c.setFillAlpha(0)
                
                if stroke:
                    c.setStrokeColor(stroke)
                    c.setLineWidth(width)
                else:
                    c.setStrokeAlpha(0)

                if etype == "rect":
                    rx, ry, rw, rh = el.get("rect", [0,0,0,0])
                    radius = el.get("radius", 0)
                    if radius > 0:
                        c.roundRect(rx*w, ry*h, rw*w, rh*h, radius*w, fill=bool(color), stroke=bool(stroke))
                    else:
                        c.rect(rx*w, ry*h, rw*w, rh*h, fill=bool(color), stroke=bool(stroke))
                
                elif etype == "rounded_rect":
                    rx, ry, rw, rh = el.get("rect", [0,0,0,0])
                    radius = el.get("radius", 0.02)
                    c.roundRect(rx*w, ry*h, rw*w, rh*h, radius*w, fill=bool(color), stroke=bool(stroke))
                
                elif etype == "circle":
                    cx, cy = el.get("x", 0)*w, el.get("y", 0)*h
                    r = el.get("r", 0)
                    # Radius can be relative to width if < 1.0 (heuristic)
                    if r < 1.0: r *= w 
                    c.circle(cx, cy, r, fill=bool(color), stroke=bool(stroke))
                    
                elif etype == "line":
                    x1, y1 = el.get("x1", 0)*w, el.get("y1", 0)*h
                    x2, y2 = el.get("x2", 0)*w, el.get("y2", 0)*h
                    c.line(x1, y1, x2, y2)
                    
                elif etype == "text":
                    text = el.get("text", "")
                    # Interpolate
                    text = text.format(**ctx)
                    
                    font = el.get("font", "Helvetica")
                    size = el.get("size", 12)
                    align = el.get("align", "left")
                    x, y = el.get("x", 0)*w, el.get("y", 0)*h
                    
                    c.setFont(font, size)
                    if not color: c.setFillColor(self.COLORS['dark'])
                        
                    if align == "center":
                        c.drawCentredString(x, y, text)
                    elif align == "right":
                        c.drawRightString(x, y, text)
                    else:
                        c.drawString(x, y, text)
                        
                elif etype == "wrapped_text":
                    text = el.get("text", "").format(**ctx)
                    font = el.get("font", "Helvetica")
                    size = el.get("size", 12)
                    max_w = el.get("width", 0.8) * w
                    x, y = el.get("x", 0)*w, el.get("y", 0)*h
                    line_h = el.get("line_height", size * 1.2)
                    align = el.get("align", "left")
                    
                    c.setFont(font, size)
                    if not color: c.setFillColor(self.COLORS['dark'])
                    
                    lines = self._wrap_text(text, c, max_w)
                    for line in lines:
                        if align == "center":
                            c.drawCentredString(x, y, line)
                        elif align == "right":
                            c.drawRightString(x, y, line)
                        else:
                            c.drawString(x, y, line)
                        y -= line_h

                elif etype == "image":
                    path_key = el.get("path_var", "logo_path")
                    path = ctx.get(path_key)
                    if path and os.path.exists(path):
                        target_w = el.get("w", 0.2) * w
                        target_h = el.get("h", 0.1) * h # Optional max height
                        x, y = el.get("x", 0)*w, el.get("y", 0)*h
                        
                        try:
                            img = ImageReader(path)
                            iw, ih = img.getSize()
                            aspect = ih / float(iw)
                            
                            # Scale to fit width, maintain aspect
                            draw_w = target_w
                            draw_h = draw_w * aspect
                            
                            c.drawImage(path, x - draw_w/2, y, width=draw_w, height=draw_h, mask='auto')
                        except:
                            pass
                
                elif etype == "path":
                    p = c.beginPath()
                    points = el.get("points", [])
                    if points:
                        start = points[0]
                        p.moveTo(start[0]*w, start[1]*h)
                        for pt in points[1:]:
                            if len(pt) == 2: # Line
                                p.lineTo(pt[0]*w, pt[1]*h)
                            elif len(pt) == 6: # Cubic Bezier
                                p.curveTo(pt[0]*w, pt[1]*h, pt[2]*w, pt[3]*h, pt[4]*w, pt[5]*h)
                        
                        if el.get("close", False):
                            p.close()
                        c.drawPath(p, fill=bool(color), stroke=bool(stroke))

                c.restoreState()
            except Exception as e:
                print(f"Error rendering element {el}: {e}")

    def _resolve_color(self, color_str, ctx):
        """Resolve color string to ReportLab color, supporting hex and named colors."""
        if not color_str:
            return None
        if color_str.startswith("{") and color_str.endswith("}"):
            var = color_str[1:-1]
            color_str = ctx.get(var, "#000000")
        
        # Check if it's a named color first
        color_lower = color_str.lower() if color_str else ""
        if color_lower in self.NAMED_COLORS:
            return self.NAMED_COLORS[color_lower]
        
        # Try to parse as hex color
        try:
            return colors.HexColor(color_str)
        except ValueError:
            # Fallback to black if parsing fails
            return colors.black

    def _wrap_text(self, text, c, max_width):
        width = c.stringWidth(text, c._fontname, c._fontsize)
        if width <= max_width:
            return [text]
        
        words = text.split()
        lines = []
        current = []
        for word in words:
            current.append(word)
            w = c.stringWidth(' '.join(current), c._fontname, c._fontsize)
            if w > max_width:
                current.pop()
                lines.append(' '.join(current))
                current = [word]
        if current:
            lines.append(' '.join(current))
        return lines
