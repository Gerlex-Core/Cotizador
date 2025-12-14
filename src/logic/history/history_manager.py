import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self):
        self.history_dir = os.path.join("media", "data", "historial")
        self.recent_file = os.path.join(self.history_dir, "recent.json")
        self.history_file = os.path.join(self.history_dir, "cotizacion.json")
        
        self._ensure_dir()
        self.max_recent = 10

    def _ensure_dir(self):
        """Ensure history directory exists."""
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)

    def _load_json(self, path):
        """Load JSON file safely."""
        if not os.path.exists(path):
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return []

    def _save_json(self, path, data):
        """Save JSON file safely."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving {path}: {e}")

    def add_to_recent(self, file_path):
        """Add file to recent list."""
        recent = self._load_json(self.recent_file)
        
        # Remove if exists to move to top
        recent = [r for r in recent if r != file_path]
        
        # Add to top
        recent.insert(0, file_path)
        
        # Limit
        recent = recent[:self.max_recent]
        
        self._save_json(self.recent_file, recent)

    def add_to_history(self, file_path, metadata):
        """Add record to full history."""
        history = self._load_json(self.history_file)
        
        # Create record
        record = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "date_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metadata": metadata
        }
        
        # Update if exists (by path)
        found = False
        for i, item in enumerate(history):
            if item["path"] == file_path:
                history[i] = record
                found = True
                break
        
        if not found:
            history.append(record)
            
        self._save_json(self.history_file, history)

    def get_recent(self):
        """Get recent files list."""
        return self._load_json(self.recent_file)

    def get_history(self):
        """Get full history."""
        return self._load_json(self.history_file)

    def search_history(self, query):
        """Search history by name or date."""
        history = self.get_history()
        query = query.lower()
        return [
            item for item in history 
            if query in item["name"].lower() or 
               query in item["date_modified"] or
               query in str(item["metadata"]).lower()
        ]
