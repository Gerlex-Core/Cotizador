
import json
import glob
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os
import math

try:
    from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QImage, QPixmap
    from PyQt6.QtCore import Qt, QRectF
    # Import canvas items (lazy import inside methods or if available)
    try:
        from src.views.components.canvas_editor import (
            CanvasTextItem, CanvasRectItem, CanvasPathItem, CanvasImageItem
        )
    except ImportError:
        pass # Might fail if running purely headless without UI code available
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

    # Default styles for dynamic blocks
    BLOCK_STYLES = {
        'logo': {'type': 'image', 'w': 0.35, 'h': 0.15, 'align': 'center', 'margin': 0.06},
        'company': {'type': 'text', 'font': 'Helvetica-Bold', 'size': 14, 'color': '#0A84FF', 'align': 'center', 'margin': 0.03, 'key': 'company_name', 'upper': True},
        'title': {'type': 'wrapped_text', 'font': 'Helvetica-Bold', 'size': 36, 'color': '#1C1C1E', 'align': 'center', 'width': 0.8, 'margin': 0.04, 'key': 'project_name'},
        'subtitle': {'type': 'wrapped_text', 'font': 'Helvetica', 'size': 18, 'color': '#8E8E93', 'align': 'center', 'width': 0.7, 'margin': 0.04, 'key': 'subtitle'},
        'client': {'type': 'text', 'font': 'Helvetica', 'size': 14, 'color': '#30D158', 'align': 'center', 'margin': 0.03, 'prefix': 'Preparado para: ', 'key': 'client_name'},
        'date': {'type': 'text', 'font': 'Helvetica', 'size': 12, 'color': '#FF9F0A', 'align': 'center', 'margin': 0.06, 'key': 'date'},
        'description': {'type': 'wrapped_text', 'font': 'Helvetica', 'size': 12, 'color': '#636366', 'align': 'center', 'width': 0.7, 'margin': 0.04, 'key': 'description'},
        'reference': {'type': 'text', 'font': 'Courier', 'size': 10, 'color': '#8E8E93', 'align': 'center', 'margin': 0.02, 'key': 'reference'},
        'footer': {'type': 'text', 'font': 'Helvetica', 'size': 10, 'color': '#8E8E93', 'align': 'center', 'y_fixed': 0.05, 'key': 'footer_text'}
    }

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.covers_dir = os.path.join(base_dir, "media", "covers")
        print(f"[COVER] Init renderer. Base: {base_dir}")
        print(f"[COVER] Covers dir: {self.covers_dir}")
        self._ensure_covers_dir()
        self.styles = self._load_styles()
        print(f"[COVER] Loaded styles: {list(self.styles.keys())}")

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
                # Removed static text elements as they are now handled dynamically
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
        """Draw cover based on JSON definition + Dynamic Flow."""
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
            "description": cover_data.get("description", ""),
            "reference": cover_data.get("reference", ""),
            "footer_text": cover_data.get("footer_text", ""),
            "company_name": empresa,
            "client_name": cliente.get("name", ""),
            "date": fecha,
            "accent_color": cover_data.get("accent_color", "#0A84FF"),
            "logo_path": datos_empresa.get("logo", ""),
            "element_order": cover_data.get("element_order", []),
            "overrides": cover_data.get("canvas_overrides", {})
        }

        # 1. Render static elements (backgrounds, lines)
        self._render_elements(c, style.get("elements", []), context, skip_text=True)
        
        # 2. Render dynamic content flow
        if context.get("element_order"):
            self._render_dynamic_flow(c, context)

    def draw_cover_qt(self, painter, width: float, height: float,
                      empresa: str, datos_empresa: dict, cliente: dict,
                      fecha: str, cover_data: dict):
        """Draw cover on QPainter based on JSON definition + Dynamic Flow."""
        if not QT_AVAILABLE:
            return

        style_name = cover_data.get("layout_style")
        print(f"[COVER] Drawing QT. Style requested: {style_name}")
        style = self.styles.get(style_name)
        
        if not style:
            print(f"[COVER] Style '{style_name}' not found. Available: {list(self.styles.keys())}")
            if self.styles:
                style = list(self.styles.values())[0]
                print(f"[COVER] Using fallback: {style.get('name')}")
            else:
                print(f"[COVER] ERROR: No styles available!")
                return

        context = {
            "width": width,
            "height": height,
            "project_name": cover_data.get("project_name", ""),
            "subtitle": cover_data.get("subtitle", ""),
            "description": cover_data.get("description", ""),
            "reference": cover_data.get("reference", ""),
            "footer_text": cover_data.get("footer_text", ""),
            "company_name": empresa,
            "client_name": cliente.get("name", ""),
            "date": fecha,
            "accent_color": cover_data.get("accent_color", "#0A84FF"),
            "logo_path": datos_empresa.get("logo", ""),
            "element_order": cover_data.get("element_order", [])
        }

        # 1. Render static elements
        self._render_elements_qt(painter, style.get("elements", []), context, skip_text=True)
        
        # 2. Render dynamic content flow
        if context.get("element_order"):
            self._render_dynamic_flow_qt(painter, context)

    def populate_scene(self, scene, width: float, height: float,
                       empresa: str, datos_empresa: dict, cliente: dict,
                       fecha: str, cover_data: dict):
        """Populate a QGraphicsScene with interactive items based on style + data."""
        if not QT_AVAILABLE: 
            print("[COVER-QT] QT NOT AVAILABLE")
            return

        # Check import of items
        try:
            from src.views.components.canvas_editor import (
                CanvasTextItem, CanvasRectItem, CanvasPathItem, CanvasImageItem
            )
        except ImportError as e:
            print(f"[COVER-QT] CRITICAL: Failed to import Canvas Items: {e}")
            return

        # CRITICAL FIX: Save positions of ALL items before clearing
        saved_positions = {}
        for item in scene.items():
            if hasattr(item, "item_id") and item.item_id:
                saved_positions[item.item_id] = {
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                    "rotation": item.rotation(),
                    "scale": item.scale(),
                    "opacity": item.opacity(),
                }
                print(f"[COVER-QT] Saving position for {item.item_id}: {item.pos().x()}, {item.pos().y()}")
        
        print(f"[COVER-QT] Saved {len(saved_positions)} item positions before clear")

        scene.clear()
        
        # Draw background (paper items are managed by scene background, but we need style elements)
        style_name = cover_data.get("layout_style")
        style = self.styles.get(style_name)
        
        print(f"[COVER-QT] Populating Scene. Style: {style_name}, Found: {bool(style)}")
        
        if not style and self.styles: 
            style = list(self.styles.values())[0]
            print(f"[COVER-QT] Fallback style: {style.get('name')}")
            
        if not style: return

        # CRITICAL FIX: Merge saved positions into overrides
        overrides = cover_data.get("canvas_overrides", {}).copy()
        # Saved positions take precedence (they're the most recent)
        overrides.update(saved_positions)

        context = {
            "width": width,
            "height": height,
            "project_name": cover_data.get("project_name", ""),
            "subtitle": cover_data.get("subtitle", ""),
            "description": cover_data.get("description", ""),
            "reference": cover_data.get("reference", ""),
            "footer_text": cover_data.get("footer_text", ""),
            "company_name": empresa,
            "client_name": cliente.get("name", ""),
            "date": fecha,
            "accent_color": cover_data.get("accent_color", "#0A84FF"),
           "logo_path": datos_empresa.get("logo", ""),
            "element_order": cover_data.get("element_order", []),
            "overrides": overrides  # Use merged overrides
        }

        # 1. Static Elements -> Items
        self._create_items_from_elements(scene, style.get("elements", []), context)

        # 2. Dynamic Elements -> Items
        if context.get("element_order"):
            self._create_items_dynamic_flow(scene, context)
            
        # 3. User Added Elements (Custom shapes)
        if "user_elements" in cover_data:
            self._create_items_user_custom(scene, cover_data["user_elements"], context)

    def _create_items_user_custom(self, scene, elements, ctx):
        """Recreate user-added custom items."""
        from src.views.components.canvas_editor import (
            CanvasTextItem, CanvasRectItem, CanvasPathItem, CanvasImageItem
        )
        from PyQt6.QtCore import QRectF, Qt
        from PyQt6.QtGui import QBrush, QColor, QPen, QPainterPath, QFont
        
        print(f"[COVER-QT] Restoring {len(elements)} user items...")
        
        for el in elements:
            try:
                item = None
                itype = el.get("type")
                
                if itype == "rect":
                    rect = QRectF(0, 0, el["w"], el["h"]) 
                    item = CanvasRectItem(rect)
                    if "color" in el:
                        item.setBrush(QBrush(QColor(el["color"])))
                    if "stroke_color" in el:
                        pen = QPen(QColor(el["stroke_color"]))
                        pen.setWidthF(el.get("stroke_width", 1.0))
                        item.setPen(pen)
                    else:
                        item.setPen(QPen(Qt.GlobalColor.black))

                elif itype == "rounded_rect":
                    path = QPainterPath()
                    path.addRoundedRect(0, 0, el["w"], el["h"], 20, 20)
                    item = CanvasPathItem(path)
                    if "color" in el:
                        item.setBrush(QBrush(QColor(el["color"])))
                    if "stroke_color" in el:
                        pen = QPen(QColor(el["stroke_color"]))
                        pen.setWidthF(el.get("stroke_width", 1.0))
                        item.setPen(pen)
                    else:
                        item.setPen(QPen(Qt.GlobalColor.black))

                elif itype == "circle":
                    path = QPainterPath()
                    path.addEllipse(0, 0, el["w"], el["h"])
                    item = CanvasPathItem(path)
                    if "color" in el:
                        item.setBrush(QBrush(QColor(el["color"])))
                    if "stroke_color" in el:
                        pen = QPen(QColor(el["stroke_color"]))
                        pen.setWidthF(el.get("stroke_width", 1.0))
                        item.setPen(pen)
                    else:
                        item.setPen(QPen(Qt.GlobalColor.black))
                        
                elif itype == "line":
                    path = QPainterPath()
                    # Line stored as x,y (pos) + w (length). Or just 0 to w.
                    # Assuming we saved 'w' as length.
                    path.moveTo(0, 0)
                    path.lineTo(el.get("w", 100), 0)
                    item = CanvasPathItem(path)
                    item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                    if "stroke_color" in el:
                        pen = QPen(QColor(el["stroke_color"]))
                        pen.setWidthF(el.get("stroke_width", 2.0))
                        item.setPen(pen)
                    else:
                        item.setPen(QPen(Qt.GlobalColor.black, 2))

                elif itype in ["triangle", "pentagon", "hexagon", "octagon"]:
                    sides_map = {"triangle": 3, "pentagon": 5, "hexagon": 6, "octagon": 8}
                    sides = sides_map.get(itype, 3)
                    # Use center of bounding box relative to 0,0?
                    # Or reuse the helper. I need to duplicate the helper logic here or import it.
                    # Simpler to duplicate the math for standalone renderer stability.
                    import math
                    path = QPainterPath()
                    radius = 60 # Default radius used in editor
                    cx, cy = 0, 0 # Local coords
                    angle = -math.pi / 2 
                    step = 2 * math.pi / sides
                    path.moveTo(cx + radius * math.cos(angle), cy + radius * math.sin(angle))
                    for i in range(1, sides):
                        angle += step
                        path.lineTo(cx + radius * math.cos(angle), cy + radius * math.sin(angle))
                    path.closeSubpath()
                    
                    item = CanvasPathItem(path)
                    if "color" in el:
                        item.setBrush(QBrush(QColor(el["color"])))
                    if "stroke_color" in el:
                        pen = QPen(QColor(el["stroke_color"]))
                        pen.setWidthF(el.get("stroke_width", 1.0))
                        item.setPen(pen)
                    else:
                        item.setPen(QPen(Qt.GlobalColor.black))

                elif itype == "star":
                    import math
                    path = QPainterPath()
                    points = 5
                    outer = 60
                    inner = 25
                    cx, cy = 0, 0
                    angle = -math.pi / 2
                    step = math.pi / points
                    path.moveTo(cx + outer * math.cos(angle), cy + outer * math.sin(angle))
                    for i in range(1, points * 2):
                        r = inner if i % 2 != 0 else outer
                        angle += step
                        path.lineTo(cx + r * math.cos(angle), cy + r * math.sin(angle))
                    path.closeSubpath()
                    
                    item = CanvasPathItem(path)
                    if "color" in el:
                        item.setBrush(QBrush(QColor(el["color"])))
                    if "stroke_color" in el:
                        pen = QPen(QColor(el["stroke_color"]))
                        pen.setWidthF(el.get("stroke_width", 1.0))
                        item.setPen(pen)
                    else:
                        item.setPen(QPen(Qt.GlobalColor.black))
                        
                elif itype == "text":
                    item = CanvasTextItem(el.get("text", ""))
                    if "color" in el:
                        item.setDefaultTextColor(QColor(el["color"]))
                    if "size" in el:
                        size = int(el["size"])
                        # Validate size is positive
                        if size <= 0:
                            size = 12  # Default fallback
                        font = QFont(el.get("font", "Helvetica"), size)
                        if el.get("bold"):
                            font.setBold(True)
                        if el.get("italic"):
                            font.setItalic(True)
                        item.setFont(font)
                        
                if item:
                    item.item_id = el["id"]
                    item.setPos(el["x"], el["y"])
                    item.setRotation(el["rotation"])
                    item.setScale(el["scale"])
                    if "opacity" in el:
                        item.setOpacity(el["opacity"])
                    if el.get("locked"):
                        item.set_locked(True)
                    
                    scene.addItem(item)
                    print(f"[COVER-QT] Restored item: {el['id']} at ({el['x']}, {el['y']})")
                    
            except Exception as e:
                print(f"[COVER-QT] Error restoring user item: {e}")

    def _apply_override(self, item, item_id, overrides):
        """Apply saved position/rotation if exists."""
        if item_id in overrides:
            data = overrides[item_id]
            if "x" in data and "y" in data:
                item.setPos(data["x"], data["y"])
            if "rotation" in data:
                item.setRotation(data["rotation"])
            if "scale" in data:
                item.setScale(data["scale"])
        item.item_id = item_id # Tag relevant for saving later

    def _create_items_from_elements(self, scene, elements, ctx):
        w, h = ctx["width"], ctx["height"]
        print(f"[COVER-QT] Creating {len(elements)} static elements...")
        
        for idx, el in enumerate(elements):
            try:
                etype = el.get("type")
                print(f"[COVER-QT] Processing {etype}")
                # Generate a semi-stable ID for static elements
                item_id = f"static_{idx}_{etype}"
                
                # Check condition
                if "if" in el:
                    if not ctx.get(el["if"]): continue

                # Resolve props
                color = self._resolve_color_qt(el.get("color"), ctx)
                stroke_color = self._resolve_color_qt(el.get("stroke"), ctx)
                stroke_width = el.get("stroke_width", 0)
                opacity = el.get("opacity", 1.0)
                
                item = None
                
                if etype in ["rect", "rounded_rect"]:
                    rx, ry, rw, rh = el.get("rect", [0,0,0,0])
                    rect = QRectF(rx*w, ry*h, rw*w, rh*h)
                    item = CanvasRectItem(rect)
                    if color: item.setBrush(QBrush(color))
                    else: item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                    
                elif etype == "circle":
                    cx, cy = el.get("x", 0)*w, el.get("y", 0)*h
                    r = el.get("r", 0)
                    if r < 1.0: r *= w
                    rect = QRectF(cx-r, cy-r, r*2, r*2)
                    # QGraphicsEllipseItem/RectItem can simplify
                    item = CanvasRectItem(rect) 
                    # Actually CanvasRectItem inherits QGraphicsRectItem. 
                    # Ideally we want Ellipse but let's stick to Rect for simplicity or add Ellipse class if needed
                    # For now, let's treat it as a rect wrapper, or assume the user won't notice circles becoming rects 
                    # Wait, "Brutal" means high quality. I should add CanvasEllipseItem. 
                    # As a fallback I'll use PathItem for circle.
                    path = QPainterPath()
                    path.addEllipse(rect)
                    item = CanvasPathItem(path)
                    if color: item.setBrush(QBrush(color))

                elif etype == "text" or etype == "wrapped_text":
                    text = el.get("text", "").format(**ctx)
                    # Skip dynamic placeholders
                    if any(x in text for x in ["{project_name}", "{subtitle}", "{company_name}", "{client_name}", "date"]):
                        continue
                        
                    item = CanvasTextItem(text)
                    font_name = el.get("font", "Arial")
                    size = el.get("size", 12)
                    font = QFont(font_name, int(size))
                    if "Bold" in font_name: font.setBold(True)
                    item.setFont(font)
                    if color: item.setDefaultTextColor(color)
                    
                    x, y = el.get("x", 0)*w, el.get("y", 0)*h
                    item.setPos(x, y)
                    
                elif etype == "image":
                    path_key = el.get("path_var", "logo_path")
                    path = ctx.get(path_key)
                    if path and os.path.exists(path):
                        pix = QPixmap(path)
                        if not pix.isNull():
                            item = CanvasImageItem(pix)
                            target_w = el.get("w", 0.2) * w
                            scale = target_w / pix.width()
                            item.setScale(scale)
                            x, y = el.get("x", 0)*w, el.get("y", 0)*h
                            # Center logic for image item?
                            # Raw item pos is top-left.
                            item.setPos(x - (pix.width()*scale)/2, y)

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
                        item = CanvasPathItem(path)
                        if color: item.setBrush(QBrush(color))

                # Common properties
                if item:
                    item.setOpacity(opacity)
                    if stroke_color and stroke_width > 0:
                        pen = QPen(stroke_color)
                        pen.setWidthF(stroke_width)
                        # All these items (Rect, Path) have setPen. Text doesn't traverse the same.
                        if hasattr(item, "setPen"):
                            item.setPen(pen)
                    
                    self._apply_override(item, item_id, ctx["overrides"])
                    scene.addItem(item)
                    print(f"[COVER-QT] Created item {idx} ({etype})")
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"[COVER-QT] Error creating item {idx} ({el}): {e}")

    def _create_items_dynamic_flow(self, scene, ctx):
        w, h = ctx["width"], ctx["height"]
        current_y = 0.2 * h 
        order = ctx.get("element_order", [])
        
        for block_type in order:
            style = self.BLOCK_STYLES.get(block_type)
            if not style: continue
            
            # Visibility checks...
            if block_type == "logo" and not ctx.get("logo_path"): continue
            if block_type in ["company", "client", "date", "reference"] and not ctx.get("show_" + block_type, True): continue

            # Footer special case
            if block_type == "footer":
                self._create_footer_item(scene, ctx, style)
                continue

            content_key = style.get("key")
            content = ctx.get(content_key, "") if content_key else ""
            if not content and style.get("type") != "image": continue

            # ID for overrides: "dynamic_title", "dynamic_logo", etc.
            item_id = f"dynamic_{block_type}"

            # Create Item
            item = None
            b_type = style.get("type")
            margin = style.get("margin", 0.05) * h
            
            if b_type == "image":
                path = ctx.get("logo_path")
                if path and os.path.exists(path):
                    pix = QPixmap(path)
                    if not pix.isNull():
                        item = CanvasImageItem(pix)
                        target_w = style.get("w", 0.2) * w
                        scale = target_w / pix.width()
                        img_h = pix.height() * scale
                        
                        # Default Pos
                        x = 0.5 * w - (pix.width()*scale)/2
                        item.setPos(x, current_y)
                        item.setScale(scale)
                        
                        current_y += img_h

            elif b_type in ["text", "wrapped_text"]:
                full_text = content
                if style.get("upper"): full_text = full_text.upper()
                if style.get("prefix"): full_text = style.get("prefix") + full_text
                
                item = CanvasTextItem(full_text)
                
                font_name = style.get("font", "Arial")
                size = style.get("size", 12)
                color = self._resolve_color_qt(style.get("color"), ctx)
                
                font = QFont(font_name, int(size))
                if "Bold" in font_name: font.setBold(True)
                item.setFont(font)
                if color: item.setDefaultTextColor(color)
                
                # Align logic (rough approximation for initial placement)
                align = style.get("align", "center")
                
                # CanvasTextItem auto-sizes. We place it roughly.
                # Center alignment needs bounding rect calc.
                rect = item.boundingRect()
                text_w = rect.width()
                
                if align == "center":
                    x = (w - text_w) / 2
                else:
                    x = 0.1 * w
                
                if b_type == "wrapped_text":
                    item.setTextWidth(style.get("width", 0.8) * w)
                    # changing text width changes height
                    rect = item.boundingRect()
                
                item.setPos(x, current_y)
                current_y += rect.height()

            if item:
                self._apply_override(item, item_id, ctx["overrides"])
                scene.addItem(item)
            
            current_y += margin

    def _create_footer_item(self, scene, ctx, style):
        w, h = ctx["width"], ctx["height"]
        content = ctx.get("footer_text", "")
        if not content: return
        
        y_fixed = style.get("y_fixed", 0.05) * h
        y = h - y_fixed
        
        item_id = "dynamic_footer"
        
        item = CanvasTextItem(content)
        font = QFont("Arial", int(style.get("size", 10)))
        item.setFont(font)
        item.setDefaultTextColor(QColor(style.get("color", "#8E8E93")))
        
        # Center
        rect = item.boundingRect()
        x = (w - rect.width()) / 2
        item.setPos(x, y - 20)
        
        self._apply_override(item, item_id, ctx["overrides"])
        scene.addItem(item)
        
        if ctx.get("show_border", True):
             border_id = "dynamic_footer_border"
             path = QPainterPath()
             path.moveTo(w*0.3, y - 30)
             path.lineTo(w*0.7, y - 30)
             
             line = CanvasPathItem(path)
             pen = QPen(QColor(style.get("color", "#8E8E93")))
             pen.setWidth(1)
             line.setPen(pen)
             
             self._apply_override(line, border_id, ctx["overrides"])
             scene.addItem(line)

    def _render_elements_qt(self, p, elements, ctx, skip_text=False):
        w, h = ctx["width"], ctx["height"]
        
        for el in elements:
            try:
                etype = el.get("type")
                
                # Skip text elements if using dynamic flow to avoid duplication
                if skip_text and etype in ["text", "wrapped_text"]:
                    text = el.get("text", "")
                    # Skip if it's one of our main dynamic fields
                    if any(x in text for x in ["{project_name}", "{subtitle}", "{company_name}", "{client_name}", "date"]):
                        continue

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
                    if "Helvetica" in font_name: font_name = "Arial"
                    elif "Times" in font_name: font_name = "Times New Roman"
                    elif "Courier" in font_name: font_name = "Courier New"
                    
                    size = el.get("size", 12)
                    if not isinstance(size, (int, float)) or size <= 0: size = 12
                    
                    font = QFont(font_name, max(1, int(size)))
                    if "Bold" in el.get("font", ""): font.setBold(True)
                    p.setFont(font)
                    
                    if not fill_color:
                        p.setPen(QPen(QColor("#1C1C1E")))
                    else:
                        p.setPen(QPen(fill_color))
                    
                    align = el.get("align", "left")
                    x, y = el.get("x", 0)*w, el.get("y", 0)*h
                    
                    flags = Qt.AlignmentFlag.AlignLeft
                    if align == "center": flags = Qt.AlignmentFlag.AlignCenter
                    elif align == "right": flags = Qt.AlignmentFlag.AlignRight
                    
                    border_w = 1000 
                    if align == "center":
                        rect = QRectF(x - border_w/2, y - size, border_w, size*1.5)
                    elif align == "right":
                        rect = QRectF(x - border_w, y - size, border_w, size*1.5)
                    else:
                        rect = QRectF(x, y - size, border_w, size*1.5)
                        
                    if etype == "wrapped_text":
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
                            p.drawImage(QRectF(x - target_w/2, y, target_w, draw_h), img)
                
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

    def _render_dynamic_flow_qt(self, p, ctx):
        """Render dynamic elements in a vertical flow (Qt)."""
        w, h = ctx["width"], ctx["height"]
        
        # Start calculating Y position. 
        # For simplicity, start from 20% down.
        current_y = 0.2 * h 
        
        # Check elements to know total height and center vertically?
        # For now, simple flow from top-ish.
        
        order = ctx.get("element_order", [])
        
        for block_type in order:
            style = self.BLOCK_STYLES.get(block_type)
            if not style: continue
            
            # Skip if hidden by checking context flags if needed
            # (UI already filters visibility, but let's be safe)
            if block_type == "logo" and not ctx.get("logo_path"): continue
            if block_type in ["company", "client", "date", "reference"] and not ctx.get("show_" + block_type, True): continue # Assuming logic from dialog
            
            # Special case: Footer is fixed at bottom usually
            if block_type == "footer":
                self._render_footer_qt(p, ctx, style)
                continue
                
            # Content
            content_key = style.get("key")
            content = ctx.get(content_key, "") if content_key else ""
            
            print(f"[COVER-QT] Block: {block_type}, Key: {content_key}, Content: '{content}'")
            
            # Render based on type
            b_type = style.get("type")
            margin = style.get("margin", 0.05) * h
            
            # Advance Y
            # current_y += margin/2
            
            p.save()
            
            if b_type == "image":
                path = ctx.get("logo_path")
                if path and os.path.exists(path):
                    target_w = style.get("w", 0.2) * w
                    
                    img = QImage(path)
                    if not img.isNull():
                        aspect = img.height() / img.width()
                        draw_h = target_w * aspect
                        
                        x = 0.5 * w # Always centered for now
                        p.drawImage(QRectF(x - target_w/2, current_y, target_w, draw_h), img)
                        current_y += draw_h
            
            elif b_type in ["text", "wrapped_text"]:
                if not content:
                    p.restore()
                    continue
                    
                if style.get("upper"): content = content.upper()
                if style.get("prefix"): content = style.get("prefix") + content
                
                font_name = style.get("font", "Arial")
                if "Helvetica" in font_name: font_name = "Arial"
                size = style.get("size", 12)
                color = QColor(style.get("color", "#000000"))
                
                font = QFont(font_name, size)
                if "Bold" in font_name: font.setBold(True)
                p.setFont(font)
                p.setPen(QPen(color))
                
                align = style.get("align", "center")
                x = 0.5 * w if align == "center" else 0.1 * w
                
                flags = Qt.AlignmentFlag.AlignCenter
                if align == "left": flags = Qt.AlignmentFlag.AlignLeft
                
                rect_w = style.get("width", 0.9) * w
                
                # Calculate height needed
                rect = QRectF(x - rect_w/2, current_y, rect_w, 1000)
                
                if b_type == "wrapped_text":
                    flags |= Qt.TextFlag.TextWordWrap
                    boundingRect = p.boundingRect(rect, flags, content)
                    draw_h = boundingRect.height()
                else:
                    draw_h = size * 1.5
                    
                print(f"[COVER-QT] Drawing text: '{content}' at {rect}")
                p.drawText(rect, flags, content)
                current_y += draw_h
            
            p.restore()
            current_y += margin

    def _render_footer_qt(self, p, ctx, style):
        w, h = ctx["width"], ctx["height"]
        content = ctx.get("footer_text", "")
        if not content: return
        
        y_fixed = style.get("y_fixed", 0.05) * h
        # Qt Y is top-down, so h - y_fixed
        y = h - y_fixed
        
        p.save()
        p.setFont(QFont("Arial", style.get("size", 10)))
        p.setPen(QPen(QColor(style.get("color", "#8E8E93"))))
        
        rect = QRectF(0, y - 20, w, 40)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, content)
        
        # Border
        if ctx.get("show_border", True):
             p.setPen(QPen(QColor(style.get("color")), 1))
             p.drawLine(int(w*0.3), int(y - 30), int(w*0.7), int(y - 30))
        
        p.restore()

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
    def _render_elements(self, c, elements, ctx, skip_text=False):
        w, h = ctx["width"], ctx["height"]
        
        for el in elements:
            try:
                etype = el.get("type")
                
                # Dynamic flow skip logic
                if skip_text and etype in ["text", "wrapped_text"]:
                    text = el.get("text", "")
                    if any(x in text for x in ["{project_name}", "{subtitle}", "{company_name}", "{client_name}", "date"]):
                        continue
                
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
                    if r < 1.0: r *= w 
                    c.circle(cx, cy, r, fill=bool(color), stroke=bool(stroke))
                    
                elif etype == "line":
                    x1, y1 = el.get("x1", 0)*w, el.get("y1", 0)*h
                    x2, y2 = el.get("x2", 0)*w, el.get("y2", 0)*h
                    c.line(x1, y1, x2, y2)
                    
                elif etype == "text":
                    text = el.get("text", "")
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
                            draw_h = target_w * aspect
                            
                            c.drawImage(path, x - target_w/2, y, width=target_w, height=draw_h, mask='auto')
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

    def _render_dynamic_flow(self, c, ctx):
        """Render dynamic elements in a vertical flow (PDF)."""
        w, h = ctx["width"], ctx["height"]
        
        # Start calculating Y position. 
        # For PDF, Y=0 is bottom. Start from top (e.g. 80%) and go down.
        current_y = 0.8 * h 
        
        order = ctx.get("element_order", [])
        
        for block_type in order:
            style = self.BLOCK_STYLES.get(block_type)
            if not style: continue
            
            if block_type == "logo" and not ctx.get("logo_path"): continue
            if block_type in ["company", "client", "date", "reference"] and not ctx.get("show_" + block_type, True): continue # Assuming logic from dialog
            
            # Special case: Footer is fixed at bottom
            if block_type == "footer":
                self._render_footer(c, ctx, style)
                continue
                
            content_key = style.get("key")
            content = ctx.get(content_key, "") if content_key else ""
            
            b_type = style.get("type")
            margin = style.get("margin", 0.05) * h
            
            # current_y -= margin/2 
            
            if b_type == "image":
                path = ctx.get("logo_path")
                if path and os.path.exists(path):
                    target_w = style.get("w", 0.2) * w
                    try:
                        img = ImageReader(path)
                        iw, ih = img.getSize()
                        aspect = ih / float(iw)
                        draw_h = target_w * aspect
                        
                        x = 0.5 * w 
                        c.drawImage(path, x - target_w/2, current_y - draw_h, width=target_w, height=draw_h, mask='auto')
                        current_y -= draw_h
                    except:
                        pass
            
            elif b_type in ["text", "wrapped_text"]:
                if not content: continue
                    
                if style.get("upper"): content = content.upper()
                if style.get("prefix"): content = style.get("prefix") + content
                
                font = style.get("font", "Helvetica")
                size = style.get("size", 12)
                color = self._resolve_color(style.get("color", "#000000"), ctx)
                
                c.setFont(font, size)
                c.setFillColor(color)
                
                x = 0.5 * w # Center
                
                if b_type == "wrapped_text":
                    max_w = style.get("width", 0.8) * w
                    lines = self._wrap_text(content, c, max_w)
                    for line in lines:
                        c.drawCentredString(x, current_y - size, line)
                        current_y -= size * 1.2
                else:
                    c.drawCentredString(x, current_y - size, content)
                    current_y -= size * 1.5
            
            current_y -= margin

    def _render_footer(self, c, ctx, style):
        w, h = ctx["width"], ctx["height"]
        content = ctx.get("footer_text", "")
        if not content: return
        
        y_fixed = style.get("y_fixed", 0.05) * h
        y = y_fixed # Bottom relative
        
        c.setFont(style.get("font", "Helvetica"), style.get("size", 10))
        c.setFillColor(self._resolve_color(style.get("color", "#8E8E93"), ctx))
        
        c.drawCentredString(w/2, y, content)
        
        if ctx.get("show_border", True):
             c.setStrokeColor(self._resolve_color(style.get("color", "#8E8E93"), ctx))
             c.setLineWidth(1)
             c.line(w*0.3, y + 15, w*0.7, y + 15)

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

    def _render_elements(self, c, elements, ctx, skip_text=False):
        w, h = ctx["width"], ctx["height"]
        
        for el in elements:
            try:
                etype = el.get("type")
                
                # Dynamic flow skip logic
                if skip_text and etype in ["text", "wrapped_text"]:
                    text = el.get("text", "")
                    if any(x in text for x in ["{project_name}", "{subtitle}", "{company_name}", "{client_name}", "date"]):
                        continue
                
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

                # ID matching populate_scene
                item_id = f"static_{idx}_{etype}"
                ov = ctx.get("overrides", {}).get(item_id)
                
                # Apply overrides to position
                # PDF uses Bottom-Left origin. Canvas uses Top-Left.
                # Canvas Y = Distance from Top.
                # PDF Y = Height - Canvas Y.
                # But we also need to account for anchor points. 
                # ReportLab Rect(x, y, w, h) draws from bottom-left corner.
                # Canvas Rect at (x, y) draws from top-left corner.
                # So PDF Y = Height - (Canvas Y + HeightOfRect).
                # Text anchors vary.
                
                if etype in ["rect", "rounded_rect"]:
                    rx, ry, rw, rh = el.get("rect", [0,0,0,0])
                    # JSON coords are assumed to be "Percentage from Bottom" if working ? 
                    # Existing code: ry*h passed to c.rect. c.rect expects Bottom-Left Y.
                    # If JSON says ry=0.1. c.rect(..., 0.1*h, ...) -> Draws near bottom.
                    # If Canvas shows it near top, then JSON ry must be 0.9?
                    # Let's assume JSON is "PDF Ready".
                    
                    x, y, w_val, h_val = rx*w, ry*h, rw*w, rh*h
                    
                    if ov:
                         # Override is in Canvas Coords (Top-Left, pixels/points)
                         # ov['y'] is Top Y.
                         # PDF Y (Bottom-Left) = PageHeight - (ov['y'] + h_val)
                         x = ov['x']
                         y = h - (ov['y'] + h_val)
                         # Scale? ov['scale']
                         if "scale" in ov:
                             s = ov["scale"]
                             # Scale affects width/height around center? Or top-left?
                             # Canvas scale is usually top-left unless transform origin changed.
                             # Let's simple-scale w/h
                             w_val *= s
                             h_val *= s
                             # Re-adjust Y because H changed?
                             y = h - (ov['y'] + h_val) 

                    radius = el.get("radius", 0)
                    if etype == "rounded_rect": radius = el.get("radius", 0.02)
                    
                    if radius > 0:
                        c.roundRect(x, y, w_val, h_val, radius*w, fill=bool(color), stroke=bool(stroke))
                    else:
                        c.rect(x, y, w_val, h_val, fill=bool(color), stroke=bool(stroke))
                
                elif etype == "circle":
                    cx, cy = el.get("x", 0)*w, el.get("y", 0)*h
                    r = el.get("r", 0)
                    if r < 1.0: r *= w 
                    
                    if ov:
                        # Circle is usually center based in logic above? (cx, cy)
                        # Canvas draws rect(cx-r, cy-r).
                        # Canvas ov['x'] is Left, ov['y'] is Top of bounding rect.
                        # Center X = ov['x'] + r
                        # Center Y (Canvas) = ov['y'] + r
                        # PDF Center Y = Height - Center Y (Canvas)
                        
                        scale = ov.get("scale", 1.0)
                        r *= scale
                        
                        center_x_canvas = ov['x'] + r
                        center_y_canvas = ov['y'] + r
                        
                        cx = center_x_canvas
                        cy = h - center_y_canvas
                    
                    c.circle(cx, cy, r, fill=bool(color), stroke=bool(stroke))
                    
                elif etype == "line":
                     # TODO: complex path overrides not fully supported yet
                    x1, y1 = el.get("x1", 0)*w, el.get("y1", 0)*h
                    x2, y2 = el.get("x2", 0)*w, el.get("y2", 0)*h
                    c.line(x1, y1, x2, y2)
                    
                elif etype == "text":
                    text = el.get("text", "")
                    text = text.format(**ctx)
                    
                    font = el.get("font", "Helvetica")
                    size = el.get("size", 12)
                    align = el.get("align", "left")
                    x, y = el.get("x", 0)*w, el.get("y", 0)*h
                    
                    if ov:
                        # Canvas item is Top-Left anchored text (usually).
                        # PDF draws text from Baseline? or Top?
                        # ReportLab drawString(x, y) is Baseline.
                        # Canvas Text Item (QGraphicsTextItem) pos() is Top-Left.
                        # Baseline is approx Top + Ascent.
                        # Simple approx: Y_PDF = Height - (Y_Canvas + Size)
                        
                        scale = ov.get("scale", 1.0)
                        size *= scale
                        x = ov['x']
                        # Approx baseline at bottom of text box
                        y = h - (ov['y'] + size*0.8) # Heuristic
                        
                    c.setFont(font, size)
                    if not color: c.setFillColor(self.COLORS['dark'])
                        
                    if align == "center" and not ov:
                        c.drawCentredString(x, y, text)
                    elif align == "right" and not ov:
                        c.drawRightString(x, y, text)
                    else:
                        c.drawString(x, y, text)
                    
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
                        x, y = el.get("x", 0)*w, el.get("y", 0)*h
                        
                        try:
                            img = ImageReader(path)
                            iw, ih = img.getSize()
                            aspect = ih / float(iw)
                            draw_h = target_w * aspect
                            
                            c.drawImage(path, x - target_w/2, y, width=target_w, height=draw_h, mask='auto')
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

    def _render_dynamic_flow(self, c, ctx):
        """Render dynamic elements in a vertical flow (PDF)."""
        w, h = ctx["width"], ctx["height"]
        
        current_y = 0.8 * h 
        
        order = ctx.get("element_order", [])
        
        for block_type in order:
            style = self.BLOCK_STYLES.get(block_type)
            if not style: continue
            
            if block_type == "logo" and not ctx.get("logo_path"): continue
            if block_type in ["company", "client", "date", "reference"] and not ctx.get("show_" + block_type, True): continue # Assuming logic from dialog
            
            # Special case: Footer is fixed at bottom
            if block_type == "footer":
                self._render_footer(c, ctx, style)
                continue
                
            content_key = style.get("key")
            content = ctx.get(content_key, "") if content_key else ""
            
            item_id = f"dynamic_{block_type}"
            ov = ctx.get("overrides", {}).get(item_id)
            
            b_type = style.get("type")
            margin = style.get("margin", 0.05) * h
            
            # Setup overrides
            # ov['x'], ov['y'] are Canvas Coords (Top-Left).
            # PDF Y (Bottom-Left) = PageHeight - (CanvasY + Height).
            
            if b_type == "image":
                path = ctx.get("logo_path")
                if path and os.path.exists(path):
                    target_w = style.get("w", 0.2) * w
                    try:
                        img = ImageReader(path)
                        iw, ih = img.getSize()
                        aspect = ih / float(iw)
                        draw_h = target_w * aspect
                        
                        # Default Pos
                        x = 0.5 * w 
                        y = current_y - draw_h
                        
                        if ov:
                            target_w = target_w * ov.get("scale", 1.0)
                            draw_h = draw_h * ov.get("scale", 1.0)
                            x = ov['x'] + target_w/2 # drawImage is bottom-left? No wait.
                            # ReportLab drawImage(x,y, w, h) -> (x,y) is bottom-left.
                            # Logic above: c.drawImage(..., x - target_w/2, current_y - draw_h ...)
                            # This implies 'x' was center, and 'current_y' was top.
                            
                            # With override:
                            # ov['x'] is Left. ov['y'] is Top.
                            # PDF X = ov['x']
                            # PDF Y = Height - (ov['y'] + draw_h)
                            x = ov['x'] + target_w/2 # To match the x - target_w/2 below?
                            # No, let's just use raw X if we change the draw call?
                            # To minimize diff, let's adjust 'x' to be center-based if the call expects center-based X?
                            # The call uses: `x - target_w/2`. So if I want left to be ov['x'], then `x` (center) = ov['x'] + w/2.
                            
                            y = h - (ov['y'] + draw_h)
                            
                        # Apply
                        c.drawImage(path, x - target_w/2, y, width=target_w, height=draw_h, mask='auto')
                        
                        if not ov:
                            current_y -= draw_h
                    except:
                        pass
            
            elif b_type in ["text", "wrapped_text"]:
                if not content: continue
                    
                if style.get("upper"): content = content.upper()
                if style.get("prefix"): content = style.get("prefix") + content
                
                font = style.get("font", "Helvetica")
                size = style.get("size", 12)
                color = self._resolve_color(style.get("color", "#000000"), ctx)
                
                if ov:
                    size = size * ov.get("scale", 1.0)
                    
                c.setFont(font, size)
                c.setFillColor(color)
                
                x = 0.5 * w # Default Center
                
                if b_type == "wrapped_text":
                    max_w = style.get("width", 0.8) * w
                    if ov and "scale" in ov: max_w *= ov["scale"]
                    
                    lines = self._wrap_text(content, c, max_w)
                    for line in lines:
                        if ov:
                            # Override X/Y
                            text_y = h - (ov['y'] + size*0.8) # Approx baseline
                            c.drawString(ov['x'], text_y, line)
                            ov['y'] += size * 1.2 # shift 'virtual' top down
                        else:
                            c.drawCentredString(x, current_y - size, line)
                            current_y -= size * 1.2
                else:
                    if ov:
                        text_y = h - (ov['y'] + size*0.8)
                        c.drawString(ov['x'], text_y, content)
                    else:
                        c.drawCentredString(x, current_y - size, content)
                        current_y -= size * 1.5

                if not ov:
                    current_y -= margin

    def _render_footer(self, c, ctx, style):
        w, h = ctx["width"], ctx["height"]
        content = ctx.get("footer_text", "")
        if not content: return
        
        y_fixed = style.get("y_fixed", 0.05) * h
        y = y_fixed # Bottom relative
        
        c.setFont(style.get("font", "Helvetica"), style.get("size", 10))
        c.setFillColor(self._resolve_color(style.get("color", "#8E8E93"), ctx))
        
        c.drawCentredString(w/2, y, content)
        
        if ctx.get("show_border", True):
             c.setStrokeColor(self._resolve_color(style.get("color", "#8E8E93"), ctx))
             c.setLineWidth(1)
             c.line(w*0.3, y + 15, w*0.7, y + 15)

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
        """Wrap text preserving existing newlines."""
        final_lines = []
        # Split by explicit newlines first to preserve paragraphs
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            # If empty line, keep it
            if not paragraph.strip():
                final_lines.append("")
                continue
                
            words = paragraph.split()
            current = []
            for word in words:
                current.append(word)
                w = c.stringWidth(' '.join(current), c._fontname, c._fontsize)
                if w > max_width:
                    current.pop()
                    final_lines.append(' '.join(current))
                    current = [word]
            if current:
                final_lines.append(' '.join(current))
                
        return final_lines
