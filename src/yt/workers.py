import re
import os
import yt_dlp
import requests
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap

# --- WORKER THREAD FOR DOWNLOADING ---
class DownloadThread(QThread):
    progress_signal = Signal(str) # To update status label
    finished_signal = Signal(dict) # To re-enable buttons & save diary. Returns info dict on success.
    
    def __init__(self, url, ydl_opts, context_info):
        super().__init__()
        self.url = url
        self.ydl_opts = ydl_opts
        self.context_info = context_info # Info passed for diary (title, creator etc)
        self.final_filename = None

    def run(self):
        # Hook into progress to emit signals
        params = self.ydl_opts.copy()
        params['progress_hooks'] = [self.my_hook]
        params['quiet'] = True
        params['no_color'] = True
        
        # Output template - ensure it goes to 'videos/' if not set
        if 'outtmpl' not in params:
             params['outtmpl'] = 'videos/%(title)s [%(height)sp].%(ext)s'

        try:
            self.progress_signal.emit("Starting download...")
            with yt_dlp.YoutubeDL(params) as ydl:
                # Run download
                info = ydl.extract_info(self.url, download=True)
                
                # Determine the filename (if not already set by hook)
                # prioritizing info.get('_filename') or info.get('filepath') if download finished
                if info.get('_filename') and os.path.exists(info['_filename']):
                    self.final_filename = info['_filename']
                elif info.get('requested_downloads') and os.path.exists(info['requested_downloads'][0].get('filepath', '')):
                    self.final_filename = info['requested_downloads'][0]['filepath']
                elif not self.final_filename:
                    # 1. Fallback 
                    if info.get('requested_downloads'):
                        self.final_filename = info['requested_downloads'][0].get('filepath')
                    # 2. Check info dict for requested_subtitles
                    elif info.get('requested_subtitles'):
                        first_lang = next(iter(info['requested_subtitles']))
                        self.final_filename = info['requested_subtitles'][first_lang].get('filepath')
                    # 3. Fallback
                    else:
                        self.final_filename = ydl.prepare_filename(info)

            self.progress_signal.emit("Download Complete!")
            # Pass back success info
            result = self.context_info.copy()
            result['filepath'] = self.final_filename
            self.finished_signal.emit(result)
            
        except Exception as e:
            self.progress_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit({}) # Emit empty dict to signal failure/end
        
    def my_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%')
            s = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            size = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str', 'N/A')
            
            # Comprehensive ANSI stripping
            def clean(t):
                return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', t).strip() if t else 'N/A'
            
            msg = f"Downloading: {clean(p)} of {clean(size)} | Speed: {clean(s)} | ETA: {clean(eta)}"
            self.progress_signal.emit(msg)
            
        elif d['status'] == 'finished':
            if 'filename' in d:
                self.final_filename = d['filename']
            self.progress_signal.emit("Download complete. Processing...")

# --- WORKER FOR THUMBNAIL FETCHING ---
class ThumbnailThread(QThread):
    loaded_signal = Signal(QPixmap)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.loaded_signal.emit(pixmap)
        except Exception:
            pass
