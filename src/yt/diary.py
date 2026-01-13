import json
import os
import re
from datetime import datetime

class DiaryManager:
    def __init__(self, storage_dir="db"):
        self.storage_dir = storage_dir
        self.file_path = os.path.join(self.storage_dir, "download_history.json")
        self.ensure_history_file()

    def ensure_history_file(self):
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def clear_history(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

    def get_history_urls(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return list(set(entry['url'] for entry in history))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def get_all_entries(self):
        try:
            if not os.path.exists(self.file_path):
                return []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def delete_entry(self, entry_id):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Find entry to get paths
            entry = next((e for e in history if e.get('id') == entry_id), None)
            if entry:
                # Remove files if they exist
                for path_key in ['video_path', 'srt_path']:
                    raw_path = entry.get(path_key)
                    if raw_path:
                        actual_path = self.resolve_path(raw_path)
                        if actual_path and os.path.exists(actual_path):
                            try:
                                os.remove(actual_path)
                            except Exception as e:
                                print(f"Error deleting file {actual_path}: {e}")
                
                # Remove from history
                new_history = [e for e in history if e.get('id') != entry_id]
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(new_history, f, indent=4, ensure_ascii=False)
                return True
            return False
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def resolve_path(self, path):
        """Robustly find the file even if extension changed or suffix added."""
        if not path: return None
        if os.path.exists(path): return path
        
        # Try different extensions
        base, ext = os.path.splitext(path)
        for alt_ext in ['.mp4', '.mkv', '.webm', '.avi', '.srt']:
            alt_path = base + alt_ext
            if os.path.exists(alt_path): return alt_path
            
        # Try stripping stream suffixes (e.g. .f251)
        cleaned_base = re.sub(r'\.f\d+$', '', base)
        if cleaned_base != base:
            for alt_ext in ['.mp4', '.mkv', '.webm', '.avi', '.srt']:
                alt_path = cleaned_base + alt_ext
                if os.path.exists(alt_path): return alt_path
        
        return path # Return original if not found

    def save_entry(self, title, url, creator, description, format_info, video_path=None, srt_path=None):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            history = []

        # Find existing entry for this URL to update it if possible
        existing_entry = next((e for e in history if e['url'] == url), None)

        if existing_entry:
            if video_path: existing_entry['video_path'] = video_path
            if srt_path: existing_entry['srt_path'] = srt_path
            existing_entry['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Possibly update title/format if missing
            if not existing_entry.get('title'): existing_entry['title'] = title
        else:
            entry = {
                "id": str(int(datetime.now().timestamp())),
                "title": title,
                "url": url,
                "creator": creator,
                "description": description[:200] + "..." if len(description) > 200 else description,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "video_path": video_path,
                "srt_path": srt_path,
                "format": format_info
            }
            history.append(entry)

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
