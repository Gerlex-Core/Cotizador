
    def _show_shapes_menu(self):
        """Show organized dropdown menu for all shapes."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
                border-radius: 4px;
                padding: 8px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 32px 8px 24px;
                color: white;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #0A84FF;
            }
            QMenu::icon {
                padding-left: 8px;
            }
        """)
        
        # Define all shapes with their metadata
        shapes = [
            ("rect", "Rectángulo", "box.png"),
            ("rounded_rect", "Rectángulo Redondeado", "formas/rectanguloRedondeado.png"),
            ("circle", "Círculo", "formas/circuloSilueta.png"),
            ("triangle", "Triángulo", "formas/trianguloSilueta.png"),
            ("pentagon", "Pentágono", "formas/pentagono.png"),
            ("hexagon", "Hexágono", "formas/hexagonoSilueta.png"),
            ("octagon", "Octágono", "formas/ocyagono.png"),
            ("line", "Línea", "formas/linea.png"),
            ("star", "Estrella", "star.png"),
        ]
        
        for shape_id, shape_name, icon_path in shapes:
            action = menu.addAction(self.icon_manager.get_icon(icon_path, 18), shape_name)
            action.triggered.connect(lambda checked, s=shape_id: self.insert_shape.emit(s))
        
        # Show menu below button
        button = self.sender()
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
