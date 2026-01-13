import sys
import os
import re
import webbrowser
import yt_dlp
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                               QSplitter, QComboBox, QMessageBox, QTextEdit, QScrollArea,
                               QTabWidget, QStatusBar, QFrame, QCompleter, QMenuBar, QMenu)
from PySide6.QtGui import QPixmap, QIcon, QFont, QColor, QAction
from PySide6.QtCore import Qt, QThread, Signal, QSize, QStringListModel
import qtawesome as qta
from yt.workers import DownloadThread, ThumbnailThread
from yt.ui.explorer_tab import ExplorerTab
try:
    from yt.diary import DiaryManager
except ImportError:
    # Fallback if running directly without package structure
    from diary import DiaryManager


# --- THEMES ---
DARK_THEME = """
    QMainWindow { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI', Roboto, Helvetica; }
    
    /* Card/Panel Style */
    QFrame#card, QFrame#stats_card {
        background-color: #1E1E1E;
        border-radius: 12px;
        border: 1px solid #333;
    }
    
    QLineEdit, QComboBox, QTextEdit { 
        padding: 10px; border-radius: 8px; border: 1px solid #333; 
        background-color: #181818; color: white; 
    }
    
    QComboBox::drop-down { border: none; }
    
    QPushButton#primary { 
        padding: 12px; border-radius: 8px; background-color: #cc0000; 
        color: white; font-weight: bold; border: none; 
    }
    QPushButton#primary:hover { background-color: #e60000; }
    QPushButton#primary:disabled { background-color: #444; color: #888; }
    
    QPushButton#secondary, QPushButton#refresh_btn { 
        padding: 8px; border-radius: 6px; background-color: #333; 
        color: white; border: none; 
    }
    QPushButton#secondary:hover, QPushButton#refresh_btn:hover { background-color: #444; }

    QTableWidget {
        background-color: #181818;
        color: #E0E0E0;
        gridline-color: #333;
        border: none;
        border-radius: 8px;
    }
    QHeaderView::section {
        background-color: #1E1E1E;
        color: #888;
        padding: 5px;
        border: none;
        font-weight: bold;
    }
    QTableWidget::item:selected {
        background-color: #333;
    }

    QTabWidget::pane { border: 1px solid #333; border-radius: 8px; background: #1E1E1E; top: -1px; }
    QTabBar::tab {
        background: #181818; color: #888; padding: 10px 20px; 
        border-top-left-radius: 8px; border-top-right-radius: 8px;
        margin-right: 2px;
    }
    QTabBar::tab:selected { background: #1E1E1E; color: white; border-bottom: 2px solid #cc0000; }
    
    QLabel#title { font-size: 24px; font-weight: bold; color: white; }
    QLabel#subtitle { color: #888; font-size: 14px; }
    QLabel#subtitle a { color: #cc0000; text-decoration: none; font-weight: bold; }
    QLabel#description { color: #E0E0E0; }
    QLabel#stat_label { color: #cc0000; font-weight: bold; }
    
    QStatusBar { background-color: #181818; color: #888; }
    
    QLabel#thumbnail { background-color: #000; border-radius: 8px; }

    QMessageBox { background-color: #1E1E1E; border: 1px solid #333; }
    QMessageBox QLabel { color: #E0E0E0; }
    QMessageBox QPushButton { 
        background-color: #333; color: white; border-radius: 4px; padding: 5px 15px; 
    }
    QMessageBox QPushButton:hover { background-color: #444; }
"""

LIGHT_THEME = """
    QMainWindow { background-color: #F5F5F7; color: #1D1D1F; font-family: 'Segoe UI', Roboto, Helvetica; }
    
    QFrame#card, QFrame#stats_card {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E1E1E1;
    }
    
    QLineEdit, QComboBox, QTextEdit { 
        padding: 10px; border-radius: 8px; border: 1px solid #D2D2D7; 
        background-color: #FFFFFF; color: #1D1D1F; 
    }
    
    QPushButton#primary { 
        padding: 12px; border-radius: 8px; background-color: #CC0000; 
        color: white; font-weight: bold; border: none; 
    }
    QPushButton#primary:hover { background-color: #B20000; }
    QPushButton#primary:disabled { background-color: #E8E8ED; color: #999; }
    
    QPushButton#secondary, QPushButton#refresh_btn { 
        padding: 8px; border-radius: 6px; background-color: #E8E8ED; 
        color: #1D1D1F; border: none; 
    }
    QPushButton#secondary:hover, QPushButton#refresh_btn:hover { background-color: #D1D1D6; }

    QTableWidget {
        background-color: #FFFFFF;
        color: #1D1D1F;
        gridline-color: #E1E1E1;
        border: none;
        border-radius: 8px;
    }
    QHeaderView::section {
        background-color: #F5F5F7;
        color: #555;
        padding: 5px;
        border: none;
        font-weight: bold;
    }
    QTableWidget::item:selected {
        background-color: #E8E8ED;
        color: #1D1D1F;
    }

    QTabWidget::pane { border: 1px solid #E1E1E1; border-radius: 8px; background: #FFFFFF; top: -1px; }
    QTabBar::tab {
        background: #E8E8ED; color: #555; padding: 10px 20px; 
        border-top-left-radius: 8px; border-top-right-radius: 8px;
    }
    QTabBar::tab:selected { background: #FFFFFF; color: #1D1D1F; border-bottom: 2px solid #CC0000; }
    
    QLabel { color: #1D1D1F; }
    QTabBar, QStatusBar { color: #1D1D1F; }
    
    QLabel#title { font-size: 24px; font-weight: bold; color: #1D1D1F; }
    QLabel#subtitle { color: #555; font-size: 14px; }
    QLabel#subtitle a { color: #CC0000; text-decoration: none; font-weight: bold; }
    QLabel#description { color: #1D1D1F; }
    QLabel#stat_label { color: #CC0000; font-weight: bold; }
    
    QStatusBar { background-color: #FFFFFF; color: #555; border-top: 1px solid #E1E1E1; }
    
    QLabel#thumbnail { background-color: #E1E1E1; border-radius: 8px; }
    
    QMenuBar { background-color: #F5F5F7; color: #1D1D1F; }
    QMenuBar::item:selected { background-color: #E8E8ED; }
    QMenu { background-color: #FFFFFF; color: #1D1D1F; border: 1px solid #E1E1E1; }
    QMenu::item:selected { background-color: #E8E8ED; }

    QMessageBox { background-color: #FFFFFF; border: 1px solid #E1E1E1; }
    QMessageBox QLabel { color: #1D1D1F; }
    QMessageBox QPushButton { 
        background-color: #E8E8ED; color: #1D1D1F; border-radius: 4px; padding: 5px 15px; 
    }
    QMessageBox QPushButton:hover { background-color: #D1D1D6; }
"""

# --- MAIN APPLICATION ---
class YouTubeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Youtube Video Manager")
        self.setWindowIcon(QIcon("assets/logo.png"))
        self.resize(1200, 850)
        
        self.diary = DiaryManager("db")
        
        self.current_theme = "dark"
        self.current_info = {}
        self.desc_expanded = False
        
        # Ensure SRT folder exists
        if not os.path.exists("videos/SRT"):
            os.makedirs("videos/SRT")

        # --- UI SETUP ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. Top Bar (Search area)
        top_bar = QFrame()
        top_bar.setObjectName("card")
        top_bar.setFixedHeight(70)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(15, 10, 15, 10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL or ID here...")
        
        self.completer = QCompleter()
        self.completer_model = QStringListModel()
        self.completer.setModel(self.completer_model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.url_input.setCompleter(self.completer)
        self.update_completer()
        
        self.fetch_btn = QPushButton(" Fetch")
        self.fetch_btn.setObjectName("primary")
        self.fetch_btn.setIcon(qta.icon('fa5s.search', color='white'))
        self.fetch_btn.clicked.connect(self.load_video_data)

        self.browser_btn = QPushButton()
        self.browser_btn.setObjectName("secondary")
        self.browser_btn.setToolTip("View on YouTube")
        self.browser_btn.setIcon(qta.icon('fa5s.external-link-alt', color='white'))
        self.browser_btn.setFixedSize(40, 40)
        self.browser_btn.clicked.connect(self.open_current_url)
        
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("secondary")
        self.theme_btn.setToolTip("Toggle Theme")
        self.theme_btn.setIcon(qta.icon('fa5s.moon', color='white'))
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)
 
        top_layout.addWidget(self.url_input)
        top_layout.addWidget(self.fetch_btn)
        top_layout.addWidget(self.browser_btn)
        top_layout.addWidget(self.theme_btn)
        main_layout.addWidget(top_bar)

        # 2. Body (Splitter)
        splitter = QSplitter(Qt.Horizontal)
        
        # --- LEFT SIDE: Content Card ---
        self.content_card = QFrame()
        self.content_card.setObjectName("card")
        content_layout = QVBoxLayout(self.content_card)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        self.thumbnail_label = QLabel("Waiting for link...")
        self.thumbnail_label.setObjectName("thumbnail")
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setMinimumHeight(350)
        content_layout.addWidget(self.thumbnail_label)

        # Metadata Area
        self.meta_title = QLabel("Video Title")
        self.meta_title.setObjectName("title")
        self.meta_title.setWordWrap(True)
        content_layout.addWidget(self.meta_title)

        self.meta_creator = QLabel("Creator Name")
        self.meta_creator.setObjectName("subtitle")
        self.meta_creator.setOpenExternalLinks(True)
        content_layout.addWidget(self.meta_creator)

        # Description with "Show More"
        desc_container = QVBoxLayout()
        
        self.desc_scroll = QScrollArea()
        self.desc_scroll.setWidgetResizable(True)
        self.desc_scroll.setFixedHeight(100)
        self.desc_scroll.setFrameShape(QFrame.NoFrame)
        self.desc_scroll.setStyleSheet("background: transparent;")
        
        self.meta_desc = QLabel("Description goes here...")
        self.meta_desc.setObjectName("description")
        self.meta_desc.setWordWrap(True)
        self.meta_desc.setAlignment(Qt.AlignTop)
        
        self.desc_scroll.setWidget(self.meta_desc)
        
        self.toggle_desc_btn = QPushButton("Show More")
        self.toggle_desc_btn.setObjectName("secondary")
        self.toggle_desc_btn.setFixedWidth(100)
        self.toggle_desc_btn.clicked.connect(self.toggle_description)
        self.toggle_desc_btn.hide() # Hide until meta loaded

        desc_container.addWidget(self.desc_scroll)
        desc_container.addWidget(self.toggle_desc_btn)
        content_layout.addLayout(desc_container)
        content_layout.addStretch()

        splitter.addWidget(self.content_card)

        # --- RIGHT SIDE: Tabs Sidebar ---
        self.tab_sidebar = QTabWidget()
        self.tab_sidebar.setMinimumWidth(400)
        
        # Tab 1: Download
        dl_tab = QWidget()
        dl_layout = QVBoxLayout(dl_tab)
        dl_layout.setSpacing(15)

        dl_layout.addWidget(QLabel("<b>Video Quality (Max 1080p)</b>"))
        self.quality_combo = QComboBox()
        self.quality_combo.setEnabled(False)
        dl_layout.addWidget(self.quality_combo)

        dl_layout.addWidget(QLabel("<b>Audio Track</b>"))
        self.audio_combo = QComboBox()
        self.audio_combo.setEnabled(False)
        dl_layout.addWidget(self.audio_combo)

        dl_layout.addStretch()
        
        self.download_btn = QPushButton(" Download Video")
        self.download_btn.setObjectName("primary")
        self.download_btn.setIcon(qta.icon('fa5s.download', color='white'))
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.start_download_video)
        dl_layout.addWidget(self.download_btn)

        # Tab 2: Transcript
        sub_tab = QWidget()
        sub_layout = QVBoxLayout(sub_tab)
        sub_layout.setSpacing(15)

        sub_layout.addWidget(QLabel("<b>Available Transcripts</b>"))
        self.subs_combo = QComboBox()
        self.subs_combo.setEnabled(False)
        sub_layout.addWidget(self.subs_combo)

        sub_layout.addStretch()

        self.dl_subs_btn = QPushButton(" Download Transcript")
        self.dl_subs_btn.setObjectName("primary")
        self.dl_subs_btn.setStyleSheet("background-color: #0077cc;")
        self.dl_subs_btn.setIcon(qta.icon('fa5s.closed-captioning', color='white'))
        self.dl_subs_btn.setEnabled(False)
        self.dl_subs_btn.clicked.connect(self.start_download_subs)
        sub_layout.addWidget(self.dl_subs_btn)

        self.tab_sidebar.addTab(dl_tab, "Download")
        self.tab_sidebar.addTab(sub_tab, "Transcript")
        
        # Tab 3: Explorer
        self.explorer_tab = ExplorerTab(self.diary)
        self.explorer_tab.status_message_signal.connect(self.statusBar().showMessage)
        self.tab_sidebar.addTab(self.explorer_tab, "Explorer")
        
        splitter.addWidget(self.tab_sidebar)
        splitter.setSizes([800, 400])
        main_layout.addWidget(splitter)

        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

        # Setup Menu
        self.setup_menu()

        self.apply_theme(DARK_THEME)
        # self.explorer_tab.refresh_explorer() is already called in ExplorerTab.__init__

    def setup_menu(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")
        
        exit_action = QAction(qta.icon('fa5s.power-off'), "Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Actions Menu
        actions_menu = menubar.addMenu("&Actions")

        fetch_action = QAction(qta.icon('fa5s.search'), "Fetch Video Data", self)
        fetch_action.setShortcut("Ctrl+F")
        fetch_action.triggered.connect(self.load_video_data)
        actions_menu.addAction(fetch_action)

        actions_menu.addSeparator()

        download_video_action = QAction(qta.icon('fa5s.download'), "Download Video", self)
        download_video_action.setShortcut("Ctrl+D")
        download_video_action.triggered.connect(self.start_download_video)
        actions_menu.addAction(download_video_action)

        download_subs_action = QAction(qta.icon('fa5s.closed-captioning'), "Download Transcript", self)
        download_subs_action.setShortcut("Ctrl+T")
        download_subs_action.triggered.connect(self.start_download_subs)
        actions_menu.addAction(download_subs_action)

        # View Menu
        view_menu = menubar.addMenu("&View")

        refresh_action = QAction(qta.icon('fa5s.sync'), "Refresh Library", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(lambda: self.explorer_tab.refresh_explorer())
        view_menu.addAction(refresh_action)

        theme_action = QAction(qta.icon('fa5s.adjust'), "Toggle Theme", self)
        theme_action.setShortcut("Ctrl+L")
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        how_to_action = QAction(qta.icon('fa5s.question-circle'), "How to Use", self)
        how_to_action.triggered.connect(self.show_help)
        help_menu.addAction(how_to_action)

        credits_action = QAction(qta.icon('fa5s.info-circle'), "Credits", self)
        credits_action.triggered.connect(self.show_credits)
        help_menu.addAction(credits_action)

    def show_help(self):
        help_text = """
        <h3>How to Use Youtube Video Manager</h3>
        <ol>
            <li><b>Fetch:</b> Paste a YouTube URL or ID in the top bar and click 'Fetch' (or press Enter).</li>
            <li><b>Select Quality:</b> Choose your preferred video resolution and audio track in the 'Download' tab.</li>
            <li><b>Download:</b> Click 'Download Video' to start. Files are saved in the <i>videos/</i> folder.</li>
            <li><b>Transcripts:</b> Use the 'Transcript' tab to download CC files as .srt.</li>
            <li><b>Explorer:</b> Manage your local files in the 'Explorer' tab. Click a title to play it!</li>
            <li><b>Shortcuts:</b> 
                <ul>
                    <li>Ctrl+F: Fetch</li>
                    <li>Ctrl+D: Download Video</li>
                    <li>Ctrl+T: Download Transcript</li>
                    <li>F5: Refresh Library</li>
                </ul>
            </li>
        </ol>
        """
        QMessageBox.about(self, "How to Use", help_text)

    def show_credits(self):
        credits_text = """
        <h3>Youtube Video Manager</h3>
        <p>Built with ❤️ using PySide6 and yt-dlp.</p>
        <p><b>Version:</b> 2.1.0</p>
        <p><b>Developer:</b> Ajendra Sharma</p>
        <p>This tool is designed for personal media archival and analysis.</p>
        """
        QMessageBox.about(self, "Credits", credits_text)

    def apply_theme(self, theme_stylesheet):
        self.setStyleSheet(theme_stylesheet)

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.apply_theme(LIGHT_THEME)
            self.current_theme = "light"
            self.theme_btn.setIcon(qta.icon('fa5s.sun', color='#1D1D1F'))
            self.browser_btn.setIcon(qta.icon('fa5s.external-link-alt', color='#1D1D1F'))
            self.explorer_tab.set_theme_style("light")
        else:
            self.apply_theme(DARK_THEME)
            self.current_theme = "dark"
            self.theme_btn.setIcon(qta.icon('fa5s.moon', color='white'))
            self.browser_btn.setIcon(qta.icon('fa5s.external-link-alt', color='white'))
            self.explorer_tab.set_theme_style("dark")

    def update_completer(self):
        urls = self.diary.get_history_urls()
        self.completer_model.setStringList(urls)

    def open_current_url(self):
        url = self.url_input.text().strip()
        if url:
            # Handle video ID
            if len(url) == 11 and re.match(r"^[a-zA-Z0-9_-]{11}$", url):
                url = f"https://www.youtube.com/watch?v={url}"
            webbrowser.open(url)

    def toggle_description(self):
        if self.desc_expanded:
            self.desc_scroll.setFixedHeight(100)
            self.toggle_desc_btn.setText("Show More")
            self.desc_expanded = False
        else:
            self.desc_scroll.setFixedHeight(300) 
            self.toggle_desc_btn.setText("Show Less")
            self.desc_expanded = True

    def load_video_data(self):
        url = self.url_input.text().strip()
        if not url: return

        # Support Video ID
        if len(url) == 11 and re.match(r"^[a-zA-Z0-9_-]{11}$", url):
            url = f"https://www.youtube.com/watch?v={url}"
            self.url_input.setText(url)

        self.statusBar().showMessage("Fetching metadata...")
        self.quality_combo.clear(); self.audio_combo.clear(); self.subs_combo.clear()
        self.fetch_btn.setEnabled(False)
        
        # Reset UI
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("Loading Preview...")
        self.meta_title.setText("Loading...")
        self.meta_creator.setText("")
        self.meta_desc.setText("")
        self.toggle_desc_btn.hide()

        # Fetch in thread (conceptually - simplistic here to keep single-block logic readable)
        # For 'uv run' context let's do synchronous but robust, or simple thread wrapper
        # To avoid blocking UI too much, we usually use Worker. 
        # For simplicity in this step, I'll execute inline but alert via status.
        # Ideally this should be threaded like DownloadThread.
        
        QApplication.processEvents() # Force UI update

        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                self.current_info = info
                
                # 1. Metadata
                self.meta_title.setText(info.get('title', 'Unknown'))
                
                uploader = info.get('uploader', 'Unknown')
                uploader_url = info.get('uploader_url') or info.get('channel_url')
                if uploader_url:
                    self.meta_creator.setText(f'<a href="{uploader_url}">{uploader}</a>')
                else:
                    self.meta_creator.setText(uploader)

                self.meta_desc.setText(info.get('description', ''))
                self.toggle_desc_btn.show()
                self.toggle_desc_btn.setText("Show More")
                self.desc_scroll.setFixedHeight(100)
                self.desc_expanded = False
                
                # 2. Thumbnail
                thumb_url = info.get('thumbnail')
                if thumb_url:
                    self.thumb_thread = ThumbnailThread(thumb_url)
                    self.thumb_thread.loaded_signal.connect(self.set_thumbnail)
                    self.thumb_thread.start()

                # 3. Formats (Video)
                formats = info.get('formats', [])
                video_options = []
                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('height'):
                        h = f['height']
                        if h <= 1080: # Max 1080p
                            # We want video-only usually to mix with best audio
                            # But yt-dlp formats list serves both mixed and unmixed.
                            # We'll filter for mp4/video-only preference
                            video_options.append((h, f))
                
                # Sort Descending by Height
                video_options.sort(key=lambda x: x[0], reverse=True)
                
                seen_res = set()
                # Determine dynamic 'Best' label
                best_vid_text = "Best Available (Max 1080p)"
                if video_options:
                    best_vid_text = f"Best Available ({video_options[0][0]}p)"
                
                self.quality_combo.addItem(best_vid_text, "best_1080")
                for h, f in video_options:
                    res_str = f"{h}p"
                    if res_str not in seen_res:
                        self.quality_combo.addItem(f"{res_str} - {f.get('ext')}", f['format_id'])
                        seen_res.add(res_str)
 
                # Language names mapping (short list of common ones)
                LANG_MAP = {
                    'en': 'English', 'ko': 'Korean', 'es': 'Spanish', 'ja': 'Japanese',
                    'zh': 'Chinese', 'fr': 'French', 'de': 'German', 'hi': 'Hindi',
                    'ru': 'Russian', 'pt': 'Portuguese', 'it': 'Italian', 'ar': 'Arabic'
                }

                # 4. Audio Tracks - Group by Language & Quality
                audio_tracks = {} # track_key -> format_info
                
                # Helper to clean up notes (remove low/medium)
                def clean_note(note):
                    if not note: return ""
                    # Remove common quality terms
                    n = note.lower()
                    for term in ["low", "medium", "ultra-low", "high"]:
                        n = n.replace(term, "")
                    n = n.strip(", ").strip()
                    return n.title() if n else ""

                for f in formats:
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        code = f.get('language')
                        lang = LANG_MAP.get(code.split('-')[0]) if code else None
                        
                        if not lang:
                             # Some tracks have it in the note or elsewhere
                             # But if really None, use 'Original Audio' as base
                             lang = 'Original Audio' if not code or code == 'und' else code
                        
                        note = clean_note(f.get('format_note'))
                        track_key = (lang, note)
                        
                        abr = f.get('abr') or 0
                        if track_key not in audio_tracks or abr > audio_tracks[track_key].get('abr', 0):
                            audio_tracks[track_key] = f

                # Sort audio tracks
                sorted_audio = sorted(audio_tracks.values(), 
                                    key=lambda x: (x.get('language') or 'und', x.get('abr') or 0), 
                                    reverse=True)

                # Determine dynamic 'Best' label
                best_audio_text = "Default / Best Audio"
                if sorted_audio:
                    f = sorted_audio[0]
                    code = f.get('language')
                    lang = LANG_MAP.get(code.split('-')[0]) if code else None
                    if not lang:
                        lang = 'Original Audio' if not code or code == 'und' else code
                    abr = int(f.get('abr') or 0)
                    best_audio_text = f"Default / Best Audio ({lang} - {abr} kbps)"

                self.audio_combo.addItem(best_audio_text, "bestaudio")
                
                for f in sorted_audio:
                    code = f.get('language')
                    lang = LANG_MAP.get(code.split('-')[0]) if code else None
                    if not lang:
                        lang = 'Original Audio' if not code or code == 'und' else code

                    note = clean_note(f.get('format_note'))
                    abr = int(f.get('abr') or 0)
                    
                    label = f"{lang}"
                    if note: label += f" ({note})"
                    if abr: label += f" - {abr} kbps"
                    
                    self.audio_combo.addItem(label, f['format_id'])

                # 5. Subtitles - Smart CC Handling
                sub_options = []  # List of (label, {"code": ..., "is_auto": ...})
                
                # Helper: English priority scoring
                def en_score(code, label):
                    c = code.lower()
                    l = label.lower()
                    if c == 'en' or l == 'english': return -2
                    if 'en' in c or 'english' in l: return -1
                    return 0
                
                # Helper: Get best label
                def get_sub_label(code, formats):
                    if formats and formats[0].get('name'):
                        name = formats[0].get('name')
                        # Clean up "English - English" -> "English"
                        if " - " in name:
                            parts = name.split(" - ")
                            if parts[0].strip() == parts[1].strip():
                                return parts[0].strip()
                        return name
                    return code

                # Add manual subtitles first (priority)
                manual_subs = info.get('subtitles') or {}
                for code, formats in manual_subs.items():
                    if code == 'live_chat': continue
                    label = get_sub_label(code, formats)
                    sub_options.append((label, {"code": code, "is_auto": False}))
                
                # Add auto-generated (marked clearly)
                auto_subs = info.get('automatic_captions') or {}
                for code, formats in auto_subs.items():
                    if code == 'live_chat': continue
                    # Only add if it's not already in manual for roughly same language
                    # (Note: manual might have code 'en-US' while auto has 'en')
                    # But if manual has ANY English, we might still want Auto English?
                    # The user said: "if manual exists... only display these 2"
                    # So if ANY manual exists for a language, we skip auto for it.
                    # We'll check if any existing code starts with this code or vice versa
                    exists = any(code in m or m in code for m in manual_subs.keys())
                    if not exists:
                        label = f"{get_sub_label(code, formats)} (auto-generated)"
                        sub_options.append((label, {"code": code, "is_auto": True}))
                
                # Sort: English first, then by score, then alphabetically
                sub_options.sort(key=lambda x: (en_score(x[1]["code"], x[0]), x[0]))
                
                # Populate combo
                if sub_options:
                    self.subs_combo.addItem("Select Subtitle", None)
                    for label, data in sub_options:
                        self.subs_combo.addItem(label, data)
                    self.subs_combo.setEnabled(True)
                    self.dl_subs_btn.setEnabled(True)
                else:
                    self.subs_combo.addItem("No CC available", None)
                    self.subs_combo.setEnabled(False)
                    self.dl_subs_btn.setEnabled(False)
                
                # Enable Video Controls
                self.quality_combo.setEnabled(True)
                self.audio_combo.setEnabled(True)
                self.download_btn.setEnabled(True)
                
                self.statusBar().showMessage("Ready")

        except Exception as e:
            self.statusBar().showMessage(f"Error: {str(e)}")
            print(e)
        
        self.fetch_btn.setEnabled(True)

    def set_thumbnail(self, pixmap):
        scaled = pixmap.scaled(self.thumbnail_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.thumbnail_label.setPixmap(scaled)

    def start_download_video(self):
        if not self.current_info: return
        
        url = self.url_input.text()
        vid_fmt = self.quality_combo.currentData()
        audio_fmt = self.audio_combo.currentData()
        
        # Build format selector
        if vid_fmt == "best_1080":
             video_sel = "bestvideo[height<=1080]"
        else:
             video_sel = vid_fmt
        
        if audio_fmt == "bestaudio":
            # Default behavior: best video (<=1080) + best audio
            final_format = f"{video_sel}+bestaudio/best[height<=1080]"
        else:
            # Strict behavior: best video (<=1080) + PRECISE audio selected by user
            # No fallback to 'best' because 'best' might have the wrong language.
            # We want to force video_sel + specific audio_fmt.
            # However, we must handle cases where the video_sel + audio_fmt can't merge.
            # Usually, + handles this if ffmpeg is present.
            final_format = f"{video_sel}+{audio_fmt}"
        
        opts = {
            'format': final_format,
            'merge_output_format': 'mp4',
        }

        context = {
            'type': 'video',
            'title': self.current_info.get('title'),
            'creator': self.current_info.get('uploader'),
            'description': self.current_info.get('description', ''),
            'url': url,
            'format_desc': f"Video: {self.quality_combo.currentText()}, Audio: {self.audio_combo.currentText()}"
        }

        self.start_download(opts, context)

    def start_download_subs(self):
        sub_data = self.subs_combo.currentData()
        if not sub_data or not isinstance(sub_data, dict):
            return
        
        code = sub_data.get("code")
        is_auto = sub_data.get("is_auto", False)
        
        opts = {
            'skip_download': True,
            'subtitleslangs': [code],
            'outtmpl': 'videos/SRT/%(title)s (Subtitle).%(ext)s',
            'writesubtitles': not is_auto,
            'writeautomaticsub': is_auto,
            'subtitlesformat': 'srt',
            'convertsubtitles': 'srt',
        }
        
        context = {
            'type': 'subtitle',
            'title': self.current_info.get('title'),
            'creator': self.current_info.get('uploader'),
            'description': "Subtitle File",
            'url': self.url_input.text(),
            'format_desc': f"Subtitle ({code}{' auto' if is_auto else ''})"
        }
        
        self.start_download(opts, context)

    def start_download(self, opts, context):
        self.download_btn.setEnabled(False)
        self.dl_subs_btn.setEnabled(False)
        
        self.download_thread = DownloadThread(self.url_input.text(), opts, context)
        self.download_thread.progress_signal.connect(self.statusBar().showMessage)
        self.download_thread.finished_signal.connect(self.on_download_finished)
        self.download_thread.start()

    def on_download_finished(self, result_info):
        self.download_btn.setEnabled(True)
        self.dl_subs_btn.setEnabled(True)
        
        if result_info.get('filepath'):
            self.statusBar().showMessage("Download Successful")
            
            is_sub = result_info.get('type') == 'subtitle'
            
            self.diary.save_entry(
                title=result_info.get('title', 'Unknown'),
                url=result_info.get('url', ''),
                creator=result_info.get('creator', 'Unknown'),
                description=result_info.get('description', ''),
                format_info=result_info.get('format_desc', ''),
                video_path=result_info['filepath'] if not is_sub else None,
                srt_path=result_info['filepath'] if is_sub else None
            )
            self.update_completer()
            QMessageBox.information(self, "Download Complete", f"Saved to: {result_info['filepath']}")
        else:
             self.statusBar().showMessage("Download Failed")
        self.explorer_tab.refresh_explorer()


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/logo.png"))
    window = YouTubeApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()