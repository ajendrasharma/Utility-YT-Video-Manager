# YT AI Analyst v2

**YT AI Analyst** is a modern, desktop-based YouTube media manager built with Python and PySide6. It allows you to download videos, extract subtitles, and manage your local library with a sleek, dark-mode interface.

## 🚀 Key Features

- **Smart Downloader**: Fetch videos in up to 1080p with selectable audio tracks.
- **Transcript Extraction**: Download subtitles/captions (manual or auto-generated) as `.srt` files.
- **Explorer Tab**: Manage your downloaded library:
  - One-click native video playback (Windows Media Player).
  - Track storage usage and subtitle availability.
  - Securely delete videos and history entries.
- **Robust History**: Local JSON database (`db/download_history.json`) tracks all your downloads.
- **Resilient File Handling**: Automatically detects downloaded files even if formats change (e.g., `.webm` merged to `.mp4`).

## 🛠️ Installation & Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast package management.

### Prerequisites

- Python 3.13+
- Windows 10/11 (for native playback features)
- `uv` installed (`pip install uv`)

### Quick Start

1.  **Clone the repository**:

    ```powershell
    git clone <repo-url>
    cd YT
    ```

2.  **Install dependencies**:

    ```powershell
    uv sync
    ```

3.  **Run the application**:
    ```powershell
    uv run yt
    ```

## 📦 Deployment (Build .exe)

You can package the application into a standalone Windows Executable that requires no Python installation to run.

1.  **Run the build script**:

    ```powershell
    uv run python deployment/build_exe.py
    ```

2.  **Locate the executable**:
    The file will be generated at: `deployment/dist/YT_AI_Analyst.exe`.

## 🧪 Development

### Project Structure

- `src/yt/`: Main source code.
  - `main.py`: UI and Application logic.
  - `diary.py`: Database and file management.
- `assets/`: Icons and static resources.
- `tests/`: Unit and integration tests.
- `deployment/`: PyInstaller configuration and output.

### Running Tests

To ensure stability, run the test suite using `pytest`:

```powershell
uv run pytest
```
