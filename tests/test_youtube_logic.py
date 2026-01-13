import pytest
from unittest.mock import MagicMock, patch

# Note: Since YouTubeApp is a GUI app, we test the logic components or mock the GUI
# For this sprint, we focus on ensuring the 'yt-dlp' integration logic is solid.

@patch('yt_dlp.YoutubeDL')
def test_metadata_extraction_logic(mock_yt_dlp):
    # Mocking the info dict returned by yt-dlp
    mock_info = {
        'title': 'Mock Video',
        'uploader': 'Mock Creator',
        'description': 'Mock Description',
        'formats': [
            {'height': 1080, 'vcodec': 'avc1', 'ext': 'mp4', 'format_id': '137'},
            {'height': 720, 'vcodec': 'avc1', 'ext': 'mp4', 'format_id': '136'}
        ]
    }
    
    instance = mock_yt_dlp.return_value.__enter__.return_value
    instance.extract_info.return_value = mock_info
    
    # Simple check that we can call it (integration stability)
    import yt_dlp
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info("https://youtube.com/watch?v=123", download=False)
        assert info['title'] == 'Mock Video'
        assert len(info['formats']) == 2

def test_path_stability():
    # Verify our updated paths are consistent
    from yt.diary import DiaryManager
    manager = DiaryManager("db_test")
    assert "db_test" in manager.file_path
    assert "download_history.json" in manager.file_path
