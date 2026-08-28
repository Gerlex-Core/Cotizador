from html.parser import HTMLParser

class ReportLabHTMLParser(HTMLParser):
    """Parse Qt HTML to ReportLab XML with robust CSS support.
    
    Handles the specifics of Qt's QTextEdit HTML export, converting it
    to ReportLab's supported XML tags for Paragraph flowables.
    """
    # Tags to completely ignore (document structure)
    IGNORE_TAGS = {'html', 'head', 'meta', '!doctype', 'title'}
    
    def __init__(self):
        super().__init__()
        self.output = []
        self.tag_stack = []
        self._ignore_content = False
        self.list_depth = 0
        self.list_counters = [] # For <ol> support later if needed

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        attrs_dict = dict(attrs)
        style = attrs_dict.get('style', '')
        
        # Parse CSS style
        css = self._parse_css(style)
        
        # Skip document structure tags
        if tag_lower in self.IGNORE_TAGS:
            return
        
        if tag_lower == 'style':
            self._ignore_content = True
            return
            
        if self._ignore_content and tag_lower not in ('body',):
            return
            
        # --- MAPPING QT HTML TO REPORTLAB XML ---
        
        tags_to_open = [] 
        
        # 1. Font Face
        font_family = css.get('font-family', '').lower()
        if font_family:
            # Map common fonts to standard PDF fonts to avoid dependency issues
            pdf_font = 'Helvetica'
            if 'times' in font_family or 'serif' in font_family: pdf_font = 'Times-Roman'
            elif 'courier' in font_family or 'mono' in font_family: pdf_font = 'Courier'
            tags_to_open.append(f'<font face="{pdf_font}">')
            
        # 2. Font Size
        font_size = css.get('font-size')
        if font_size:
            # Handle 'pt', 'px'
            import re
            match = re.search(r'([\d\.]+)(pt|px)', font_size)
            if match:
                val = float(match.group(1))
                unit = match.group(2)
                # Adjust size? ReportLab usually takes points roughly
                if unit == 'px': val *= 0.75
                tags_to_open.append(f'<font size="{int(val)}">')

        # 3. Colors (Text & Background)
        color = css.get('color')
        if color and self._is_valid_color(color):
             tags_to_open.append(f'<font color="{color}">')
             
        bg_color = css.get('background-color')
        if bg_color and self._is_valid_color(bg_color) and bg_color != 'transparent':
             # ReportLab supports backColor in font tag
             tags_to_open.append(f'<font backColor="{bg_color}">')
             
        # 4. Font Weight (Bold)
        weight = css.get('font-weight', '400')
        is_bold = False
        if weight in ('bold', 'bolder') or (weight.isdigit() and int(weight) >= 600):
            is_bold = True
            tags_to_open.append('<b>')
            
        # 5. Font Style (Italic)
        if css.get('font-style') in ('italic', 'oblique'):
            tags_to_open.append('<i>')
            
        # 6. Text Decoration (Underline, Strike)
        decoration = css.get('text-decoration', '')
        if 'underline' in decoration:
            tags_to_open.append('<u>')
        if 'line-through' in decoration:
            tags_to_open.append('<strike>')
            
        # 7. Semantic Tags
        if tag_lower in ('b', 'strong') and not is_bold:
            tags_to_open.append('<b>')
        elif tag_lower in ('i', 'em'):
            tags_to_open.append('<i>')
        elif tag_lower == 'u':
            tags_to_open.append('<u>')
        elif tag_lower in ('s', 'strike', 'del'):
            tags_to_open.append('<strike>')
        elif tag_lower == 'sub':
            tags_to_open.append('<sub>')
        elif tag_lower == 'sup':
            tags_to_open.append('<sup>')
        
        # 8. Block Elements (Lists, Paragraphs)
        elif tag_lower == 'p':
            if self.output: self.output.append('<br/>')
            
        elif tag_lower == 'br':
            self.output.append('<br/>')
            
        elif tag_lower in ('ul', 'ol'):
            self.list_depth += 1
            if self.output and not self.output[-1].endswith('<br/>'):
                self.output.append('<br/>')
        
        elif tag_lower == 'li':
            indent = "&nbsp;" * (self.list_depth * 4)
            bullet = "&bull;" # Simple bullet
            self.output.append(f'<br/>{indent}{bullet} ')

        # Push to stack to close in correct order
        self.tag_stack.append(tags_to_open)
        for t in tags_to_open:
            self.output.append(t)

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        
        if tag_lower == 'style':
            self._ignore_content = False
            return
            
        if self._ignore_content and tag_lower not in ('body',):
            return
            
        if self.tag_stack:
            tags_to_close = self.tag_stack.pop()
            # Close in reverse order
            for t in reversed(tags_to_close):
                # Extract tag name from <tag ...>
                tag_name = t.split(' ')[0][1:].strip('>')
                self.output.append(f'</{tag_name}>')
        
        if tag_lower in ('ul', 'ol'):
            self.list_depth = max(0, self.list_depth - 1)
            # self.output.append('<br/>')

    def handle_data(self, data):
        if self._ignore_content: return
        
        # Clean data
        data = data.replace('\t', '    ')
        
        if data:
            # Escape XML entities if needed? 
            # HTMLParser provides unescaped data. ReportLab XML needs escaping.
            # But ReportLab Paragraph handles basic entities. 
            # We strictly should escape <, >, & for XML validity inside the tags.
            from xml.sax.saxutils import escape
            self.output.append(escape(data))

    def _parse_css(self, style_str):
        """Parse CSS style string into dict."""
        styles = {}
        if not style_str: return styles
        for item in style_str.split(';'):
            if ':' in item:
                key, val = item.split(':', 1)
                styles[key.strip().lower()] = val.strip().lower()
        return styles

    def _is_valid_color(self, color):
        """Check if color is relevant to keep (not white/black default if redundant)."""
        if not color: return False
        c = color.lower()
        # Keep everything to be safe as user requested full fidelity
        return True

    def get_result(self):
        # Close any lingering tags
        while self.tag_stack:
            tags = self.tag_stack.pop()
            for t in reversed(tags):
                tag_name = t.split(' ')[0][1:].strip('>')
                self.output.append(f'</{tag_name}>')
        return "".join(self.output).strip()
