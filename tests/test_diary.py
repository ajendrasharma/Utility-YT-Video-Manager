import os
import json
import pytest
from yt.diary import DiaryManager

@pytest.fixture
def temp_db(tmp_path):
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    return db_dir

def test_diary_initialization(temp_db):
    manager = DiaryManager(storage_dir=str(temp_db))
    assert os.path.exists(manager.file_path)
    with open(manager.file_path, 'r') as f:
        assert json.load(f) == []

def test_save_entry(temp_db):
    manager = DiaryManager(storage_dir=str(temp_db))
    manager.save_entry(
        title="Test Video",
        url="https://youtube.com/watch?v=123",
        creator="Test Creator",
        description="Test Desc",
        format_info="1080p",
        video_path="videos/test.mp4"
    )
    
    urls = manager.get_history_urls()
    assert "https://youtube.com/watch?v=123" in urls
    
    with open(manager.file_path, 'r') as f:
        history = json.load(f)
        assert len(history) == 1
        assert history[0]['title'] == "Test Video"

def test_clear_history(temp_db):
    manager = DiaryManager(storage_dir=str(temp_db))
    manager.save_entry("T", "U", "C", "D", "F")
    manager.clear_history()
    assert manager.get_history_urls() == []
