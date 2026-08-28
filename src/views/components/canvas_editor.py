
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsPixmapItem, QGraphicsPathItem, QMenu,
    QGraphicsSceneMouseEvent
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QTransform, QPainterPath

from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QTransform, QPainterPath, QPolygonF


class CanvasItemMixin:
    """Mixin for common canvas item functionality (selection, properties)."""
    
    def __init__(self):
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsFocusable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.item_id = None 
        self.is_locked = False
        
        # Layer properties
        self.layer_name = "Capa sin nombre"
        self.user_z_index = 50  # Default middle range
        self.layer_visible = True
        
        # Rotation/Scaling state
        self._interaction_mode = None  # None, "rotate", "scale"
        self._start_pos = None
        self._start_rotation = 0
        self._start_scale = 1.0
    
    def set_locked(self, locked):
        self.is_locked = locked
        # Disable movement flag
        current_flags = self.flags()
        if locked:
           self.setFlags(current_flags & ~QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        else:
           self.setFlags(current_flags | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    
    def set_layer_visible(self, visible: bool):
        """Set layer visibility."""
        self.layer_visible = visible
        self.setVisible(visible)
    
    def set_layer_name(self, name: str):
        """Set layer name."""
        self.layer_name = name
    
    def set_z_index(self, z: int):
        """Set z-index for layer ordering."""
        self.user_z_index = z
        self.setZValue(z)
    
    def move_layer_up(self):
        """Move layer up (increase z-index)."""
        self.set_z_index(self.user_z_index + 10)
    
    def move_layer_down(self):
        """Move layer down (decrease z-index)."""
        self.set_z_index(self.user_z_index - 10)
    
    def to_front(self):
        """Bring to front (top layer)."""
        if self.scene():
            max_z = max([item.zValue() for item in self.scene().items()], default=0)
            self.set_z_index(int(max_z) + 10)
    
    def to_back(self):
        """Send to back (bottom layer)."""
        if self.scene():
            min_z = min([item.zValue() for item in self.scene().items()], default=0)
            self.set_z_index(int(min_z) - 10)

    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #2D2D2D; color: white; } QMenu::item:selected { background-color: #0A84FF; }")
        
        act_front = menu.addAction("Traer al Frente")
        act_back = menu.addAction("Enviar al Fondo")
        menu.addSeparator()
        act_lock = menu.addAction("Desbloquear" if self.is_locked else "Bloquear")
        act_del = menu.addAction("Eliminar")
        
        action = menu.exec(event.screenPos())
        
        if action == act_front:
            self.setZValue(self.zValue() + 1)
        elif action == act_back:
            self.setZValue(self.zValue() - 1)
        elif action == act_lock:
            self.set_locked(not self.is_locked)
        elif action == act_del:
            if self.scene():
                self.scene().removeItem(self)

    def hoverMoveEvent(self, event):
        """Detect if mouse is near corner for rotation or on corner for scaling."""
        if self.is_locked or not self.isSelected():
            super().hoverMoveEvent(event)
            return
        
        rect = self.boundingRect()
        pos = event.pos()
        
        # Check all four corners
        corners = [
            rect.topLeft(), rect.topRight(),
            rect.bottomLeft(), rect.bottomRight()
        ]
        
        closest_dist = float('inf')
        for corner in corners:
            dist = (pos - corner).manhattanLength()
            if dist < closest_dist:
                closest_dist = dist
        
        # Rotation zone: 10-30 pixels from corner
        # Scaling zone: 0-10 pixels from corner
        if closest_dist <= 10:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)  # Scale cursor
        elif closest_dist <= 30:
            # Rotation cursor - using closed hand as Qt doesn't have a rotation cursor
            self.setCursor(Qt.CursorShape.ClosedHandCursor)  
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().hoverMoveEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Reset cursor when leaving item."""
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Check if we're starting a rotation or scale operation."""
        if self.is_locked:
            super().mousePressEvent(event)
            return
        
        rect = self.boundingRect()
        pos = event.pos()
        
        # Check distance to nearest corner
        corners = [
            rect.topLeft(), rect.topRight(),
            rect.bottomLeft(), rect.bottomRight()
        ]
        
        closest_dist = float('inf')
        for corner in corners:
            dist = (pos - corner).manhattanLength()
            if dist < closest_dist:
                closest_dist = dist
        
        if closest_dist <= 10:
            # Scaling mode
            self._interaction_mode = "scale"
            self._start_pos = event.scenePos()
            self._start_scale = self.scale()
            event.accept()
        elif closest_dist <= 30:
            # Rotation mode
            self._interaction_mode = "rotate"
            self._start_pos = event.scenePos()
            self._start_rotation = self.rotation()
            event.accept()
        else:
            # Normal drag mode
            self._interaction_mode = None
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle rotation or scaling."""
        if self._interaction_mode == "rotate":
            # Calculate angle from center to mouse
            center = self.sceneBoundingRect().center()
            start_vec = self._start_pos - center
            current_vec = event.scenePos() - center
            
            import math
            start_angle = math.atan2(start_vec.y(), start_vec.x())
            current_angle = math.atan2(current_vec.y(), current_vec.x())
            angle_diff = math.degrees(current_angle - start_angle)
            
            self.setRotation(self._start_rotation + angle_diff)
            event.accept()
            
        elif self._interaction_mode == "scale":
            # Calculate distance change
            center = self.sceneBoundingRect().center()
            start_dist = (self._start_pos - center).manhattanLength()
            current_dist = (event.scenePos() - center).manhattanLength()
            
            if start_dist > 0:
                scale_factor = current_dist / start_dist
                new_scale = self._start_scale * scale_factor
                # Clamp scale
                new_scale = max(0.1, min(5.0, new_scale))
                self.setScale(new_scale)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """End rotation or scaling."""
        if self._interaction_mode:
            self._interaction_mode = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            if self.is_locked: return self.pos() # Reject move
            
            # Don't snap during rotation/scaling
            if self._interaction_mode:
                return value
            
            new_pos = value
            # Calculate Snap
            if hasattr(self.scene(), "calculate_snap"):
                snapped_pos, guides = self.scene().calculate_snap(self, new_pos)
                self.scene().current_guides = guides
                self.scene().update() 
                return snapped_pos
            
        return super().itemChange(change, value)

class CanvasTextItem(CanvasItemMixin, QGraphicsTextItem):
    """Editable text item."""
    
    content_changed = pyqtSignal(str, str) # item_id, new_text
    
    def __init__(self, text="", parent=None):
        QGraphicsTextItem.__init__(self, text, parent)
        CanvasItemMixin.__init__(self)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction) 
        
    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == Qt.TextInteractionFlag.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.setFocus()
        super().mouseDoubleClickEvent(event)
        
    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        if self.item_id:
            self.content_changed.emit(self.item_id, self.toPlainText())
        super().focusOutEvent(event)

class CanvasRectItem(CanvasItemMixin, QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        QGraphicsRectItem.__init__(self, rect, parent)
        CanvasItemMixin.__init__(self)

class CanvasPathItem(CanvasItemMixin, QGraphicsPathItem):
    def __init__(self, path, parent=None):
        QGraphicsPathItem.__init__(self, path, parent)
        CanvasItemMixin.__init__(self)

class CanvasImageItem(CanvasItemMixin, QGraphicsPixmapItem):
    def __init__(self, pixmap, parent=None):
        QGraphicsPixmapItem.__init__(self, pixmap, parent)
        CanvasItemMixin.__init__(self)
        self.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)

class CoverScene(QGraphicsScene):
    """The scene representing the A4 paper."""
    
    item_selected = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_width = 595
        self.page_height = 842
        self.setSceneRect(0, 0, self.page_width, self.page_height)
        self.setBackgroundBrush(QBrush(QColor("#F0F0F0")))
        
        self.current_guides = [] 
        self.snap_threshold = 10.0
        
    def calculate_snap(self, item, pos):
        """Calculate snapped position and guides for an item."""
        x, y = pos.x(), pos.y()
        rect = item.boundingRect()
        
        item_center_x = x + rect.width() / 2
        item_center_y = y + rect.height() / 2
        
        target_center_x = self.page_width / 2
        target_center_y = self.page_height / 2
        
        guides = []
        
        if abs(item_center_x - target_center_x) < self.snap_threshold:
            diff = target_center_x - item_center_x
            x += diff
            guides.append((target_center_x, 0, target_center_x, self.page_height))
            
        if abs(item_center_y - target_center_y) < self.snap_threshold:
            diff = target_center_y - item_center_y
            y += diff
            guides.append((0, target_center_y, self.page_width, target_center_y))
            
        return QPointF(x, y), guides
        
    def mouseReleaseEvent(self, event):
        self.current_guides = []
        self.update()
        super().mouseReleaseEvent(event)

    def drawForeground(self, painter, rect):
        if self.current_guides:
            painter.save()
            pen = QPen(QColor("#00FFFF"))
            pen.setWidth(1)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            
            for line in self.current_guides:
                painter.drawLine(QPointF(line[0], line[1]), QPointF(line[2], line[3]))
            
            painter.restore()
            
    def drawBackground(self, painter, rect):
        painter.save()
        painter.fillRect(rect, QColor("#e0e0e0"))
        
        paper_rect = QRectF(0, 0, self.page_width, self.page_height)
        shadow_rect = paper_rect.translated(4, 4)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 50))
        
        painter.setBrush(Qt.BrushStyle.SolidPattern)
        painter.setBrush(QColor("white"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(paper_rect)
        
        painter.restore()

class CoverCanvasView(QGraphicsView):
    """Interactive view for the cover scene."""
    
    item_changed = pyqtSignal(str, str) # id, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scene = CoverScene(self)
        self.setScene(self.scene)
        
        self.setScene(self.scene)
        
        # Drawing State
        self.drawing_mode = None 
        self.current_poly_points = []
        self.temp_poly_item = None
        
        # Scene selection
        self.scene.selectionChanged.connect(self._on_selection_changed)
        
        self.scale(1.0, 1.0)
        
    def _on_selection_changed(self):
        # Selection handled by external panel
        pass
            
    def _update_item_color(self, color):
        for item in self.scene.selectedItems():
            if hasattr(item, "setDefaultTextColor"): # Text
                item.setDefaultTextColor(color)
            if hasattr(item, "setBrush"): # Shape
                item.setBrush(QBrush(color))

    def _update_item_stroke_color(self, color):
        for item in self.scene.selectedItems():
            if hasattr(item, "setPen"):
                pen = item.pen()
                pen.setColor(color)
                item.setPen(pen)

    def _update_item_stroke_width(self, width):
        for item in self.scene.selectedItems():
            if hasattr(item, "setPen"):
                pen = item.pen()
                pen.setWidthF(width)
                item.setPen(pen)

    
    def _update_item_scale(self, scale):
        for item in self.scene.selectedItems():
            item.setScale(scale)

    def _update_item_rotation(self, rot):
        for item in self.scene.selectedItems():
            item.setRotation(rot)
            
    def _update_item_opacity(self, opacity):
        for item in self.scene.selectedItems():
            item.setOpacity(opacity)

    def _update_item_lock(self, locked):
        for item in self.scene.selectedItems():
            if hasattr(item, "set_locked"):
                item.set_locked(locked)

    def _update_item_z_order(self, action):
        for item in self.scene.selectedItems():
            z = item.zValue()
            if action == "front": item.setZValue(z + 1)
            elif action == "back": item.setZValue(z - 1)

    def _delete_item(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)

    def start_drawing(self, mode):
        """Enter drawing mode."""
        self.drawing_mode = mode
        self.current_poly_points = []
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def mousePressEvent(self, event):
        if self.drawing_mode == "polygon":
            pos = self.mapToScene(event.pos())
            self.current_poly_points.append(pos)
            self._update_temp_poly()
            event.accept()
        else:
            super().mousePressEvent(event)
            
    def mouseDoubleClickEvent(self, event):
        if self.drawing_mode == "polygon":
            self._finish_polygon()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)
            
    def _update_temp_poly(self):
        """Update temporary preview line."""
        if not self.current_poly_points: return
        
        if self.temp_poly_item:
            self.scene.removeItem(self.temp_poly_item)
            
        poly = QPolygonF(self.current_poly_points)
        path = QPainterPath()
        path.addPolygon(poly)
        self.temp_poly_item = QGraphicsPathItem(path)
        pen = QPen(Qt.GlobalColor.blue, 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        self.temp_poly_item.setPen(pen)
        self.scene.addItem(self.temp_poly_item)
        
    def _finish_polygon(self):
        """Finalize polygon creation."""
        if len(self.current_poly_points) < 2: return
        
        if self.temp_poly_item:
            self.scene.removeItem(self.temp_poly_item)
            self.temp_poly_item = None
            
        poly = QPolygonF(self.current_poly_points)
        path = QPainterPath()
        path.addPolygon(poly)
        path.closeSubpath() # Close the shape
        
        item = CanvasPathItem(path)
        item.setBrush(QBrush(QColor("#CCCCCC")))
        item.setPen(QPen(Qt.GlobalColor.black))
        
        import time
        item.item_id = f"user_poly_{int(time.time()*1000)}"
        self.scene.addItem(item)
        item.setSelected(True)
        
        # Reset state
        self.drawing_mode = None
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        


    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            # Delete selected items
            for item in self.scene.selectedItems():
                self.scene.removeItem(item)
            event.accept()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            factor = 1.1 if zoom_in else 0.9
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def fit_to_view(self):
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.scale(0.9, 0.9)

    def add_shape(self, shape_type):
        """Add a new user shape to the center of the view."""
        if shape_type == "polygon":
            self.start_drawing("polygon")
            return

        scene = self.scene
        center = scene.sceneRect().center()
        x, y = center.x(), center.y()
        
        item = None
        brush = QBrush(QColor("#CCCCCC"))
        pen = QPen(Qt.GlobalColor.black, 2)
        
        if shape_type == "rect":
            # 100x100 rect
            rect = QRectF(x - 50, y - 50, 100, 100)
            item = CanvasRectItem(rect)
            item.setBrush(brush)
            item.setPen(pen)
            
        elif shape_type == "rounded_rect":
            path = QPainterPath()
            path.addRoundedRect(x - 50, y - 50, 100, 100, 20, 20)
            item = CanvasPathItem(path)
            item.setBrush(brush)
            item.setPen(pen)
            
        elif shape_type == "circle":
            path = QPainterPath()
            path.addEllipse(x - 50, y - 50, 100, 100)
            item = CanvasPathItem(path)
            item.setBrush(brush)
            item.setPen(pen)
            
        elif shape_type == "triangle":
            item = CanvasPathItem(self._create_regular_polygon_path(3, 60, x, y))
            item.setBrush(brush)
            item.setPen(pen)
            
        elif shape_type == "pentagon":
            item = CanvasPathItem(self._create_regular_polygon_path(5, 60, x, y))
            item.setBrush(brush)
            item.setPen(pen)
            
        elif shape_type == "hexagon":
            item = CanvasPathItem(self._create_regular_polygon_path(6, 60, x, y))
            item.setBrush(brush)
            item.setPen(pen)
            
        elif shape_type == "octagon":
            item = CanvasPathItem(self._create_regular_polygon_path(8, 60, x, y))
            item.setBrush(brush)
            item.setPen(pen)
            
        elif shape_type == "star":
            item = CanvasPathItem(self._create_star_path(5, 60, 25, x, y))
            item.setBrush(brush)
            item.setPen(pen)
            
        elif shape_type == "line":
            path = QPainterPath()
            path.moveTo(x - 50, y)
            path.lineTo(x + 50, y)
            item = CanvasPathItem(path)
            # Lines don't have fill usually
            item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            item.setPen(pen)

        elif shape_type == "text":
            item = CanvasTextItem("Nuevo Texto")
            item.setDefaultTextColor(QColor("black"))
            font = QFont("Helvetica", 12)
            item.setFont(font)
            item.setPos(x - 60, y)
            
        if item:
            import time
            item.item_id = f"user_{shape_type}_{int(time.time()*1000)}"
            scene.addItem(item)
            item.setSelected(True)

    def _create_regular_polygon_path(self, sides, radius, cx, cy):
        """Helper to create N-sided polygon path."""
        import math
        path = QPainterPath()
        angle = -math.pi / 2 # Start top
        step = 2 * math.pi / sides
        
        path.moveTo(cx + radius * math.cos(angle), cy + radius * math.sin(angle))
        for i in range(1, sides):
            angle += step
            path.lineTo(cx + radius * math.cos(angle), cy + radius * math.sin(angle))
        path.closeSubpath()
        return path

    def _create_star_path(self, points, outer_radius, inner_radius, cx, cy):
        """Helper to create Star path."""
        import math
        path = QPainterPath()
        angle = -math.pi / 2
        step = math.pi / points
        
        path.moveTo(cx + outer_radius * math.cos(angle), cy + outer_radius * math.sin(angle))
        for i in range(1, points * 2):
            r = inner_radius if i % 2 != 0 else outer_radius
            angle += step
            path.lineTo(cx + r * math.cos(angle), cy + r * math.sin(angle))
        path.closeSubpath()
        return path
