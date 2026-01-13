import os
import webbrowser
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QFrame, QTableWidget, QTableWidgetItem, 
                                QAbstractItemView, QHeaderView, QPushButton,
                                QMessageBox)
from PySide6.QtCore import Qt, Signal

class ExplorerTab(QWidget):
    status_message_signal = Signal(str)

    def __init__(self, diary_manager, parent=None):
        super().__init__(parent)
        self.diary = diary_manager
        self.setup_ui()
        self.refresh_explorer()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Stats Area
        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("stats_card")
        stats_layout = QHBoxLayout(self.stats_frame)
        
        self.stat_videos = QLabel("Videos: 0")
        self.stat_size = QLabel("Size: 0 MB")
        self.stat_srts = QLabel("SRTs: 0")
        for lbl in [self.stat_videos, self.stat_size, self.stat_srts]:
            lbl.setObjectName("stat_label")
            stats_layout.addWidget(lbl)
        
        layout.addWidget(self.stats_frame)

        # Table for videos
        self.explorer_table = QTableWidget(0, 4)
        self.explorer_table.setHorizontalHeaderLabels(["Video Title", "Size", "SRT", "Actions"])
        self.explorer_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.explorer_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.explorer_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.explorer_table.setShowGrid(False)
        
        layout.addWidget(self.explorer_table)
        
        self.refresh_btn = QPushButton(" Refresh Library")
        self.refresh_btn.setObjectName("refresh_btn")
        self.refresh_theme_icons("white")
        self.refresh_btn.clicked.connect(self.refresh_explorer)
        layout.addWidget(self.refresh_btn)

    def set_theme_style(self, theme):
        icon_color = "white" if theme == "dark" else "#1D1D1F"
        self.refresh_theme_icons(icon_color)
        self.refresh_explorer() # Redraw with new icon colors

    def refresh_theme_icons(self, color):
        self.refresh_btn.setIcon(qta.icon('fa5s.sync', color=color))

    def refresh_explorer(self):
        entries = self.diary.get_all_entries()
        self.explorer_table.setRowCount(0)
        
        total_size = 0
        srt_count = 0
        video_count = 0
        
        is_dark = self.refresh_btn.palette().buttonText().color().lightness() > 128
        # Simple detection might not work if stylesheet is active, but we can pass the theme state if needed.
        # Let's just use the current icon color logic.
        icon_color = "#CC0000" # Red icons for actions look good on both
        
        for entry in entries:
            row = self.explorer_table.rowCount()
            self.explorer_table.insertRow(row)
            
            # 1. Title (Clickable)
            title = entry.get('title', 'Unknown')
            # Use robust resolution from diary
            v_path = self.diary.resolve_path(entry.get('video_path'))
            
            title_btn = QPushButton(title)
            title_btn.setStyleSheet("text-align: left; border: none; color: #3498db; text-decoration: underline; background: transparent;")
            title_btn.setCursor(Qt.PointingHandCursor)
            title_btn.clicked.connect(lambda checked, p=v_path: self.play_video(p))
            self.explorer_table.setCellWidget(row, 0, title_btn)
            
            # 2. Size
            size_str = "N/A"
            if v_path and os.path.exists(v_path):
                video_count += 1
                s = os.path.getsize(v_path)
                total_size += s
                size_str = f"{s/1024/1024:.1f} MB"
            
            self.explorer_table.setItem(row, 1, QTableWidgetItem(size_str))
            
            # 3. SRT Status
            srt_path = self.diary.resolve_path(entry.get('srt_path'))
            has_srt = srt_path and os.path.exists(srt_path)
            if has_srt: srt_count += 1
            srt_icon = "✅" if has_srt else "❌"
            self.explorer_table.setItem(row, 2, QTableWidgetItem(srt_icon))
            
            # 4. Actions (URL + Delete)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            url_btn = QPushButton()
            url_btn.setIcon(qta.icon('fa5s.external-link-alt', color=icon_color))
            url_btn.setToolTip("Open YouTube Link")
            url_btn.setStyleSheet("border: none; background: transparent;")
            url_btn.clicked.connect(lambda checked, u=entry.get('url'): webbrowser.open(u))
            
            del_btn = QPushButton()
            del_btn.setIcon(qta.icon('fa5s.trash-alt', color=icon_color))
            del_btn.setToolTip("Delete Video & Entry")
            del_btn.setStyleSheet("border: none; background: transparent;")
            del_btn.clicked.connect(lambda checked, eid=entry.get('id'): self.delete_video(eid))
            
            actions_layout.addWidget(url_btn)
            actions_layout.addWidget(del_btn)
            self.explorer_table.setCellWidget(row, 3, actions_widget)
            
        self.stat_videos.setText(f"Videos: {video_count}")
        self.stat_size.setText(f"Size: {total_size/1024/1024:.1f} MB")
        self.stat_srts.setText(f"SRTs: {srt_count}")

    def play_video(self, path):
        if path and os.path.exists(path):
            try:
                os.startfile(os.path.abspath(path))
            except Exception as e:
                QMessageBox.warning(self, "Playback Error", f"Could not open video: {e}")
        else:
            QMessageBox.warning(self, "File Not Found", "The video file no longer exists at the recorded location.")

    def delete_video(self, entry_id):
        reply = QMessageBox.question(self, 'Confirm Deletion', 
                                   "Are you sure you want to delete this video and its history entry?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.diary.delete_entry(entry_id):
                self.refresh_explorer()
                self.status_message_signal.emit("Entry deleted")
            else:
                self.status_message_signal.emit("Failed to delete entry")
